from __future__ import annotations

import json
import os
import re
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import ChromeOptions
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from .browser_runtime import BrowserRuntimeManager
from .config import WorkerConfig
from .control_plane import YouTubeUploadTarget


UploadProgressCallback = Callable[[float, str | None], None]

VI_15_MINUTES = "15 ph\u00fat"
VI_VERIFY = "x\u00e1c minh"
VI_PHONE = "\u0111i\u1ec7n tho\u1ea1i"
VI_UPLOAD_LIMIT = "qu\u00e1 gi\u1edbi h\u1ea1n t\u1ea3i l\u00ean"
VI_UPLOAD_LIMIT_EXCEEDED = "\u0111\u00e3 v\u01b0\u1ee3t gi\u1edbi h\u1ea1n t\u1ea3i l\u00ean"
VI_UPLOAD_FAILED = "t\u1ea3i l\u00ean kh\u00f4ng th\u00e0nh c\u00f4ng"
VI_CANT_UPLOAD = "kh\u00f4ng th\u1ec3 t\u1ea3i video"
VI_UPLOAD_ERROR = "\u0111\u00e3 x\u1ea3y ra l\u1ed7i khi t\u1ea3i l\u00ean"
VI_PROCESSING = "\u0111ang ch\u1edd x\u1eed l\u00fd"
VI_TRANSFER_COMPLETE = "\u0111\u00e3 t\u1ea3i \u0111\u01b0\u1ee3c 100%"
VI_CANCEL_UPLOAD = "h\u1ee7y t\u1ea3i l\u00ean"
VI_UPLOADED = "\u0111\u00e3 t\u1ea3i l\u00ean"

PROCESSING_ROW_TOKENS = (
    VI_PROCESSING,
    "checking",
    "processing",
    VI_TRANSFER_COMPLETE,
    "uploaded 100%",
    VI_CANCEL_UPLOAD,
    "cancel upload",
)

UPLOADED_ROW_TOKENS = (
    VI_UPLOADED,
    "uploaded",
    "published",
    "scheduled",
)


@dataclass
class BrowserUploadResult:
    studio_url: str
    watch_url: str | None = None
    cleanup_safe: bool = False


def _read_visible_page_text(driver: webdriver.Chrome) -> str:
    snippets: list[str] = []
    for xpath in (
        "//ytcp-uploads-dialog",
        "//*[@role='dialog']",
        "//body",
    ):
        for element in driver.find_elements(By.XPATH, xpath):
            if not element.is_displayed():
                continue
            text = re.sub(r"\s+", " ", (element.text or "").strip())
            if text:
                snippets.append(text)
        if snippets:
            break
    return " ".join(snippets)


def _detect_blocking_upload_error_safe(driver: webdriver.Chrome) -> str | None:
    page_text = _read_visible_page_text(driver).casefold()
    if not page_text:
        return None

    if (
        any(token in page_text for token in ("15 minutes", "longer than 15 minutes", VI_15_MINUTES))
        and (
            "verify" in page_text
            or VI_VERIFY in page_text
            or "phone number" in page_text
            or "verify your phone number" in page_text
            or VI_PHONE in page_text
            or "increase your limit" in page_text
        )
    ):
        return "K\u00eanh n\u00e0y ch\u01b0a x\u00e1c minh n\u00ean ch\u01b0a th\u1ec3 \u0111\u0103ng video d\u00e0i h\u01a1n 15 ph\u00fat."

    if any(
        token in page_text
        for token in (
            "daily upload limit",
            "upload limit exceeded",
            "too many videos",
            VI_UPLOAD_LIMIT,
            VI_UPLOAD_LIMIT_EXCEEDED,
        )
    ):
        return "K\u00eanh n\u00e0y \u0111\u00e3 ch\u1ea1m gi\u1edbi h\u1ea1n upload c\u1ee7a YouTube. H\u00e3y th\u1eed l\u1ea1i sau."

    if any(
        token in page_text
        for token in (
            "there was a problem uploading",
            "couldn't upload",
            "we couldn't upload your video",
            "upload failed",
            VI_UPLOAD_FAILED,
            VI_CANT_UPLOAD,
            VI_UPLOAD_ERROR,
        )
    ):
        return "YouTube Studio b\u00e1o l\u1ed7i upload. H\u00e3y ki\u1ec3m tra l\u1ea1i k\u00eanh r\u1ed3i th\u1eed l\u1ea1i job."

    return None


