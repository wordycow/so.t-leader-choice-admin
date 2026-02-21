// === 설정(Config) ===
const CONFIG = {
    // 서버 주소 (사용자님 고유 주소)
    API_URL: "https://script.google.com/macros/s/AKfycbxtdOVoV2PtB_UbCLu2OzZHo6JjNks-0gk4s2fci52HjuuBNy3uwuf7DP7ePTK7S6VI/exec",
    
    imgObj: {
        path: 'https://wordycow.github.io/so.t-leader-choice/games/img/slot/', 
        bg: ['bg1.png', 'bg2.png', 'bg3.png', 'bg4.png', 'bg5.png'],
        symbols: [
            'star1.png', 'star2.png', 'star3.png',
            'pro1.png', 'pro2.png', 'pro3.png', 'pro4.png', 'pro5.png',
            'pro6.png', 'pro7.png', 'pro8.png', 'pro9.png', 'pro10.png'
        ]
    },
    soundObj: {
        path: 'https://wordycow.github.io/so.t-leader-choice/games/sounds/',
        spin: 'spinning-sound.MP3',
        stop: 'stop-stop-stop-sound.MP3',
        win: 'win-sound.MP3',
        lose: 'lose-sound.MP3',
        jackpot: 'jackpot-sound.MP3',
        btn: 'start-button-sound.MP3'
    },
    reels: 5, 
    rows: 3, 
    symbolHeight: 0, 
    bgIntervalTime: 200, 
    dummySymbolCount: 150 
};

let state = {
    id: null, wallet: 0, bet: 10, 
    isSpinning: false, audioEnabled: true, 
    isAuto: false, 
    bgIntervalId: null, jackpotPool: 0   
};

let els = {};
const audios = {};

// === 초기화 ===
async function init() {
    console.log("SLOT ENGINE: FINAL FIXED VERSION");

    els = {
        bg: document.getElementById('game-bg'),
        overlay: document.getElementById('start-overlay'),
        reelsContainer: document.getElementById('reels-container'),
        spinBtn: document.getElementById('btn-spin'),
        walletSpan: document.getElementById('wallet-balance'),
        betSpan: document.getElementById('current-bet'),
        winPanel: document.querySelector('.win-info-panel'),
        winLabel: document.getElementById('win-label'),
        winAmount: document.getElementById('win-amount'),
        plus: document.getElementById('btn-bet-plus'),
        minus: document.getElementById('btn-bet-minus'),
        userId: document.getElementById('user-id'),
        jackpotPool: document.getElementById('jackpot-pool'),
        gameContainer: document.getElementById('game-container'),
        btnSound: document.getElementById('btn-sound'),
        btnAuto: document.getElementById('btn-auto')
    };

    const localId = localStorage.getItem('user_id') || localStorage.getItem('loginId') || localStorage.getItem('id');
    state.id = localId || new URLSearchParams(window.location.search).get('id');

    if (!state.id) {
        if(els.userId) els.userId.innerText = "GUEST";
        if(els.spinBtn) els.spinBtn.disabled = true;
        updateWinPanel("PLEASE LOGIN", "로그인 필요");
    } else {
        if(els.userId) els.userId.innerText = state.id;
        await syncUserData();
    }

    // 오디오 로드
    Object.keys(CONFIG.soundObj).forEach(key => {
        if (key !== 'path') {
            try {
                const audio = new Audio(CONFIG.soundObj.path + CONFIG.soundObj[key]);
                if(key === 'spin') audio.loop = true;
                audios[key] = audio;
            } catch(e) {}
        }
    });

    createReels(); // 최초 1회만 생성 (중요!)

    if(els.overlay) els.overlay.addEventListener('click', unlockAudio);
    if(els.spinBtn) els.spinBtn.addEventListener('click', () => { state.isAuto = false; updateAutoBtn(); onSpinClick(); });
    if(els.plus) els.plus.addEventListener('click', () => changeBet(5));
    if(els.minus) els.minus.addEventListener('click', () => changeBet(-5));
    if(els.btnSound) els.btnSound.addEventListener('click', toggleSound);
    if(els.btnAuto) els.btnAuto.addEventListener('click', toggleAuto);
}

