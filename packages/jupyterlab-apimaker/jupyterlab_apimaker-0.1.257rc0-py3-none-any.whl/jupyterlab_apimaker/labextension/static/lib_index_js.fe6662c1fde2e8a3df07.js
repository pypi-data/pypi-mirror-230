(self["webpackChunkjupyterlab_apimaker"] = self["webpackChunkjupyterlab_apimaker"] || []).push([["lib_index_js"],{

/***/ "./lib/components/APICard.js":
/*!***********************************!*\
  !*** ./lib/components/APICard.js ***!
  \***********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _UserFunctionDialog__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./UserFunctionDialog */ "./lib/components/UserFunctionDialog.js");



const APICardComponent = (props) => {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Card, { variant: 'outlined' },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CardContent, null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Stack, { direction: 'row', justifyContent: "space-between", alignItems: "center" },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { sx: { fontSize: 14 }, color: "text.secondary", noWrap: true, gutterBottom: true }, props.project.function_name)),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: "h6", noWrap: true }, `Image Tag: ${props.project.image_tag}`),
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { noWrap: true, paragraph: true }, `Description: ${props.project.help_message ? props.project.help_message : 'No description provided.'}`)),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CardActions, null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_UserFunctionDialog__WEBPACK_IMPORTED_MODULE_2__["default"], { project: props.project })))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (APICardComponent);


/***/ }),

/***/ "./lib/components/APICatalogComponent.js":
/*!***********************************************!*\
  !*** ./lib/components/APICatalogComponent.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "APICatalogComponent": () => (/* binding */ APICatalogComponent)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _APICard__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ./APICard */ "./lib/components/APICard.js");
/* harmony import */ var _Footer__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! ./Footer */ "./lib/components/Footer.js");




class APICatalogComponent extends (react__WEBPACK_IMPORTED_MODULE_0___default().Component) {
    constructor(props) {
        super(props);
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { container: true, spacing: 2, sx: {
                    paddingLeft: '20px',
                    paddingRight: '20px',
                    paddingTop: '20px',
                    overflow: 'auto',
                    maxHeight: '100%'
                } },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true, xs: 12 },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Box, { sx: { my: 4 } },
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'h1', component: 'div', align: 'center', gutterBottom: true }, "API Collection"))),
                (this.props.projects.available.length == 0 && this.props.projects.unavailable.length == 0) ? (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true, xs: 12 },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Box, { sx: { my: 4 } },
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'h3', component: 'div', align: 'center', gutterBottom: true }, "No API found yet.")))) : (null),
                this.props.projects.available.map((item) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true, xs: 12, md: 6, xl: 2 },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_APICard__WEBPACK_IMPORTED_MODULE_2__["default"], { project: item })))),
                this.props.projects.unavailable.map((item) => (react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true, xs: 12, md: 6, xl: 2 },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_APICard__WEBPACK_IMPORTED_MODULE_2__["default"], { project: item }))))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_Footer__WEBPACK_IMPORTED_MODULE_3__["default"], null)));
    }
}


/***/ }),

/***/ "./lib/components/Footer.js":
/*!**********************************!*\
  !*** ./lib/components/Footer.js ***!
  \**********************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);


const Footer = () => {
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Container, { maxWidth: 'lg' },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Box, { sx: {
                    display: "flex",
                    position: "fixed",
                    bottom: "15px",
                    right: "20px",
                    paddingRight: "20px",
                    paddingBottom: "15px",
                    width: "100%",
                    justifyContent: "flex-end"
                } },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Typography, { variant: 'body2' }, "Made with \u2764\uFE0F by Navteca.")))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (Footer);


/***/ }),

/***/ "./lib/components/TokenInfo.js":
/*!*************************************!*\
  !*** ./lib/components/TokenInfo.js ***!
  \*************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "TokensInfoComponent": () => (/* binding */ TokensInfoComponent)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_icons_material_Autorenew__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/icons-material/Autorenew */ "./node_modules/@mui/icons-material/Autorenew.js");
/* harmony import */ var _mui_icons_material_Delete__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/icons-material/Delete */ "./node_modules/@mui/icons-material/Delete.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");