def _detect_blocking_upload_error(driver: webdriver.Chrome) -> str | None:
    page_text = _read_visible_page_text(driver).lower()
    if not page_text:
        return None

    if (
        any(token in page_text for token in ("15 minutes", "longer than 15 minutes", "15 phút"))
        and (
            "verify" in page_text
            or "xác minh" in page_text
            or "phone number" in page_text
            or "verify your phone number" in page_text
            or "điện thoại" in page_text
            or "increase your limit" in page_text
        )
    ):
        return "Kênh này chưa xác minh nên chưa thể đăng video dài hơn 15 phút."

    if any(
        token in page_text
        for token in (
            "daily upload limit",
            "upload limit exceeded",
            "too many videos",
            "quá giới hạn tải lên",
            "đã vượt giới hạn tải lên",
        )
    ):
        return "Kênh này đã chạm giới hạn upload của YouTube. Hãy thử lại sau."

    if any(
        token in page_text
        for token in (
            "there was a problem uploading",
            "couldn't upload",
            "we couldn't upload your video",
            "upload failed",
            "tải lên không thành công",
            "không thể tải video",
            "đã xảy ra lỗi khi tải lên",
        )
    ):
        return "YouTube Studio báo lỗi upload. Hãy kiểm tra lại kênh rồi thử lại job."

    return None


def _raise_if_upload_blocked(driver: webdriver.Chrome) -> None:
    detected_message = _detect_blocking_upload_error_safe(driver) or _detect_blocking_upload_error(driver)
    if detected_message:
        raise RuntimeError(detected_message)


def _format_browser_exception(exc: Exception, driver: webdriver.Chrome | None = None) -> str:
    detected_message = (
        (_detect_blocking_upload_error_safe(driver) or _detect_blocking_upload_error(driver))
        if driver is not None
        else None
    )
    if detected_message:
        return detected_message

    exception_name = exc.__class__.__name__
    detail = re.sub(r"\s+", " ", str(exc or "")).strip(" :\n\t")
    if detail and detail.lower() not in {"message", exception_name.lower()}:
        if exception_name == "RuntimeError":
            return detail
        return f"{exception_name}: {detail}"
    return f"{exception_name}: Khong the hoan tat browser upload tren YouTube Studio."


def _normalize_title(value: str | None) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip()).casefold()


def _build_job_marker(job_id: str) -> str:
    marker = re.sub(r"[^a-z0-9-]", "", str(job_id or "").strip().lower())
    return f"[job-marker:{marker}]"


def _merge_description_with_marker(description: str | None, marker: str) -> str:
    base = str(description or "").rstrip()
    if marker.casefold() in base.casefold():
        return base
    return f"{base}\n\n{marker}".strip()


def _pick_display_number(start: int = 300, end: int = 360) -> int:
    for candidate in range(start, end):
        if not Path(f"/tmp/.X11-unix/X{candidate}").exists():
            return candidate
    raise RuntimeError("Khong tim thay DISPLAY trong de mo browser upload.")


def _stop_process(process: subprocess.Popen[bytes] | None) -> None:
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=5)
        return
    except subprocess.TimeoutExpired:
        process.kill()
    process.wait(timeout=5)


def _set_textbox(driver: webdriver.Chrome, element, value: str) -> None:
    driver.execute_script(
        """
        const element = arguments[0];
        const value = arguments[1];
        element.focus();
        if ('value' in element) {
          element.value = value;
        } else {
          element.textContent = value;
          element.innerText = value;
        }
        element.dispatchEvent(new Event('input', { bubbles: true }));
        element.dispatchEvent(new Event('change', { bubbles: true }));
        """,
        element,
        value,
    )


