'use strict';

(function () {
    const UPDATE_TIMEOUT = 1000;
    const PARAM_NAME = "autoUpdate"
    const WORLD_URL = '/world';
    const WORLD_CONTAINER_ID = 'worldContainer';
    const HIDDEN_COUNTER_ID = 'hiddenCounter';
    const COUNTER_ID = 'counter';
    const REFRESH_BUTTON_ID = 'refreshButton';
    const STOP_LABEL = 'Остановить';
    const CONTINUE_LABEL = 'Продолжить';

    let worldContainer;
    let counter;
    let refreshButton;
    let updateLoopId = 0;
    let timerId = null;
    init();

    // ------------------------------------------------------------------------

    function init() {
        if (document.readyState === 'loading') {
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

    // usage: [oldValue =] autoUpdate([newValue]);
    function autoUpdate(value) {
        const url = new URL(location);
        const oldValue = url.searchParams.has(PARAM_NAME);

        if (value !== undefined && value !== oldValue) {
            updateLoopId++;
            if (value) {
                url.searchParams.set(PARAM_NAME, 'on');
                startAutoUpdateNow();
            } else {
                url.searchParams.delete(PARAM_NAME);
                stopAutoUpdate();
            }
            history.replaceState(null, null, url);
            updateRefreshButtonLabel();
        }

        return oldValue;
    }

    function startAutoUpdateNow() {
        if (timerId === null) {
            setTimeout(async () => await updateWorld(), 0);
            startAutoUpdateWithTimeout()
        }
    }

    function startAutoUpdateWithTimeout() {
        if (timerId === null) {
            timerId = setInterval(async () => {
                await updateWorld((susses) => susses || stopAutoUpdate())
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

    async function updateWorld(callback) {
        const response = await fetch(WORLD_URL);
        const html_text = await response.text();
        showWorld(html_text);
        callback && callback(response.ok);
    }

    function showWorld(html_text) {
        worldContainer.innerHTML = html_text;
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

})();
