(() => {
  const renderTable = document.querySelector(".render-table");
  const renderTableHeaders = renderTable ? Array.from(renderTable.querySelectorAll("thead th")) : [];
  const renderTableBody = renderTable ? renderTable.querySelector("tbody") : null;
  const renderHeaderLabels = ["STT", "Thông tin job", "Kênh", "BOT", "Tiến độ", "Timeline", "Trạng thái", "Tác vụ"];
  const originalRenderRows = renderTableBody ? Array.from(renderTableBody.querySelectorAll("tr")) : [];
  const renderSortState = { index: null, direction: "asc" };

  const showFormMessage = (message, type = "info") => {
    const node = document.getElementById("jobFormMessage");
    if (!node) return;
    node.className = "text-[12px] font-medium";
    node.classList.remove("hidden", "text-brand-600", "text-rose-600", "text-emerald-600");
    node.classList.add(type === "error" ? "text-rose-600" : type === "success" ? "text-emerald-600" : "text-brand-600");
    node.textContent = message;
  };

  const getRenderSortValue = (row, index) => {
    const cells = row.querySelectorAll("td");
    const cell = cells[index];
    if (!cell) return "";

    const text = cell.innerText.replace(/\s+/g, " ").trim();
    if (index === 0) return Number(text) || 0;
    if (index === 4) return Number(text.replace(/[^\d.-]/g, "")) || 0;
    return text.toLowerCase();
  };

  const renderHeaderMarkup = (label, index) => {
    const alignClass = index === 0 ? "center" : index === renderHeaderLabels.length - 1 ? "end" : "";
    const isActive = renderSortState.index === index;
    const direction = isActive ? renderSortState.direction : "none";
    return `
      <button type="button" class="sortable-button ${alignClass} ${isActive ? "active" : ""}" data-sort-index="${index}" data-direction="${direction}" aria-label="Sắp xếp theo ${label}">
        <span>${label}</span>
        <span class="sort-arrows" aria-hidden="true">
          <span class="sort-up">↑</span>
          <span class="sort-down">↓</span>
        </span>
      </button>
    `;
  };

  const bindRenderSortButtons = () => {
    if (!renderTable || !renderTableBody) return;
    renderTable.querySelectorAll(".sortable-button").forEach((button) => {
      button.addEventListener("click", () => {
        const index = Number(button.dataset.sortIndex);
        if (renderSortState.index === index) {
          renderSortState.direction = renderSortState.direction === "asc" ? "desc" : "asc";
        } else {
          renderSortState.index = index;
          renderSortState.direction = "asc";
        }

        const rows = [...originalRenderRows].sort((rowA, rowB) => {
          const valueA = getRenderSortValue(rowA, index);
          const valueB = getRenderSortValue(rowB, index);
          if (valueA === valueB) return 0;
          const comparison = valueA > valueB ? 1 : -1;
          return renderSortState.direction === "asc" ? comparison : -comparison;
        });

        renderTableBody.replaceChildren(...rows);
        renderTableHeaders.forEach((th, headerIndex) => {
          if (!renderHeaderLabels[headerIndex]) return;
          th.innerHTML = renderHeaderMarkup(renderHeaderLabels[headerIndex], headerIndex);
        });
        bindRenderSortButtons();
      });
    });
  };

  const initChannelSelect = () => {
    const channelSelect = document.querySelector(".channel-select");
    if (!channelSelect) return;

    const channelTrigger = channelSelect.querySelector(".channel-select-trigger");
    const channelAvatar = channelSelect.querySelector(".channel-select-avatar");
    const channelValue = channelSelect.querySelector(".channel-select-value");
    const channelOptions = Array.from(channelSelect.querySelectorAll(".channel-option"));
    const channelInput = channelSelect.querySelector("#selectedChannel");
    if (!channelTrigger || !channelAvatar || !channelValue || !channelInput) return;

    const setChannelOpen = (open) => {
      channelSelect.dataset.open = open ? "true" : "false";
      channelTrigger.setAttribute("aria-expanded", open ? "true" : "false");
    };

    const setChannelValue = (option) => {
      channelValue.textContent = option.dataset.label || "";
      channelValue.classList.toggle("is-placeholder", option.dataset.value === "");
      channelInput.value = option.dataset.value || "";
      if (option.dataset.avatar) {
        channelAvatar.textContent = option.dataset.avatar;
        channelAvatar.className = `channel-select-avatar ${option.dataset.avatarClass || ""}`;
      } else {
        channelAvatar.textContent = "";
        channelAvatar.className = "channel-select-avatar is-hidden";
      }
      channelOptions.forEach((item) => {
        const active = item === option;
        item.classList.toggle("is-active", active);
        item.setAttribute("aria-selected", active ? "true" : "false");
      });
    };

    channelTrigger.addEventListener("click", () => {
      setChannelOpen(channelSelect.dataset.open !== "true");
    });

    channelOptions.forEach((option) => {
      option.addEventListener("click", () => {
        setChannelValue(option);
        setChannelOpen(false);
      });
    });

    document.addEventListener("click", (event) => {
      if (!channelSelect.contains(event.target)) {
        setChannelOpen(false);
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") {
        setChannelOpen(false);
      }
    });

    const activeOption = channelOptions.find((option) => option.classList.contains("is-active")) || channelOptions[0];
    if (activeOption) {
      setChannelValue(activeOption);
    }
  };

  const initFlatpickr = () => {
    if (!window.flatpickr) return;
    window.flatpickr("#scheduleAt", {
      enableTime: true,
      time_24hr: true,
      allowInput: true,
      minuteIncrement: 5,
      dateFormat: "d/m/Y H:i",
      locale: window.flatpickr.l10ns.vn || window.flatpickr.l10ns.default,
    });
  };

  const initFileInputs = () => {
    const assetFieldBySlot = {
      intro: "introAssetId",
      video_loop: "videoLoopAssetId",
      audio_loop: "audioLoopAssetId",
      outro: "outroAssetId",
    };
    const defaultStatus = "Có thể nhập link hoặc chọn file local.";

    const setSlotStatus = (slot, message, tone = "neutral") => {
      const node = document.querySelector(`[data-upload-status="${slot}"]`);
      if (!node) return;
      node.className = "mt-1.5 text-[11px]";
      node.classList.add(
        tone === "error"
          ? "text-rose-600"
          : tone === "success"
            ? "text-emerald-600"
            : tone === "uploading"
              ? "text-brand-600"
              : "text-slate-400"
      );
      node.textContent = message;
    };

    document.querySelectorAll(".file-input").forEach((input) => {
      input.addEventListener("change", (event) => {
        const targetId = event.target.getAttribute("data-target");
        const file = event.target.files?.[0];
        const slot = event.target.name.replace("_file", "");
        if (!targetId) return;
        const inputEl = document.getElementById(targetId);
        if (inputEl && file) {
          inputEl.value = file.name;
        }
        const hiddenAssetField = document.getElementById(assetFieldBySlot[slot]);
        if (hiddenAssetField) {
          hiddenAssetField.value = "";
        }
        if (file) {
          setSlotStatus(slot, `Sẵn sàng upload: ${file.name}`, "neutral");
        } else {
          setSlotStatus(slot, defaultStatus, "neutral");
        }
      });
    });
  };

  const initForm = () => {
    const form = document.getElementById("job-form");
    const submitButton = document.getElementById("submitJobButton");
    const resetButton = document.getElementById("resetJobForm");
    if (!form || !submitButton || !resetButton) return;

    const slotToAssetField = {
      intro: "introAssetId",
      video_loop: "videoLoopAssetId",
      audio_loop: "audioLoopAssetId",
      outro: "outroAssetId",
    };
    const defaultStatus = "Có thể nhập link hoặc chọn file local.";
    const allowedExtensions = String(form.dataset.allowedExtensions || "")
      .split(",")
      .map((item) => item.trim().toLowerCase())
      .filter(Boolean);
    const maxUploadBytes = Number(form.dataset.maxUploadBytes || 0);
    const fallbackChunkBytes = Number(form.dataset.chunkBytes || 8388608);

    const setSlotStatus = (slot, message, tone = "neutral") => {
      const node = document.querySelector(`[data-upload-status="${slot}"]`);
      if (!node) return;
      node.className = "mt-1.5 text-[11px]";
      node.classList.add(
        tone === "error"
          ? "text-rose-600"
          : tone === "success"
            ? "text-emerald-600"
            : tone === "uploading"
              ? "text-brand-600"
              : "text-slate-400"
      );
      node.textContent = message;
    };

    const formatBytes = (value) => {
      if (!Number.isFinite(value) || value <= 0) return "0 B";
      const units = ["B", "KB", "MB", "GB", "TB"];
      let size = value;
      let index = 0;
      while (size >= 1024 && index < units.length - 1) {
        size /= 1024;
        index += 1;
      }
      return `${size.toFixed(size >= 10 || index === 0 ? 0 : 1)} ${units[index]}`;
    };

    const buildUploadStorageKey = (slot, file) => {
      return `ytlush-upload:${slot}:${file.name}:${file.size}:${file.lastModified}`;
    };

    const validateLocalFile = (file) => {
      const extension = `.${String(file.name || "").split(".").pop() || ""}`.toLowerCase();
      if (allowedExtensions.length && !allowedExtensions.includes(extension)) {
        throw new Error(`File ${file.name} không nằm trong danh sách cho phép.`);
      }
      if (maxUploadBytes > 0 && file.size > maxUploadBytes) {
        throw new Error(`File ${file.name} vượt quá giới hạn ${formatBytes(maxUploadBytes)}.`);
      }
    };

    const getOrCreateUploadSession = async (slot, file) => {
      const storageKey = buildUploadStorageKey(slot, file);
      const cachedSessionId = window.localStorage.getItem(storageKey);
      if (cachedSessionId) {
        const statusResponse = await fetch(`/api/user/uploads/sessions/${cachedSessionId}`);
        if (statusResponse.ok) {
          const payload = await statusResponse.json();
          if (payload.file_name === file.name || payload.file_name === file.name.replace(/[^A-Za-z0-9._-]+/g, "-")) {
            return { storageKey, session: payload };
          }
        }
        window.localStorage.removeItem(storageKey);
      }

      const response = await fetch("/api/user/uploads/sessions", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          slot,
          file_name: file.name,
          size_bytes: file.size,
          content_type: file.type || "application/octet-stream",
        }),
      });
      const payload = await response.json();
      if (!response.ok) {
        throw new Error(payload.detail || "Không thể tạo upload session.");
      }
      window.localStorage.setItem(storageKey, payload.session_id);
      return { storageKey, session: payload };
    };

    const uploadLocalFile = async (slot, file) => {
      validateLocalFile(file);
      const assetField = document.getElementById(slotToAssetField[slot]);
      if (!assetField) {
        throw new Error(`Thiếu hidden field cho slot ${slot}.`);
      }
      assetField.value = "";

      const { storageKey, session: initialSession } = await getOrCreateUploadSession(slot, file);
      let session = initialSession;
      if (session.status === "completed" && session.asset_id) {
        assetField.value = session.asset_id;
        setSlotStatus(slot, `Đã sẵn sàng: ${file.name}`, "success");
        return session.asset_id;
      }

      const chunkBytes = Number(session.chunk_size || fallbackChunkBytes);
      let offset = Number(session.received_bytes || 0);
      while (offset < file.size) {
        const nextChunk = file.slice(offset, Math.min(offset + chunkBytes, file.size));
        setSlotStatus(
          slot,
          `Đang upload ${file.name}: ${Math.floor((offset / file.size) * 100)}% (${formatBytes(offset)}/${formatBytes(file.size)})`,
          "uploading"
        );
        const response = await fetch(`/api/user/uploads/sessions/${session.session_id}`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/octet-stream",
            "x-upload-offset": String(offset),
          },
          body: nextChunk,
        });
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload.detail || `Upload ${file.name} thất bại.`);
        }
        session = payload;
        offset = Number(payload.received_bytes || 0);
      }

      if (!session.asset_id) {
        throw new Error(`Upload ${file.name} đã xong nhưng chưa có asset id.`);
      }
      assetField.value = session.asset_id;
      window.localStorage.setItem(storageKey, session.session_id);
      setSlotStatus(slot, `Hoàn tất: ${file.name} (${formatBytes(file.size)})`, "success");
      return session.asset_id;
    };

    const setSubmitting = (submitting) => {
      submitButton.disabled = submitting;
      submitButton.textContent = submitting ? "Đang tạo..." : "Tạo job render";
    };

    resetButton.addEventListener("click", () => {
      form.reset();
      const channelInput = document.getElementById("selectedChannel");
      if (channelInput) {
        channelInput.value = "";
      }
      const placeholderOption = document.querySelector(".channel-option[data-value='']");
      if (placeholderOption) {
        placeholderOption.click();
      }
      Object.entries(slotToAssetField).forEach(([slot, fieldId]) => {
        const field = document.getElementById(fieldId);
        if (field) field.value = "";
        setSlotStatus(slot, defaultStatus, "neutral");
      });
      showFormMessage("Đã đặt lại form.", "info");
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const formData = new FormData(form);
      const hasLocalFile = ["intro_file", "video_loop_file", "audio_loop_file", "outro_file"].some((field) => {
        const file = formData.get(field);
        return file instanceof File && file.name;
      });
      formData.set("source_mode", hasLocalFile ? "local" : "drive");

      if (!formData.get("channel_id")) {
        showFormMessage("Cần chọn kênh trước khi tạo job.", "error");
        return;
      }

      const title = String(formData.get("title") || "").trim();
      if (!title) {
        showFormMessage("Tên video là bắt buộc.", "error");
        return;
      }

      setSubmitting(true);
      showFormMessage("Đang chuẩn bị job...", "info");

      try {
        const localFiles = [
          { slot: "intro", field: "intro_file" },
          { slot: "video_loop", field: "video_loop_file" },
          { slot: "audio_loop", field: "audio_loop_file" },
          { slot: "outro", field: "outro_file" },
        ];

        for (const item of localFiles) {
          const file = formData.get(item.field);
          if (file instanceof File && file.name) {
            showFormMessage(`Đang upload file local cho ${item.slot}...`, "info");
            await uploadLocalFile(item.slot, file);
            formData.delete(item.field);
          }
        }

        const hasUploadedAsset = Object.values(slotToAssetField).some((fieldId) => {
          const field = document.getElementById(fieldId);
          return Boolean(field?.value);
        });
        formData.set("source_mode", hasUploadedAsset || hasLocalFile ? "local" : "drive");

        Object.values(slotToAssetField).forEach((fieldId) => {
          const field = document.getElementById(fieldId);
          if (field?.value) {
            formData.set(field.name || field.id, field.value);
          }
        });

        showFormMessage(hasUploadedAsset ? "Upload xong, đang tạo job..." : "Đang gửi job lên backend...", "info");
        const response = await fetch("/api/user/jobs", {
          method: "POST",
          body: formData,
        });
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload.detail || "Không thể tạo job.");
        }
        showFormMessage("Tạo job thành công. Đang tải lại danh sách...", "success");
        window.setTimeout(() => window.location.reload(), 500);
      } catch (error) {
        showFormMessage(error.message || "Không thể tạo job.", "error");
      } finally {
        setSubmitting(false);
      }
    });
  };

  const initOAuthButton = () => {
    const button = document.getElementById("connectYouTubeButton");
    if (!button) return;

    button.addEventListener("click", async () => {
      button.disabled = true;
      try {
        const response = await fetch("/api/user/oauth/connect/start", { method: "POST" });
        const payload = await response.json();
        if (payload.auth_url) {
          window.location.href = payload.auth_url;
          return;
        }
        window.alert(payload.message || "OAuth chưa được cấu hình đầy đủ.");
      } catch (error) {
        window.alert(error.message || "Không thể khởi động OAuth.");
      } finally {
        button.disabled = false;
      }
    });
  };

  const initJobActions = () => {
    document.querySelectorAll("[data-job-action]").forEach((button) => {
      button.addEventListener("click", async () => {
        const action = button.dataset.jobAction;
        const jobId = button.dataset.jobId;
        if (!jobId || !action) return;

        const confirmed = action === "delete" ? window.confirm("Xóa job này?") : window.confirm("Huỷ job này?");
        if (!confirmed) return;

        button.disabled = true;
        try {
          const response = await fetch(`/api/user/jobs/${jobId}${action === "cancel" ? "/cancel" : ""}`, {
            method: action === "cancel" ? "PATCH" : "DELETE",
          });
          const payload = await response.json();
          if (!response.ok) {
            throw new Error(payload.detail || "Không thể cập nhật job.");
          }
          window.location.reload();
        } catch (error) {
          window.alert(error.message || "Không thể cập nhật job.");
          button.disabled = false;
        }
      });
    });
  };

  const initChannelActions = () => {
    document.querySelectorAll("[data-channel-action='delete']").forEach((button) => {
      button.addEventListener("click", async () => {
        const channelId = button.dataset.channelId;
        const channelTitle = button.dataset.channelTitle || "kênh này";
        if (!channelId) return;

        const confirmed = window.confirm(`Xóa ${channelTitle}? Toàn bộ job gắn với kênh này cũng sẽ bị xóa.`);
        if (!confirmed) return;

        button.disabled = true;
        try {
          const response = await fetch(`/api/user/channels/${channelId}`, {
            method: "DELETE",
          });
          const payload = await response.json();
          if (!response.ok) {
            throw new Error(payload.detail || "Không thể xóa kênh.");
          }
          window.location.reload();
        } catch (error) {
          window.alert(error.message || "Không thể xóa kênh.");
          button.disabled = false;
        }
      });
    });
  };

  const initSearch = () => {
    const input = document.getElementById("jobSearchInput");
    if (!input || !renderTableBody) return;

    const rows = Array.from(renderTableBody.querySelectorAll("tr"));
    input.addEventListener("input", () => {
      const query = input.value.trim().toLowerCase();
      rows.forEach((row) => {
        const visible = row.innerText.toLowerCase().includes(query);
        row.classList.toggle("hidden", !visible);
      });
    });
  };

  const clearTransientNoticeParams = () => {
    const url = new URL(window.location.href);
    let changed = false;
    ["notice", "notice_level"].forEach((key) => {
      if (url.searchParams.has(key)) {
        url.searchParams.delete(key);
        changed = true;
      }
    });
    if (!changed) return;
    const search = url.searchParams.toString();
    const nextUrl = `${url.pathname}${search ? `?${search}` : ""}${url.hash}`;
    window.history.replaceState({}, document.title, nextUrl);
  };

  if (window.lucide) {
    window.lucide.createIcons();
  }

  renderTableHeaders.forEach((th, index) => {
    if (!renderHeaderLabels[index]) return;
    th.classList.remove("text-slate-400");
    th.innerHTML = renderHeaderMarkup(renderHeaderLabels[index], index);
  });

  bindRenderSortButtons();
  initChannelSelect();
  initFlatpickr();
  initFileInputs();
  initForm();
  initOAuthButton();
  initJobActions();
  initChannelActions();
  initSearch();
  clearTransientNoticeParams();
})();
