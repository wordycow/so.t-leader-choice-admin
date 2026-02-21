// Global state and utility functions
const logOutput = () => document.getElementById('log-output');

function addLog(message) {
    const output = logOutput();
    if (!output) return;
    
    const timestamp = new Date().toLocaleTimeString('ko-KR');
    const logEntry = document.createElement('div');
    logEntry.textContent = `[${timestamp}] ${message}`;
    output.appendChild(logEntry);
    output.scrollTop = output.scrollHeight;
    
    // Keep only last 100 logs
    while (output.children.length > 100) {
        output.removeChild(output.firstChild);
    }
}

async function refreshStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        if (data.success) {
            updateStatusIndicators(data.services);
            addLog(`✅ 상태 업데이트: ${data.services.filter(s => s.status === 'running').length}/${data.services.length} 서비스 실행 중`);
        }
    } catch (error) {
        addLog(`❌ 상태 확인 실패: ${error.message}`);
    }
}

function updateStatusIndicators(services) {
    services.forEach(service => {
        const indicator = document.querySelector(`[data-service="${service.name}"]`);
        if (indicator) {
            const card = indicator.closest('.status-card');
            const statusText = card.querySelector('.status-text');
            
            if (service.status === 'running') {
                indicator.textContent = '🟢';
                statusText.textContent = '실행 중';
                statusText.style.color = '#10b981';
            } else if (service.status === 'stopped') {
                indicator.textContent = '🔴';
                statusText.textContent = '정지됨';
                statusText.style.color = '#ef4444';
            } else {
                indicator.textContent = '🟡';
                statusText.textContent = '확인 중...';
                statusText.style.color = '#f59e0b';
            }
        }
    });
}

// API helper functions
async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
            }
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(endpoint, options);
        return await response.json();
    } catch (error) {
        addLog(`❌ API 호출 실패 (${endpoint}): ${error.message}`);
        return { success: false, error: error.message };
    }
}

// Export functions for use in HTML
window.addLog = addLog;
window.refreshStatus = refreshStatus;
window.apiCall = apiCall;
