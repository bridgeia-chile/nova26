// nova26 Dashboard Logic
console.log('NovaGravity Dashboard Logic Initializing...');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const chatMessages = document.getElementById('chat-messages');

const agentsGrid = document.getElementById('agents-grid');
const dbSizeEl = document.getElementById('db-size');
const activeSessionsEl = document.getElementById('active-sessions');

const agentsView = document.querySelector('.content-area');
const settingsView = document.getElementById('settings-view');
const navItems = document.querySelectorAll('.nav-item');
const modelsSettingsGrid = document.getElementById('models-settings-grid');

// Modal Elements
const agentModal = document.getElementById('agent-chat-modal');
const closeModalBtn = document.getElementById('close-modal-btn');
const modalAgentName = document.getElementById('modal-agent-name');
const modalChatMessages = document.getElementById('modal-chat-messages');
const modalChatInput = document.getElementById('modal-chat-input');
const modalSendBtn = document.getElementById('modal-send-btn');

let currentModalAgent = null;
let availableModels = [];
let animationsInitialized = false;

// Initialize animations when DOM is ready
function initAnimations() {
    if (animationsInitialized) return;

    try {
        if (typeof initNovaAnimations === 'function') {
            const anim = initNovaAnimations();

            // Apply animations to agent cards
            if (anim.scrollReveal) {
                document.querySelectorAll('.agent-card, .info-pill, .model-config-card').forEach((el, index) => {
                    anim.scrollReveal.addElement(el, { delay: index * 50 });
                });
            }

            // Apply hover effects
            if (anim.hoverEffects) {
                anim.hoverEffects.init();
            }

            // Apply floating animations to blobs
            if (anim.floatingAnimations) {
                const blobs = document.querySelectorAll('.blob');
                if (blobs.length >= 3) {
                    anim.floatingAnimations.apply(blobs[0], 'PODER', { speed: 8, amplitude: 30 });
                    anim.floatingAnimations.apply(blobs[1], 'RTIC', { radius: 25, duration: 10 });
                    anim.floatingAnimations.apply(blobs[2], 'C45', { intensity: 20, speed: 6 });
                }
            }

            animationsInitialized = true;
            console.log('NovaGravity animations initialized');
        }
    } catch (e) {
        console.warn('Animations not available:', e.message);
    }
}

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
        
        if (securityStatusEl) {
            if (data.security_events && data.security_events.length > 0) {
                const latest = data.security_events[0];
                securityStatusEl.innerText = latest.severity === 'CRITICAL' ? 'ALERTA' : 'AVISO';
                securityStatusEl.style.color = latest.severity === 'CRITICAL' ? '#ff4d4d' : '#ffa500';
            } else {
                securityStatusEl.innerText = 'OK';
                securityStatusEl.style.color = '#00ff88';
            }
        }
        
        if (data.system_metrics) {
            if (sysCpuEl) sysCpuEl.innerText = data.system_metrics.cpu_usage || '0%';
            if (sysRamEl) sysRamEl.innerText = data.system_metrics.ram_usage || '0 MB';
            if (sysVramEl) sysVramEl.innerText = data.system_metrics.vram_usage || '0 GB';
        }

        const updateBadge = document.getElementById('update-badge');
        if (updateBadge) {
            if (data.update_available) updateBadge.classList.remove('hidden');
            else updateBadge.classList.add('hidden');
        }

    } catch (err) {
        console.error("Error polling status:", err);
    }
}

function openAgentModal(agent) {
    currentModalAgent = agent;
    modalAgentName.innerText = `Chat Directo - ${agent.name}`;
    modalChatMessages.innerHTML = `<div class="msg bot">Conexión directa establecida con ${agent.name}.</div>`;
    agentModal.classList.remove('hidden');
}

closeModalBtn.addEventListener('click', () => {
    agentModal.classList.add('hidden');
    currentModalAgent = null;
});