class TokensInfoComponent extends (react__WEBPACK_IMPORTED_MODULE_0___default().Component) {
    constructor(props) {
        super(props);
        this.state = {
            allTokens: this.props.allTokens,
            newTokenName: ''
        };
        this._handleRefreshClick = this._handleRefreshClick.bind(this);
        this._handleDeleteClick = this._handleDeleteClick.bind(this);
    }
    _getHumanDate(currentTimestamp) {
        if (currentTimestamp) {
            return new Intl.DateTimeFormat('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' }).format(currentTimestamp * 1000);
        }
        return '-';
    }
    async _handleRefreshClick(event, item) {
        event.preventDefault();
        console.log(`Item => ${JSON.stringify(item)}`);
        const updated = await (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('tokenops', {
            method: 'PUT',
            body: JSON.stringify({ item, url: this.props.url })
        });
        console.log(`Updated Token => ${JSON.stringify(updated.token_info, null, 2)}`);
        let token_obj_id = this.state.allTokens.findIndex(obj => obj.rowid === JSON.parse(updated.token_info).rowid);
        let current_tokens = [...this.state.allTokens];
        let single_item = Object.assign({}, this.state.allTokens[token_obj_id]);
        single_item = JSON.parse(updated.token_info);
        current_tokens[token_obj_id] = single_item;
        console.log(`Token Object Id => ${token_obj_id}`);
        console.log(`Single Item => ${JSON.stringify(single_item, null, 2)}`);
        console.log(`Current Token => ${JSON.stringify(current_tokens[token_obj_id], null, 2)}`);
        console.log(`Old Tokens List => ${JSON.stringify(this.state.allTokens, null, 2)}`);
        console.log(`Updated Tokens List => ${JSON.stringify(current_tokens, null, 2)}`);
        this.setState(Object.assign(Object.assign({}, this.state), { allTokens: current_tokens }));
        this.forceUpdate();
    }
    async _handleDeleteClick(event, item) {
        event.preventDefault();
        console.log(`Item => ${JSON.stringify(item)}`);
        const deleteInfo = await (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('tokenops', {
            method: 'DELETE',
            body: JSON.stringify({ item, url: this.props.url })
        });
        this.setState(Object.assign(Object.assign({}, this.state), { allTokens: this.state.allTokens.filter(i => { if (i.rowid != item.rowid) {
                return i;
            } }) }));
        console.log(`Delete Token Info => ${JSON.stringify(deleteInfo, null, 2)}`);
    }
    render() {
        return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CssBaseline, null),
            this.state.allTokens.map((item, index) => {
                return react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Grid, { item: true, key: index, xs: 12, md: 8, lg: 6 },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.Card, null,
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CardHeader, { title: item.name }),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CardContent, null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("p", null,
                                "Id: ",
                                item.rowid),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("p", null,
                                "Token: ",
                                item.token),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("p", null,
                                "Status: ",
                                item.status),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("p", null,
                                "Created: ",
                                this._getHumanDate(item.created)),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement("p", null,
                                "Expires: ",
                                this._getHumanDate(item.expires))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.CardActions, null,
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton, { onClick: (e) => this._handleRefreshClick(e, item) },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_Autorenew__WEBPACK_IMPORTED_MODULE_3__["default"], null)),
                            item.name === 'Default' ?
                                '' :
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_1__.IconButton, { onClick: (e) => this._handleDeleteClick(e, item) },
                                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_Delete__WEBPACK_IMPORTED_MODULE_4__["default"], null)))));
            })));
    }
}


/***/ }),

/***/ "./lib/components/TokensConfiguration.js":
/*!***********************************************!*\
  !*** ./lib/components/TokensConfiguration.js ***!
  \***********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "TokensConfigurationComponent": () => (/* binding */ TokensConfigurationComponent)
/* harmony export */ });
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _mui_material_Button__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/material/Button */ "./node_modules/@mui/material/Button/Button.js");
/* harmony import */ var _mui_material_Dialog__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @mui/material/Dialog */ "./node_modules/@mui/material/Dialog/Dialog.js");
/* harmony import */ var _mui_material_DialogActions__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @mui/material/DialogActions */ "./node_modules/@mui/material/DialogActions/DialogActions.js");
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../handler */ "./lib/handler.js");
/* harmony import */ var _TokenInfo__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! ./TokenInfo */ "./lib/components/TokenInfo.js");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);