def _collect_upload_dialog_editors(driver: webdriver.Chrome) -> list[object]:
    script = """
    const dialog = document.querySelector('ytcp-uploads-dialog') || document;
    const selectors = [
      '#textbox',
      '[contenteditable="true"]',
      'textarea',
      'input:not([type="file"])',
      '[role="textbox"]'
    ];
    const nodes = [];
    for (const selector of selectors) {
      for (const node of dialog.querySelectorAll(selector)) {
        if (!node || nodes.includes(node)) continue;
        const rect = node.getBoundingClientRect();
        const style = window.getComputedStyle(node);
        if (!rect || rect.width < 8 || rect.height < 8) continue;
        if (style.display === 'none' || style.visibility === 'hidden') continue;
        const text = [
          node.getAttribute('aria-label') || '',
          node.getAttribute('label') || '',
          node.getAttribute('placeholder') || '',
          node.id || '',
          node.name || '',
          node.textContent || ''
        ].join(' ').toLowerCase();
        nodes.push({
          element: node,
          score:
            (text.includes('title') || text.includes('tiêu đề') ? 4 : 0) +
            (text.includes('description') || text.includes('mô tả') ? 2 : 0) +
            (node.id === 'textbox' ? 1 : 0),
        });
      }
    }
    nodes.sort((a, b) => b.score - a.score);
    return nodes.map((item) => item.element);
    """
    try:
        return list(driver.execute_script(script) or [])
    except Exception:
        return []


def _find_title_and_description_boxes(driver: webdriver.Chrome, wait: WebDriverWait) -> tuple[object, object | None]:
    def _locate(drv: webdriver.Chrome):
        visible = _collect_upload_dialog_editors(drv)
        if not visible:
            return False
        title_box = visible[0]
        description_box = visible[1] if len(visible) > 1 else None
        return title_box, description_box

    result = wait.until(_locate)
    return result[0], result[1]


def _collect_upload_dialog_editors(driver: webdriver.Chrome) -> list[object]:
    script = """
    const selectors = [
      '#textbox',
      '[contenteditable="true"]',
      'textarea',
      'input:not([type="file"])',
      '[role="textbox"]'
    ];
    const roots = [];
    const seenRoots = new Set();
    const queue = [document];
    while (queue.length) {
      const root = queue.shift();
      if (!root || seenRoots.has(root)) continue;
      seenRoots.add(root);
      roots.push(root);
      const elements = root.querySelectorAll ? root.querySelectorAll('*') : [];
      for (const element of elements) {
        if (element && element.shadowRoot && !seenRoots.has(element.shadowRoot)) {
          queue.push(element.shadowRoot);
        }
      }
    }
    const dialogs = [];
    for (const root of roots) {
      if (!root.querySelectorAll) continue;
      for (const dialog of root.querySelectorAll('ytcp-uploads-dialog, [role="dialog"]')) {
        if (!dialog || dialogs.includes(dialog)) continue;
        dialogs.push(dialog);
      }
    }
    const searchRoots = dialogs.length ? dialogs : roots;
    const nodes = [];
    for (const root of searchRoots) {
      if (!root.querySelectorAll) continue;
      for (const selector of selectors) {
        for (const node of root.querySelectorAll(selector)) {
          if (!node || nodes.some((item) => item.element === node)) continue;
          const rect = node.getBoundingClientRect();
          const style = window.getComputedStyle(node);
          if (!rect || rect.width < 8 || rect.height < 8) continue;
          if (style.display === 'none' || style.visibility === 'hidden') continue;
          const text = [
            node.getAttribute('aria-label') || '',
            node.getAttribute('label') || '',
            node.getAttribute('placeholder') || '',
            node.id || '',
            node.name || '',
            node.textContent || ''
          ].join(' ').toLowerCase();
          nodes.push({
            element: node,
            score:
              (text.includes('title') || text.includes('tiêu đề') ? 6 : 0) +
              (text.includes('description') || text.includes('mô tả') ? 4 : 0) +
              (text.includes('details') ? 2 : 0) +
              (node.id === 'textbox' ? 1 : 0),
          });
        }
      }
    }
    nodes.sort((a, b) => b.score - a.score);
    return nodes.map((item) => item.element);
    """
    try:
        return list(driver.execute_script(script) or [])
    except Exception:
        return []