function toggleSound() {
    state.audioEnabled = !state.audioEnabled;
    if(els.btnSound) els.btnSound.classList.toggle("active", state.audioEnabled);
}

function toggleAuto() {
    state.isAuto = !state.isAuto;
    updateAutoBtn();
    if (state.isAuto && !state.isSpinning) {
        onSpinClick();
    }
}

function updateAutoBtn() {
    if(els.btnAuto) {
        els.btnAuto.innerHTML = state.isAuto ? "AUTO<br>ON" : "AUTO<br>OFF";
        els.btnAuto.classList.toggle("active", state.isAuto);
    }
}

function updateWinPanel(label, amount) {
    if (els.winLabel) els.winLabel.innerText = label;
    if (els.winAmount) els.winAmount.innerText = amount;
}

function animateValue(obj, start, end, duration) {
    if(!obj) return;
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.innerText = Math.floor(progress * (end - start) + start).toLocaleString();
        if (progress < 1) window.requestAnimationFrame(step);
        else obj.innerText = end.toLocaleString();
    };
    window.requestAnimationFrame(step);
}

async function syncUserData(animate = false) {
    if (!state.id) return;
    try {
        const res = await jsonpRequest('getSlotState', { id: state.id });
        if (res.ok) {
            const newWallet = Number(res.user.balance);
            state.jackpotPool = Number(res.jackpotTotal);
            if (animate && state.wallet !== newWallet) animateValue(els.walletSpan, state.wallet, newWallet, 1000);
            else if(els.walletSpan) els.walletSpan.innerText = newWallet.toLocaleString();
            state.wallet = newWallet;
            updateUI();
            if(!animate) updateWinPanel("READY", "GOOD LUCK!");
            if(els.spinBtn) els.spinBtn.disabled = false;
        } else {
            updateWinPanel("ERROR", "USER NOT FOUND");
            if(els.spinBtn) els.spinBtn.disabled = true;
        }
    } catch (e) {
        updateWinPanel("ERROR", "NETWORK FAIL");
    }
}

function jsonpRequest(action, params = {}) {
    return new Promise((resolve, reject) => {
        const callbackName = 'cb_' + Math.round(100000 * Math.random());
        const script = document.createElement('script');
        const timeout = setTimeout(() => { cleanup(); reject(new Error("Timeout")); }, 15000); 
        window[callbackName] = function(data) { cleanup(); resolve(data); };
        function cleanup() {
            clearTimeout(timeout);
            if(document.body.contains(script)) document.body.removeChild(script);
            delete window[callbackName];
        }
        params.action = action; params.callback = callbackName;
        script.src = `${CONFIG.API_URL}?${new URLSearchParams(params).toString()}`;
        document.body.appendChild(script);
    });
}

// 릴 생성 (최초 1회만)
function createReels() {
    if(!els.reelsContainer) return;
    els.reelsContainer.innerHTML = '';
    for (let i = 0; i < CONFIG.reels; i++) {
        const reelDiv = document.createElement('div');
        reelDiv.className = 'reel';
        const stripDiv = document.createElement('div');
        stripDiv.className = 'reel-strip';
        let html = '';
        for(let j=0; j < CONFIG.dummySymbolCount; j++) {
            const sym = getRandomSymbolName();
            html += `<div class="symbol" style="background-image: url('${CONFIG.imgObj.path}${sym}')"></div>`;
        }
        stripDiv.innerHTML = html;
        reelDiv.appendChild(stripDiv);
        els.reelsContainer.appendChild(reelDiv);
    }
    setTimeout(() => {
        const firstSymbol = document.querySelector('.symbol');
        if(firstSymbol) CONFIG.symbolHeight = firstSymbol.offsetHeight;
    }, 100);
}

function getRandomSymbolName() {
    return CONFIG.imgObj.symbols[Math.floor(Math.random() * CONFIG.imgObj.symbols.length)];
}

