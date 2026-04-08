document.addEventListener('DOMContentLoaded', () => {
    const nameInput = document.getElementById('userName');
    const keywordsInput = document.getElementById('triggerKeywords');
    const toggleBtn = document.getElementById('toggleGhosting');
    const statusIndicator = document.getElementById('statusIndicator');
    const statusText = document.getElementById('statusText');

    // Load saved settings
    chrome.storage.local.get(['userName', 'triggerKeywords', 'isGhosting'], (result) => {
        if (result.userName) nameInput.value = result.userName;
        if (result.triggerKeywords) keywordsInput.value = result.triggerKeywords;
        
        if (result.isGhosting) {
            setGhostingState(true);
        }
    });

    // Save settings on input change
    const saveSettings = () => {
        chrome.storage.local.set({
            userName: nameInput.value,
            triggerKeywords: keywordsInput.value
        });
    };

    nameInput.addEventListener('input', saveSettings);
    keywordsInput.addEventListener('input', saveSettings);

    // Toggle ghosting
    toggleBtn.addEventListener('click', () => {
        chrome.storage.local.get(['isGhosting'], (result) => {
            const newState = !result.isGhosting;
            setGhostingState(newState);
            chrome.storage.local.set({ isGhosting: newState });
            
            // Send message to content script or background
            chrome.tabs.query({active: true, currentWindow: true}, (tabs) => {
                if (tabs[0]) {
                    chrome.tabs.sendMessage(tabs[0].id, {
                        type: 'TOGGLE_GHOSTING',
                        payload: { isGhosting: newState }
                    });
                }
            });
        });
    });

    function setGhostingState(isActive) {
        if (isActive) {
            toggleBtn.textContent = 'Stop Ghosting';
            toggleBtn.classList.add('active');
            statusIndicator.classList.remove('offline');
            statusIndicator.classList.add('online');
            statusText.textContent = 'Ghosting active';
        } else {
            toggleBtn.textContent = 'Start Ghosting';
            toggleBtn.classList.remove('active');
            statusIndicator.classList.remove('online');
            statusIndicator.classList.add('offline');
            statusText.textContent = 'Ready to start';
        }
    }
});