class TokensConfigurationComponent extends (react__WEBPACK_IMPORTED_MODULE_1___default().Component) {
    constructor(props) {
        super(props);
        this._onClick = (event) => {
            event.stopPropagation();
            this.setState({
                open: true
            });
        };
        this._onClose = (event) => {
            event.stopPropagation();
            this.setState({
                open: false
            });
        };
        this.state = {
            open: true,
            notebook_name: '',
            function_name: '',
            function_url: '',
            tokens: [],
            isFetching: true,
            newTokenName: '',
            endpoints: []
        };
        this._handleChange = this._handleChange.bind(this);
        this._handleSubmit = this._handleSubmit.bind(this);
        this._handleInputChange = this._handleInputChange.bind(this);
    }
    async _handleChange(event) {
        event.preventDefault();
        const function_name = event.target.value.split('/')[1];
        const notebook_name = event.target.value.split('/')[0];
        console.log(`Chosen Option => ${event.target.value}`);
        const function_url = this.props.endpoints.endpoints.filter(item => item.function_name === function_name && item.notebook_name === notebook_name);
        this.setState(Object.assign(Object.assign({}, this.state), { isFetching: true }));
        const getAllTokens = await (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('tokens_container', {
            method: 'POST',
            body: JSON.stringify({ function_name, notebook_name })
        });
        console.log(`Tokens List => ${JSON.stringify(getAllTokens.tokens_list, null, 2)}`);
        this.setState(Object.assign(Object.assign({}, this.state), { tokens: getAllTokens.tokens_list, isFetching: false, function_name: function_name, notebook_name: notebook_name, function_url: function_url[0].url }));
        this.forceUpdate();
        console.log(`Response Tokens from React => ${JSON.stringify(getAllTokens.tokens_list, null, 2)}`);
    }
    ;
    async _handleSubmit(event) {
        event.preventDefault();
        this.setState(Object.assign(Object.assign({}, this.state), { isFetching: true }));
        const newTokeninfo = await (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('tokenops', {
            method: 'POST',
            body: JSON.stringify({ token_name: this.state.newTokenName, url: this.state.function_url })
        });
        console.log(`New Token Info => ${JSON.stringify(newTokeninfo.new_token_info)}`);
        const function_name = this.state.function_name;
        const notebook_name = this.state.notebook_name;
        const getAllTokens = await (0,_handler__WEBPACK_IMPORTED_MODULE_2__.requestAPI)('tokens_container', {
            method: 'POST',
            body: JSON.stringify({ function_name, notebook_name })
        });
        this.setState(Object.assign(Object.assign({}, this.state), { tokens: getAllTokens.tokens_list, isFetching: false }));
        this.forceUpdate();
    }
    _handleInputChange(event) {
        event.preventDefault();
        this.setState({
            newTokenName: event.target.value
        });
    }
    componentDidMount() {
        this.setState(Object.assign(Object.assign({}, this.state), { endpoints: this.props.endpoints.endpoints }));
    }
    render() {
        let endpoints = this.state.endpoints.length > 0 ? true : false;
        return (react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null,
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.CssBaseline, null),
            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material_Dialog__WEBPACK_IMPORTED_MODULE_3__["default"], { open: this.state.open, onClick: this._onClick, onClose: this._onClose, maxWidth: 'md', fullWidth: true, scroll: 'paper' },
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.DialogTitle, null, "Tokens Configuration"),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.DialogContent, null,
                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid, { container: true, spacing: 2, direction: 'row', alignItems: "center", justifyContent: "center" },
                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid, { item: true, xs: 12, md: 8, lg: 6 },
                            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.FormControl, { fullWidth: true, sx: { mt: 1 }, margin: "normal" },
                                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.InputLabel, { htmlFor: "select-label" }, "Function name"),
                                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Select, { labelId: "select-label", id: "simple-select", value: this.state.notebook_name + "/" + this.state.function_name, label: "Function name", onChange: (e) => this._handleChange(e), autoFocus: true, inputProps: {
                                        id: "select-label",
                                    } }, endpoints ?
                                    (this.state.endpoints.map((item, index) => {
                                        return react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.MenuItem, { key: index, value: item.notebook_name + "/" + item.function_name },
                                            item.notebook_name + "/" + item.function_name,
                                            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("br", null));
                                    })) :
                                    (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.MenuItem, { key: "1", value: "" },
                                        "No Function Found",
                                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement("br", null)))))),
                        this.state.function_name ? (react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid, { item: true },
                            react__WEBPACK_IMPORTED_MODULE_1___default().createElement("form", { onSubmit: this._handleSubmit },
                                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid, { container: true, alignItems: "center", justifyContent: "center", direction: "row" },
                                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid, { item: true },
                                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.TextField, { id: "name-input", name: "name", label: "Name", type: "text", variant: 'outlined', value: this.state.newTokenName, onChange: this._handleInputChange })),
                                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid, { item: true, sx: { ml: 1 } },
                                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material_Button__WEBPACK_IMPORTED_MODULE_4__["default"], { variant: "contained", color: "primary", type: "submit" }, "Create")))))) : ''),
                    !this.state.isFetching ? (react__WEBPACK_IMPORTED_MODULE_1___default().createElement((react__WEBPACK_IMPORTED_MODULE_1___default().Fragment), null,
                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Typography, { variant: "h6", sx: { m: 2 } },
                            "Endpoint URL:",
                            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Link, { href: this.state.function_url, underline: "hover" }, this.state.function_url)),
                        react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_0__.Grid, { container: true, spacing: 2 },
                            react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_TokenInfo__WEBPACK_IMPORTED_MODULE_5__.TokensInfoComponent, { allTokens: this.state.tokens, url: this.state.function_url })))) : ''),
                react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material_DialogActions__WEBPACK_IMPORTED_MODULE_6__["default"], null,
                    react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_mui_material_Button__WEBPACK_IMPORTED_MODULE_4__["default"], { onClick: this._onClose, autoFocus: true, sx: { p: 2 } }, "Ok")))));
    }
}


/***/ }),

/***/ "./lib/components/UserFunctionDialog.js":
/*!**********************************************!*\
  !*** ./lib/components/UserFunctionDialog.js ***!
  \**********************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @mui/material */ "webpack/sharing/consume/default/@mui/material/@mui/material");
/* harmony import */ var _mui_material__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_mui_material__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _mui_icons_material_ContentCopy__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @mui/icons-material/ContentCopy */ "./node_modules/@mui/icons-material/ContentCopy.js");
/* harmony import */ var lodash_isundefined__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! lodash.isundefined */ "webpack/sharing/consume/default/lodash.isundefined/lodash.isundefined");
/* harmony import */ var lodash_isundefined__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(lodash_isundefined__WEBPACK_IMPORTED_MODULE_3__);





