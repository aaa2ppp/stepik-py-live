'use strict';

(function() {
    const UPDATE_TIMEOUT = 1000;
    const WORLD_URL = '/live?worldOnly=1';
    const WORLD_CONTAINER_ID = 'worldContainer';
    const HIDDEN_COUNTER_ID = 'hiddenCounter';
    const COUNTER_ID = 'counter';
    const REFRESH_BUTTON_ID = 'refreshButton';
    const STOP_LABEL = 'Остановить';
    const CONTINUE_LABEL = 'Продолжить';

    let worldContainer;
    let counter;
    let refreshButton;

    function init() {
        if (document.readyState == 'loading') {
            document.addEventListener('DOMContentLoaded', init);
            return;
        }

        worldContainer = document.getElementById(WORLD_CONTAINER_ID);
        if (!worldContainer) {
            console.error(`Element with id='${WORLD_CONTAINER_ID}' was not found on the page`);
            return;
        }
        counter = document.getElementById(COUNTER_ID) ||
            console.warn(`Element with id='${COUNTER_ID}' was not found on the page`);

        refreshButton = document.getElementById(REFRESH_BUTTON_ID) ||
            console.warn(`Element with id='${REFRESH_BUTTON_ID}' was not found on the page`);

        if (autoUpdate()) {
            setTimeout(startUpdateWorldLoop, UPDATE_TIMEOUT);
        }

        refreshButton?.addEventListener('click', (event) => {
            autoUpdate(!autoUpdate());
            event.preventDefault();
        });
        updateRefreshButtonLabel();
    }

    // usage: [oldValue =] autoUpdate([newValue]); 
    function autoUpdate(value) {
        const url = new URL(document.location);
        const params = url.searchParams;
        const oldValue = params.has('autoUpdate');

        if (value !== undefined && value != oldValue) {
            if (value) {
                startUpdateWorldLoop();
                params.set('autoUpdate', 1);
            } else {
                stopUpdateWorldLoop();
                if (params.has('autoUpdate')) {
                    params.delete('autoUpdate');
                }
            }
            history.pushState(null, null, url);
            updateRefreshButtonLabel();
        }

        return oldValue;
    };

    let _autoUpdate = false;
    let timerId = null;
    
    function startUpdateWorldLoop() {
        if (!_autoUpdate) {
            _autoUpdate = true;
            const _loop = () => {
                timerId = setTimeout(() => {
                    timerId = null;
                    if (_autoUpdate) {
                        updateWorld(_loop);
                    }
                }, UPDATE_TIMEOUT);
            };
            updateWorld(_loop);
        }
    }

    function stopUpdateWorldLoop() {
        if (timerId) {
            setTimeout(timerId);
            timerId = null;
        }
        _autoUpdate = false;
    }

    function updateWorld(callback) {
        fetch(WORLD_URL)
        .then(response => {
            if (!response.ok) {
                autoUpdate(false);
            }
            return response.text();
        })
        .then(html => {
            worldContainer.innerHTML = html;
            if (counter) {
                const hiddenCounter = document.getElementById(HIDDEN_COUNTER_ID) ||
                    console.warn(`Element with id='${HIDDEN_COUNTER_ID}' was not found in the loaded HTML of the world`);
                counter.textContent = hiddenCounter?.textContent || '??';
            }
            if (callback) {
                callback();
            }
        });        
    }

    function updateRefreshButtonLabel() {
        if (refreshButton) {
            refreshButton.textContent = autoUpdate() ? STOP_LABEL : CONTINUE_LABEL;
        }
    }

    init();
})();
