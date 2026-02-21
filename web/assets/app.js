// Lee May Trading System - Unified JavaScript
// Common functions for both control and trading dashboards

// Global state
let refreshInterval = null;

// Add log entry
function addLog(message, type = 'info') {
    const logOutput = document.getElementById('log-output');
    if (!logOutput) return;
    
    const timestamp = new Date().toLocaleTimeString('ko-KR');
    const logEntry = document.createElement('div');
    logEntry.className = `log-entry ${type}`;
    logEntry.textContent = `[${timestamp}] ${message}`;
    
    // Add to top
    logOutput.insertBefore(logEntry, logOutput.firstChild);
    
    // Keep only last 50 entries
    while (logOutput.children.length > 50) {
        logOutput.removeChild(logOutput.lastChild);
    }
}

// Refresh system status
async function refreshStatus() {
    try {
        // Check Control Server (5001)
        const controlStatus = document.getElementById('control-status');
        if (controlStatus) {
            try {
                const controlResponse = await fetch('/api/health', { 
                    method: 'GET',
                    signal: AbortSignal.timeout(3000)
                });
                
                if (controlResponse.ok) {
                    controlStatus.textContent = '● Running';
                    controlStatus.classList.add('active');
                } else {
                    controlStatus.textContent = '○ Offline';
                    controlStatus.classList.remove('active');
                }
            } catch (error) {
                controlStatus.textContent = '○ Error';
                controlStatus.classList.remove('active');
            }
        }
        
        // Check Trading Server (5000)
        const tradingStatus = document.getElementById('trading-status');
        if (tradingStatus) {
            try {
                const tradingResponse = await fetch('/api/health', {
                    method: 'GET',
                    signal: AbortSignal.timeout(3000)
                });
                
                if (tradingResponse.ok) {
                    tradingStatus.textContent = '● Running';
                    tradingStatus.classList.add('active');
                } else {
                    tradingStatus.textContent = '○ Offline';
                    tradingStatus.classList.remove('active');
                }
            } catch (error) {
                tradingStatus.textContent = '○ Error';
                tradingStatus.classList.remove('active');
            }
        }
        
        // Check Bot Engines
        const botsStatus = document.getElementById('bots-status');
        if (botsStatus) {
            try {
                const botsResponse = await fetch('/api/status', {
                    method: 'GET',
                    signal: AbortSignal.timeout(3000)
                });
                
                if (botsResponse.ok) {
                    const data = await botsResponse.json();
                    const runningBots = data.bots ? data.bots.filter(b => b.status === 'running').length : 0;
                    
                    if (runningBots > 0) {
                        botsStatus.textContent = `● ${runningBots} Running`;
                        botsStatus.classList.add('active');
                    } else {
                        botsStatus.textContent = '○ Stopped';
                        botsStatus.classList.remove('active');
                    }
                } else {
                    botsStatus.textContent = '○ Unknown';
                    botsStatus.classList.remove('active');
                }
            } catch (error) {
                botsStatus.textContent = '○ Error';
                botsStatus.classList.remove('active');
            }
        }
        
        // Check IMEI AI
        const imeiStatus = document.getElementById('imei-status');
        if (imeiStatus) {
            try {
                const imeiResponse = await fetch('/api/health', {
                    method: 'GET',
                    signal: AbortSignal.timeout(3000)
                });
                
                if (imeiResponse.ok) {
                    imeiStatus.textContent = '● Active';
                    imeiStatus.classList.add('active');
                } else {
                    imeiStatus.textContent = '○ Offline';
                    imeiStatus.classList.remove('active');
                }
            } catch (error) {
                imeiStatus.textContent = '○ Error';
                imeiStatus.classList.remove('active');
            }
        }
        
        // Update bot engine status indicators
        updateBotEngineStatus('signal-status', '/api/bots/signal/status');
        updateBotEngineStatus('strategy-status', '/api/bots/strategy/status');
        updateBotEngineStatus('execution-status', '/api/bots/execution/status');
        updateBotEngineStatus('risk-status', '/api/bots/risk/status');
        
    } catch (error) {
        console.error('Status refresh error:', error);
    }
}

