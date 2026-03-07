// nova26 Dashboard Logic
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const chatMessages = document.getElementById('chat-messages');

const agentsGrid = document.getElementById('agents-grid');
const dbSizeEl = document.getElementById('db-size');
const activeSessionsEl = document.getElementById('active-sessions');

// Modal Elements
const agentModal = document.getElementById('agent-chat-modal');
const closeModalBtn = document.getElementById('close-modal-btn');
const modalAgentName = document.getElementById('modal-agent-name');
const modalChatMessages = document.getElementById('modal-chat-messages');
const modalChatInput = document.getElementById('modal-chat-input');
const modalSendBtn = document.getElementById('modal-send-btn');

let currentModalAgent = null;
let availableModels = [];

// Fetch Available Models
async function fetchModels() {
    try {
        const res = await fetch('/api/v1/models');
        const data = await res.json();
        availableModels = data.models || [];
    } catch(e) {
        console.error("Error fetching models:", e);
    }
}

// Change Agent Model
async function changeAgentModel(agentId, newModel) {
    try {
        await fetch(`/api/v1/agents/${agentId}/model`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ model: newModel })
        });
        updateStatus(); // fast refresh
    } catch(e) {
        console.error("Error changing model:", e);
    }
}

const sysCpuEl = document.getElementById('sys-cpu');
const sysRamEl = document.getElementById('sys-ram');
const sysVramEl = document.getElementById('sys-vram');
const stitchUsageEl = document.getElementById('stitch-usage');
const securityStatusEl = document.getElementById('security-status');

// Poll System Status
async function updateStatus() {
    try {
        const response = await fetch('/api/v1/status');
        const data = await response.json();
        
        if (data.agents) {
            renderAgents(data.agents);
        }
        
        if (dbSizeEl) dbSizeEl.innerText = data.db_size || '0 KB';
        if (activeSessionsEl) activeSessionsEl.innerText = data.sessions_count || '0';
        if (stitchUsageEl) stitchUsageEl.innerText = data.stitch_usage_monthly || '0';
        
        // Security Status Logic
        if (securityStatusEl) {
            if (data.security_events && data.security_events.length > 0) {
                const latest = data.security_events[0];
                securityStatusEl.innerText = latest.severity === 'CRITICAL' ? 'ALERTA' : 'AVISO';
                securityStatusEl.style.color = latest.severity === 'CRITICAL' ? '#ff4d4d' : '#ffa500';
                securityStatusEl.title = `${latest.type}: ${latest.details}`;
            } else {
                securityStatusEl.innerText = 'OK';
                securityStatusEl.style.color = '#00ff88';
                securityStatusEl.title = 'Sistemas protegidos por Nova Sentry';
            }
        }
        
        if (data.system_metrics) {
            if (sysCpuEl) sysCpuEl.innerText = data.system_metrics.cpu_usage || '0%';
            if (sysRamEl) sysRamEl.innerText = data.system_metrics.ram_usage || '0 MB';
            if (sysVramEl) sysVramEl.innerText = data.system_metrics.vram_usage || '0 GB';
        }

        // Update notification
        const updateBadge = document.getElementById('update-badge');
        if (updateBadge) {
            if (data.update_available) {
                updateBadge.classList.remove('hidden');
            } else {
                updateBadge.classList.add('hidden');
            }
        }
    } catch (err) {
        console.error("Error polling status:", err);
    }
}

function openAgentModal(agent) {
    currentModalAgent = agent;
    modalAgentName.innerText = `Chat Directo - ${agent.name}`;
    modalChatMessages.innerHTML = `<div class="msg bot">Conexión directa establecida con ${agent.name} (${agent.id}). ¿Qué necesitas?</div>`;
    agentModal.classList.remove('hidden');
}

closeModalBtn.addEventListener('click', () => {
    agentModal.classList.add('hidden');
    currentModalAgent = null;
});