def _collect_upload_dialog_debug(driver: webdriver.Chrome) -> dict[str, object]:
    script = """
    const roots = [];
    const seenRoots = new Set();
    const queue = [document];
    while (queue.length) {
      const root = queue.shift();
      if (!root || seenRoots.has(root)) continue;
      seenRoots.add(root);
      roots.push(root);
      const elements = root.querySelectorAll ? root.querySelectorAll('*') : [];
      for (const element of elements) {
        if (element && element.shadowRoot && !seenRoots.has(element.shadowRoot)) {
          queue.push(element.shadowRoot);
        }
      }
    }
    const selectors = ['#textbox', '[contenteditable="true"]', 'textarea', 'input:not([type="file"])', '[role="textbox"]'];
    const candidates = [];
    for (const root of roots) {
      if (!root.querySelectorAll) continue;
      for (const selector of selectors) {
        for (const node of root.querySelectorAll(selector)) {
          if (!node || candidates.some((item) => item.element === node)) continue;
          const rect = node.getBoundingClientRect();
          const style = window.getComputedStyle(node);
          if (!rect || rect.width < 8 || rect.height < 8) continue;
          if (style.display === 'none' || style.visibility === 'hidden') continue;
          candidates.push({
            element: node,
            tag: (node.tagName || '').toLowerCase(),
            id: node.id || '',
            name: node.getAttribute('name') || '',
            ariaLabel: node.getAttribute('aria-label') || '',
            label: node.getAttribute('label') || '',
            placeholder: node.getAttribute('placeholder') || '',
            role: node.getAttribute('role') || '',
            text: (node.textContent || '').trim().slice(0, 160),
            classes: (node.className || '').toString().slice(0, 160),
            rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
          });
        }
      }
    }
    return {
      url: window.location.href,
      title: document.title,
      readyState: document.readyState,
      rootCount: roots.length,
      dialogCount: roots.reduce((count, root) => count + (root.querySelectorAll ? root.querySelectorAll('ytcp-uploads-dialog, [role="dialog"]').length : 0), 0),
      visibleText: (document.body?.innerText || '').slice(0, 4000),
      candidates: candidates.slice(0, 25),
    };
    """
    try:
        payload = driver.execute_script(script)
    except Exception as exc:
        return {"collection_error": str(exc)}
    if isinstance(payload, dict):
        return payload
    return {"payload": payload}


def _capture_upload_debug_artifacts(
    driver: webdriver.Chrome,
    *,
    debug_root: Path,
    job_id: str,
    stage: str,
) -> Path | None:
    timestamp = time.strftime("%Y%m%d-%H%M%S")
    target_dir = debug_root / "browser-upload-debug" / f"{job_id}-{stage}-{timestamp}"
    try:
        target_dir.mkdir(parents=True, exist_ok=True)
        driver.save_screenshot(str(target_dir / "page.png"))
        (target_dir / "page.html").write_text(driver.page_source, encoding="utf-8")
        payload = _collect_upload_dialog_debug(driver)
        (target_dir / "dialog.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        return target_dir
    except Exception:
        return None


def _click_when_available(driver: webdriver.Chrome, wait: WebDriverWait, xpath: str) -> bool:
    try:
        element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
    except TimeoutException:
        return False
    driver.execute_script("arguments[0].click();", element)
    return True


def _best_effort_watch_url(driver: webdriver.Chrome) -> str | None:
    anchors = driver.find_elements(By.XPATH, "//a[contains(@href, 'youtube.com/watch')]")
    for anchor in anchors:
        href = (anchor.get_attribute("href") or "").strip()
        if "youtube.com/watch" in href:
            return href
    edit_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/video/') and contains(@href, '/edit')]")
    for anchor in edit_links:
        href = (anchor.get_attribute("href") or "").strip()
        match = re.search(r"/video/([^/?]+)/edit", href)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}"
    return None


def _extract_row_text_from_element(driver: webdriver.Chrome, element) -> str:
    try:
        row_text = driver.execute_script(
            """
            const element = arguments[0];
            const row = element.closest('ytcp-video-row,[role="row"],tr,tp-yt-paper-item') || element;
            return (row.innerText || row.textContent || '').trim();
            """,
            element,
        )
    except Exception:
        row_text = ""
    return re.sub(r"\s+", " ", str(row_text or "").strip()).casefold()


def _read_visible_textboxes(driver: webdriver.Chrome) -> list[str]:
    values: list[str] = []
    for element in driver.find_elements(By.XPATH, "//*[@id='textbox']"):
        if not element.is_displayed():
            continue
        text = (
            element.get_attribute("value")
            or element.text
            or element.get_attribute("innerText")
            or element.get_attribute("textContent")
            or ""
        )
        normalized = re.sub(r"\s+", " ", str(text or "").strip())
        if normalized:
            values.append(normalized)
    return values