// Update individual bot engine status
async function updateBotEngineStatus(elementId, endpoint) {
    const element = document.getElementById(elementId);
    if (!element) return;
    
    try {
        const response = await fetch(endpoint, {
            method: 'GET',
            signal: AbortSignal.timeout(2000)
        });
        
        if (response.ok) {
            const data = await response.json();
            
            if (data.running) {
                element.textContent = '●';
                element.classList.add('active');
            } else {
                element.textContent = '○';
                element.classList.remove('active');
            }
            
            // Update metrics if available
            if (elementId === 'signal-status' && data.signal_count !== undefined) {
                const countElement = document.getElementById('signal-count');
                if (countElement) countElement.textContent = `신호: ${data.signal_count}`;
            }
            
            if (elementId === 'strategy-status' && data.strategy_count !== undefined) {
                const countElement = document.getElementById('strategy-count');
                if (countElement) countElement.textContent = `전략: ${data.strategy_count}`;
            }
            
            if (elementId === 'execution-status' && data.execution_count !== undefined) {
                const countElement = document.getElementById('execution-count');
                if (countElement) countElement.textContent = `실행: ${data.execution_count}`;
            }
            
            if (elementId === 'risk-status' && data.risk_level !== undefined) {
                const levelElement = document.getElementById('risk-level');
                if (levelElement) levelElement.textContent = `리스크: ${data.risk_level}`;
            }
        } else {
            element.textContent = '○';
            element.classList.remove('active');
        }
    } catch (error) {
        element.textContent = '○';
        element.classList.remove('active');
    }
}

// Format utilities
function formatCurrency(value, currency = 'KRW') {
    if (currency === 'KRW') {
        return new Intl.NumberFormat('ko-KR').format(Math.round(value)) + '원';
    }
    return new Intl.NumberFormat('ko-KR', {
        style: 'currency',
        currency: currency
    }).format(value);
}

function formatNumber(value, maxDecimals = 8) {
    return new Intl.NumberFormat('ko-KR', {
        maximumFractionDigits: maxDecimals
    }).format(value);
}

function formatPercent(value, decimals = 2) {
    const sign = value >= 0 ? '+' : '';
    return sign + value.toFixed(decimals) + '%';
}

function formatDateTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleString('ko-KR');
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    return date.toLocaleTimeString('ko-KR');
}

// API request helper
async function apiRequest(endpoint, options = {}) {
    try {
        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json',
            },
            signal: AbortSignal.timeout(10000)
        };
        
        const response = await fetch(endpoint, {
            ...defaultOptions,
            ...options
        });
        
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API Request failed:', error);
        throw error;
    }
}

// Notification helper
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 2rem;
        background: var(--bg-secondary);
        border: 2px solid var(--${type}-color);
        border-radius: 8px;
        color: var(--text-primary);
        box-shadow: var(--shadow-xl);
        z-index: 9999;
        animation: slideIn 0.3s ease-out;
    `;
    
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
    }, 5000);
}

// Add CSS for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

// Error handler
window.addEventListener('error', (event) => {
    console.error('Global error:', event.error);
    addLog('❌ 오류 발생: ' + event.error.message, 'error');
});

// Unhandled promise rejection handler
window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason);
    addLog('❌ 비동기 오류: ' + event.reason, 'error');
});

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('Lee May Trading System - JavaScript Loaded');
    addLog('✅ 시스템 JavaScript 로드 완료', 'success');
});

// Export functions for global use
window.LeeMaxTrading = {
    addLog,
    refreshStatus,
    formatCurrency,
    formatNumber,
    formatPercent,
    formatDateTime,
    formatTime,
    apiRequest,
    showNotification
};

// Auto-start status check
setTimeout(() => {
    if (typeof refreshStatus === 'function') {
        refreshStatus();
    }
}, 1000);

console.log('Lee May Trading System - app.js loaded successfully');