async function onSpinClick() {
    if (state.isSpinning) return;
    if (state.wallet < state.bet) {
        state.isAuto = false; updateAutoBtn();
        await syncUserData(); 
        if(state.wallet < state.bet) { alert("잔액 부족 (UT)"); return; }
    }

    state.isSpinning = true;
    els.spinBtn.disabled = true;
    updateWinPanel("SPINNING...", `BET: ${state.bet}`);
    
    animateValue(els.walletSpan, state.wallet, state.wallet - state.bet, 500);
    state.wallet -= state.bet; 

    if(state.audioEnabled) {
        audios.btn.play();
        audios.spin.currentTime = 0;
        audios.spin.play();
    }
    startBgEffect(); 

    const strips = document.querySelectorAll('.reel-strip');
    const symbolDom = document.querySelector('.symbol');
    if(symbolDom) CONFIG.symbolHeight = symbolDom.offsetHeight;

    // [핵심 1] 스핀 시작할 때 몰래 원위치로 리셋 (사용자 눈에는 순식간이라 안 보임)
    strips.forEach((strip) => {
        strip.style.transition = 'none';
        strip.style.transform = 'translateY(0px)';
    });
    void els.gameContainer.offsetWidth; // 브라우저가 리셋을 인식하게 강제

    // [핵심 2] 왼쪽부터 순차 출발 (다다다닥)
    strips.forEach((strip, index) => {
        const startDelay = index * 100; // 0.1초 차이
        setTimeout(() => {
            strip.style.transition = `transform 4s linear`; 
            // 130번째 심볼까지 쭉 이동
            const targetY = -(CONFIG.symbolHeight * (CONFIG.dummySymbolCount - 20));
            strip.style.transform = `translateY(${targetY}px)`; 
        }, startDelay);
    });

    try {
        const res = await jsonpRequest('slotSpin', { id: state.id, bet: state.bet });
        if (!res.ok) throw new Error(res.error || "Spin Failed");
        stopReelsWithResult(res);
    } catch (err) {
        console.error(err);
        stopBgEffect();
        audios.spin.pause();
        state.isSpinning = false;
        els.spinBtn.disabled = false;
        updateWinPanel("ERROR", "TRY AGAIN");
        state.isAuto = false; updateAutoBtn();
        syncUserData(true);
    }
}

function stopReelsWithResult(data) {
    const serverKeys = data.spin.keys;
    const strips = document.querySelectorAll('.reel-strip');
    const STOP_INDEX = CONFIG.dummySymbolCount - 30; // 멈출 위치

    strips.forEach((strip, colIdx) => {
        const topSym = serverKeys[colIdx] + ".png";       
        const midSym = serverKeys[colIdx + 5] + ".png";   
        const botSym = serverKeys[colIdx + 10] + ".png";  

        // 멈출 위치(STOP_INDEX)에 서버 결과 이미지를 심어둠
        const symbols = strip.querySelectorAll('.symbol');
        if(symbols[STOP_INDEX]) symbols[STOP_INDEX].style.backgroundImage = `url('${CONFIG.imgObj.path}${topSym}')`;
        if(symbols[STOP_INDEX + 1]) symbols[STOP_INDEX + 1].style.backgroundImage = `url('${CONFIG.imgObj.path}${midSym}')`;
        if(symbols[STOP_INDEX + 2]) symbols[STOP_INDEX + 2].style.backgroundImage = `url('${CONFIG.imgObj.path}${botSym}')`;

        // [핵심 3] 순차 정지 (왼쪽부터 탁.. 탁.. 탁..)
        const stopDelay = colIdx * 500; // 0.5초 차이
        
        setTimeout(() => {
            strip.style.transition = 'transform 0.5s cubic-bezier(0.16, 1, 0.3, 1)'; 
            const finalY = -(STOP_INDEX * CONFIG.symbolHeight);
            strip.style.transform = `translateY(${finalY}px)`;

            if(state.audioEnabled) {
                const stopSound = audios.stop.cloneNode();
                stopSound.volume = 0.6;
                stopSound.play();
            }

            // 마지막 릴이 멈출 때 화면 흔들림
            if (colIdx === CONFIG.reels - 1) {
                if(els.gameContainer) {
                    els.gameContainer.classList.add('shake');
                    setTimeout(() => els.gameContainer.classList.remove('shake'), 500);
                }
            }
        }, 1500 + stopDelay); // 기본 스핀 시간 + 시차
    });

    const totalTime = 1500 + ((CONFIG.reels - 1) * 500) + 700;
    setTimeout(() => {
        handleSpinEnd(data);
    }, totalTime);
}