def _page_contains_marker(driver: webdriver.Chrome, marker: str) -> bool:
    marker_cf = marker.casefold()
    for text in _read_visible_textboxes(driver):
        if marker_cf in text.casefold():
            return True
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text or ""
    except Exception:
        body_text = ""
    return marker_cf in body_text.casefold()


def _classify_studio_row(row_text: str) -> str:
    normalized = re.sub(r"\s+", " ", str(row_text or "").strip()).casefold()
    if not normalized:
        return "missing"
    if any(token in normalized for token in PROCESSING_ROW_TOKENS):
        return "processing"
    if any(token in normalized for token in UPLOADED_ROW_TOKENS):
        return "uploaded"
    return "visible"


def _is_studio_row_uploaded(row_text: str) -> bool:
    normalized = re.sub(r"\s+", " ", str(row_text or "").strip()).casefold()
    if not normalized:
        return False
    if any(
        token in normalized
        for token in (
            "đang chờ xử lý",
            "checking",
            "processing",
            "đã tải được 100%",
            "uploaded 100%",
            "hủy tải lên",
            "cancel upload",
        )
    ):
        return False
    return any(
        token in normalized
        for token in (
            "đã tải lên",
            "uploaded",
            "published",
            "scheduled",
        )
    )


def _find_matching_studio_row(driver: webdriver.Chrome, title: str) -> tuple[str | None, str] | None:
    target_title = _normalize_title(title)
    if not target_title:
        return None

    for anchor in driver.find_elements(By.XPATH, "//a[contains(@href, '/video/') and contains(@href, '/edit')]"):
        if not anchor.is_displayed():
            continue
        anchor_title = _normalize_title(anchor.text or anchor.get_attribute("title") or anchor.get_attribute("aria-label"))
        if anchor_title != target_title:
            continue
        href = (anchor.get_attribute("href") or "").strip()
        row_state = _classify_studio_row(_extract_row_text_from_element(driver, anchor))
        match = re.search(r"/video/([^/?]+)/edit", href)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}", row_state
        if href:
            return href, row_state
        return None, row_state

    for element in driver.find_elements(By.XPATH, "//*[@id='video-title' or @title]"):
        if not element.is_displayed():
            continue
        element_title = _normalize_title(element.text or element.get_attribute("title") or element.get_attribute("aria-label"))
        if element_title != target_title:
            continue
        href = (element.get_attribute("href") or "").strip()
        row_state = _classify_studio_row(_extract_row_text_from_element(driver, element))
        match = re.search(r"/video/([^/?]+)/edit", href)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}", row_state
        if href:
            return href, row_state
        return None, row_state
    return None


def _find_matching_studio_row_by_marker(
    driver: webdriver.Chrome,
    *,
    content_list_url: str,
    marker: str,
    title_hint: str,
) -> tuple[str | None, str] | None:
    target_title = _normalize_title(title_hint)
    candidate_links: list[tuple[str, str]] = []

    for anchor in driver.find_elements(By.XPATH, "//a[contains(@href, '/video/') and contains(@href, '/edit')]"):
        if not anchor.is_displayed():
            continue
        href = (anchor.get_attribute("href") or "").strip()
        if not href:
            continue
        row_text = _extract_row_text_from_element(driver, anchor)
        anchor_title = _normalize_title(anchor.text or anchor.get_attribute("title") or anchor.get_attribute("aria-label"))
        if target_title and anchor_title and anchor_title != target_title:
            continue
        candidate_links.append((href, row_text))

    if not candidate_links:
        return None

    original_url = driver.current_url
    for href, row_text in candidate_links[:8]:
        try:
            driver.get(href)
            WebDriverWait(driver, 15).until(lambda drv: bool(_read_visible_textboxes(drv)))
            if not _page_contains_marker(driver, marker):
                continue
            match = re.search(r"/video/([^/?]+)/edit", href)
            watch_url = f"https://www.youtube.com/watch?v={match.group(1)}" if match else href
            return watch_url, _classify_studio_row(row_text)
        except Exception:
            continue
        finally:
            if driver.current_url != content_list_url:
                try:
                    driver.get(content_list_url)
                except Exception:
                    pass
    if driver.current_url != original_url and driver.current_url != content_list_url:
        try:
            driver.get(content_list_url)
        except Exception:
            pass
    return None