const UserFunctionDialog = (props) => {
    const [open, setOpen] = react__WEBPACK_IMPORTED_MODULE_0___default().useState(false);
    const handleClickOpen = () => {
        setOpen(true);
    };
    const handleClose = () => {
        setOpen(false);
    };
    const getCode = `import requests\nr = requests.get('${props.project.endpoint_url}')\nr.content`;
    const postCode = `import requests\nr = requests.post('${props.project.endpoint_url}', json={<function_params>})\nr.content`;
    const prepareJSONForExample = (function_params) => {
        let postCodeFixed = '';
        if (lodash_isundefined__WEBPACK_IMPORTED_MODULE_3___default()(function_params)) {
            const re = /<function_params>/gi;
            postCodeFixed = postCode.replace(re, '');
            return postCodeFixed;
        }
        let params = [];
        for (let p of function_params.split(',')) {
            params.push(`"${p.trim()}": <value>`);
        }
        const re = /<function_params>/gi;
        postCodeFixed = postCode.replace(re, params.join(', '));
        return postCodeFixed;
    };
    return (react__WEBPACK_IMPORTED_MODULE_0___default().createElement((react__WEBPACK_IMPORTED_MODULE_0___default().Fragment), null,
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Button, { size: "small", onClick: handleClickOpen }, "Learn More"),
        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Dialog, { open: open, keepMounted: true, onClose: handleClose, "aria-labelledby": 'user-function-dialog-title', "aria-describedby": 'user-function-dialog-description' },
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.DialogTitle, { id: 'user-function-dialog-title' },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Typography, { variant: 'h5', gutterBottom: true }, 'Endpoint Information')),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.DialogContent, { sx: { paddingBottom: '8px' } },
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.DialogContentText, { id: 'user-function-dialog-description' },
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Typography, null, `Description: ${props.project.help_message ? props.project.help_message : 'No description has been provided.'}\n`),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Typography, null, `Parameters: ${props.project.function_params ? props.project.function_params : 'This functions doesn\'t require parameters.'}`),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Divider, null),
                    react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Stack, { justifyContent: "flex-start", alignItems: "stretch", spacing: 0, sx: { paddingTop: '8px' } },
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Typography, { variant: 'h6' }, 'GET Method'),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Box, { sx: {
                                backgroundColor: '#f5f5f5',
                                border: '1px solid #cccccc',
                                padding: '8px 40px 8px 8px',
                                position: 'relative'
                            } },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Typography, { noWrap: true, paragraph: true, gutterBottom: true, sx: {
                                    display: 'block',
                                    fontFamily: 'monospace',
                                    fontSize: '13px',
                                    tabSize: 2,
                                    whiteSpace: 'pre-wrap',
                                    wordBreak: 'break-all',
                                    wordWrap: 'break-word'
                                } }, getCode),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.IconButton, { "aria-label": 'copy', onClick: () => _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Clipboard.copyToSystem(getCode), sx: {
                                    bottom: '0px',
                                    position: 'absolute',
                                    right: '8px'
                                } },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_ContentCopy__WEBPACK_IMPORTED_MODULE_4__["default"], { color: "action", fontSize: 'small' }))),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Typography, { variant: 'h6', sx: { paddingTop: '8px' } }, 'POST Method'),
                        react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Box, { sx: {
                                backgroundColor: '#f5f5f5',
                                border: '1px solid #cccccc',
                                padding: '8px 40px 8px 8px',
                                position: 'relative'
                            } },
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Typography, { noWrap: true, paragraph: true, gutterBottom: true, sx: {
                                    display: 'block',
                                    fontFamily: 'monospace',
                                    fontSize: '13px',
                                    tabSize: 2,
                                    whiteSpace: 'pre-wrap',
                                    wordBreak: 'break-all',
                                    wordWrap: 'break-word'
                                } }, prepareJSONForExample(props.project.function_params ? props.project.function_params : undefined)),
                            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.IconButton, { "aria-label": 'copy', onClick: () => _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_1__.Clipboard.copyToSystem(prepareJSONForExample(props.project.function_params ? props.project.function_params : undefined)), sx: {
                                    bottom: '0px',
                                    position: 'absolute',
                                    right: '8px'
                                } },
                                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_icons_material_ContentCopy__WEBPACK_IMPORTED_MODULE_4__["default"], { color: "action", fontSize: 'small' })))))),
            react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.DialogActions, null,
                react__WEBPACK_IMPORTED_MODULE_0___default().createElement(_mui_material__WEBPACK_IMPORTED_MODULE_2__.Button, { onClick: handleClose }, "Close")))));
};
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (UserFunctionDialog);


/***/ }),

/***/ "./lib/handler.js":
/*!************************!*\
  !*** ./lib/handler.js ***!
  \************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "requestAPI": () => (/* binding */ requestAPI)
/* harmony export */ });
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/services */ "webpack/sharing/consume/default/@jupyterlab/services");
/* harmony import */ var _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__);


async function requestAPI(endPoint = '', init = {}) {
    // Make request to Jupyter API
    const settings = _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeSettings();
    const requestUrl = _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_0__.URLExt.join(settings.baseUrl, 'jupyterlab_apimaker', // API Namespace
    endPoint);
    let response;
    try {
        response = await _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.makeRequest(requestUrl, init, settings);
    }
    catch (error) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.NetworkError(error);
    }
    let data = await response.text();
    if (data.length > 0) {
        try {
            data = JSON.parse(data);
        }
        catch (error) {
            console.log('Not a JSON response body.', response);
        }
    }
    if (!response.ok) {
        throw new _jupyterlab_services__WEBPACK_IMPORTED_MODULE_1__.ServerConnection.ResponseError(response, data.message || data);
    }
    return data;
}


/***/ }),

