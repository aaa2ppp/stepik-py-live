'use strict';

(function () {
    const UPDATE_TIMEOUT = 1000;
    const WORLD_URL = '/live?worldOnly=on';
    const WORLD_CONTAINER_ID = 'worldContainer';
    const HIDDEN_COUNTER_ID = 'hiddenCounter';
    const COUNTER_ID = 'counter';
    const REFRESH_BUTTON_ID = 'refreshButton';
    const STOP_LABEL = 'Остановить';
    const CONTINUE_LABEL = 'Продолжить';

    let worldContainer;
    let counter;
    let refreshButton;

    // ------------------------------------------------------------------------

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

        counter = document.getElementById(COUNTER_ID);
        if (!counter) {
            console.warn(`Element with id='${COUNTER_ID}' was not found on the page`);
        }

        refreshButton = document.getElementById(REFRESH_BUTTON_ID);
        if (!refreshButton) {
            console.warn(`Element with id='${REFRESH_BUTTON_ID}' was not found on the page`);
        }

        if (autoUpdate()) {
            startAutoUpdateWithTimeout();
        }

        refreshButton?.addEventListener('click', refreshButtonClick);
        updateRefreshButtonLabel();
    }

    // ------------------------------------------------------------------------

    let updateId = 0;

    // usage: [oldValue =] autoUpdate([newValue]);
    function autoUpdate(value) {
        const url = new URL(location);
        const oldValue = url.searchParams.has('autoUpdate');

        if (value !== undefined && value != oldValue) {
            updateId++;
            if (value) {
                url.searchParams.set('autoUpdate', 'on');
                startAutoUpdateNow();
            } else {
                url.searchParams.delete('autoUpdate');
                stopAutoUpdate();
            }
            history.replaceState(null, null, url);
            updateRefreshButtonLabel();
        }

        return oldValue;
    }

    function startAutoUpdateNow() {
        const id = updateId;
        updateWorld((success) => {
            if (!success) {
                autoUpdate(false);
                return;
            }
            if (id === updateId) {
                startAutoUpdateWithTimeout();
            }
        });
    }

    let timerId = null;

    function startAutoUpdateWithTimeout() {
        if (timerId === null) {
            timerId = setTimeout(() => {
                timerId = null;
                startAutoUpdateNow();
            }, UPDATE_TIMEOUT);
        }
    }

    function stopAutoUpdate() {
        if (timerId !== null) {
            clearTimeout(timerId);
            timerId = null;
        }
    }

    // ------------------------------------------------------------------------

    function updateWorld(callback) {
        let success;
        fetch(WORLD_URL)
            .then((response) => ((success = response.ok), response.text()))
            .then((html) => (showWorld(html), callback && callback(success)));
    }

    function showWorld(html) {
        worldContainer.innerHTML = html;
        if (counter) {
            const hiddenCounter = document.getElementById(HIDDEN_COUNTER_ID);
            if (hiddenCounter) {
                counter.textContent = hiddenCounter.textContent;
            } else {
                console.warn(`Element with id='${HIDDEN_COUNTER_ID}' was not found in the loaded HTML of the world`);
                counter.textContent = '??';
            }
        }
    }

    // ------------------------------------------------------------------------

    function refreshButtonClick(event) {
        autoUpdate(!autoUpdate());
        event.preventDefault();
    }

    function updateRefreshButtonLabel() {
        if (refreshButton) {
            refreshButton.textContent = autoUpdate() ? STOP_LABEL : CONTINUE_LABEL;
        }
    }

    // ------------------------------------------------------------------------

    init();
})();