def _find_studio_row_watch_url(driver: webdriver.Chrome, title: str) -> tuple[str | None, bool] | None:
    target_title = _normalize_title(title)
    if not target_title:
        return None

    for anchor in driver.find_elements(By.XPATH, "//a[contains(@href, '/video/') and contains(@href, '/edit')]"):
        if not anchor.is_displayed():
            continue
        anchor_title = _normalize_title(anchor.text or anchor.get_attribute("title") or anchor.get_attribute("aria-label"))
        if anchor_title != target_title:
            continue
        href = (anchor.get_attribute("href") or "").strip()
        row_uploaded = _is_studio_row_uploaded(_extract_row_text_from_element(driver, anchor))
        match = re.search(r"/video/([^/?]+)/edit", href)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}", row_uploaded
        if href:
            return href, row_uploaded

    for element in driver.find_elements(By.XPATH, "//*[@id='video-title' or @title]"):
        if not element.is_displayed():
            continue
        element_title = _normalize_title(element.text or element.get_attribute("title") or element.get_attribute("aria-label"))
        if element_title != target_title:
            continue
        href = (element.get_attribute("href") or "").strip()
        row_uploaded = _is_studio_row_uploaded(_extract_row_text_from_element(driver, element))
        match = re.search(r"/video/([^/?]+)/edit", href)
        if match:
            return f"https://www.youtube.com/watch?v={match.group(1)}", row_uploaded
        if href:
            return href, row_uploaded
        return "studio:detected", row_uploaded
    return None


def _extract_upload_ratio(driver: webdriver.Chrome) -> float | None:
    try:
        body_text = driver.find_element(By.TAG_NAME, "body").text
    except Exception:
        body_text = ""

    for pattern in (
        r"Da tai(?: len)? duoc\s*(\d{1,3})%",
        r"Uploading\s*(\d{1,3})%",
        r"Uploaded\s*(\d{1,3})%",
        r"Đã tải(?: lên)? được\s*(\d{1,3})%",
    ):
        match = re.search(pattern, body_text, flags=re.IGNORECASE)
        if not match:
            continue
        try:
            value = float(match.group(1))
        except ValueError:
            continue
        if 0 <= value <= 100:
            return value / 100.0

    candidates: list[float] = []
    for xpath in (
        "//*[@aria-valuenow]",
        "//progress[@value]",
    ):
        for element in driver.find_elements(By.XPATH, xpath):
            if not element.is_displayed():
                continue
            raw_value = (element.get_attribute("aria-valuenow") or element.get_attribute("value") or "").strip()
            if not raw_value:
                continue
            try:
                value = float(raw_value)
            except ValueError:
                continue
            if 0 <= value <= 100:
                candidates.append(value)

    if not candidates:
        return None
    return max(candidates) / 100.0


def _has_transfer_completed_signal(driver: webdriver.Chrome) -> bool:
    ratio = _extract_upload_ratio(driver)
    if ratio is not None and ratio >= 1.0:
        return True

    page_text = _read_visible_page_text(driver).casefold()
    if not page_text:
        return False
    if VI_TRANSFER_COMPLETE in page_text:
        return True
    if "uploaded 100%" in page_text or "100% uploaded" in page_text:
        return True
    return bool(
        re.search(
            r"(đã tải.*100%.*video lên|100%.*video lên|uploaded.*100%|100%.*uploaded)",
            page_text,
            flags=re.IGNORECASE,
        )
    )


def _has_cancel_upload_button(driver: webdriver.Chrome) -> bool:
    for xpath in (
        "//button[contains(normalize-space(.), 'Huy tai len')]",
        "//button[contains(normalize-space(.), 'Cancel upload')]",
        "//button[contains(normalize-space(.), 'Hủy tải lên')]",
        "//ytcp-button[contains(normalize-space(.), 'Hủy tải lên')]",
        "//ytcp-button[contains(normalize-space(.), 'Cancel upload')]",
    ):
        for element in driver.find_elements(By.XPATH, xpath):
            if element.is_displayed():
                return True
    return False


def _emit_upload_progress(
    progress_callback: UploadProgressCallback | None,
    ratio: float,
    message: str,
    *,
    state: dict[str, float],
) -> None:
    if not progress_callback:
        return
    clamped_ratio = max(0.0, min(1.0, ratio))
    last_ratio = state.get("last_ratio", -1.0)
    if clamped_ratio >= 1.0 or last_ratio < 0 or abs(clamped_ratio - last_ratio) >= 0.01:
        state["last_ratio"] = clamped_ratio
        progress_callback(clamped_ratio, message)