/***/ "./lib/index.js":
/*!**********************!*\
  !*** ./lib/index.js ***!
  \**********************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "ButtonExtension": () => (/* binding */ ButtonExtension),
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! @jupyterlab/coreutils */ "webpack/sharing/consume/default/@jupyterlab/coreutils");
/* harmony import */ var _jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! @jupyterlab/launcher */ "webpack/sharing/consume/default/@jupyterlab/launcher");
/* harmony import */ var _jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__);
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3__ = __webpack_require__(/*! @jupyterlab/mainmenu */ "webpack/sharing/consume/default/@jupyterlab/mainmenu");
/* harmony import */ var _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3__);
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_4__ = __webpack_require__(/*! @jupyterlab/ui-components */ "webpack/sharing/consume/default/@jupyterlab/ui-components");
/* harmony import */ var _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_4___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_4__);
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_5__ = __webpack_require__(/*! @lumino/disposable */ "webpack/sharing/consume/default/@lumino/disposable");
/* harmony import */ var _lumino_disposable__WEBPACK_IMPORTED_MODULE_5___default = /*#__PURE__*/__webpack_require__.n(_lumino_disposable__WEBPACK_IMPORTED_MODULE_5__);
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_6__ = __webpack_require__(/*! @lumino/widgets */ "webpack/sharing/consume/default/@lumino/widgets");
/* harmony import */ var _lumino_widgets__WEBPACK_IMPORTED_MODULE_6___default = /*#__PURE__*/__webpack_require__.n(_lumino_widgets__WEBPACK_IMPORTED_MODULE_6__);
/* harmony import */ var jupyterlab_toastify__WEBPACK_IMPORTED_MODULE_7__ = __webpack_require__(/*! jupyterlab_toastify */ "webpack/sharing/consume/default/jupyterlab_toastify/jupyterlab_toastify");
/* harmony import */ var jupyterlab_toastify__WEBPACK_IMPORTED_MODULE_7___default = /*#__PURE__*/__webpack_require__.n(jupyterlab_toastify__WEBPACK_IMPORTED_MODULE_7__);
/* harmony import */ var lodash_isempty__WEBPACK_IMPORTED_MODULE_8__ = __webpack_require__(/*! lodash.isempty */ "webpack/sharing/consume/default/lodash.isempty/lodash.isempty");
/* harmony import */ var lodash_isempty__WEBPACK_IMPORTED_MODULE_8___default = /*#__PURE__*/__webpack_require__.n(lodash_isempty__WEBPACK_IMPORTED_MODULE_8__);
/* harmony import */ var lodash_isequal__WEBPACK_IMPORTED_MODULE_9__ = __webpack_require__(/*! lodash.isequal */ "webpack/sharing/consume/default/lodash.isequal/lodash.isequal");
/* harmony import */ var lodash_isequal__WEBPACK_IMPORTED_MODULE_9___default = /*#__PURE__*/__webpack_require__.n(lodash_isequal__WEBPACK_IMPORTED_MODULE_9__);
/* harmony import */ var lodash_isundefined__WEBPACK_IMPORTED_MODULE_10__ = __webpack_require__(/*! lodash.isundefined */ "webpack/sharing/consume/default/lodash.isundefined/lodash.isundefined");
/* harmony import */ var lodash_isundefined__WEBPACK_IMPORTED_MODULE_10___default = /*#__PURE__*/__webpack_require__.n(lodash_isundefined__WEBPACK_IMPORTED_MODULE_10__);
/* harmony import */ var _handler__WEBPACK_IMPORTED_MODULE_11__ = __webpack_require__(/*! ./handler */ "./lib/handler.js");
/* harmony import */ var _widgets_APICatalogWidget__WEBPACK_IMPORTED_MODULE_12__ = __webpack_require__(/*! ./widgets/APICatalogWidget */ "./lib/widgets/APICatalogWidget.js");
/* harmony import */ var _widgets_TokensConfigurationWidget__WEBPACK_IMPORTED_MODULE_13__ = __webpack_require__(/*! ./widgets/TokensConfigurationWidget */ "./lib/widgets/TokensConfigurationWidget.js");