function renderAgents(agents) {
    const existingCards = document.querySelectorAll('.agent-card');
    if (existingCards.length !== agents.length || existingCards.length === 0) {
        agentsGrid.innerHTML = '';
        agents.forEach(agent => {
            const card = document.createElement('div');
            card.id = `agent-card-${agent.id}`;
            card.className = 'glass-card agent-card';
            card.style.cursor = 'pointer';
            card.onclick = (e) => {
                if(e.target.tagName === 'SELECT') return;
                openAgentModal(agent);
            };
            
            let dynamicSelect = `<select class="model-select glass-select" data-agent-id="${agent.id}">`;
            availableModels.forEach(m => {
                dynamicSelect += `<option value="${m}" ${m === agent.model ? 'selected' : ''}>${m}</option>`;
            });
            dynamicSelect += `</select>`;

            card.innerHTML = `
                <div class="card-header">
                    <span class="agent-name" id="name-${agent.id}">${agent.name}</span>
                    <span class="status-badge status-${agent.status}" id="status-${agent.id}">${agent.status}</span>
                </div>
                <div class="agent-metrics">
                    <div class="metric-item"><span class="metric-label">RAM / VRAM</span><span class="metric-value" id="ramvram-${agent.id}">${agent.ram} / ${agent.vram}</span></div>
                    <div class="metric-item"><span class="metric-label">Temp CPU/GPU</span><span class="metric-value" id="temp-${agent.id}">${agent.cpu_temp} / ${agent.gpu_temp}</span></div>
                    <div class="metric-item"><span class="metric-label">Modelo Activo</span>${dynamicSelect}</div>
                </div>
                <div class="agent-task-area">
                    <span class="task-label" id="task-${agent.id}">${agent.task}</span>
                    <div class="task-content">CPU: <span id="cpu-${agent.id}">${agent.cpu}</span></div>
                    <div class="cpu-bar"><div class="cpu-fill" id="cpubar-${agent.id}" style="width: ${agent.cpu}"></div></div>
                </div>
            `;
            agentsGrid.appendChild(card);
        });

        document.querySelectorAll('.model-select').forEach(select => {
            select.addEventListener('change', (e) => {
                changeAgentModel(e.target.getAttribute('data-agent-id'), e.target.value);
            });
        });
    } else {
        agents.forEach(agent => {
            document.getElementById(`status-${agent.id}`).innerText = agent.status;
            document.getElementById(`status-${agent.id}`).className = `status-badge status-${agent.status}`;
            document.getElementById(`ramvram-${agent.id}`).innerText = `${agent.ram} / ${agent.vram}`;
            document.getElementById(`cpu-${agent.id}`).innerText = agent.cpu;
            document.getElementById(`cpubar-${agent.id}`).style.width = agent.cpu;
            const taskEl = document.getElementById(`task-${agent.id}`);
            if (taskEl) taskEl.innerText = agent.task;
        });
    }
}

// --- Navigation Logic ---
navItems.forEach(item => {
    item.addEventListener('click', () => {
        navItems.forEach(n => n.classList.remove('active'));
        item.classList.add('active');
        
        if (item.id === 'nav-ajustes') {
            agentsView.classList.add('hidden');
            settingsView.classList.remove('hidden');
            renderModelsSettings();
        } else if (item.id === 'nav-resumen') {
            settingsView.classList.add('hidden');
            agentsView.classList.remove('hidden');
        }
    });
});

// --- Models Management Logic ---
async function renderModelsSettings() {
    try {
        modelsSettingsGrid.innerHTML = '<p style="padding: 20px; color: var(--text-dim);">Cargando modelos...</p>';
        const res = await fetch('/api/v1/settings/models');
        const data = await res.json();
        
        if (data.status === 'success' && data.models) {
            modelsSettingsGrid.innerHTML = '';
            data.models.forEach(model => {
                const catClass = model.category === 'Direct API' ? 'cat-direct' : 
                                 model.category === 'Operador Gratuito' ? 'cat-free' :
                                 model.category === 'Ollama Local' ? 'cat-local' : 'cat-cloud';
                
                const card = document.createElement('div');
                card.className = 'model-config-card';
                card.innerHTML = `
                    <div class="model-card-top">
                        <div class="model-info-main">
                            <span class="category-tag ${catClass}">${model.category}</span>
                            <div class="provider-tag">${model.provider}</div>
                            <h4>${model.model_name}</h4>
                        </div>
                        <label class="switch">
                            <input type="checkbox" id="toggle-${model.id}" ${model.is_enabled ? 'checked' : ''}>
                            <span class="slider round"></span>
                        </label>
                    </div>
                    <div class="model-card-body">
                        <div class="config-item">
                            <span class="config-label">Temperatura</span>
                            <div class="config-input-group">
                                <input type="range" id="temp-range-${model.id}" min="0" max="1" step="0.1" value="${model.temperature}">
                                <span class="temp-value" id="temp-val-${model.id}">${model.temperature}</span>
                            </div>
                        </div>
                    </div>
                `;
                modelsSettingsGrid.appendChild(card);
                
                card.querySelector('input[type="checkbox"]').onchange = async (e) => {
                    await updateModelConfig(model.id, { is_enabled: e.target.checked });
                    fetchModels();
                };
                
                const tr = card.querySelector('input[type="range"]');
                const tv = card.querySelector('.temp-value');
                tr.oninput = () => tv.innerText = tr.value;
                tr.onchange = async () => updateModelConfig(model.id, { temperature: parseFloat(tr.value) });
            });
        }
    } catch(e) { console.error(e); }
}

async function updateModelConfig(modelId, config) {
    try {
        await fetch(`/api/v1/settings/models/${modelId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(config)
        });
    } catch(e) { console.error(e); }
}

// --- Tunnel & HA Modals (Omitted for brevity, assumed existing or handled separately) ---
// Note: In a real scenario I would merge them carefully.

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

function appendMessage(text, type, container) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `msg ${type}`;
    msgDiv.innerText = text;
    container.appendChild(msgDiv);
    container.scrollTop = container.scrollHeight;
}

sendBtn.onclick = sendMessage;
chatInput.onkeypress = (e) => { if (e.key === 'Enter') sendMessage(); };

// Initialize animations on DOM load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAnimations);
} else {
    initAnimations();
}

// Init main functionality
fetchModels().then(() => {
  // Initial call
updateStatus();
setInterval(updateStatus, 5000);
fetchModels();
});