def _wait_for_post_submit_completion(
    driver: webdriver.Chrome,
    *,
    channel_id: str,
    title: str,
    marker: str,
    progress_callback: UploadProgressCallback | None,
    timeout_seconds: int = 3600,
) -> str | None:
    deadline = time.monotonic() + timeout_seconds
    content_list_url = f"https://studio.youtube.com/channel/{channel_id}/videos/upload"
    switched_to_content_list = False
    progress_state = {"last_ratio": -1.0}
    transfer_completed = False

    while time.monotonic() < deadline:
        _raise_if_upload_blocked(driver)
        cancel_visible = _has_cancel_upload_button(driver)
        transfer_completed = transfer_completed or _has_transfer_completed_signal(driver)

        row_match = _find_matching_studio_row_by_marker(
            driver,
            content_list_url=content_list_url,
            marker=marker,
            title_hint=title,
        )
        if row_match:
            studio_row_watch_url, row_state = row_match
        else:
            studio_row_watch_url, row_state = None, "missing"

        if row_match and studio_row_watch_url and not cancel_visible:
            if progress_callback:
                if row_state == "uploaded":
                    progress_callback(1.0, "YouTube da dua video vao danh sach noi dung")
                else:
                    progress_callback(1.0, "YouTube da nhan file, video dang duoc xu ly tren Studio")
            return studio_row_watch_url
        if row_match and progress_callback:
            progress_callback(0.99, "YouTube dang xu ly video sau khi nhan file")

        ratio = _extract_upload_ratio(driver)
        if ratio is not None:
            _emit_upload_progress(
                progress_callback,
                min(0.99, ratio),
                f"YouTube dang nhan file {int(ratio * 100)}%",
                state=progress_state,
            )
            if ratio >= 1.0 and progress_callback and cancel_visible:
                transfer_completed = True
                progress_callback(0.99, "YouTube da nhan 100%, dang hoan tat upload")
            if ratio >= 1.0 and not switched_to_content_list:
                driver.get(content_list_url)
                switched_to_content_list = True
        elif cancel_visible:
            last_ratio = progress_state.get("last_ratio", -1.0)
            if last_ratio >= 0 and progress_callback:
                progress_callback(last_ratio, "YouTube van dang nhan file")
        elif not switched_to_content_list:
            driver.get(content_list_url)
            switched_to_content_list = True
        elif row_match and progress_callback:
            progress_callback(0.99, "YouTube dang cho YouTube Studio hoan tat upload")
        time.sleep(3)

    raise RuntimeError("Khong xac nhan duoc YouTube da nhan xong file upload.")


def _click_done_or_raise(
    driver: webdriver.Chrome,
    *,
    timeout_seconds: int = 600,
) -> None:
    deadline = time.monotonic() + timeout_seconds
    while time.monotonic() < deadline:
        _raise_if_upload_blocked(driver)
        if _click_when_available(driver, WebDriverWait(driver, 3), "//*[@id='done-button']//button"):
            return
        time.sleep(1)
    raise RuntimeError("Khong tim thay nut Done trong YouTube Studio upload flow.")