const plugin = {
    id: "jupyterlab_apimaker:plugin",
    autoStart: true,
    optional: [_jupyterlab_launcher__WEBPACK_IMPORTED_MODULE_2__.ILauncher, _jupyterlab_mainmenu__WEBPACK_IMPORTED_MODULE_3__.IMainMenu],
    activate,
};
let openedFilename;
let pathToNotebook;
async function sendNotebookText(panel) {
    var _a, _b, _c, _d;
    openedFilename = panel.title.label.split(".")[0].replace(/[ ._]/g, "-");
    console.log(`Panel Name => ${panel.title.label}`);
    console.log(`Panel Name Fix => ${openedFilename}`);
    console.log(`Panel Model => ${(_a = panel.model) === null || _a === void 0 ? void 0 : _a.toJSON()}`);
    console.log(`Panel PageConfig and Model Path => ${_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PageConfig.getOption('serverRoot')} - ${(_b = panel.context.contentsModel) === null || _b === void 0 ? void 0 : _b.path}`);
    pathToNotebook = `${_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PageConfig.getOption('serverRoot')}/${(_c = panel.context.contentsModel) === null || _c === void 0 ? void 0 : _c.path}`;
    const createProjectResult = await (0,_handler__WEBPACK_IMPORTED_MODULE_11__.requestAPI)("process_notebook", {
        method: "POST",
        body: JSON.stringify((_d = panel.model) === null || _d === void 0 ? void 0 : _d.toJSON()),
    });
    if (createProjectResult.functions) {
        return createProjectResult;
    }
    return undefined;
}
async function showFunctions(functionsInNotebook) {
    let functionsToSelect = functionsInNotebook.functions.map((el) => el.function_name);
    const functionSelector = await _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.InputDialog.getItem({
        title: "Create New API",
        label: "Select Function:",
        items: functionsToSelect,
        okLabel: "Next",
        cancelLabel: "Cancel",
    });
    if (!functionSelector.button.accept) {
        return;
    }
    if (lodash_isundefined__WEBPACK_IMPORTED_MODULE_10___default()(functionSelector.value)) {
        return undefined;
    }
    return functionSelector.value;
}
class ButtonExtension {
    createNew(panel, _) {
        const printNotebookText = async () => {
            var _a, _b;
            //         notebookTracker.currentWidget?.update()
            // notebookTracker.currentWidget?.title.label
            const functionsInNotebook = await sendNotebookText(panel);
            if (lodash_isundefined__WEBPACK_IMPORTED_MODULE_10___default()(functionsInNotebook)) {
                jupyterlab_toastify__WEBPACK_IMPORTED_MODULE_7__.INotification.warning("There are no functions in this notebook. Please, add one at least.", { autoClose: 3000 });
                return;
            }
            const selectedFunction = await showFunctions(functionsInNotebook);
            if (lodash_isundefined__WEBPACK_IMPORTED_MODULE_10___default()(selectedFunction)) {
                return;
            }
            const functionToMakeAPIFrom = functionsInNotebook.functions.filter((el) => el.function_name == selectedFunction);
            if (lodash_isempty__WEBPACK_IMPORTED_MODULE_8___default()(functionToMakeAPIFrom)) {
                jupyterlab_toastify__WEBPACK_IMPORTED_MODULE_7__.INotification.warning(`There is not a function with the name ${selectedFunction}.`, { autoClose: 3000 });
                return;
            }
            const requestDomain = await _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.InputDialog.getText({
                title: "Create New API",
                label: "Provide the domain of the API:",
                okLabel: "Next",
                cancelLabel: "Cancel",
            });
            if (!requestDomain.button.accept) {
                return;
            }
            if (lodash_isempty__WEBPACK_IMPORTED_MODULE_8___default()(requestDomain.value)) {
                jupyterlab_toastify__WEBPACK_IMPORTED_MODULE_7__.INotification.warning(`Please, insert a domain.`, { autoClose: 3000 });
                return;
            }
            const requestedDomain = (_a = requestDomain.value) === null || _a === void 0 ? void 0 : _a.replace(" ", "_").replace(/[^a-zA-Z0-9]/g, "_");
            const requestAPIVersion = await _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.InputDialog.getText({
                title: "Create New API",
                label: "Provide the version of the API:",
                okLabel: "Create",
                cancelLabel: "Cancel",
            });
            if (!requestAPIVersion.button.accept) {
                return;
            }
            if (lodash_isempty__WEBPACK_IMPORTED_MODULE_8___default()(requestAPIVersion.value)) {
                jupyterlab_toastify__WEBPACK_IMPORTED_MODULE_7__.INotification.warning(`Please, insert a version.`, { autoClose: 3000 });
                return;
            }
            const requestedAPIVersion = (_b = requestAPIVersion.value) === null || _b === void 0 ? void 0 : _b.replace(/[ ._]/g, "-");
            console.log(`Version => ${requestedAPIVersion}`);
            let id = await jupyterlab_toastify__WEBPACK_IMPORTED_MODULE_7__.INotification.inProgress("Baking API...");
            const sendFunctionToMakeAPIFrom = await (0,_handler__WEBPACK_IMPORTED_MODULE_11__.requestAPI)("make_api", {
                method: "POST",
                body: JSON.stringify({
                    userCode: functionToMakeAPIFrom[0],
                    notebookName: openedFilename,
                    domain: requestedDomain,
                    apiVersion: requestedAPIVersion,
                    pathToNotebook: pathToNotebook
                }),
            });
            if (!lodash_isequal__WEBPACK_IMPORTED_MODULE_9___default()(sendFunctionToMakeAPIFrom.statusCode, 200)) {
                jupyterlab_toastify__WEBPACK_IMPORTED_MODULE_7__.INotification.update({
                    toastId: id,
                    message: `There has been an error creating the endpoint, please contact the administrator os API Maker.`,
                    type: "warning",
                });
                return;
            }
            let messages = [
                `Let's wait for the service to be ready. This may take a while.`,
                `We're still working on it. Thank you for your patience`,
                `This process usually take some time. Please be patient.`,
                `We will let you know when your serivce is ready.`,
                `Thank you for your patience, we're still working on it.`
            ];
            const delay = (ms) => new Promise(res => setTimeout(res, ms));
            const updateNotification = (toastId, message) => {
                jupyterlab_toastify__WEBPACK_IMPORTED_MODULE_7__.INotification.update({
                    toastId: toastId,
                    message
                });
            };
            for (let i = 1; i <= 15; i++) {
                let timer = i * Math.floor(Math.random() * (30000 - 15000 + 1)) + 15000;
                let message = messages[Math.floor(Math.random() * messages.length)];
                await delay(timer);
                updateNotification(id, message);
            }
            jupyterlab_toastify__WEBPACK_IMPORTED_MODULE_7__.INotification.update({
                toastId: id,
                message: `Your service is ready: ${sendFunctionToMakeAPIFrom.body.url}`,
                type: "success",
                buttons: [
                    {
                        label: 'Copy',
                        callback: () => _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.Clipboard.copyToSystem(sendFunctionToMakeAPIFrom.body.url)
                    }
                ],
            });
            console.log(`URL and Token => ${JSON.stringify(sendFunctionToMakeAPIFrom.body.defaultToken, null, 2)}`);
        };
        const button = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ToolbarButton({
            className: "apimaker",
            label: "Bake API",
            onClick: printNotebookText,
            tooltip: "Create an API based on a selected function.",
        });
        panel.toolbar.insertItem(10, "make-api", button);
        return new _lumino_disposable__WEBPACK_IMPORTED_MODULE_5__.DisposableDelegate(() => {
            button.dispose();
        });
    }
}
function activate(app, launcher, mainMenu, panel) {
    console.log("API Baker Extension Activated");
    const { commands } = app;
    commands.addCommand("create-react-widget", {
        caption: "Show API Collection",
        label: "API Collection",
        icon: (args) => (args["isPalette"] ? undefined : _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_4__.reactIcon),
        execute: async () => {
            const getProjects = await (0,_handler__WEBPACK_IMPORTED_MODULE_11__.requestAPI)("api_catalog", {
                method: "GET",
            });
            if (lodash_isequal__WEBPACK_IMPORTED_MODULE_9___default()(getProjects.statusCode, 200)) {
                console.log(`Projects => ${JSON.stringify(getProjects, null, 2)}`);
            }
            const content = new _widgets_APICatalogWidget__WEBPACK_IMPORTED_MODULE_12__.APICatalogWidget(getProjects);
            const widget = new _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.MainAreaWidget({ content });
            widget.title.label = "API Collection";
            widget.title.icon = _jupyterlab_ui_components__WEBPACK_IMPORTED_MODULE_4__.reactIcon;
            app.shell.add(widget, "main");
        },
    });
    const command = "jlab-apibaker:command";
    commands.addCommand(command, {
        label: "Tokens Configuration",
        caption: "Tokens Configuration",
        execute: async () => {
            const getAllEndpoints = await (0,_handler__WEBPACK_IMPORTED_MODULE_11__.requestAPI)("tokens", {
                method: "GET",
            });
            const content = new _widgets_TokensConfigurationWidget__WEBPACK_IMPORTED_MODULE_13__.TokensConfigurationWidget({
                endpoints: getAllEndpoints.all_endpoints,
                jwt: getAllEndpoints.jwt,
            });
            _lumino_widgets__WEBPACK_IMPORTED_MODULE_6__.Widget.attach(content, document.body);
        },
    });
    const menu = new _lumino_widgets__WEBPACK_IMPORTED_MODULE_6__.Menu({ commands: app.commands });
    menu.title.label = "API Baker";
    menu.addItem({ command });
    mainMenu.addMenu(menu, { rank: 900 });
    Promise.all([app.restored]).then(() => {
        var _a;
        if (app.shell.currentWidget) {
            app.shell.currentWidget.update();
            if (lodash_isequal__WEBPACK_IMPORTED_MODULE_9___default()(app.shell.currentWidget.title.label.split(".").pop(), "ipynb")) {
                openedFilename = app.shell.currentWidget.title.label.split(".")[0];
                pathToNotebook = `${_jupyterlab_coreutils__WEBPACK_IMPORTED_MODULE_1__.PageConfig.getOption('serverRoot')}/${(_a = panel.context.contentsModel) === null || _a === void 0 ? void 0 : _a.path}`;
            }
        }
    });
    if (launcher) {
        launcher.add({
            command: "create-react-widget",
        });
    }
    app.docRegistry.addWidgetExtension("Notebook", new ButtonExtension());
}
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (plugin);


