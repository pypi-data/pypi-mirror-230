"use strict";
(self["webpackChunkjupyterlab_local_browser"] = self["webpackChunkjupyterlab_local_browser"] || []).push([["lib_index_js"],{

/***/ "./lib/icon.js":
/*!*********************!*\
  !*** ./lib/icon.js ***!
  \*********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   webIcon: () => (/* binding */ webIcon)
/* harmony export */ });
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__);

const webIcon = new _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_0__.LabIcon({
    name: 'jupyterlab_local_browser:web',
    svgstr: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><title>web</title><path d="M16.36,14C16.44,13.34 16.5,12.68 16.5,12C16.5,11.32 16.44,10.66 16.36,10H19.74C19.9,10.64 20,11.31 20,12C20,12.69 19.9,13.36 19.74,14M14.59,19.56C15.19,18.45 15.65,17.25 15.97,16H18.92C17.96,17.65 16.43,18.93 14.59,19.56M14.34,14H9.66C9.56,13.34 9.5,12.68 9.5,12C9.5,11.32 9.56,10.65 9.66,10H14.34C14.43,10.65 14.5,11.32 14.5,12C14.5,12.68 14.43,13.34 14.34,14M12,19.96C11.17,18.76 10.5,17.43 10.09,16H13.91C13.5,17.43 12.83,18.76 12,19.96M8,8H5.08C6.03,6.34 7.57,5.06 9.4,4.44C8.8,5.55 8.35,6.75 8,8M5.08,16H8C8.35,17.25 8.8,18.45 9.4,19.56C7.57,18.93 6.03,17.65 5.08,16M4.26,14C4.1,13.36 4,12.69 4,12C4,11.31 4.1,10.64 4.26,10H7.64C7.56,10.66 7.5,11.32 7.5,12C7.5,12.68 7.56,13.34 7.64,14M12,4.03C12.83,5.23 13.5,6.57 13.91,8H10.09C10.5,6.57 11.17,5.23 12,4.03M18.92,8H15.97C15.65,6.75 15.19,5.55 14.59,4.44C16.43,5.07 17.96,6.34 18.92,8M12,2C6.47,2 2,6.5 2,12A10,10 0 0,0 12,22A10,10 0 0,0 22,12A10,10 0 0,0 12,2Z" /></svg>',
});


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/application */ "webpack/sharing/consume/default/@jupyterlab/application");
/* harmony import */ var _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_statedb__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/statedb */ "webpack/sharing/consume/default/@jupyterlab/statedb");
/* harmony import */ var _jupyterlab_statedb__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_statedb__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var uuid__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! uuid */ "webpack/sharing/consume/default/uuid/uuid");
/* harmony import */ var uuid__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(uuid__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _icon__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./icon */ "./lib/icon.js");
/* harmony import */ var _widget__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! ./widget */ "./lib/widget.js");







/**
 * Initialization data for the jupyterlab_local_browser extension.
 */
const plugin = {
    id: 'jupyterlab_local_browser:plugin',
    description: 'JupyterLab Local Browser',
    requires: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.ICommandPalette, _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__.ILauncher, _jupyterlab_application__WEBPACK_IMPORTED_MODULE_0__.ILayoutRestorer, _jupyterlab_statedb__WEBPACK_IMPORTED_MODULE_3__.IStateDB],
    autoStart: true,
    activate: (app, palette, launcher, restorer, statedb) => {
        // Add the command to open the local browser
        const command = 'jupyterlab_local_browser:open';
        app.commands.addCommand(command, {
            label: (args) => (args['isPalette'] ? 'New Local Browser' : 'Local Browser'),
            caption: 'Start a new Local Browser',
            icon: _icon__WEBPACK_IMPORTED_MODULE_5__.webIcon,
            execute: (args) => {
                // Create the widget
                const uuid = args && args.uuid ? args.uuid : 'lb-' + (0,uuid__WEBPACK_IMPORTED_MODULE_4__.v4)();
                const widget = new _widget__WEBPACK_IMPORTED_MODULE_6__.LocalBrowserWidget({ uuid: uuid, statedb: statedb });
                // Track the state of the widget for later restoration
                tracker.add(widget);
                app.shell.add(widget, 'main');
                widget.content.update();
                // Activate the widget
                app.shell.activateById(widget.id);
            }
        });
        // Add the command to the palette.
        palette.addItem({ command, category: 'Local Browser' });
        // Add the command to the launcher.
        launcher.add({
            command,
            category: 'Open Computing Lab',
            rank: 1,
        });
        // Track and restore the widget state
        const tracker = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.WidgetTracker({
            namespace: 'local_browser'
        });
        restorer.restore(tracker, {
            command,
            name: obj => obj.node.id,
            args: obj => {
                return { uuid: obj.node.id };
            }
        });
    }
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   LocalBrowserWidget: () => (/* binding */ LocalBrowserWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _icon__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./icon */ "./lib/icon.js");






/**
 * A widget providing a browser for local servers.
 */
class LocalBrowserWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.MainAreaWidget {
    constructor(options) {
        super({
            content: new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.IFrame({
                sandbox: ['allow-same-origin', 'allow-scripts']
            }),
        });
        this._loadPortsInterval = -1;
        this.id = options.uuid;
        this.title.label = 'Local Browser';
        this.title.closable = true;
        this.title.icon = _icon__WEBPACK_IMPORTED_MODULE_5__.webIcon;
        this.content.addClass('lb-localBrowser');
        this._modeWidget = new SelectWidget({
            onChange: () => {
                this.toolbarChanged();
            },
            value: 'relative'
        });
        this._modeWidget.values = [
            ['relative', 'Relative Path'],
            ['absolute', 'Absolute Path'],
        ];
        this.toolbar.addItem('mode', this._modeWidget);
        this._portsWidget = new SelectWidget({
            onChange: () => {
                this.toolbarChanged();
            },
            value: '_placeholder'
        });
        this.toolbar.addItem('ports', this._portsWidget);
        this._pathWidget = new PathWidget({
            onChange: () => {
                this.toolbarChanged();
            },
            value: '',
        });
        this.toolbar.addItem('path', this._pathWidget);
        const reloadButton = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
            icon: _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.refreshIcon,
            iconLabel: 'Reload',
            onClick: () => {
                const contentDocument = this.content.node.children[0]
                    .contentDocument;
                if (contentDocument) {
                    contentDocument.location.reload();
                }
            }
        });
        this.toolbar.addItem('reload', reloadButton);
        this._statedb = options.statedb;
        this._serverSettings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_2__.ServerConnection.makeSettings();
        this.content.url = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__.URLExt.join(this._serverSettings.baseUrl, 'jupyterlab-local-browser', 'public', 'index.html');
        options.statedb.fetch(options.uuid).then((data) => {
            if (data) {
                this._modeWidget.value = data.mode;
                this._portsWidget.value = data.port;
                this._pathWidget.value =
                    data.pathname.charAt(0) === '/'
                        ? data.pathname.substring(1)
                        : data.pathname;
                this.toolbarChanged();
            }
        });
        this.content.node.children[0].addEventListener('load', this);
        this._loadPortsInterval = setInterval(() => {
            this._evtLoadPortsTimer();
        }, 10000);
        this._evtLoadPortsTimer();
    }
    handleEvent(evt) {
        if (evt.type === 'load') {
            this._evtIFrameLoad();
        }
        else {
            console.log(evt);
        }
    }
    toolbarChanged() {
        if (this._portsWidget.value === '_placeholder') {
            this.content.url = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__.URLExt.join(this._serverSettings.baseUrl, 'jupyterlab-local-browser', 'public', 'index.html');
        }
        else {
            this.content.url =
                this._serverSettings.baseUrl +
                    'proxy' +
                    (this._modeWidget.value === 'absolute' ? '/absolute/' : '/') +
                    this._portsWidget.value +
                    '/' +
                    this._pathWidget.value;
        }
    }
    onCloseRequest(msg) {
        this.content.node.children[0].removeEventListener('load', this);
        clearInterval(this._loadPortsInterval);
        super.onCloseRequest(msg);
    }
    _evtIFrameLoad() {
        const contentDocument = this.content.node.children[0]
            .contentDocument;
        if (contentDocument) {
            this.title.label = contentDocument.title;
            const iFrameLocation = contentDocument.location;
            if (iFrameLocation.pathname.indexOf('/jupyterlab-local-browser/public/index.html') >= 0) {
                this._statedb.remove(this.id);
            }
            else {
                let pathname = iFrameLocation.href.substring(this._serverSettings.baseUrl.length);
                const mode = (pathname.startsWith('proxy/absolute/') ? 'absolute' : 'relative');
                if (mode === 'absolute') {
                    pathname = pathname.substring(15);
                }
                else {
                    pathname = pathname.substring(6);
                }
                const port = pathname.substring(0, pathname.indexOf('/'));
                pathname = pathname.substring(pathname.indexOf('/'));
                this._statedb.save(this.id, {
                    mode: mode,
                    port: port,
                    pathname: pathname,
                    search: iFrameLocation.search,
                    hash: iFrameLocation.hash
                });
                this._pathWidget.value =
                    pathname.charAt(0) === '/' ? pathname.substring(1) : pathname;
            }
        }
    }
    _evtLoadPortsTimer() {
        const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_3__.URLExt.join(this._serverSettings.baseUrl, 'jupyterlab-local-browser', 'open-ports');
        _jupyterlab_services__WEBPACK_IMPORTED_MODULE_2__.ServerConnection.makeRequest(requestUrl, {}, this._serverSettings).then(response => {
            response.json().then((data) => {
                const baseUrl = new URL(this._serverSettings.baseUrl);
                const basePort = baseUrl.port;
                const values = data
                    .map(([port, label]) => {
                    if (port !== basePort) {
                        return [port, label];
                    }
                    else {
                        return null;
                    }
                })
                    .filter(value => value !== null);
                values.splice(0, 0, ['_placeholder', 'Select a Port']);
                this._portsWidget.values = values;
            });
        });
    }
}
class SelectWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(options) {
        super();
        this._values = [];
        this._value = options.value ? options.value : '';
        this._onChange = options.onChange;
    }
    set values(value) {
        this._values = value;
        this.update();
    }
    get value() {
        return this._value;
    }
    set value(value) {
        this._value = value;
        this.update();
    }
    onChange(evt) {
        this._value = evt.target.value;
        this._onChange();
        this.update();
    }
    render() {
        const values = [];
        for (const [value, label] of this._values) {
            values.push(react__WEBPACK_IMPORTED_MODULE_4___default().createElement("option", { value: value, selected: value === this._value }, label));
        }
        return react__WEBPACK_IMPORTED_MODULE_4___default().createElement(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_1__.HTMLSelect, { onChange: evt => this.onChange(evt) }, values);
    }
}
class PathWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(options) {
        super();
        this._onChange = options.onChange;
        this._value = options.value ? options.value : '';
    }
    get value() {
        return this._value;
    }
    set value(value) {
        this._value = value;
        this.update();
    }
    onChange(evt) {
        this._value = evt.target.value;
        this._onChange();
        this.update();
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_4___default().createElement("input", { type: "text", value: this._value, onChange: evt => this.onChange(evt), className: "jp-Default" }));
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.5f46ce2087aead2d8eae.js.map