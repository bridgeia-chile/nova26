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

        // Update Sync Toggle
        const syncToggle = document.getElementById('sync-toggle-checkbox');
        if (syncToggle && document.activeElement !== syncToggle) {
            syncToggle.checked = data.sync_enabled;
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
    const existingCards = document.querySelectorAll('.agent-card');
    
    // Si la cantidad de agentes cambió o es la primera carga, renderizamos todo
    if (existingCards.length !== agents.length || existingCards.length === 0) {
        agentsGrid.innerHTML = '';
        
        agents.forEach(agent => {
            const card = document.createElement('div');
            card.id = `agent-card-${agent.id}`;
            card.className = 'glass-card agent-card';
            card.style.cursor = 'pointer';
            
            card.addEventListener('click', (e) => {
                if(e.target.tagName.toLowerCase() === 'select' || e.target.tagName.toLowerCase() === 'option') return;
                openAgentModal(agent);
            });
            
            const statusClass = `status-${agent.status}`;
            
            let dynamicSelect = `<select class="model-select glass-select" id="model-${agent.id}" data-agent-id="${agent.id}">`;
            if(!availableModels.includes(agent.model)) {
                dynamicSelect += `<option value="${agent.model}" selected>${agent.model}</option>`;
            }
            availableModels.forEach(m => {
                dynamicSelect += `<option value="${m}" ${m === agent.model ? 'selected' : ''}>${m}</option>`;
            });
            dynamicSelect += `</select>`;

            card.innerHTML = `
                <div class="card-header">
                    <span class="agent-name" id="name-${agent.id}">${agent.name}</span>
                    <span class="status-badge ${statusClass}" id="status-${agent.id}">${agent.status}</span>
                </div>
                
                <div class="agent-metrics">
                    <div class="metric-item">
                        <span class="metric-label">RAM / VRAM</span>
                        <span class="metric-value" id="ramvram-${agent.id}">${agent.ram} / ${agent.vram}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Temp CPU/GPU</span>
                        <span class="metric-value" id="temp-${agent.id}">${agent.cpu_temp} / ${agent.gpu_temp}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Tokens Mensuales</span>
                        <span class="metric-value" id="tokens-${agent.id}">${agent.tokens || 0}</span>
                    </div>
                    <div class="metric-item">
                        <span class="metric-label">Modelo Activo</span>
                        ${dynamicSelect}
                    </div>
                </div>
                
                ${agent.id === 'agent-01' ? `
                <div class="sync-toggle-container glass-card" style="margin-bottom: 10px; padding: 8px; display: flex; justify-content: space-between; align-items: center;">
                    <span class="metric-label" style="font-size: 0.75rem;">Sincronización P2P</span>
                    <label class="switch">
                        <input type="checkbox" id="sync-toggle-checkbox">
                        <span class="slider round"></span>
                    </label>
                </div>
                ` : ''}
                
                <div class="agent-task-area" style="margin-top: 5px;">
                    <span class="task-label" id="task-${agent.id}">${agent.task}</span>
                    <div class="task-content">CPU: <span id="cpu-${agent.id}">${agent.cpu}</span> | <span id="detail-${agent.id}">${agent.detail}</span></div>
                    <div class="cpu-bar"><div class="cpu-fill" id="cpubar-${agent.id}" style="width: ${agent.cpu}"></div></div>
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
        
        const syncToggleCheckbox = document.getElementById('sync-toggle-checkbox');
        if (syncToggleCheckbox) {
            syncToggleCheckbox.addEventListener('change', (e) => {
                toggleSync(e.target.checked);
            });
        }
    } else {
        // En lugar de recrear, actualizamos los valores de las tarjetas existentes en tiempo real.
        agents.forEach(agent => {
            const nameEl = document.getElementById(`name-${agent.id}`);
            if (nameEl && nameEl.innerText !== agent.name) nameEl.innerText = agent.name;
            
            const statusEl = document.getElementById(`status-${agent.id}`);
            if (statusEl) {
                statusEl.innerText = agent.status;
                statusEl.className = `status-badge status-${agent.status}`;
            }
            
            const ramvramEl = document.getElementById(`ramvram-${agent.id}`);
            if (ramvramEl) ramvramEl.innerText = `${agent.ram} / ${agent.vram}`;
            
            const tempEl = document.getElementById(`temp-${agent.id}`);
            if (tempEl) tempEl.innerText = `${agent.cpu_temp} / ${agent.gpu_temp}`;
            
            const tokensEl = document.getElementById(`tokens-${agent.id}`);
            if (tokensEl) tokensEl.innerText = agent.tokens || 0;
            
            const taskEl = document.getElementById(`task-${agent.id}`);
            if (taskEl && taskEl.innerText !== agent.task) taskEl.innerText = agent.task;
            
            const cpuEl = document.getElementById(`cpu-${agent.id}`);
            if (cpuEl) cpuEl.innerText = agent.cpu;
            
            const detailEl = document.getElementById(`detail-${agent.id}`);
            if (detailEl && detailEl.innerText !== agent.detail) detailEl.innerText = agent.detail;
            
            const cpubarEl = document.getElementById(`cpubar-${agent.id}`);
            if (cpubarEl) cpubarEl.style.width = agent.cpu;
            
            const modelEl = document.getElementById(`model-${agent.id}`);
            if (modelEl && document.activeElement !== modelEl) {
                // Solo actualizar si el usuario no tiene abierto el seleccionador desplegable
                if (modelEl.value !== agent.model && availableModels.includes(agent.model)) {
                    modelEl.value = agent.model;
                }
            }
        });
    }
}

// Toggle Sync API Call
async function toggleSync(enabled) {
    try {
        await fetch('/api/v1/sync/toggle', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ enabled })
        });
        updateStatus(); // fast refresh
    } catch(e) {
        console.error("Error toggling sync:", e);
    }
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