/***/ }),

/***/ "./lib/widgets/APICatalogWidget.js":
/*!*****************************************!*\
  !*** ./lib/widgets/APICatalogWidget.js ***!
  \*****************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "APICatalogWidget": () => (/* binding */ APICatalogWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_APICatalogComponent__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components/APICatalogComponent */ "./lib/components/APICatalogComponent.js");



class APICatalogWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(projects) {
        super();
        this.projects = projects.projects;
        console.log(`Projects in Component => ${JSON.stringify(this.projects, null, 2)}`);
    }
    render() {
        return react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_components_APICatalogComponent__WEBPACK_IMPORTED_MODULE_2__.APICatalogComponent, { projects: this.projects });
    }
}


/***/ }),

/***/ "./lib/widgets/TokensConfigurationWidget.js":
/*!**************************************************!*\
  !*** ./lib/widgets/TokensConfigurationWidget.js ***!
  \**************************************************/
/***/ ((__unused_webpack_module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "TokensConfigurationWidget": () => (/* binding */ TokensConfigurationWidget)
/* harmony export */ });
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! @jupyterlab/apputils */ "webpack/sharing/consume/default/@jupyterlab/apputils");
/* harmony import */ var _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! react */ "webpack/sharing/consume/default/react");
/* harmony import */ var react__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(react__WEBPACK_IMPORTED_MODULE_1__);
/* harmony import */ var _components_TokensConfiguration__WEBPACK_IMPORTED_MODULE_2__ = __webpack_require__(/*! ../components/TokensConfiguration */ "./lib/components/TokensConfiguration.js");



