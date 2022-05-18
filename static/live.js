'use strict';

(function () {
    const UPDATE_TIMEOUT = 1000;
    const URL_PARAM = "autoUpdate"
    const WORLD_URL = '/world';
    const WORLD_CONTAINER_ID = 'worldContainer';
    const COUNTER_ID = 'counter';
    const HIDDEN_COUNTER_ID = 'hiddenCounter';
    const EXIT_BUTTON_ID = 'exitButton';
    const REFRESH_BUTTON_ID = 'refreshButton';
    const GAME_OVER_ID = 'gameOver';
    const STOP_LABEL = 'Остановить';
    const CONTINUE_LABEL = 'Продолжить';
    const QUEUE_SIZE = 5;
    const QUEUE_TIMEOUT = 10;

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
    } else {
        run();
    }

    function run() {
        const worldContainer = getElementById(WORLD_CONTAINER_ID);
        const counter = getElementById(COUNTER_ID);
        const refreshButton = getElementById(REFRESH_BUTTON_ID);
        const exitButton = getElementById(EXIT_BUTTON_ID);
        const queue = [];

        let currentUpdateLoopId = 0;
        let _autoUpdate = undefined;
        init();

        function init() {
            if (!worldContainer) {
                console.error(`${WORLD_CONTAINER_ID}' is required`);
                return;
            }

            const url = new URL(location);
            autoUpdate(url.searchParams.has(URL_PARAM) && !document.getElementById(GAME_OVER_ID))
            exitButton?.addEventListener('clist', () => autoUpdate(false));
            refreshButton?.addEventListener('click', (event) => {
                autoUpdate(!autoUpdate());
                event.preventDefault();
                event.currentTarget.blur();
            });
        }

        function getElementById(id) {
            const el = document.getElementById(id);
            if (!el) {
                console.warn(`Element with id='${id}' was not found on the page`);
            }
            return el;
        }

        // ------------------------------------------------------------------------

        // Usage: [oldValue =] autoUpdate([newValue]);
        function autoUpdate(value) {
            const oldValue = _autoUpdate;

            if (value !== undefined && value !== oldValue) {
                _autoUpdate = value;

                if (value) {
                    if (oldValue === undefined) {
                        startAutoUpdateWithTimeout();
                    } else {
                        startAutoUpdateNow();
                    }
                } else {
                    stopAutoUpdate();
                }

                updateRefreshButtonLabel();
                updateUrl();
            }

            return oldValue;
        }

        // ------------------------------------------------------------------------

        function startAutoUpdateNow() {
            stopAutoUpdate();
            loadWorldLoop(currentUpdateLoopId).then();
            showWorldLoop(currentUpdateLoopId).then();
        }

        function startAutoUpdateWithTimeout() {
            stopAutoUpdate();
            loadWorldLoop(currentUpdateLoopId).then();
            const loopId = currentUpdateLoopId;
            setTimeout(() => showWorldLoop(loopId).then(), UPDATE_TIMEOUT);
        }

        function stopAutoUpdate() {
            currentUpdateLoopId++;
        }

        // ------------------------------------------------------------------------

        async function loadWorldLoop(loopId) {

            while (loopId === currentUpdateLoopId) {
                if (queue.length === QUEUE_SIZE) {
                    await sleep(UPDATE_TIMEOUT);
                    continue;
                }

                try {
                    const response = await fetch(WORLD_URL);
                    const html_text = await response.text();

                    // const template = document.createElement('template');
                    // template.innerHTML = html_text;
                    // const content = template.content;
                    // const isGameOver = !!content.getElementById(GAME_OVER_ID);

                    // queue.push({content: template.content, end: !response. ok || isGameOver});

                    // if (isGameOver) {
                    //     break;
                    // }
                    queue.push({content: html_text, end: !response.ok});
                } catch (e) {
                    queue.push({html_text: `<h1>Error</h1><p>Can't load world: ${e.message}</p>`, end: true});
                    break;
                }
            }
        }

        async function showWorldLoop(loopId) {
            let startTime = Date.now();

            while (loopId === currentUpdateLoopId) {

                if (queue.length === 0) {
                    await sleep(UPDATE_TIMEOUT / 2);
                    startTime = Date.now();
                    continue;
                }

                const response = queue.shift();
                showWorld(response.content);

                if (response.end || document.getElementById(GAME_OVER_ID)) {
                    autoUpdate(false);
                    break;
                }

                const endTime = Date.now();
                const timeout = UPDATE_TIMEOUT - (endTime - startTime);

                if (timeout > 0) {
                    startTime = endTime + timeout;
                    await sleep(timeout);
                } else {
                    startTime = endTime;
                    await sleep(0);
                }
            }
        }

        function showWorld(content) {
            // if (content) {
            //     counter.textContent = parseInt(content.getElementById(HIDDEN_COUNTER_ID)?.textContent).toString();
            // }
            // worldContainer.replaceChildren(content);
            worldContainer.innerHTML = content;
            if (content) {
                const hiddenCounter = document.getElementById(HIDDEN_COUNTER_ID);
                counter.textContent = hiddenCounter?.textContent || 'NaN';
            }
        }


        async function sleep(timeout) {
            await new Promise(f => setTimeout(f, timeout));
        }

        // ------------------------------------------------------------------------

        function updateRefreshButtonLabel() {
            if (refreshButton) {
                refreshButton.textContent = autoUpdate() ? STOP_LABEL : CONTINUE_LABEL;
            }
        }

        // ------------------------------------------------------------------------

        function updateUrl() {
            const url = new URL(location);

            if (autoUpdate()) {
                url.searchParams.set(URL_PARAM, 'on');
            } else {
                url.searchParams.delete(URL_PARAM);
            }

            history.replaceState(null, null, url);
        }
    }

})();
