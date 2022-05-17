'use strict';

(function () {
    const UPDATE_TIMEOUT = 1000;
    const PARAM_NAME = "autoUpdate"
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
        const queue = new Queue(QUEUE_SIZE);
        let _autoUpdate = undefined;
        init();

        function init() {
            if (!worldContainer) {
                console.error(`${WORLD_CONTAINER_ID}' is required`);
                return;
            }

            const url = new URL(location);
            autoUpdate(url.searchParams.has(PARAM_NAME) && !document.getElementById(GAME_OVER_ID))
            refreshButton?.addEventListener('click', refreshButtonClick);
            exitButton?.addEventListener('clist', () => autoUpdate(false));
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
                if (queue.isFull()) {
                    await sleep(QUEUE_TIMEOUT);
                } else {
                    try {
                        const response = await fetch(WORLD_URL);

                        if (response.ok) {
                            queue.push({html_text: await response.text(), susses: true});
                        } else {
                            queue.push({html_text: await response.text(), susses: false});
                            break;
                        }
                    } catch (e) {
                        queue.push({html_text: `<h1>Error</h1><p>Can't load world: ${e.message}</p>`, susses: false});
                        break;
                    }
                }
            }
        }

        async function showWorldLoop(loopId) {
            let startTime = Date.now();

            while (loopId === currentUpdateLoopId) {

                if (queue.isEmpty()) {
                    await sleep(QUEUE_TIMEOUT);
                    startTime = Date.now();
                    continue;
                }

                const response = queue.shift();
                showWorld(response.html_text);

                if (!response.susses || document.getElementById(GAME_OVER_ID)) {
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

        async function sleep(timeout) {
            await new Promise(f => setTimeout(f, timeout));
        }

        class Queue {
            constructor(capacity) {
                this._array = new Array(capacity);
                this._size = 0;
                this._first = 0;
                this._last = 0;
            }

            get capacity() {
                return this._array.length;
            }

            isEmpty() {
                return this._size === 0;
            }

            isFull() {
                return this._size === this._array.length;
            }

            push(value) {
                if (this.isFull()) {
                    return false;
                } else {
                    this._array[this._last] = value;
                    this._last = (this._last + 1) % this.capacity;
                    this._size++;
                    return true;
                }
            }

            shift() {
                if (this.isEmpty()) {
                    return null;
                } else {
                    const result = this._array[this._first];
                    this._first = (this._first + 1) % this.capacity;
                    this._size--;
                    return result;
                }
            }
        }

        // ------------------------------------------------------------------------

        function refreshButtonClick(event) {
            autoUpdate(!autoUpdate());
            event.preventDefault();
            event.currentTarget.blur();
        }

        function updateRefreshButtonLabel() {
            if (refreshButton) {
                refreshButton.textContent = autoUpdate() ? STOP_LABEL : CONTINUE_LABEL;
            }
        }

        // ------------------------------------------------------------------------

        function updateUrl() {
            const url = new URL(location);

            if (autoUpdate()) {
                url.searchParams.set(PARAM_NAME, 'on');
            } else {
                url.searchParams.delete(PARAM_NAME);
            }

            history.replaceState(null, null, url);
        }
    }

})();