class TokensConfigurationWidget extends _jupyterlab_apputils__WEBPACK_IMPORTED_MODULE_0__.ReactWidget {
    constructor(master_db_info) {
        super();
        this.tokenDummyData = master_db_info;
    }
    render() {
        return react__WEBPACK_IMPORTED_MODULE_1___default().createElement(_components_TokensConfiguration__WEBPACK_IMPORTED_MODULE_2__.TokensConfigurationComponent, { endpoints: this.tokenDummyData });
    }
}


/***/ }),

/***/ "./node_modules/@babel/runtime/helpers/interopRequireDefault.js":
/*!**********************************************************************!*\
  !*** ./node_modules/@babel/runtime/helpers/interopRequireDefault.js ***!
  \**********************************************************************/
/***/ ((module) => {

function _interopRequireDefault(obj) {
  return obj && obj.__esModule ? obj : {
    "default": obj
  };
}

module.exports = _interopRequireDefault;
module.exports["default"] = module.exports, module.exports.__esModule = true;

/***/ }),

/***/ "./node_modules/@mui/icons-material/Autorenew.js":
/*!*******************************************************!*\
  !*** ./node_modules/@mui/icons-material/Autorenew.js ***!
  \*******************************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";


var _interopRequireDefault = __webpack_require__(/*! @babel/runtime/helpers/interopRequireDefault */ "./node_modules/@babel/runtime/helpers/interopRequireDefault.js");

Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports["default"] = void 0;

var _createSvgIcon = _interopRequireDefault(__webpack_require__(/*! ./utils/createSvgIcon */ "./node_modules/@mui/icons-material/utils/createSvgIcon.js"));

var _jsxRuntime = __webpack_require__(/*! react/jsx-runtime */ "./node_modules/react/jsx-runtime.js");

var _default = (0, _createSvgIcon.default)( /*#__PURE__*/(0, _jsxRuntime.jsx)("path", {
  d: "M12 6v3l4-4-4-4v3c-4.42 0-8 3.58-8 8 0 1.57.46 3.03 1.24 4.26L6.7 14.8c-.45-.83-.7-1.79-.7-2.8 0-3.31 2.69-6 6-6zm6.76 1.74L17.3 9.2c.44.84.7 1.79.7 2.8 0 3.31-2.69 6-6 6v-3l-4 4 4 4v-3c4.42 0 8-3.58 8-8 0-1.57-.46-3.03-1.24-4.26z"
}), 'Autorenew');

exports["default"] = _default;

/***/ }),

/***/ "./node_modules/@mui/icons-material/ContentCopy.js":
/*!*********************************************************!*\
  !*** ./node_modules/@mui/icons-material/ContentCopy.js ***!
  \*********************************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";


var _interopRequireDefault = __webpack_require__(/*! @babel/runtime/helpers/interopRequireDefault */ "./node_modules/@babel/runtime/helpers/interopRequireDefault.js");

Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports["default"] = void 0;

var _createSvgIcon = _interopRequireDefault(__webpack_require__(/*! ./utils/createSvgIcon */ "./node_modules/@mui/icons-material/utils/createSvgIcon.js"));

var _jsxRuntime = __webpack_require__(/*! react/jsx-runtime */ "./node_modules/react/jsx-runtime.js");

var _default = (0, _createSvgIcon.default)( /*#__PURE__*/(0, _jsxRuntime.jsx)("path", {
  d: "M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"
}), 'ContentCopy');

exports["default"] = _default;

/***/ }),

/***/ "./node_modules/@mui/icons-material/Delete.js":
/*!****************************************************!*\
  !*** ./node_modules/@mui/icons-material/Delete.js ***!
  \****************************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";


var _interopRequireDefault = __webpack_require__(/*! @babel/runtime/helpers/interopRequireDefault */ "./node_modules/@babel/runtime/helpers/interopRequireDefault.js");

Object.defineProperty(exports, "__esModule", ({
  value: true
}));
exports["default"] = void 0;

var _createSvgIcon = _interopRequireDefault(__webpack_require__(/*! ./utils/createSvgIcon */ "./node_modules/@mui/icons-material/utils/createSvgIcon.js"));

var _jsxRuntime = __webpack_require__(/*! react/jsx-runtime */ "./node_modules/react/jsx-runtime.js");

var _default = (0, _createSvgIcon.default)( /*#__PURE__*/(0, _jsxRuntime.jsx)("path", {
  d: "M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"
}), 'Delete');

exports["default"] = _default;

/***/ }),

/***/ "./node_modules/@mui/icons-material/utils/createSvgIcon.js":
/*!*****************************************************************!*\
  !*** ./node_modules/@mui/icons-material/utils/createSvgIcon.js ***!
  \*****************************************************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";


Object.defineProperty(exports, "__esModule", ({
  value: true
}));
Object.defineProperty(exports, "default", ({
  enumerable: true,
  get: function () {
    return _utils.createSvgIcon;
  }
}));

var _utils = __webpack_require__(/*! @mui/material/utils */ "./node_modules/@mui/material/utils/index.js");

/***/ })

}]);
//# sourceMappingURL=lib_index_js.fe6662c1fde2e8a3df07.js.map