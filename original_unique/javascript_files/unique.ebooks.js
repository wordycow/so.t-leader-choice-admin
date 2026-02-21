(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  function render(items){
    const listEl = document.getElementById("ebook-list");
    if (!listEl) return;

    const visible = (items || []).filter(x => x && x.visible !== false);
    if (!visible.length){
      listEl.innerHTML = '<div style="color:#64748b;font-size:12px;padding:8px;">eBook 목록이 없습니다.</div>';
      return;
    }

    visible.sort((a,b) => (a.order||0)-(b.order||0));
    listEl.innerHTML = "";

    visible.forEach(book => {
      const card = document.createElement("a");
      card.className = "ebook-card";
      card.href = book.link || "#";

      // ✅ 링크가 있는 경우만 인터셉트(보상 + 새탭 열기)
      if (book.link && book.link !== "#"){
        card.addEventListener("click", async (e) => {
          e.preventDefault();

          const KEY = "lastEbookRewardDate";
          const today = U.utils.getTodayKST();
          const already = (localStorage.getItem(KEY) === today);

          // 이미 오늘 받았으면 보상 없이 새탭만 열고 종료
          if (already) {
            window.open(book.link, "_blank", "noopener,noreferrer");
            return;
          }

          // 오늘 첫 보상 시도
          localStorage.setItem(KEY, today);
          try{
            await U.wallet.addUt(U.STATE.ebookReward);
            alert(`📖 [${book.title || "EBOOK"}] 학습 시작!\n(오늘의 독서 보너스 +${U.STATE.ebookReward} UT 지급)`);
            window.open(book.link, "_blank", "noopener,noreferrer");
          } catch(e2){
            localStorage.removeItem(KEY);
            alert("독서 보너스 지급 실패: " + (e2.message || e2));
            // 실패해도 ebook은 열어준다(원하면 이 줄 제거)
            window.open(book.link, "_blank", "noopener,noreferrer");
          }
        });
      }

      const thumb = document.createElement("div");
      thumb.className = "ebook-thumb";
      const img = document.createElement("img");
      img.src = book.cover || "img/ebook-the-unique-system-book.jpg";
      img.alt = book.title || "";
      img.style.objectPosition = "50% " + ((typeof book.posY === "number") ? book.posY : 50) + "%";
      thumb.appendChild(img);

      const body = document.createElement("div");
      const t = document.createElement("div");
      t.className = "ebook-meta-title";
      t.textContent = book.title || "";
      const d = document.createElement("div");
      d.className = "ebook-meta-desc";
      d.textContent = book.description || book.subtitle || "";
      const cta = document.createElement("div");
      cta.className = "ebook-meta-cta";
      cta.textContent = "클릭하여 eBook 열람";

      body.appendChild(t);
      body.appendChild(d);
      body.appendChild(cta);

      card.appendChild(thumb);
      card.appendChild(body);
      listEl.appendChild(card);
    });
  }

  U.ebooks = {
    async load(){
      try{
        const res = await fetch(U.CONFIG.EBOOK_JSON, { cache: "no-store" });
        if (!res.ok) throw new Error("ebook-config.json not found");
        const data = await res.json();
        const items = Array.isArray(data) ? data : (data.items || []);
        if (items && items.length) { render(items); return; }
      } catch(_){}
      render(U.CONFIG.EBOOK_FALLBACK);
    }
  };
})();
