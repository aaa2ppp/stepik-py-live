'use strict';

(function run() {
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', run);
        return;
    }

    const AUTO_UPDATE_PARAM = "autoupdate"
    const UPDATE_PERIOD_PARAM = "update_period";
    const WORLD_SERIAL_PARAM = "serial";

    const WORLD_URL = '/plain_world';

    const GAME_OVER_SECTOR = '#gameOver';
    const CONTENT_SECTOR = '.app_content';

    const STOP_LABEL = 'Остановить';
    const CONTINUE_LABEL = 'Продолжить';

    const CELL_CLASS = ['cell empty-cell', 'cell living-cell', 'cell dead-cell', 'cell surviving-cell'];
    // const CELL_COLOR = ['whitesmoke', 'lightgreen', 'darkred', 'green'];

    const worldContainer = getElementById('worldContainer', true);
    const wordHeader = getElementById("worldHeader");
    const worldTable = getElementById("worldTable", true);
    const counter = getElementById('counter');
    const refreshButton = getElementById('refreshButton');
    const exitButton = getElementById('exitButton');

    const FRAME_QUEUE_SIZE = 5;
    const FRAME_QUEUE_TIMEOUT = 10;
    const frameQueue = [];
    let latestLoadedWorld = parseInt(counter?.textContent);
    let latestShownWorld = latestLoadedWorld;

    let autoUpdateEnabled;
    let updatePeriod;
    let currentUpdateLoopId = 0;
    let latestCellStates;

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

        setAutoUpdate(_autoupdate && !worldContainer.querySelector(GAME_OVER_SECTOR));

        exitButton?.addEventListener('click', () => setAutoUpdate(false));

        refreshButton?.setAttribute('href', '?#');
        refreshButton?.addEventListener('click', (event) => {
            setAutoUpdate(!autoUpdateEnabled);
            event.preventDefault();
            event.currentTarget.blur();
        });
    }

    // ------------------------------------------------------------------------

    function getElementById(id, required) {
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
        // minimal timeout 200 ms to fill the queue
        setTimeout(() => showWorldLoop(loopId).then(), updatePeriod < 200 ? 200 : updatePeriod);
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

        if (isNaN(latestShownWorld)) {
            params.delete(WORLD_SERIAL_PARAM)
        } else {
            params.set(WORLD_SERIAL_PARAM, latestShownWorld.toString());
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

            const frame = createFrame(await loadWorld(latestLoadedWorld + 1));
            frameQueue.push(frame);

            if (!isNaN(frame.serial)) {
                latestLoadedWorld = frame.serial;
            }

            if (frame.eof) {
                break;
            }
        }
    }

    async function loadWorld(serial) {
        let success;
        let html_text;

        try {
            const url = new URL(WORLD_URL, location);
            if (!isNaN(serial)) {
                url.searchParams.set('serial', serial)
            }
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
        let serial, eof, error;

        if (success) {
            // get 'serial' from fist line
            let [_start, _end] = [0, html_text.indexOf('\n')]
            serial = parseInt(html_text.substring(_start, _end));
            _start = _end + 1;

            // check the 'game over' in the second line
            _end = html_text.indexOf('\n', _start);
            eof = html_text.substring(_start, _end).toLowerCase() === "game over";
        } else {
            serial = NaN;
            error = true;
            eof = true;
        }

        return {html_text, serial, eof, error};
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
            if (frame.error) {
                showError(frame.html_text)
            } else {
                showWorld(frame.html_text);
                latestShownWorld = frame.serial;
            }

            if (frame.eof) {
                setAutoUpdate(false);
                break;
            }

            // XXX: Disabled because it causes an error in Safari and floods history.
            //      SecurityError: Attempt to use history.replaceState() more than 100 times per 30 seconds
            // updateAddressLine();

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

    function showWorld(text) {
        const lines = text.split('\n');

        // get counter from first line
        if (counter) {
            counter.textContent = lines[0];
        }

        // get header from second line
        if (wordHeader) {
            wordHeader.innerHTML = `<h2>${lines[1]}</h2>`;
        }

        // get cell states from next rows
        const newCellStates = new Uint32Array(lines.length - 2);
        for (let i = 0; i < newCellStates.length; ++i) {
            newCellStates[i] = parseInt(lines[i + 2]);
        }

        let i = 0;
        for (const tr of worldTable.rows) {
            for (const td of tr.cells) {
                const record = i >> 4;
                const offset = (i << 1) & 31;
                const cell_state = (newCellStates[record] >> offset) & 3;
                if (latestCellStates === undefined || cell_state !== ((latestCellStates[record] >> offset) & 3)) {
                    td.className = CELL_CLASS[cell_state];
                    // td.style.backgroundColor = CELL_COLOR[cell_state]
                }
                i++;
            }
        }
        latestCellStates = newCellStates;
    }

    function showError(html_text) {
        const template = document.createElement('template');
        template.innerHTML = html_text
        const content = template.content.querySelector(CONTENT_SECTOR) ||
            template.content.querySelector('body') ||
            template.content;
        worldContainer.replaceChild(content, worldContainer.firstElementChild);
    }

})();
