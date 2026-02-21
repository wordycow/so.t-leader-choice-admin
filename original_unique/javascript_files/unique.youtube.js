(function () {
  window.UNIQUE = window.UNIQUE || {};
  const U = window.UNIQUE;

  function loadYouTubeApi() {
    if (document.querySelector('script[data-yt="1"]')) return;
    const tag = document.createElement("script");
    tag.setAttribute("data-yt", "1");
    tag.src = "https://www.youtube.com/iframe_api";
    const first = document.getElementsByTagName("script")[0];
    first.parentNode.insertBefore(tag, first);
  }

  U.youtube = {
    init() {
      loadYouTubeApi();

      // ✅ 전역 콜백 (YT가 호출)
      window.onYouTubeIframeAPIReady = () => {
        const KEY = "mining_video_claim_date";
        const today = U.utils.getTodayKST();

        const statusText = document.getElementById("yt-status-text");
        const rewardBtn = document.getElementById("btn-claim-video-reward");

        const last = localStorage.getItem(KEY);
        if (last === today) {
          if (statusText) { statusText.textContent = "✅ 오늘 학습 완료 (내일 다시 도전!)"; statusText.className = "mining-status done"; }
          if (rewardBtn) { rewardBtn.textContent = "오늘 보상 완료"; rewardBtn.disabled = true; rewardBtn.classList.remove("ready"); }
        } else {
          if (rewardBtn) { rewardBtn.textContent = "학습 보상 받기 (대기중)"; rewardBtn.disabled = true; }
        }

        new YT.Player("youtube-player", {
          height: "100%",
          width: "100%",
          videoId:"S6ypLQqX1qY",
          playerVars: { origin: window.location.origin, rel: 0, playsinline: 1 },
          events: {
            onStateChange: function (ev) {
              const today = U.utils.getTodayKST();
              const last = localStorage.getItem(KEY);

              if (ev.data === YT.PlayerState.PLAYING && last !== today) {
                if (statusText) { statusText.textContent = "🔥 시청 중... 끝까지 보세요!"; statusText.className = "mining-status"; }
              }
              if (ev.data === YT.PlayerState.ENDED && last !== today) {
                if (rewardBtn) {
                  rewardBtn.textContent = "보상을 받을 준비가 완료 됐습니다";
                  rewardBtn.disabled = false;
                  rewardBtn.classList.add("ready");
                }
                if (statusText) {
                  statusText.textContent = "✅ 시청 완료! 왼쪽 버튼을 눌러 보상을 받으세요.";
                  statusText.className = "mining-status done";
                }
              }
            }
          }
        });
      };
    },

    bindRewardButton() {
      const rewardBtn = document.getElementById("btn-claim-video-reward");
      if (!rewardBtn || rewardBtn.dataset.bound === "1") return;
      rewardBtn.dataset.bound = "1";

      rewardBtn.addEventListener("click", async function () {
        const KEY = "mining_video_claim_date";
        const today = U.utils.getTodayKST();
        if (localStorage.getItem(KEY) === today) return;

        this.disabled = true;
        const prev = this.textContent;
        this.textContent = "지급 중...";

        try {
          await U.wallet.addUt(U.STATE.videoReward);
          localStorage.setItem(KEY, today);

          this.textContent = "오늘 보상 완료";
          this.classList.remove("ready");

          const statusText = document.getElementById("yt-status-text");
          if (statusText) { statusText.textContent = "✅ 오늘 학습 완료 (내일 다시 도전!)"; statusText.className = "mining-status done"; }

          alert(`🎉 ${U.STATE.videoReward} UT가 지급되었습니다!`);
        } catch (e) {
          console.error(e);
          this.disabled = false;
          this.textContent = prev || "학습 보상 받기";
          alert("보상 지급 실패: " + (e.message || e));
        }
      });
    },

    bindLuckyBox() {
      const luckyBtn = document.getElementById("btn-lucky-box");
      if (!luckyBtn || luckyBtn.dataset.bound === "1") return;
      luckyBtn.dataset.bound = "1";

      const KEY = "lucky_box_claim_date";
      const today = U.utils.getTodayKST();
      if (localStorage.getItem(KEY) === today) {
        luckyBtn.disabled = true;
        luckyBtn.textContent = "오늘의 행운 완료 (내일 다시)";
      }

      luckyBtn.addEventListener("click", async function () {
        const today = U.utils.getTodayKST();
        if (localStorage.getItem(KEY) === today) return;

        const reward = Math.floor(Math.random() * (U.STATE.luckyMax - U.STATE.luckyMin + 1)) + U.STATE.luckyMin;

        this.disabled = true;
        const prev = this.textContent;
        this.textContent = "지급 중...";

        try {
          await U.wallet.addUt(reward);
          localStorage.setItem(KEY, today);
          this.textContent = "오늘의 행운 완료";
          alert(`🎁 럭키박스 당첨! +${reward} UT 지급되었습니다.`);
        } catch (e) {
          console.error(e);
          this.disabled = false;
          this.textContent = prev || "🎁 데일리 럭키박스 (1일 1회)";
          alert("럭키박스 지급 실패: " + (e.message || e));
        }
      });
    }
  };
})();
