(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  // ✅ gviz callback (전역)
  window.handleScheduleSheet = function handleScheduleSheet(resp) {
    try {
      const rows = (resp && resp.table && resp.table.rows) ? resp.table.rows : [];
      const byDay = {};
      const dayLabelByCol = {};
      let currentPeriod = "";

      rows.forEach((row) => {
        const cells = row.c || [];
        const values = cells.map(c => (c && c.v != null) ? String(c.v).trim() : "");

        for (let j = 1; j < values.length; j++) {
          const v = values[j];
          if (v && v.includes("요일")) dayLabelByCol[j] = v;
        }

        const v0 = values[0];
        if (!v0) return;

        if (v0.includes("오전") || v0.includes("오후")) { currentPeriod = v0; return; }
        if (!v0.endsWith("시")) return;

        const timeLabel = currentPeriod ? (currentPeriod + " " + v0) : v0;

        for (let j = 1; j < values.length; j++) {
          const title = values[j];
          const dayLabel = dayLabelByCol[j];
          if (!dayLabel) continue;
          if (!byDay[dayLabel]) byDay[dayLabel] = [];
          if (title) byDay[dayLabel].push({ time: timeLabel, title: title });
        }
      });

      const gridEl  = document.getElementById("top-schedule-grid");
      const emptyEl = document.getElementById("top-schedule-empty");
      if (!gridEl || !emptyEl) return;

      gridEl.innerHTML = "";
      emptyEl.style.display = "none";

      const dayOrder = ["월요일","화요일","수요일","목요일","금요일","토요일","일요일"];
      dayOrder.forEach(dayLabel => {
        const dayDiv = document.createElement("div");
        dayDiv.className = "top-schedule-day";

        const nameDiv = document.createElement("div");
        nameDiv.className = "top-schedule-day-name";
        nameDiv.textContent = dayLabel;
        dayDiv.appendChild(nameDiv);

        const items = byDay[dayLabel] || [];
        if (!items.length) {
          const none = document.createElement("div");
          none.className = "top-schedule-empty-day";
          none.textContent = "-";
          dayDiv.appendChild(none);
        } else {
          items.forEach(item => {
            const itemDiv = document.createElement("div");
            itemDiv.className = "top-schedule-item";
            itemDiv.innerHTML =
              '<div class="top-schedule-time">' + item.time + '</div>' +
              '<div class="top-schedule-title">' + item.title + '</div>';
            dayDiv.appendChild(itemDiv);
          });
        }
        gridEl.appendChild(dayDiv);
      });

    } catch (e) {
      console.error("schedule sheet parse error:", e);
      const emptyEl = document.getElementById("top-schedule-empty");
      if (emptyEl) {
        emptyEl.textContent = "스케쥴 정보를 불러오는 중 오류가 발생했습니다.";
        emptyEl.style.display = "block";
      }
    }
  };

  U.schedule = {
    init() {
      // ✅ gviz 스크립트는 여기서만 1회 로드 (중복 방지)
      if (!U.CONFIG || !U.CONFIG.SCHEDULE_GVIZ_URL) return;

      if (!document.querySelector('script[data-schedule="1"]')) {
        const s = document.createElement("script");
        s.setAttribute("data-schedule", "1");
        s.src = U.CONFIG.SCHEDULE_GVIZ_URL;
        document.body.appendChild(s);
      }

      // ✅ 5초 후에도 비어있으면 안내
      setTimeout(() => {
        const emptyEl = document.getElementById("top-schedule-empty");
        const gridEl = document.getElementById("top-schedule-grid");
        const hasItems = gridEl && gridEl.children && gridEl.children.length > 0;
        if (emptyEl && emptyEl.style.display !== "none" && !hasItems) {
          emptyEl.textContent = "주간 스케쥴을 불러오지 못했습니다. (docs.google.com 차단/확장프로그램 확인)";
        }
      }, 5000);
    }
  };
})();
