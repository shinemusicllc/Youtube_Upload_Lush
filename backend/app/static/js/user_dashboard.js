(() => {
  const renderTable = document.querySelector(".render-table");
  const renderSortButtons = renderTable ? Array.from(renderTable.querySelectorAll("thead .sortable-button[data-sort]")) : [];
  const renderTableBody = renderTable ? renderTable.querySelector("tbody") : null;
  const renderSortState = { key: null, direction: "asc" };
  const renderSearchInput = document.getElementById("jobSearchInput");
  const renderSummaryNode = document.getElementById("renderSummaryText");
  const renderPaginationNode = document.getElementById("renderPagination");
  const deleteVisibleJobsButton = document.getElementById("deleteVisibleJobsButton");
  const dashboardSeedNode = document.getElementById("dashboard-seed");
  const renderPageSize = Math.max(1, Number(renderTable?.dataset.pageSize || 10) || 10);
  const renderPaginationState = { page: 1, pageSize: renderPageSize };
  let renderJobsState = [];
  let liveRefreshHandle = null;
  let liveRefreshInFlight = false;
  let lastLivePayloadSignature = "";

  const escapeHtml = (value) =>
    String(value ?? "")
      .replace(/&/g, "&")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/\"/g, "&quot;")
      .replace(/'/g, "&#39;");

  const clampRenderPage = (page, totalPages) => {
    if (totalPages <= 0) return 1;
    return Math.min(Math.max(page, 1), totalPages);
  };

  const showFormMessage = (message, type = "info") => {
    const node = document.getElementById("jobFormMessage");
    if (!node) return;
    node.className = "text-[12px] font-medium";
    node.classList.remove("hidden", "text-brand-600", "text-rose-600", "text-emerald-600");
    node.classList.add(type === "error" ? "text-rose-600" : type === "success" ? "text-emerald-600" : "text-brand-600");
    node.textContent = message;
  };

  const getRenderSortValue = (job, key) => {
    if (key === "stt") return Number(job.index) || 0;
    if (key === "job") return `${job.title || ""} ${job.job_id || ""} ${job.description || ""}`.trim().toLowerCase();
    if (key === "channel") return String(job.channel_name || "").toLowerCase();
    if (key === "vps") return String(job.bot || "").toLowerCase();
    if (key === "progress") return (Number(job.render_progress) || 0) * 1000 + (Number(job.upload_progress) || 0);
    if (key === "timeline") return `${job.created_at || ""} ${job.render_at || ""} ${job.uploaded_at || ""}`.toLowerCase();
    if (key === "status") return String(job.status || "").toLowerCase();
    return "";
  };

  const refreshRenderHeaderButtons = () => {
    renderSortButtons.forEach((button) => {
      const key = button.dataset.sort || "";
      const isActive = renderSortState.key === key;
      const direction = isActive ? renderSortState.direction : "none";
      button.classList.toggle("active", isActive);
      button.dataset.direction = direction;
      const headerCell = button.closest("th");
      if (headerCell) {
        headerCell.setAttribute("aria-sort", isActive ? (direction === "asc" ? "ascending" : "descending") : "none");
      }
    });
  };

  const bindRenderSortButtons = () => {
    renderSortButtons.forEach((button) => {
      if (button.dataset.sortBound === "true") return;
      button.dataset.sortBound = "true";
      button.addEventListener("click", () => {
        const key = button.dataset.sort || "";
        if (!key || key === "actions") return;
        if (renderSortState.key === key) {
          renderSortState.direction = renderSortState.direction === "asc" ? "desc" : "asc";
        } else {
          renderSortState.key = key;
          renderSortState.direction = "asc";
        }
        refreshRenderHeaderButtons();
        applyRenderSort();
      });
    });
  };

  const initChannelSelect = () => {
    const channelSelect = document.querySelector(".channel-select");
    if (!channelSelect) return;

    const channelTrigger = channelSelect.querySelector(".channel-select-trigger");
    const channelAvatar = channelSelect.querySelector(".channel-select-trigger-avatar");
    const channelValue = channelSelect.querySelector(".channel-select-value");
    const channelMeta = channelSelect.querySelector(".channel-select-meta");
    const channelOptions = Array.from(channelSelect.querySelectorAll(".channel-option"));
    const channelInput = channelSelect.querySelector("#selectedChannel");
    if (!channelTrigger || !channelAvatar || !channelValue || !channelMeta || !channelInput) return;

    const setChannelOpen = (open) => {
      channelSelect.dataset.open = open ? "true" : "false";
      channelTrigger.setAttribute("aria-expanded", open ? "true" : "false");
    };

    const setChannelValue = (option) => {
      channelValue.textContent = option.dataset.label || "";
      channelValue.classList.toggle("is-placeholder", option.dataset.value === "");
      channelMeta.textContent = option.dataset.meta || "";
      channelMeta.classList.toggle("is-hidden", !option.dataset.meta || option.dataset.value === "");
      channelInput.value = option.dataset.value || "";
      const avatarUrl = (option.dataset.avatarUrl || "").trim();
      if (avatarUrl) {
        channelAvatar.innerHTML = `<img src="${avatarUrl}" alt="${option.dataset.label || ""}" class="w-full h-full rounded-[inherit] object-cover" loading="lazy" referrerpolicy="no-referrer">`;
        channelAvatar.className = "channel-select-trigger-avatar channel-select-avatar channel-avatar-media overflow-hidden";
      } else if (option.dataset.avatar) {
        channelAvatar.innerHTML = "";
        channelAvatar.textContent = option.dataset.avatar;
        channelAvatar.className = `channel-select-trigger-avatar channel-select-avatar ${option.dataset.avatarClass || ""}`;
      } else {
        channelAvatar.innerHTML = "";
        channelAvatar.textContent = "";
        channelAvatar.className = "channel-select-trigger-avatar channel-select-avatar is-hidden";
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
    const scheduleInput = document.getElementById("scheduleAt");
    if (!(scheduleInput instanceof HTMLInputElement)) return;

    const setPickerToClientNow = (instance) => {
      const now = new Date();
      instance.setDate(now, true);
      instance.jumpToDate(now);
    };

    const picker = window.flatpickr(scheduleInput, {
      enableTime: true,
      time_24hr: true,
      allowInput: true,
      minuteIncrement: 5,
      dateFormat: "d/m/Y H:i",
      locale: window.flatpickr.l10ns.vn || window.flatpickr.l10ns.default,
      onOpen: [
        (_selectedDates, _dateStr, instance) => {
          setPickerToClientNow(instance);
        },
      ],
    });

    const syncScheduleInputToClientNow = () => {
      setPickerToClientNow(picker);
    };

    scheduleInput.addEventListener("focus", syncScheduleInputToClientNow);
    scheduleInput.addEventListener("click", syncScheduleInputToClientNow);

    scheduleInput.addEventListener("keydown", (event) => {
      if (event.key !== "Enter" || !picker.isOpen) return;
      event.preventDefault();
      if (!picker.selectedDates.length) {
        setPickerToClientNow(picker);
      } else {
        picker.setDate(picker.selectedDates[0], true);
      }
      picker.close();
      scheduleInput.blur();
    });
  };

  const initFileInputs = () => {
    document.querySelectorAll("[data-upload-trigger]").forEach((button) => {
      button.addEventListener("click", () => {
      const state = button.dataset.state || "idle";
      if (state !== "idle") return;
        const slot = button.getAttribute("data-upload-trigger");
        const input = slot ? document.querySelector(`[data-upload-input="${slot}"]`) : null;
        if (input instanceof HTMLInputElement) {
          input.click();
        }
      });
    });
  };

  const applyRenderSearch = () => {
    if (!renderTableBody) return;
    renderPaginationState.page = 1;
    renderRenderTable();
  };

  const applyRenderSort = () => {
    if (!renderTableBody) return;
    renderRenderTable();
  };

  const renderJobPreviewMarkup = (job) => {
    if (job.preview_url) {
      if (job.preview_kind === "image") {
        return `
          <div class="w-24 aspect-[4/3] bg-slate-100 border border-slate-200 rounded-xl relative shrink-0 overflow-hidden">
            <img src="${escapeHtml(job.preview_url)}" alt="${escapeHtml(job.title)}" class="job-preview-media" loading="lazy" referrerpolicy="no-referrer">
            <div class="absolute inset-x-0 bottom-0 h-[2px] bg-brand-600"></div>
          </div>
        `;
      }
      return `
        <div class="w-24 aspect-[4/3] bg-slate-100 border border-slate-200 rounded-xl relative shrink-0 overflow-hidden">
          <video class="job-preview-media" src="${escapeHtml(job.preview_url)}" muted playsinline preload="metadata"></video>
          <div class="absolute inset-x-0 bottom-0 h-[2px] bg-brand-600"></div>
        </div>
      `;
    }

    if (job.icon) {
      return `
        <div class="w-24 aspect-[4/3] bg-slate-100 border border-slate-200 rounded-xl relative shrink-0 flex items-center justify-center">
          <i data-lucide="${escapeHtml(job.icon)}" class="w-6 h-6 ${escapeHtml(job.icon_class || "")}"></i>
        </div>
      `;
    }

    return `
      <div class="w-24 aspect-[4/3] bg-slate-900 rounded-xl relative border border-slate-800 flex justify-center items-center overflow-hidden shrink-0">
        <div class="text-[7px] text-white/80 font-mono">${escapeHtml(job.preview_text || "Preview..")}</div>
        <div class="absolute bottom-0 w-full h-[2px] bg-brand-600"></div>
      </div>
    `;
  };

  const renderChannelAvatarMarkup = (job) => {
    if (job.channel_avatar_url) {
      return `<img src="${escapeHtml(job.channel_avatar_url)}" alt="${escapeHtml(job.channel_name)}" class="channel-avatar-media w-7 h-7 rounded-[6px] object-cover shrink-0" loading="lazy" referrerpolicy="no-referrer">`;
    }
    return `<div class="w-7 h-7 bg-emerald-800 text-white rounded-[4px] flex items-center justify-center text-[10px] font-bold shrink-0">${escapeHtml(job.channel_avatar || "?")}</div>`;
  };

  const renderJobActionsMarkup = (job) => `
    <div class="flex flex-nowrap items-center justify-end gap-2 whitespace-nowrap">
      ${job.youtube_watch_url ? `
        <a href="${escapeHtml(job.youtube_watch_url)}" target="_blank" rel="noopener noreferrer" class="shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-bold text-sky-700 bg-sky-50 border border-sky-200 rounded-lg hover:bg-sky-100 hover:text-sky-800 hover:shadow-sm transition-all" title="Mở YouTube">
          <i data-lucide="external-link" class="w-3 h-3"></i> Xem
        </a>
      ` : ""}
      <button type="button" class="shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-bold text-emerald-800 bg-emerald-50 border border-emerald-300 rounded-lg hover:bg-emerald-100 hover:text-emerald-900 hover:shadow-sm transition-all" title="Sửa"><i data-lucide="edit-2" class="w-3 h-3"></i> Sửa</button>
      ${job.can_cancel ? `
        <button type="button" data-job-action="cancel" data-job-id="${escapeHtml(job.id)}" class="shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-bold text-amber-700 bg-amber-50 border border-amber-200 rounded-lg hover:bg-amber-100 hover:text-amber-800 hover:shadow-sm transition-all" title="Huỷ"><i data-lucide="x-circle" class="w-3 h-3"></i> Huỷ</button>
      ` : ""}
      <button type="button" data-job-action="delete" data-job-id="${escapeHtml(job.id)}" class="shrink-0 flex items-center gap-1.5 px-2.5 py-1.5 text-[11px] font-bold text-rose-700 bg-rose-50 border border-rose-200 rounded-lg hover:bg-rose-100 hover:text-rose-800 hover:shadow-sm transition-all" title="Xóa"><i data-lucide="trash" class="w-3 h-3"></i> Xóa</button>
    </div>
  `;

  const renderJobRowMarkup = (job) => `
    <tr class="hover:bg-slate-50 transition-colors group" data-job-id="${escapeHtml(job.id)}">
      <td class="px-6 py-5 text-left font-mono text-[13px] text-slate-500">${escapeHtml(job.index)}</td>
      <td class="px-6 py-5">
        <div class="flex items-center gap-3 min-w-0">
          ${renderJobPreviewMarkup(job)}
          <div class="min-w-0 flex-1 max-w-[328px] pb-0.5">
            <p class="text-[11px] font-bold uppercase tracking-[0.18em] ${job.kind === "Upload" ? "text-violet-500" : "text-brand-500"}">${escapeHtml(job.kind || "Upload")}</p>
            <p class="font-semibold ${job.kind === "Upload" ? "text-violet-700" : "text-brand-700"} text-[15px] leading-[1.4] render-job-title" title="${escapeHtml(job.title)}">${escapeHtml(job.title)}</p>
            <p class="mt-1 text-[11px] text-slate-600 font-mono truncate" title="${escapeHtml(`${job.meta || ""} ${job.job_id || ""}`.trim())}">${escapeHtml(job.meta || "")} <span class="${job.kind === "Upload" ? "text-violet-500" : "text-brand-500"}">${escapeHtml(job.job_id || "")}</span></p>
            ${job.description ? `<p class="mt-1 text-[11px] text-slate-500 truncate" title="${escapeHtml(job.description)}">${escapeHtml(job.description)}</p>` : ""}
          </div>
        </div>
      </td>
      <td class="px-6 py-4">
        <div class="flex items-center gap-3">
          ${renderChannelAvatarMarkup(job)}
          <div class="min-w-0">
            <p class="text-[12px] font-bold text-slate-900 leading-none mb-1 truncate">${escapeHtml(job.channel_name)}</p>
            <p class="text-[10px] text-emerald-600 font-medium">${escapeHtml(job.queue_label)}</p>
          </div>
        </div>
      </td>
      <td class="px-6 py-4">
        <div class="min-w-0">
          <p class="font-bold text-[12px] text-slate-900 leading-none mb-1 truncate">${escapeHtml(job.bot)}</p>
          <p class="text-[10px] text-brand-600 font-mono truncate">${escapeHtml(job.bot_meta || job.owner || "-")}</p>
        </div>
      </td>
      <td class="progress-cell px-6 py-4">
        <div class="w-[92px] mx-auto flex flex-col justify-start gap-1 pt-0">
          <div style="margin-top: 6px;">
            <div class="flex items-center justify-between gap-2 text-[9px] font-mono font-semibold uppercase tracking-[0.08em] text-emerald-700">
              <span>Render</span>
              <span>${escapeHtml(job.render_progress)}%</span>
            </div>
            <div class="mt-0.5 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
              <div class="h-full bg-emerald-500" style="width: ${Number(job.render_progress) || 0}%;"></div>
            </div>
          </div>
          <div style="margin-top: 1px;">
            <div class="flex items-center justify-between gap-2 text-[9px] font-mono font-semibold uppercase tracking-[0.08em] text-amber-700">
              <span>Upload</span>
              <span>${escapeHtml(job.upload_progress)}%</span>
            </div>
            <div class="mt-0.5 h-1.5 w-full bg-slate-100 rounded-full overflow-hidden">
              <div class="h-full bg-amber-500" style="width: ${Number(job.upload_progress) || 0}%;"></div>
            </div>
          </div>
        </div>
      </td>
      <td class="px-6 py-4 text-[10px] text-slate-500 font-mono leading-relaxed">
        <p class="truncate"><span class="text-slate-500">Tạo:</span> <span class="text-slate-700">${escapeHtml(job.created_at)}</span></p>
        <p class="truncate mt-0.5"><span class="text-slate-500">Render:</span> <span class="text-slate-700">${escapeHtml(job.render_at)}</span></p>
        <p class="truncate mt-0.5"><span class="text-slate-500">Upload:</span> <span class="text-slate-700">${escapeHtml(job.uploaded_at)}</span></p>
      </td>
      <td class="px-6 py-4">
        <span class="inline-flex justify-center items-center px-2.5 py-1 ${escapeHtml(job.status_class)} text-[10px] font-bold border rounded-full whitespace-nowrap">${escapeHtml(job.status)}</span>
      </td>
      <td class="px-6 py-4 text-right">
        ${renderJobActionsMarkup(job)}
      </td>
    </tr>
  `;

  const renderEmptyRowMarkup = (message) => `
    <tr>
      <td colspan="8" class="px-6 py-10 text-center text-[13px] text-slate-500">${escapeHtml(message)}</td>
    </tr>
  `;

  const getFilteredRenderJobs = () => {
    const query = renderSearchInput ? renderSearchInput.value.trim().toLowerCase() : "";
    let jobs = Array.isArray(renderJobsState) ? [...renderJobsState] : [];

    if (query) {
      jobs = jobs.filter((job) => {
        const haystack = [
          job.title,
          job.job_id,
          job.description,
          job.channel_name,
          job.bot,
          job.bot_meta,
          job.status,
          job.created_at,
          job.render_at,
          job.uploaded_at,
        ]
          .join(" ")
          .toLowerCase();
        return haystack.includes(query);
      });
    }

    if (renderSortState.key !== null) {
      jobs.sort((jobA, jobB) => {
        const valueA = getRenderSortValue(jobA, renderSortState.key);
        const valueB = getRenderSortValue(jobB, renderSortState.key);
        if (valueA === valueB) return 0;
        const comparison = valueA > valueB ? 1 : -1;
        return renderSortState.direction === "asc" ? comparison : -comparison;
      });
    }

    return jobs;
  };

  const getVisibleRenderPageJobs = () => {
    const filteredJobs = getFilteredRenderJobs();
    const totalPages = Math.max(1, Math.ceil(filteredJobs.length / renderPaginationState.pageSize));
    renderPaginationState.page = clampRenderPage(renderPaginationState.page, totalPages);
    const start = (renderPaginationState.page - 1) * renderPaginationState.pageSize;
    const end = start + renderPaginationState.pageSize;
    return {
      filteredJobs,
      totalPages,
      start,
      pageJobs: filteredJobs.slice(start, end),
    };
  };

  const renderPaginationControls = (currentPage, totalPages) => {
    if (!renderPaginationNode) return;

    const previousDisabled = currentPage <= 1;
    const nextDisabled = currentPage >= totalPages;
    const pages = totalPages <= 1 ? [1] : Array.from({ length: totalPages }, (_, index) => index + 1);

    renderPaginationNode.innerHTML = `
      <button
        type="button"
        class="w-9 h-9 border border-slate-200 rounded-lg ${previousDisabled ? "text-slate-300 cursor-not-allowed" : "text-slate-600 hover:text-slate-900 hover:border-slate-300 hover:shadow-sm"} transition-all flex items-center justify-center"
        data-pagination-action="previous"
        ${previousDisabled ? "disabled" : ""}
      >
        <i data-lucide="chevron-left" class="w-4 h-4"></i>
      </button>
      ${pages
        .map(
          (page) => `
            <button
              type="button"
              class="w-9 h-9 ${page === currentPage ? "bg-brand-600 text-white shadow-md shadow-brand-600/20" : "border border-slate-200 text-slate-600 hover:text-slate-900 hover:border-slate-300 hover:shadow-sm"} font-semibold text-[13px] rounded-lg transition-all flex items-center justify-center"
              data-pagination-page="${page}"
            >
              ${page}
            </button>
          `
        )
        .join("")}
      <button
        type="button"
        class="w-9 h-9 border border-slate-200 rounded-lg ${nextDisabled ? "text-slate-300 cursor-not-allowed" : "text-slate-600 hover:text-slate-900 hover:border-slate-300 hover:shadow-sm"} transition-all flex items-center justify-center"
        data-pagination-action="next"
        ${nextDisabled ? "disabled" : ""}
      >
        <i data-lucide="chevron-right" class="w-4 h-4"></i>
      </button>
    `;

    renderPaginationNode.querySelectorAll("[data-pagination-page]").forEach((button) => {
      button.addEventListener("click", () => {
        renderPaginationState.page = Number(button.dataset.paginationPage) || 1;
        renderRenderTable();
      });
    });

    renderPaginationNode.querySelectorAll("[data-pagination-action]").forEach((button) => {
      button.addEventListener("click", () => {
        if (button.dataset.paginationAction === "previous") {
          renderPaginationState.page -= 1;
        } else {
          renderPaginationState.page += 1;
        }
        renderRenderTable();
      });
    });
  };

  const updateRenderSummary = (start, visibleCount, totalCount) => {
    if (!renderSummaryNode) return;
    if (totalCount <= 0) {
      renderSummaryNode.textContent = renderSearchInput?.value.trim()
        ? "Khong tim thay job nao phu hop"
        : "Chua co job nao trong hang doi";
      return;
    }

    const from = start + 1;
    const to = start + visibleCount;
    renderSummaryNode.textContent = `Hiển thị ${from} đến ${to} trong số ${totalCount} kết quả`;
  };

  const updateDeleteVisibleJobsButton = (pageJobs, totalCount) => {
    if (!(deleteVisibleJobsButton instanceof HTMLButtonElement)) return;
    const disabled = !pageJobs.length;
    deleteVisibleJobsButton.disabled = disabled;
    deleteVisibleJobsButton.dataset.visibleCount = String(pageJobs.length);
    deleteVisibleJobsButton.title = disabled
      ? "Khong co job nao de xoa tren trang nay"
      : `Xóa nhanh ${pageJobs.length} job đang hiển thị`;
    deleteVisibleJobsButton.classList.toggle("opacity-80", totalCount > 0 && !pageJobs.length);
  };

  const renderRenderTable = () => {
    if (!renderTableBody) return;

    const { filteredJobs, totalPages, start, pageJobs } = getVisibleRenderPageJobs();
    if (!pageJobs.length) {
      renderTableBody.innerHTML = renderEmptyRowMarkup(
        filteredJobs.length ? "Khong co job nao trong trang nay" : renderSearchInput?.value.trim() ? "Khong tim thay job nao phu hop" : "Chua co job nao trong hang doi"
      );
    } else {
      renderTableBody.innerHTML = pageJobs
        .map((job, index) =>
          renderJobRowMarkup({
            ...job,
            index: start + index + 1,
          })
        )
        .join("");
    }

    updateRenderSummary(start, pageJobs.length, filteredJobs.length);
    renderPaginationControls(renderPaginationState.page, totalPages);
    updateDeleteVisibleJobsButton(pageJobs, filteredJobs.length);
    initJobActions();
    initJobPreviewVideos();
    if (window.lucide) window.lucide.createIcons();
  };

  const updateRenderDashboard = (payload) => {
    if (!payload || !renderTableBody) return;

    if (Array.isArray(payload.kpis)) {
      payload.kpis.forEach((kpi, index) => {
        const card = document.querySelector(`[data-kpi-index="${index}"]`);
        if (!card) return;
        const valueNode = card.querySelector("[data-kpi-value]");
        const accentNode = card.querySelector("[data-kpi-accent]");
        const barNode = card.querySelector("[data-kpi-bar]");
        if (valueNode) {
          valueNode.textContent = kpi.value;
          valueNode.className = `text-[28px] font-display font-bold ${kpi.value_class || kpi.accent_class} leading-none tracking-tight`;
        }
          if (accentNode) {
            accentNode.textContent = kpi.accent;
            accentNode.className = `text-[11px] font-semibold ${(kpi.accent_class || kpi.value_class || "")} mt-2.5`;
          }
        if (barNode) {
          barNode.className = `absolute bottom-0 left-1/2 -translate-x-1/2 w-12 h-[3px] rounded-full ${kpi.bar_class}`;
        }
      });
    }

    if (Array.isArray(payload.render_tabs)) {
      payload.render_tabs.forEach((tab, index) => {
        const tabButton = document.querySelector(`[data-render-tab-index="${index}"]`);
        if (!tabButton) return;
        tabButton.textContent = `${tab.label} (${tab.count})`;
      });
    }

    renderJobsState = Array.isArray(payload.render_jobs) ? payload.render_jobs : [];
    renderRenderTable();
  };

  const buildLivePayloadSignature = (payload) => {
    if (!payload) return "";
    const compact = {
      kpis: Array.isArray(payload.kpis)
        ? payload.kpis.map((item) => [item.value, item.accent, item.value_class, item.bar_class])
        : [],
      render_tabs: Array.isArray(payload.render_tabs)
        ? payload.render_tabs.map((item) => [item.label, item.count, item.active])
        : [],
      render_summary: payload.render_summary || "",
      render_jobs: Array.isArray(payload.render_jobs)
        ? payload.render_jobs.map((job) => [
            job.id,
            job.status,
            job.status_class,
            job.render_progress,
            job.upload_progress,
            job.created_at,
            job.render_at,
            job.uploaded_at,
            job.queue_label,
            job.bot,
            job.owner,
            job.preview_url,
            job.channel_avatar_url,
            job.youtube_watch_url,
            job.can_cancel,
          ])
        : [],
    };
    return JSON.stringify(compact);
  };

  const pollLiveDashboard = async () => {
    if (liveRefreshInFlight) return;
    liveRefreshInFlight = true;
    try {
      const response = await fetch("/api/user/dashboard/live", {
        headers: { Accept: "application/json", "Cache-Control": "no-cache" },
      });
      if (!response.ok) return;
      const payload = await response.json();
      const nextSignature = buildLivePayloadSignature(payload);
      if (nextSignature && nextSignature === lastLivePayloadSignature) {
        return;
      }
      lastLivePayloadSignature = nextSignature;
      updateRenderDashboard(payload);
    } catch (_error) {
      // Keep current UI state if polling fails transiently.
    } finally {
      liveRefreshInFlight = false;
    }
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
    const defaultStatus = "";
    const allowedExtensions = String(form.dataset.allowedExtensions || "")
      .split(",")
      .map((item) => item.trim().toLowerCase())
      .filter(Boolean);
    const maxUploadBytes = Number(form.dataset.maxUploadBytes || 0);
    const fallbackChunkBytes = Number(form.dataset.chunkBytes || 8388608);
    const uploadCircumference = 43.98;
    const uploadState = new Map();
    const remoteValidationTimers = new Map();

    const setSlotStatus = (slot, message, tone = "neutral") => {
      const node = document.querySelector(`[data-upload-status="${slot}"]`);
      if (!node) return;
      node.className = "upload-slot-status";
      node.title = message || "";
      if (!message) {
        node.textContent = "";
        return;
      }
      node.classList.add(
        "is-visible",
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

    const extractGoogleDriveFileId = (value) => {
      try {
        const parsed = new URL(String(value || "").trim());
        const host = (parsed.hostname || "").toLowerCase();
        if (!["drive.google.com", "docs.google.com"].includes(host)) {
          return null;
        }
        const queryId = parsed.searchParams.get("id");
        if (queryId) {
          return queryId;
        }
        const match = parsed.pathname.match(/\/file\/d\/([^/]+)/);
        return match?.[1] || null;
      } catch (_error) {
        return null;
      }
    };

    const isSupportedGoogleDriveUrl = (value) => Boolean(extractGoogleDriveFileId(value));

    const validateRemoteSlotValue = (slot, value) => {
      const assetField = document.getElementById(slotToAssetField[slot]);
      const runtime = uploadState.get(slot);
      if ((assetField && assetField.value) || runtime?.state === "uploading" || runtime?.state === "success") {
        return;
      }

      const trimmed = String(value || "").trim();
      if (!trimmed) {
        setSlotStatus(slot, defaultStatus, "neutral");
        return;
      }

      let parsed;
      try {
        parsed = new URL(trimmed);
      } catch (_error) {
        setSlotStatus(slot, "Link không hợp lệ", "error");
        return;
      }

      if (!["http:", "https:"].includes(parsed.protocol)) {
        setSlotStatus(slot, "Link không hợp lệ", "error");
        return;
      }

      const host = (parsed.hostname || "").toLowerCase();
      if (host === "drive.google.com" || host === "docs.google.com") {
        if (isSupportedGoogleDriveUrl(trimmed)) {
          setSlotStatus(slot, "Link hoạt động", "success");
          return;
        }
        setSlotStatus(slot, "Link Drive chưa đúng định dạng", "error");
        return;
      }

      setSlotStatus(slot, "Chỉ nhận link Drive", "error");
    };

    const scheduleRemoteSlotValidation = (slot, value) => {
      const existingTimer = remoteValidationTimers.get(slot);
      if (existingTimer) {
        window.clearTimeout(existingTimer);
      }

      const trimmed = String(value || "").trim();
      if (!trimmed) {
        setSlotStatus(slot, defaultStatus, "neutral");
        remoteValidationTimers.delete(slot);
        return;
      }

      setSlotStatus(slot, "Đang kiểm tra...", "uploading");
      const timer = window.setTimeout(() => {
        validateRemoteSlotValue(slot, value);
        remoteValidationTimers.delete(slot);
      }, 220);
      remoteValidationTimers.set(slot, timer);
    };

    const getSlotNodes = (slot) => ({
      trigger: document.querySelector(`[data-upload-trigger="${slot}"]`),
      ring: document.querySelector(`[data-upload-ring="${slot}"]`),
      center: document.querySelector(`[data-upload-center="${slot}"]`),
      input: document.querySelector(`[data-upload-input="${slot}"]`),
      path: document.querySelector(`[data-upload-slot="${slot}"] input[type="text"]`),
      asset: document.getElementById(slotToAssetField[slot]),
    });

    const setUploadVisual = (slot, state, options = {}) => {
      const { progress = 0 } = options;
      const nodes = getSlotNodes(slot);
      if (!(nodes.trigger instanceof HTMLElement)) return;
      nodes.trigger.dataset.state = state;
      if (nodes.ring instanceof SVGCircleElement) {
        const clamped = Math.max(0, Math.min(1, progress));
        nodes.ring.style.strokeDasharray = String(uploadCircumference);
        nodes.ring.style.strokeDashoffset = String(uploadCircumference * (1 - clamped));
      }
    };

    const clearSlotUpload = async (slot, options = {}) => {
      const { preservePath = false, preserveStatus = false, skipRemoteAbort = false } = options;
      const nodes = getSlotNodes(slot);
      const runtime = uploadState.get(slot);

      if (runtime?.controller) {
        runtime.controller.abort();
      }

      if (!skipRemoteAbort && runtime?.sessionId) {
        try {
          await fetch(`/api/user/uploads/sessions/${runtime.sessionId}`, { method: "DELETE" });
        } catch (_error) {
          // Ignore cleanup failure; UI should still recover locally.
        }
      }

      if (runtime?.storageKey) {
        window.localStorage.removeItem(runtime.storageKey);
      }

      uploadState.delete(slot);
      if (nodes.asset) nodes.asset.value = "";
      if (nodes.input instanceof HTMLInputElement) nodes.input.value = "";
      if (!preservePath && nodes.path instanceof HTMLInputElement) nodes.path.value = "";
      if (!preserveStatus) setSlotStatus(slot, defaultStatus, "neutral");
      setUploadVisual(slot, "idle", { progress: 0 });
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

    const getOrCreateUploadSession = async (slot, file, signal) => {
      const storageKey = buildUploadStorageKey(slot, file);
      const cachedSessionId = window.localStorage.getItem(storageKey);
      if (cachedSessionId) {
        const statusResponse = await fetch(`/api/user/uploads/sessions/${cachedSessionId}`, { signal });
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
        signal,
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

    const uploadLocalFile = async (slot, file, options = {}) => {
      const { signal, onProgress, onSession } = options;
      validateLocalFile(file);
      const assetField = document.getElementById(slotToAssetField[slot]);
      if (!assetField) {
        throw new Error(`Thiếu hidden field cho slot ${slot}.`);
      }
      assetField.value = "";

      const { storageKey, session: initialSession } = await getOrCreateUploadSession(slot, file, signal);
      let session = initialSession;
      onSession?.(session, storageKey);
      if (session.status === "completed" && session.asset_id) {
        assetField.value = session.asset_id;
        setSlotStatus(slot, `Sẵn sàng: ${file.name}`, "success");
        onProgress?.(1, session);
        return { assetId: session.asset_id, session, storageKey };
      }

      const chunkBytes = Number(session.chunk_size || fallbackChunkBytes);
      let offset = Number(session.received_bytes || 0);
      while (offset < file.size) {
        const nextChunk = file.slice(offset, Math.min(offset + chunkBytes, file.size));
        onProgress?.(file.size > 0 ? offset / file.size : 0, session);
        setSlotStatus(
          slot,
          `${Math.floor((offset / file.size) * 100)}% · ${formatBytes(offset)}/${formatBytes(file.size)}`,
          "uploading"
        );
        const response = await fetch(`/api/user/uploads/sessions/${session.session_id}`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/octet-stream",
            "x-upload-offset": String(offset),
          },
          signal,
          body: nextChunk,
        });
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload.detail || `Upload ${file.name} thất bại.`);
        }
        session = payload;
        onSession?.(session, storageKey);
        offset = Number(payload.received_bytes || 0);
      }

      if (!session.asset_id) {
        throw new Error(`Upload ${file.name} đã xong nhưng chưa có asset id.`);
      }
      assetField.value = session.asset_id;
      window.localStorage.setItem(storageKey, session.session_id);
      onProgress?.(1, session);
      setSlotStatus(slot, `Hoàn tất: ${file.name} (${formatBytes(file.size)})`, "success");
      return { assetId: session.asset_id, session, storageKey };
    };

    const startSlotUpload = async (slot, file) => {
      const nodes = getSlotNodes(slot);
      if (!(nodes.input instanceof HTMLInputElement) || !(nodes.path instanceof HTMLInputElement)) return;

      await clearSlotUpload(slot, { preserveStatus: true, skipRemoteAbort: false });
      nodes.path.value = file.name;
      setSlotStatus(slot, "Đang chuẩn bị upload...", "uploading");
      setUploadVisual(slot, "uploading", { progress: 0 });

      const controller = new AbortController();
      uploadState.set(slot, {
        state: "uploading",
        controller,
        sessionId: null,
        storageKey: null,
        fileName: file.name,
      });

      try {
        const result = await uploadLocalFile(slot, file, {
          signal: controller.signal,
          onSession: (session, storageKey) => {
            const current = uploadState.get(slot) || {};
            uploadState.set(slot, {
              ...current,
              state: session.status === "completed" ? "success" : "uploading",
              sessionId: session.session_id,
              storageKey,
              fileName: file.name,
            });
          },
          onProgress: (progress) => {
            setUploadVisual(slot, "uploading", { progress });
          },
        });

        uploadState.set(slot, {
          state: "success",
          controller: null,
          sessionId: result.session.session_id,
          storageKey: result.storageKey,
          fileName: file.name,
        });
        nodes.input.value = "";
        setUploadVisual(slot, "success", { progress: 1 });
      } catch (error) {
        if (error?.name === "AbortError") {
          await clearSlotUpload(slot, { skipRemoteAbort: false });
          setSlotStatus(slot, "", "neutral");
          return;
        }
        await clearSlotUpload(slot, { preservePath: true, skipRemoteAbort: false });
        setUploadVisual(slot, "error", { progress: 0 });
        setSlotStatus(slot, error.message || "Upload file local thất bại.", "error");
      }
    };

    document.querySelectorAll("[data-upload-input]").forEach((input) => {
      input.addEventListener("change", async (event) => {
        const target = event.currentTarget;
        if (!(target instanceof HTMLInputElement)) return;
        const slot = target.dataset.uploadInput;
        const file = target.files?.[0];
        if (!slot || !file) return;
        await startSlotUpload(slot, file);
      });
    });

    document.querySelectorAll("[data-upload-trigger]").forEach((button) => {
      button.addEventListener("click", async () => {
        const slot = button.getAttribute("data-upload-trigger");
        if (!slot) return;
        const state = button.dataset.state || "idle";
        if (state === "idle") return;
        await clearSlotUpload(slot, { skipRemoteAbort: false });
      });
    });

    document.querySelectorAll("[data-upload-slot] input[type='text']").forEach((input) => {
      input.addEventListener("input", async (event) => {
        const target = event.currentTarget;
        if (!(target instanceof HTMLInputElement)) return;
        const slotRoot = target.closest("[data-upload-slot]");
        const slot = slotRoot?.getAttribute("data-upload-slot");
        if (!slot) return;
        const assetField = document.getElementById(slotToAssetField[slot]);
        const runtime = uploadState.get(slot);
        if ((assetField && assetField.value) || runtime) {
          await clearSlotUpload(slot, { preservePath: true, skipRemoteAbort: false });
        }
        scheduleRemoteSlotValidation(slot, target.value);
      });

      input.addEventListener("blur", (event) => {
        const target = event.currentTarget;
        if (!(target instanceof HTMLInputElement)) return;
        const slotRoot = target.closest("[data-upload-slot]");
        const slot = slotRoot?.getAttribute("data-upload-slot");
        if (!slot) return;
        const existingTimer = remoteValidationTimers.get(slot);
        if (existingTimer) {
          window.clearTimeout(existingTimer);
          remoteValidationTimers.delete(slot);
        }
        validateRemoteSlotValue(slot, target.value);
      });
    });

    const setSubmitting = (submitting) => {
      submitButton.disabled = submitting;
      submitButton.textContent = submitting ? "Đang tạo..." : "Tạo job render";
    };

    resetButton.addEventListener("click", async () => {
      form.reset();
      const channelInput = document.getElementById("selectedChannel");
      if (channelInput) {
        channelInput.value = "";
      }
      const placeholderOption = document.querySelector(".channel-option[data-value='']");
      if (placeholderOption) {
        placeholderOption.click();
      }
      for (const [slot, fieldId] of Object.entries(slotToAssetField)) {
        const field = document.getElementById(fieldId);
        if (field) field.value = "";
        const validationTimer = remoteValidationTimers.get(slot);
        if (validationTimer) {
          window.clearTimeout(validationTimer);
          remoteValidationTimers.delete(slot);
        }
        await clearSlotUpload(slot, { skipRemoteAbort: false });
      }
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

      if ([...uploadState.values()].some((item) => item?.state === "uploading")) {
        showFormMessage("Đang có file local chưa upload xong. Hoàn tất hoặc hủy upload trước khi tạo job.", "error");
        return;
      }

      const remoteSlots = [
        { slot: "intro", label: "Link video Intro" },
        { slot: "video_loop", label: "Link video loop" },
        { slot: "audio_loop", label: "Link audio loop" },
        { slot: "outro", label: "Link Outro" },
      ];

      for (const item of remoteSlots) {
        const nodes = getSlotNodes(item.slot);
        const remoteValue = nodes.path instanceof HTMLInputElement ? nodes.path.value.trim() : "";
        const hasLocalAsset = nodes.asset instanceof HTMLInputElement ? Boolean(nodes.asset.value) : false;
        const runtime = uploadState.get(item.slot);
        if (!remoteValue || hasLocalAsset || runtime?.state === "uploading" || runtime?.state === "success") {
          continue;
        }
        if (!isSupportedGoogleDriveUrl(remoteValue)) {
          validateRemoteSlotValue(item.slot, remoteValue);
          showFormMessage(`${item.label} chỉ nhận link Google Drive hợp lệ.`, "error");
          return;
        }
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

  const initBulkDeleteVisibleJobs = () => {
    if (!(deleteVisibleJobsButton instanceof HTMLButtonElement)) return;

    deleteVisibleJobsButton.addEventListener("click", async () => {
      const { pageJobs } = getVisibleRenderPageJobs();
      if (!pageJobs.length) return;

      const confirmed = window.confirm(`Xóa nhanh ${pageJobs.length} job đang hiển thị trên trang này?`);
      if (!confirmed) return;

      deleteVisibleJobsButton.disabled = true;
      try {
        const response = await fetch("/api/user/jobs/actions/bulk-delete", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            job_ids: pageJobs.map((job) => job.id),
          }),
        });
        const payload = await response.json();
        if (!response.ok) {
          throw new Error(payload.detail || "Khong the xoa danh sach dang hien thi.");
        }
        window.location.reload();
      } catch (error) {
        window.alert(error.message || "Khong the xoa danh sach dang hien thi.");
        renderRenderTable();
      }
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
    if (!renderSearchInput || !renderTableBody) return;
    renderSearchInput.addEventListener("input", () => {
      applyRenderSearch();
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

  const initTransientNotice = () => {
    const notice = document.querySelector("[data-transient-notice]");
    if (!notice) {
      clearTransientNoticeParams();
      return;
    }

    let dismissed = false;
    const dismiss = () => {
      if (dismissed) return;
      dismissed = true;
      notice.classList.add("opacity-0", "-translate-y-1");
      window.setTimeout(() => {
        notice.remove();
      }, 200);
      clearTransientNoticeParams();
    };

    notice.querySelector("[data-notice-close]")?.addEventListener("click", dismiss);

    const autoHideMs = Number(notice.getAttribute("data-notice-autohide") || 0);
    if (autoHideMs > 0) {
      window.setTimeout(dismiss, autoHideMs);
    }
  };

  const initJobPreviewVideos = () => {
    document.querySelectorAll(".job-preview-media[src]").forEach((node) => {
      if (!(node instanceof HTMLVideoElement)) return;
      node.addEventListener("loadeddata", () => {
        try {
          if (node.readyState >= 2) {
            node.currentTime = Math.min(0.1, Number(node.duration || 0.1));
          }
        } catch (_error) {
          // Ignore preview seek failures; fallback is still acceptable.
        }
      }, { once: true });
    });
  };

  if (window.lucide) {
    window.lucide.createIcons();
  }

  if (dashboardSeedNode?.textContent) {
    try {
      const dashboardSeed = JSON.parse(dashboardSeedNode.textContent);
      renderJobsState = Array.isArray(dashboardSeed.render_jobs) ? dashboardSeed.render_jobs : [];
      lastLivePayloadSignature = buildLivePayloadSignature(dashboardSeed);
    } catch (_error) {
      renderJobsState = [];
      lastLivePayloadSignature = "";
    }
  }

  refreshRenderHeaderButtons();

  bindRenderSortButtons();
  initChannelSelect();
  initFlatpickr();
  initFileInputs();
  initForm();
  initOAuthButton();
  initBulkDeleteVisibleJobs();
  initChannelActions();
  initSearch();
  renderRenderTable();
  initTransientNotice();
  pollLiveDashboard();
  liveRefreshHandle = window.setInterval(pollLiveDashboard, 5000);
})();