function handleSpinEnd(data) {
    state.isSpinning = false;
    stopBgEffect();
    els.spinBtn.disabled = false;
    audios.spin.pause();

    const spin = data.spin;
    const oldWallet = state.wallet;
    const newWallet = data.user.balance;
    state.jackpotPool = data.jackpotTotal;

    if (newWallet > oldWallet) {
        animateValue(els.walletSpan, oldWallet, newWallet, 1500);
    } else {
        if(els.walletSpan) els.walletSpan.innerText = newWallet.toLocaleString();
    }
    state.wallet = newWallet;

    let sound = audios.lose;
    let labelText = "RESULT";
    let amountText = "NO WIN";

    if (spin.kind === "lose") {
        labelText = "TRY AGAIN";
        amountText = "NO WIN";
    } else {
        const payout = spin.payout;
        amountText = `+${payout.toLocaleString()} UT`;
        if (spin.kind === "jackpot") {
            labelText = "★ JACKPOT HIT! ★";
            sound = audios.jackpot;
        } else {
            labelText = "BIG WIN!";
            sound = audios.win;
        }
    }

    updateWinPanel(labelText, amountText);

    if (spin.payout > 0 && state.audioEnabled) {
        sound.currentTime = 0;
        sound.play();
    }

    updateUI();
    if(els.jackpotPool) els.jackpotPool.innerText = state.jackpotPool.toLocaleString();

    // [핵심 4] 여기에 있던 '릴 리셋 코드'를 삭제했습니다!
    // 이제 멈춘 상태 그대로 유지됩니다.

    // 오토 스핀 대기
    if (state.isAuto) {
        setTimeout(() => {
            if (state.isAuto && state.wallet >= state.bet) {
                onSpinClick();
            } else if (state.wallet < state.bet) {
                state.isAuto = false;
                updateAutoBtn();
                alert("잔액 부족으로 자동 스핀이 중지되었습니다.");
            }
        }, 2000); 
    }
}

function startBgEffect() {
    let idx = 0;
    state.bgIntervalId = setInterval(() => {
        idx = (idx + 1) % CONFIG.imgObj.bg.length;
        if(els.bg) els.bg.style.backgroundImage = `url('${CONFIG.imgObj.path}${CONFIG.imgObj.bg[idx]}')`;
    }, CONFIG.bgIntervalTime);
}

function stopBgEffect() {
    clearInterval(state.bgIntervalId);
    if(els.bg) els.bg.style.backgroundImage = `url('${CONFIG.imgObj.path}bg1.png')`;
}

function unlockAudio() {
    if(els.overlay) els.overlay.style.display = 'none';
    audios.btn.play().catch(()=>{}); 
}

function updateUI() {
    if(els.betSpan) els.betSpan.innerText = state.bet.toLocaleString();
}

function updateTicker(jackpotAmount) {
    if(els.ticker) els.ticker.innerText = `★ JACKPOT POOL: ${jackpotAmount.toLocaleString()} UT ★ [NOTICE] 5연속 MEGA WIN 25배 지급! ★ THE UNIQUE SLOT OPEN ★`;
}

function changeBet(delta) {
    if(state.isSpinning) return;
    const newBet = state.bet + delta;
    if(newBet >= 5 && newBet <= 1000) {
        state.bet = newBet;
        updateUI();
    }
}

window.onload = init;
