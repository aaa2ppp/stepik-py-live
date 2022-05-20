'use strict';

(function run() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
        return;
    }

    const AUTO_UPDATE_PARAM = "autoupdate"
    const UPDATE_PERIOD_PARAM = "update_period";
    const GENERATION_SERIAL_PARAM = "serial";

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
    let lastLoad = parseInt(counter?.textContent);
    let lastShow = lastLoad;

    let autoUpdateEnabled = undefined;
    let currentUpdateLoopId = 0;

    let _params = new URL(location).searchParams;

    let updatePeriod = parseInt(_params.get(UPDATE_PERIOD_PARAM)) || 1000;
    if (updatePeriod < 100) {
        console.warn(`Too small value of ${UPDATE_PERIOD_PARAM}=${updatePeriod}. Set it to 100`);
        updatePeriod = 100;
    }

    let _autoupdate = _params.has(AUTO_UPDATE_PARAM) && ["no", "off", "false", "0"].indexOf(_params.get(AUTO_UPDATE_PARAM).toLowerCase()) === -1;

    _params = null;

    setAutoUpdate(_autoupdate && !document.getElementById(GAME_OVER_ID));

    exitButton?.addEventListener('click', () => setAutoUpdate(false));

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
        const params = url.searchParams;

        if (autoUpdateEnabled) {
            params.set(AUTO_UPDATE_PARAM, 'on');
        } else {
            params.delete(AUTO_UPDATE_PARAM);
        }

        params.set(UPDATE_PERIOD_PARAM, updatePeriod.toString());
        if (isNaN(lastShow)) {
            params.delete(GENERATION_SERIAL_PARAM)
        } else {
            params.set(GENERATION_SERIAL_PARAM, lastShow.toString());
        }

        history.replaceState(null, null, url);
    }

    // ------------------------------------------------------------------------

    async function sleep(timeout) {
        await new Promise(f => setTimeout(f, timeout));
    }

    async function loadWorldLoop(loopId) {

        while (loopId === currentUpdateLoopId) {

            if (frameQueue.length >= FRAME_QUEUE_SIZE) {
                await sleep(updatePeriod);
                continue;
            }

            const frame = createFrame(await loadWorld(lastLoad + 1));
            frameQueue.push(frame);

            if (!isNaN(frame.serial)) {
                lastLoad = frame.serial;
            }

            if (frame.end) {
                break;
            }
        }
    }

    async function loadWorld(serial) {
        let success;
        let html_text;

        try {
            const url = isNaN(serial) ? WORLD_URL : WORLD_URL + `?serial=${serial}`;
            const response = await fetch(url);
            success = response.ok;
            html_text = await response.text();
        } catch (e) {
            html_text = html_error_message('Ошибка сети', `Я не могу получить ${serial} поколение жизни: ${e.message}`);
            success = false;
        }

        return [success, html_text];
    }

    function html_error_message(title, message) {
        // see templates/message.html
        return `<div class="text"><div class="column centered"><h1>${title}</h1><p>${message}</p><hr></div></div>`;
    }

    function createFrame([success, html_text]) {
        let serial, content, end;

        const template = document.createElement('template');
        template.innerHTML = html_text;
        content = template.content;

        if (success) {
            end = !!content.getElementById(GAME_OVER_ID);
            serial = parseInt(content.getElementById(HIDDEN_COUNTER_ID)?.textContent);
        } else {
            end = true;
            serial = NaN;
            const app_content = template.content.querySelector(".app_content");
            if (app_content !== null) {
                content = new DocumentFragment();
                content.append(app_content);
            }
        }

        return {serial, content, end};
    }

    // ------------------------------------------------------------------------

    async function showWorldLoop(loopId) {
        let startTime = Date.now();

        while (loopId === currentUpdateLoopId) {

            if (frameQueue.length === 0) {
                await sleep(FRAME_QUEUE_TIMEOUT);
                continue;
            }

            const frame = frameQueue.shift();
            showWorld(frame);
            lastShow = frame.serial;

            if (frame.end) {
                setAutoUpdate(false);
                break;
            }

            updateUrl();

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

    function showWorld({content, serial}) {
        if (counter) {
            counter.textContent = serial.toString();
        }
        worldContainer.replaceChild(content, worldContainer.firstElementChild);
    }

})();