def upload_video_via_browser(
    *,
    config: WorkerConfig,
    target: YouTubeUploadTarget,
    file_path: Path,
    progress_callback: UploadProgressCallback | None = None,
) -> BrowserUploadResult:
    if target.connection_mode != "browser_profile":
        raise RuntimeError("Browser uploader chi dung cho browser_profile channel.")
    if not file_path.exists():
        raise RuntimeError("Khong tim thay file output de upload browser.")

    browser_runtime = BrowserRuntimeManager(config.work_root / "browser-runtime")
    browser_config = browser_runtime.load_config()
    profile_path = Path(str(target.browser_profile_path or "").strip()) if target.browser_profile_path else None
    if profile_path is None or not profile_path.exists():
        if not target.browser_profile_key:
            raise RuntimeError("Channel browser_profile thieu browser profile key/path.")
        profile_path = browser_config.profile_root / str(target.browser_profile_key)
    if not profile_path.exists():
        raise RuntimeError(f"Khong tim thay Chrome profile cua kenh tai {profile_path}.")

    for lock_name in ("SingletonCookie", "SingletonLock", "SingletonSocket"):
        (profile_path / lock_name).unlink(missing_ok=True)

    display_number = _pick_display_number()
    display = f":{display_number}"
    xvfb_process: subprocess.Popen[bytes] | None = None
    driver: webdriver.Chrome | None = None
    studio_url = f"https://studio.youtube.com/channel/{target.channel_id}/videos/upload?d=ud"
    marker = _build_job_marker(target.job_id)
    description_with_marker = _merge_description_with_marker(target.description, marker)
    try:
        xvfb_process = subprocess.Popen(
            ["Xvfb", display, "-screen", "0", "1440x900x24", "-ac", "-nolisten", "tcp"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(0.7)
        if xvfb_process.poll() is not None:
            raise RuntimeError("Khong the khoi dong Xvfb cho browser upload.")

        options = ChromeOptions()
        options.binary_location = browser_config.chromium_bin
        options.add_argument(f"--user-data-dir={profile_path}")
        options.add_argument("--profile-directory=Default")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-setuid-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-background-networking")
        options.add_argument("--disable-features=PasswordManagerOnboarding,PasswordsImport,Translate,MediaRouter")
        options.add_argument("--window-size=1440,900")
        options.add_argument("--lang=en-US")

        service = ChromeService()
        service.env = {**os.environ, "DISPLAY": display}
        driver = webdriver.Chrome(service=service, options=options)
        wait = WebDriverWait(driver, 90)

        if progress_callback:
            progress_callback(0.01, "Da mo Chrome profile cua kenh")
        driver.get(studio_url)

        file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
        file_input.send_keys(str(file_path))
        _raise_if_upload_blocked(driver)
        if progress_callback:
            progress_callback(0.03, "Da gan file output vao Studio upload")

        try:
            title_box, description_box = _find_title_and_description_boxes(driver, wait)
        except TimeoutException as exc:
            debug_dir = _capture_upload_debug_artifacts(
                driver,
                debug_root=config.work_root,
                job_id=target.job_id,
                stage="editor-timeout",
            )
            detail = "Khong tim thay title/description editor tren YouTube Studio."
            if debug_dir is not None:
                detail = f"{detail} Debug: {debug_dir}"
            raise RuntimeError(detail) from exc
        _set_textbox(driver, title_box, target.title)
        if description_box is not None:
            _set_textbox(driver, description_box, description_with_marker)
        _raise_if_upload_blocked(driver)
        if progress_callback:
            progress_callback(0.05, "Da dien title va description")

        _click_when_available(
            driver,
            WebDriverWait(driver, 5),
            "//tp-yt-paper-radio-button[@name='VIDEO_MADE_FOR_KIDS_NOT_MFK']",
        )

        for _ in range(3):
            _click_when_available(driver, wait, "//*[@id='next-button']//button")
            _raise_if_upload_blocked(driver)
            time.sleep(0.6)

        _click_when_available(driver, WebDriverWait(driver, 10), "//tp-yt-paper-radio-button[@name='PRIVATE']")
        _raise_if_upload_blocked(driver)
        if progress_callback:
            progress_callback(0.08, "Da cau hinh cac buoc upload co ban")

        try:
            _click_done_or_raise(driver)
        except RuntimeError as exc:
            debug_dir = _capture_upload_debug_artifacts(
                driver,
                debug_root=config.work_root,
                job_id=target.job_id,
                stage="done-timeout",
            )
            detail = str(exc)
            if debug_dir is not None:
                detail = f"{detail} Debug: {debug_dir}"
            raise RuntimeError(detail) from exc

        current_ratio = _extract_upload_ratio(driver)
        if current_ratio is not None and progress_callback:
            progress_callback(min(0.99, current_ratio), f"YouTube dang nhan file {int(current_ratio * 100)}%")

        watch_url = _wait_for_post_submit_completion(
            driver,
            channel_id=target.channel_id,
            title=target.title,
            marker=marker,
            progress_callback=progress_callback,
        )
        if progress_callback:
            progress_callback(1.0, "Da xac nhan YouTube nhan xong file upload")
        return BrowserUploadResult(studio_url=studio_url, watch_url=watch_url, cleanup_safe=True)
    except Exception as exc:
        raise RuntimeError(_format_browser_exception(exc, driver)) from exc
    finally:
        if driver is not None:
            driver.quit()
        _stop_process(xvfb_process)