function renderAgents(agents) {
    agentsGrid.innerHTML = '';
    
    agents.forEach(agent => {
        const card = document.createElement('div');
        card.className = 'glass-card agent-card';
        card.style.cursor = 'pointer';
        
        card.addEventListener('click', (e) => {
            // No abrir modal si hicieron click en el selector de modelo
            if(e.target.tagName.toLowerCase() === 'select' || e.target.tagName.toLowerCase() === 'option') return;
            openAgentModal(agent);
        });
        
        const statusClass = `status-${agent.status}`;
        
        let dynamicSelect = `<select class="model-select glass-select" data-agent-id="${agent.id}">`;
        if(!availableModels.includes(agent.model)) {
            dynamicSelect += `<option value="${agent.model}" selected>${agent.model}</option>`;
        }
        availableModels.forEach(m => {
            dynamicSelect += `<option value="${m}" ${m === agent.model ? 'selected' : ''}>${m}</option>`;
        });
        dynamicSelect += `</select>`;

        card.innerHTML = `
            <div class="card-header">
                <span class="agent-name">${agent.name}</span>
                <span class="status-badge ${statusClass}">${agent.status}</span>
            </div>
            
            <div class="agent-metrics">
                <div class="metric-item">
                    <span class="metric-label">RAM / VRAM</span>
                    <span class="metric-value">${agent.ram} / ${agent.vram}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Temp CPU/GPU</span>
                    <span class="metric-value">${agent.cpu_temp} / ${agent.gpu_temp}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Tokens Mensuales</span>
                    <span class="metric-value">${agent.tokens || 0}</span>
                </div>
                <div class="metric-item">
                    <span class="metric-label">Modelo Activo</span>
                    ${dynamicSelect}
                </div>
            </div>
            
            <div class="agent-task-area" style="margin-top: 5px;">
                <span class="task-label">${agent.task}</span>
                <div class="task-content">CPU: ${agent.cpu} | ${agent.detail}</div>
                <div class="cpu-bar"><div class="cpu-fill" style="width: ${agent.cpu}"></div></div>
            </div>
        `;
        agentsGrid.appendChild(card);
    });

    document.querySelectorAll('.model-select').forEach(select => {
        select.addEventListener('change', (e) => {
            const agentId = e.target.getAttribute('data-agent-id');
            const newModel = e.target.value;
            changeAgentModel(agentId, newModel);
        });
    });
}

// Send Main Chat Message
async function sendMessage() {
    const text = chatInput.value.trim();
    if (!text) return;
    appendMessage(text, 'user', chatMessages);
    chatInput.value = '';
    try {
        const response = await fetch('/api/v1/interact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text })
        });
        const data = await response.json();
        appendMessage(data.response, 'bot', chatMessages);
    } catch (err) {
        appendMessage("Error conectando con el cerebro.", 'bot', chatMessages);
    }
}

// Send Modal Agent Message
async function sendModalMessage() {
    if(!currentModalAgent) return;
    const text = modalChatInput.value.trim();
    if (!text) return;
    appendMessage(text, 'user', modalChatMessages);
    modalChatInput.value = '';
    try {
        const response = await fetch('/api/v1/interact', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ text: `[Para ${currentModalAgent.id}]: ${text}` })
        });
        const data = await response.json();
        appendMessage(data.response, 'bot', modalChatMessages);
    } catch (err) {
        appendMessage("Error conectando con el agente.", 'bot', modalChatMessages);
    }
}

function appendMessage(text, type, container) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `msg ${type}`;
    msgDiv.innerText = text;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

sendBtn.addEventListener('click', sendMessage);
chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendMessage();
});

modalSendBtn.addEventListener('click', sendModalMessage);
modalChatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendModalMessage();
});

// Init
fetchModels().then(() => {
    updateStatus();
    setInterval(updateStatus, 3000);
});
console.log("nova26 Dashboard Active");
