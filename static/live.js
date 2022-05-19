'use strict';

(function run() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
        return;
    }

    const AUTO_UPDATE_PARAM = "autoupdate"
    const UPDATE_PERIOD_PARAM = "update_period";

    const WORLD_URL = '/world';

    const WORLD_CONTAINER_ID = 'worldContainer';
    const COUNTER_ID = 'counter';
    const HIDDEN_COUNTER_ID = 'hiddenCounter';
    const EXIT_BUTTON_ID = 'exitButton';
    const REFRESH_BUTTON_ID = 'refreshButton';
    const GAME_OVER_ID = 'gameOver';

    const STOP_LABEL = 'Остановить';
    const CONTINUE_LABEL = 'Продолжить';

    const FRAME_QUEUE_SIZE = 5;
    const FRAME_QUEUE_TIMEOUT = 10;

    const worldContainer = getElementById(WORLD_CONTAINER_ID);
    if (!worldContainer) {
        console.error(`${WORLD_CONTAINER_ID}' is required`);
        return;
    }

    const counter = getElementById(COUNTER_ID);
    const refreshButton = getElementById(REFRESH_BUTTON_ID);
    const exitButton = getElementById(EXIT_BUTTON_ID);

    const frameQueue = [];
    let autoUpdateEnabled = undefined;
    let currentUpdateLoopId = 0;

    let _url = new URL(location);

    let updatePeriod = parseInt(_url.searchParams.get(UPDATE_PERIOD_PARAM)) || 1000;
    if (updatePeriod < 100) {
        console.warn(`Too small value of ${UPDATE_PERIOD_PARAM}=${updatePeriod}. Set it to 100`);
        updatePeriod = 100;
    }

    let _autoupdate = _url.searchParams.has(AUTO_UPDATE_PARAM) &&
        ["no", "off", "false", "0"].indexOf(_url.searchParams.get(AUTO_UPDATE_PARAM)) === -1;

    _url = null;

    setAutoUpdate(_autoupdate && !document.getElementById(GAME_OVER_ID));

    exitButton?.addEventListener('clist', () => setAutoUpdate(false));

    refreshButton?.addEventListener('click', (event) => {
        setAutoUpdate(!autoUpdateEnabled);
        event.preventDefault();
        event.currentTarget.blur();
    });

    // ------------------------------------------------------------------------

    function getElementById(id) {
        const el = document.getElementById(id);
        if (!el) {
            console.warn(`Element with id='${id}' was not found on this page`);
        }
        return el;
    }

    // ------------------------------------------------------------------------

    function setAutoUpdate(value) {
        const oldValue = autoUpdateEnabled;

        if (value !== undefined && value !== oldValue) {
            autoUpdateEnabled = value;

            updateRefreshButtonLabel();
            updateUrl();

            if (value) {
                if (oldValue === undefined) {
                    // at first time
                    startUpdateLoopsWithTimeout();
                } else {
                    startUpdateLoopsNow();
                }
            } else {
                stopUpdateLoops();
            }
        }
    }

    // ------------------------------------------------------------------------

    function startUpdateLoopsNow() {
        stopUpdateLoops();
        loadWorldLoop(currentUpdateLoopId).then();
        showWorldLoop(currentUpdateLoopId).then();
    }

    function startUpdateLoopsWithTimeout() {
        stopUpdateLoops();
        loadWorldLoop(currentUpdateLoopId).then();
        const loopId = currentUpdateLoopId;
        setTimeout(() => showWorldLoop(loopId).then(), updatePeriod);
    }

    function stopUpdateLoops() {
        currentUpdateLoopId++;
    }

    // ------------------------------------------------------------------------

    function updateRefreshButtonLabel() {
        if (refreshButton) {
            refreshButton.textContent = autoUpdateEnabled ? STOP_LABEL : CONTINUE_LABEL;
        }
    }

    function updateUrl() {
        const url = new URL(location);

        if (autoUpdateEnabled) {
            url.searchParams.set(AUTO_UPDATE_PARAM, 'on');
        } else {
            url.searchParams.delete(AUTO_UPDATE_PARAM);
        }

        url.searchParams.set(UPDATE_PERIOD_PARAM, updatePeriod.toString());

        history.replaceState(null, null, url);
    }

    // ------------------------------------------------------------------------

    async function sleep(timeout) {
        await new Promise(f => setTimeout(f, timeout));
    }

    async function loadWorldLoop(loopId) {

        while (loopId === currentUpdateLoopId) {
            if (frameQueue.length === FRAME_QUEUE_SIZE) {
                await sleep(Math.floor(updatePeriod / 2));
                continue;
            }

            try {
                const response = await fetch(WORLD_URL);
                const html_text = await response.text();

                const template = document.createElement('template');
                template.innerHTML = html_text;
                const content = template.content;
                const isGameOver = !!content.getElementById(GAME_OVER_ID);

                frameQueue.push({content, end: !response.ok || isGameOver});

                if (isGameOver) {
                    break;
                }
            } catch (e) {
                frameQueue.push({html_text: `<h1>Error</h1><p>Can't load world: ${e.message}</p>`, end: true});
                break;
            }
        }
    }

    async function showWorldLoop(loopId) {
        let startTime = Date.now();

        while (loopId === currentUpdateLoopId) {

            if (frameQueue.length === 0) {
                await sleep(FRAME_QUEUE_TIMEOUT);
                continue;
            }

            const {content, end} = frameQueue.shift();
            showWorld(content);

            if (end) {
                setAutoUpdate(false);
                break;
            }

            const endTime = Date.now();
            const timeout = updatePeriod - (endTime - startTime);

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
        if (counter) {
            counter.textContent = parseInt(content.getElementById(HIDDEN_COUNTER_ID)?.textContent).toString();
        }
        worldContainer.replaceChild(content, worldContainer.firstElementChild)
    }

})();
