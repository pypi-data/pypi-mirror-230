"use strict";
(self["webpackChunktransient_display_data"] = self["webpackChunktransient_display_data"] || []).push([["lib_index_js"],{

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__),
/* harmony export */   transient: () => (/* binding */ transient)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_console__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/console */ "webpack/sharing/consume/default/@jupyterlab/console");
/* harmony import */ var _jupyterlab_console__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_console__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _transient__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./transient */ "./lib/transient.js");
/* harmony import */ var _lumino_properties__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @lumino/properties */ "webpack/sharing/consume/default/@lumino/properties");
/* harmony import */ var _lumino_properties__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_lumino_properties__WEBPACK_IMPORTED_MODULE_3__);
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.




/**
 * The console widget tracker provider.
 */
const transient = {
    id: 'vatlab/jupyterlab-extension:transient',
    requires: [_jupyterlab_console__WEBPACK_IMPORTED_MODULE_1__.IConsoleTracker],
    optional: [_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ICommandPalette],
    activate: activateTransient,
    autoStart: true
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (transient);
function activateTransient(app, tracker, palette) {
    const { shell } = app;
    tracker.widgetAdded.connect((sender, widget) => {
        const console = widget.console;
        const handler = new _transient__WEBPACK_IMPORTED_MODULE_2__.TransientHandler({
            sessionContext: console.sessionContext,
            parent: console
        });
        Private.transientHandlerProperty.set(console, handler);
        console.disposed.connect(() => {
            handler.dispose();
        });
    });
    const { commands } = app;
    const category = 'Console';
    const toggleShowTransientMessage = 'console:toggle-show-transient-message';
    // Get the current widget and activate unless the args specify otherwise.
    function getCurrent(args) {
        let widget = tracker.currentWidget;
        let activate = args['activate'] !== false;
        if (activate && widget) {
            shell.activateById(widget.id);
        }
        return widget;
    }
    commands.addCommand(toggleShowTransientMessage, {
        label: args => 'Show Transient Messages',
        execute: args => {
            let current = getCurrent(args);
            if (!current) {
                return;
            }
            const handler = Private.transientHandlerProperty.get(current.console);
            if (handler) {
                handler.enabled = !handler.enabled;
            }
        },
        isToggled: () => {
            var _a;
            return tracker.currentWidget !== null &&
                !!((_a = Private.transientHandlerProperty.get(tracker.currentWidget.console)) === null || _a === void 0 ? void 0 : _a.enabled);
        },
        isEnabled: () => tracker.currentWidget !== null &&
            tracker.currentWidget === shell.currentWidget
    });
    if (palette) {
        palette.addItem({
            command: toggleShowTransientMessage,
            category,
            args: { isPalette: true }
        });
    }
    app.contextMenu.addItem({
        command: toggleShowTransientMessage,
        selector: '.jp-CodeConsole'
    });
}
/*
 * A namespace for private data.
 */
var Private;
(function (Private) {
    /**
     * An attached property for a console's transient handler.
     */
    Private.transientHandlerProperty = new _lumino_properties__WEBPACK_IMPORTED_MODULE_3__.AttachedProperty({
        name: 'transientHandler',
        create: () => undefined
    });
})(Private || (Private = {}));


/***/ }),

/***/ "./lib/transient.js":
/*!**************************!*\
  !*** ./lib/transient.js ***!
  \**************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   TransientHandler: () => (/* binding */ TransientHandler)
/* harmony export */ });
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @lumino/signaling */ "webpack/sharing/consume/default/@lumino/signaling");
/* harmony import */ var _lumino_signaling__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_lumino_signaling__WEBPACK_IMPORTED_MODULE_0__);
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.

const TRANSIENT_CELL_CLASS = 'jp-CodeConsole-transientCell';
/**
 * A handler for capturing API messages from other sessions that should be
 * rendered in a given parent.
 */
class TransientHandler {
    /**
     * Construct a new transient message handler.
     */
    constructor(options) {
        this._enabled = true;
        this._isDisposed = false;
        this.sessionContext = options.sessionContext;
        this.sessionContext.iopubMessage.connect(this.onIOPubMessage, this);
        this._parent = options.parent;
    }
    /**
     * Set whether the handler is able to inject transient cells into a console.
     */
    get enabled() {
        return this._enabled;
    }
    set enabled(value) {
        this._enabled = value;
    }
    /**
     * The transient handler's parent receiver.
     */
    get parent() {
        return this._parent;
    }
    /**
     * Test whether the handler is disposed.
     */
    get isDisposed() {
        return this._isDisposed;
    }
    /**
     * Dispose the resources held by the handler.
     */
    dispose() {
        if (this.isDisposed) {
            return;
        }
        this._isDisposed = true;
        _lumino_signaling__WEBPACK_IMPORTED_MODULE_0__.Signal.clearData(this);
    }
    /**
     * Handler IOPub messages.
     *
     * @returns `true` if the message resulted in a new cell injection or a
     * previously injected cell being updated and `false` for all other messages.
     */
    onIOPubMessage(sender, msg) {
        var _a;
        // Only process messages if Transient cell injection is enabled.
        if (!this._enabled) {
            return false;
        }
        let kernel = (_a = this.sessionContext.session) === null || _a === void 0 ? void 0 : _a.kernel;
        if (!kernel) {
            return false;
        }
        // Check whether this message came from an external session.
        let parent = this._parent;
        let session = msg.parent_header.session;
        if (session === kernel.clientId) {
            return false;
        }
        let msgType = msg.header.msg_type;
        if (msgType !== 'transient_display_data') {
            return false;
        }
        let parentHeader = msg.parent_header;
        let parentMsgId = parentHeader.msg_id;
        let cell;
        cell = this._parent.getCell(parentMsgId);
        if (!cell) {
            // if not cell with the same parentMsgId, create a dedicated cell
            cell = this._newCell(parentMsgId);
        }
        let output = msg.content;
        output.output_type = 'display_data';
        cell.model.outputs.add(output);
        parent.update();
        return true;
    }
    /**
     * Create a new code cell for an input originated from a transient session.
     */
    _newCell(parentMsgId) {
        let cell = this.parent.createCodeCell();
        cell.addClass(TRANSIENT_CELL_CLASS);
        this._parent.addCell(cell, parentMsgId);
        return cell;
    }
}


/***/ })

}]);
//# sourceMappingURL=lib_index_js.1e2dc1b3ae89daabd4a4.js.map