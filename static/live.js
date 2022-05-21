'use strict';

(function run() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
        return;
    }

    const AUTO_UPDATE_PARAM = "autoupdate"
    const UPDATE_PERIOD_PARAM = "update_period";
    const WORLD_SERIAL_PARAM = "serial";

    const WORLD_URL = '/world';
    const HIDDEN_COUNTER_ID = 'hiddenCounter';
    const GAME_OVER_ID = 'gameOver';

    const CONTENT_SECTOR = '.app_content';

    const STOP_LABEL = 'Остановить';
    const CONTINUE_LABEL = 'Продолжить';

    const worldContainer = getElement('worldContainer', true);
    const counter = getElement('counter');
    const refreshButton = getElement('refreshButton');
    const exitButton = getElement('exitButton');

    const FRAME_QUEUE_SIZE = 5;
    const FRAME_QUEUE_TIMEOUT = 10;
    const frameQueue = [];
    let lastLoadedWorld = parseInt(counter?.textContent);
    let lastShownWorld = lastLoadedWorld;

    let autoUpdateEnabled;
    let updatePeriod;
    let currentUpdateLoopId = 0;

    init();

    // ------------------------------------------------------------------------

    function init() {
        const searchParams = new URL(location).searchParams;

        updatePeriod = parseInt(searchParams.get(UPDATE_PERIOD_PARAM));
        if (isNaN(updatePeriod)) {
            updatePeriod = 1000;
        } else if (updatePeriod < 100) {
            console.warn(`Too small value of ${UPDATE_PERIOD_PARAM}=${updatePeriod}. Set it to 100`);
            updatePeriod = 100;
        }

        let _autoupdate = searchParams.has(AUTO_UPDATE_PARAM) &&
            ["no", "off", "false", "0"].indexOf(searchParams.get(AUTO_UPDATE_PARAM).toLowerCase()) === -1;

        setAutoUpdate(_autoupdate && !document.getElementById(GAME_OVER_ID));

        exitButton?.addEventListener('click', () => setAutoUpdate(false));

        refreshButton?.setAttribute('href', '?#');
        refreshButton?.addEventListener('click', (event) => {
            setAutoUpdate(!autoUpdateEnabled);
            event.preventDefault();
            event.currentTarget.blur();
        });
    }

    // ------------------------------------------------------------------------

    function getElement(id, required) {
        const el = document.getElementById(id);
        if (el === null) {
            if (required) {
                throw new Error(`Required element with di='${id}' not found on this page`);
            } else {
                console.warn(`Element with di='${id}' not found on this page`);
            }
        }
        return el;
    }

    // ------------------------------------------------------------------------

    function setAutoUpdate(value) {
        if (value === autoUpdateEnabled) {
            return;
        }

        const oldValue = autoUpdateEnabled;
        autoUpdateEnabled = value;

        updateRefreshButtonLabel();
        updateAddressLine();

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

    function updateAddressLine() {
        const url = new URL(location);
        const params = url.searchParams;

        if (autoUpdateEnabled) {
            params.set(AUTO_UPDATE_PARAM, 'on');
        } else {
            params.delete(AUTO_UPDATE_PARAM);
        }

        params.set(UPDATE_PERIOD_PARAM, updatePeriod.toString());

        if (isNaN(lastShownWorld)) {
            params.delete(WORLD_SERIAL_PARAM)
        } else {
            params.set(WORLD_SERIAL_PARAM, lastShownWorld.toString());
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

            const frame = createFrame(await loadWorld(lastLoadedWorld + 1));
            frameQueue.push(frame);

            if (!isNaN(frame.serial)) {
                lastLoadedWorld = frame.serial;
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
        let content, serial, end;

        const template = document.createElement('template');
        template.innerHTML = html_text;
        content = template.content;

        if (success) {
            serial = parseInt(content.getElementById(HIDDEN_COUNTER_ID)?.textContent);
            end = !!content.getElementById(GAME_OVER_ID);
        } else {
            const app_content = template.content.querySelector(CONTENT_SECTOR);
            if (app_content !== null) {
                content = new DocumentFragment();
                content.append(app_content);
            }
            serial = NaN;
            end = true;
        }

        return {content, serial, end};
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
            lastShownWorld = frame.serial;

            if (frame.end) {
                setAutoUpdate(false);
                break;
            }

            updateAddressLine();

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
        worldContainer.replaceChild(content, worldContainer.firstElementChild);
        if (counter) {
            counter.textContent = serial.toString();
        }
    }

})();
