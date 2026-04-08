let isGhosting = false;
let widget = null;
let ws = null;

// Listen for messages from popup
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.type === 'TOGGLE_GHOSTING') {
        isGhosting = request.payload.isGhosting;
        if (isGhosting) {
            injectWidget();
            connectWebSocket();
        } else {
            removeWidget();
            disconnectWebSocket();
        }
    }
});

// Check initial state
chrome.storage.local.get(['isGhosting'], (result) => {
    if (result.isGhosting) {
        isGhosting = true;
        injectWidget();
        connectWebSocket();
    }
});

function injectWidget() {
    if (document.getElementById('ghost-meeting-widget')) return;

    widget = document.createElement('div');
    widget.id = 'ghost-meeting-widget';
    
    // Create widget HTML structure
    widget.innerHTML = `
        <div class="gm-header">
            <span class="gm-logo">👻 Ghost Meeting</span>
            <div class="gm-drag-handle">≡</div>
        </div>
        <div class="gm-content">
            <div class="gm-section gm-transcript" id="gm-transcript">
                <div class="gm-placeholder">Waiting for transcript...</div>
            </div>
            <div class="gm-divider"></div>
            <div class="gm-section gm-actions" id="gm-actions">
                <div class="gm-section-title">Action Items</div>
                <ul class="gm-actions-list" id="gm-actions-list">
                    <li class="gm-placeholder">No action items yet.</li>
                </ul>
            </div>
        </div>
    `;

    document.body.appendChild(widget);
    makeDraggable(widget);
}

function removeWidget() {
    if (widget) {
        widget.remove();
        widget = null;
    }
}

function connectWebSocket() {
    if (ws && ws.readyState === WebSocket.OPEN) return;

    ws = new WebSocket('ws://localhost:8000/ws/audio');

    ws.onopen = () => {
        console.log('Ghost Meeting: WebSocket connected');
    };

    ws.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            if (data.type === 'transcript') {
                updateTranscript(data.text);
            } else if (data.type === 'summary') {
                updateActionItems(data.items);
            }
        } catch (e) {
            console.error('Ghost Meeting error parsing WS message:', e);
        }
    };

    ws.onerror = (error) => {
        console.error('Ghost Meeting: WebSocket error', error);
    };

    ws.onclose = () => {
        console.log('Ghost Meeting: WebSocket disconnected');
        // Attempt reconnect if still ghosting
        if (isGhosting) {
            setTimeout(connectWebSocket, 5000);
        }
    };
}

function disconnectWebSocket() {
    if (ws) {
        ws.close();
        ws = null;
    }
}

function updateTranscript(text) {
    const container = document.getElementById('gm-transcript');
    if (!container) return;

    // Remove placeholder if present
    const placeholder = container.querySelector('.gm-placeholder');
    if (placeholder) placeholder.remove();

    const tElement = document.createElement('div');
    tElement.className = 'gm-transcript-line';
    tElement.textContent = text;
    
    container.appendChild(tElement);
    
    // Auto-scroll to bottom
    container.scrollTop = container.scrollHeight;
}

function updateActionItems(items) {
    const list = document.getElementById('gm-actions-list');
    if (!list) return;
    
    // Handle case where items is single string or array
    const itemsArray = Array.isArray(items) ? items : [items];
    
    if (itemsArray.length > 0) {
        // Remove placeholder
        const placeholder = list.querySelector('.gm-placeholder');
        if (placeholder) placeholder.remove();
        
        itemsArray.forEach(item => {
            const li = document.createElement('li');
            li.className = 'gm-action-item';
            li.textContent = item;
            list.appendChild(li);
        });
    }
}

function makeDraggable(element) {
    const header = element.querySelector('.gm-header');
    let isDragging = false;
    let currentX;
    let currentY;
    let initialX;
    let initialY;
    let xOffset = 0;
    let yOffset = 0;

    header.addEventListener('mousedown', dragStart);
    document.addEventListener('mousemove', drag);
    document.addEventListener('mouseup', dragEnd);

    function dragStart(e) {
        initialX = e.clientX - xOffset;
        initialY = e.clientY - yOffset;
        if (e.target.closest('.gm-header')) {
            isDragging = true;
        }
    }

    function drag(e) {
        if (isDragging) {
            e.preventDefault();
            currentX = e.clientX - initialX;
            currentY = e.clientY - initialY;
            xOffset = currentX;
            yOffset = currentY;
            
            setTranslate(currentX, currentY, element);
        }
    }

    function setTranslate(xPos, yPos, el) {
        el.style.transform = `translate3d(${xPos}px, ${yPos}px, 0)`;
    }

    function dragEnd() {
        initialX = currentX;
        initialY = currentY;
        isDragging = false;
    }
}
