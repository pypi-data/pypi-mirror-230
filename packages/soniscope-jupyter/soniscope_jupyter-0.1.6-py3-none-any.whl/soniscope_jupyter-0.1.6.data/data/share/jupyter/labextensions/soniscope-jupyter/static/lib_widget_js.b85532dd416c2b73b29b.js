(self["webpackChunksoniscope_jupyter"] = self["webpackChunksoniscope_jupyter"] || []).push([["lib_widget_js"],{

/***/ "./node_modules/css-loader/dist/cjs.js!./css/widget.css":
/*!**************************************************************!*\
  !*** ./node_modules/css-loader/dist/cjs.js!./css/widget.css ***!
  \**************************************************************/
/***/ ((module, __webpack_exports__, __webpack_require__) => {

"use strict";
__webpack_require__.r(__webpack_exports__);
/* harmony export */ __webpack_require__.d(__webpack_exports__, {
/* harmony export */   "default": () => (__WEBPACK_DEFAULT_EXPORT__)
/* harmony export */ });
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/sourceMaps.js */ "./node_modules/css-loader/dist/runtime/sourceMaps.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0__);
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__ = __webpack_require__(/*! ../node_modules/css-loader/dist/runtime/api.js */ "./node_modules/css-loader/dist/runtime/api.js");
/* harmony import */ var _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default = /*#__PURE__*/__webpack_require__.n(_node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1__);
// Imports


var ___CSS_LOADER_EXPORT___ = _node_modules_css_loader_dist_runtime_api_js__WEBPACK_IMPORTED_MODULE_1___default()((_node_modules_css_loader_dist_runtime_sourceMaps_js__WEBPACK_IMPORTED_MODULE_0___default()));
// Module
___CSS_LOADER_EXPORT___.push([module.id, `.custom-widget {
  background-color: lightseagreen;
  padding: 0px 2px;
}

.substrate .label {
  font-size: 10px;
  font-family: sans-serif;
  color: #404040;
}

.substrate .axis {
  font-size: 10px;
  font-family: sans-serif;
  color: #404040;
}

.substrate {
  pointer-events: none;
}

.cursor.overlay {
  pointer-events: all;
  fill: none;
  cursor: crosshair;
  shape-rendering: auto;
}

.cursor.lens * {
  stroke: none;
  fill: #3f3f3f;
  /* fill: rgb(0, 0, 165);  */
  /* opacity: 0; */
}

.cursor.lens.active {
  stroke: none;
  fill: rgb(165, 0, 0);
  opacity: 0;
}
`, "",{"version":3,"sources":["webpack://./css/widget.css"],"names":[],"mappings":"AAAA;EACE,+BAA+B;EAC/B,gBAAgB;AAClB;;AAEA;EACE,eAAe;EACf,uBAAuB;EACvB,cAAc;AAChB;;AAEA;EACE,eAAe;EACf,uBAAuB;EACvB,cAAc;AAChB;;AAEA;EACE,oBAAoB;AACtB;;AAEA;EACE,mBAAmB;EACnB,UAAU;EACV,iBAAiB;EACjB,qBAAqB;AACvB;;AAEA;EACE,YAAY;EACZ,aAAa;EACb,2BAA2B;EAC3B,gBAAgB;AAClB;;AAEA;EACE,YAAY;EACZ,oBAAoB;EACpB,UAAU;AACZ","sourcesContent":[".custom-widget {\n  background-color: lightseagreen;\n  padding: 0px 2px;\n}\n\n.substrate .label {\n  font-size: 10px;\n  font-family: sans-serif;\n  color: #404040;\n}\n\n.substrate .axis {\n  font-size: 10px;\n  font-family: sans-serif;\n  color: #404040;\n}\n\n.substrate {\n  pointer-events: none;\n}\n\n.cursor.overlay {\n  pointer-events: all;\n  fill: none;\n  cursor: crosshair;\n  shape-rendering: auto;\n}\n\n.cursor.lens * {\n  stroke: none;\n  fill: #3f3f3f;\n  /* fill: rgb(0, 0, 165);  */\n  /* opacity: 0; */\n}\n\n.cursor.lens.active {\n  stroke: none;\n  fill: rgb(165, 0, 0);\n  opacity: 0;\n}\n"],"sourceRoot":""}]);
// Exports
/* harmony default export */ const __WEBPACK_DEFAULT_EXPORT__ = (___CSS_LOADER_EXPORT___);


/***/ }),

/***/ "./lib/lensCursor.js":
/*!***************************!*\
  !*** ./lib/lensCursor.js ***!
  \***************************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

// Copyright (c) Alexander Rind & the SoniVis team.
// Distributed under the terms of the MIT License (see LICENSE.txt).
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.removeLensCursor = exports.LensCursor = void 0;
const d3 = __importStar(__webpack_require__(/*! d3 */ "webpack/sharing/consume/default/d3/d3"));
const DEFAULT_OPACITY = 0.3;
class LensCursor {
    constructor(view, gPlot) {
        this.smallerSize = 100;
        this.rPixels = 10;
        this.transform = (x, y) => {
            return { x, y };
        };
        this.view = view;
        // prepare a clip-path, which will be defined in updateSubstrateSize()
        this.clipId =
            'clip' + (Math.random().toString(36) + '00000000000000000').slice(2, 14);
        d3.select(this.view.el)
            .select('svg')
            .append('defs')
            .append('clipPath')
            .attr('id', this.clipId);
        this.selLens = gPlot
            .append('g')
            .attr('clip-path', `url(#${this.clipId})`)
            // clipping must happen before translation
            .append('g')
            .classed('cursor lens', true)
            .style('opacity', 0)
            .attr('transform', 'translate(0, 0)');
        this.updateLensShape();
        this.view.model.on('change:shape', () => this.updateLensShape(), this.view);
        // add invisible rect to track mouse position (as last svg element)
        this.selOverlay = gPlot
            .append('rect')
            .classed('cursor overlay', true)
            .attr('x', 0)
            // .on('touchstart', (event) => event.preventDefault())
            .on('mouseenter', () => {
            this.selLens.style('opacity', DEFAULT_OPACITY);
        })
            .on('mouseleave', () => {
            this.selLens.style('opacity', 0);
        })
            .on('wheel', (evt) => {
            evt.preventDefault();
            evt.stopPropagation();
            // TODO prevent screen from scrolling on Firefox
            const oldLensSize = this.view.model.get('size');
            const scaledLensSize = oldLensSize * Math.pow(1.25, evt.deltaY / -100);
            const newLensSize = Math.min(1.5, Math.max(0.01, scaledLensSize));
            // console.log('g', evt, newLensSize);
            this.view.model.set('size', newLensSize);
            this.view.model.save_changes();
            return false;
        }, { passive: false })
            .on('mousemove', (evt) => {
            const rawX = d3.pointer(evt)[0];
            const rawY = d3.pointer(evt)[1];
            // circle.attr('cx', rawX).attr('cy', rawY);
            this.selLens.attr('transform', `translate(${rawX}, ${rawY})`);
        })
            .on('pointerup', () => {
            view.send({
                event: 'lens_released',
            });
        })
            .on('touchend', () => {
            // lens fade out
            this.selLens.transition().duration(800).style('opacity', 0);
        })
            .on('mousedown touchstart', (evt) => {
            evt.preventDefault();
            // recover coordinate we need
            let rawX = -1;
            let rawY = -1;
            if (evt.type === 'touchstart') {
                rawX = d3.pointers(evt)[0][0];
                rawY = d3.pointers(evt)[0][1];
            }
            else if (evt.type === 'mousedown') {
                rawX = d3.pointer(evt)[0];
                rawY = d3.pointer(evt)[1];
            }
            if (rawX < 0 || rawY < 0) {
                return;
            }
            // delegate coordinate transformations to caller
            const center = this.transform(rawX, rawY);
            // console.log(center);
            // TODO assumption of a linear scale
            const corner = this.transform(rawX + this.rPixels, rawY - this.rPixels);
            view.send(Object.assign(Object.assign({ event: 'lens' }, center), { edgeX: corner.x, edgeY: corner.y }));
            // lens positioned here
            this.selLens.attr('transform', `translate(${rawX}, ${rawY})`);
            // lens visible (fade out after touchend)
            this.selLens.style('opacity', DEFAULT_OPACITY);
        });
        // TODO change lense size by multi-touch cp. <https://observablehq.com/@d3/multitouch#cell-308>
        this.updateSubstrateSize();
        this.view.model.on('change:substrate_width change:substrate_height', () => this.updateSubstrateSize(), this.view);
        this.updateLensSize();
        this.view.model.on('change:size', () => this.updateLensSize(), this.view);
    }
    updateSubstrateSize() {
        const substWidth = this.view.model.get('substrate_width');
        const substHeight = this.view.model.get('substrate_height');
        this.selOverlay.attr('width', substWidth);
        this.selOverlay.attr('height', substHeight);
        d3.select(this.view.el)
            .select('#' + this.clipId)
            .html(`<rect x="0" y="0" width="${substWidth}" height="${substHeight}" />`);
        this.smallerSize = Math.min(substWidth, substHeight);
        this.updateLensSize();
    }
    updateLensSize() {
        const lensSize = this.view.model.get('size');
        // console.log('client swidth ', this.smallerSize);
        this.rPixels = (lensSize * this.smallerSize) / 2.0;
        // this.selLens.attr('r', this.rPixels);
        // console.log(this.selLens.selectAll('*'));
        this.selLens.selectAll('*').attr('transform', `scale(${this.rPixels})`);
    }
    updateLensShape() {
        //   this.selLens.html('');
        if (this.view.model.get('shape') === 'circle') {
            this.selLens.html(`<circle r="1" cx="0", cy="0" transform="scale(${this.rPixels})"/>`);
        }
        else if (this.view.model.get('shape') === 'square') {
            this.selLens.html(`<rect x="-1" y="-1" width="2" height="2" transform="scale(${this.rPixels})"/>`);
        }
        else if (this.view.model.get('shape') === 'xonly') {
            this.selLens.html(`<rect x="-1" y="-40000" width="2" height="80000" transform="scale(${this.rPixels})"/>`);
        }
        else if (this.view.model.get('shape') === 'yonly') {
            this.selLens.html(`<rect x="-40000" y="-1" width="80000" height="2" transform="scale(${this.rPixels})"/>`);
        }
        else if (this.view.model.get('shape') === 'none') {
            this.selLens.html('');
        }
    }
}
exports.LensCursor = LensCursor;
function removeLensCursor(gPlot) {
    gPlot.selectAll('.cursor').remove();
}
exports.removeLensCursor = removeLensCursor;


/***/ }),

/***/ "./lib/scatterPlot.js":
/*!****************************!*\
  !*** ./lib/scatterPlot.js ***!
  \****************************/
/***/ (function(__unused_webpack_module, exports, __webpack_require__) {

"use strict";

// Copyright (c) Alexander Rind & the SoniVis team.
// Distributed under the terms of the MIT License (see LICENSE.txt).
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    Object.defineProperty(o, k2, { enumerable: true, get: function() { return m[k]; } });
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.ScatterPlot = void 0;
const d3 = __importStar(__webpack_require__(/*! d3 */ "webpack/sharing/consume/default/d3/d3"));
const lensCursor_1 = __webpack_require__(/*! ./lensCursor */ "./lib/lensCursor.js");
const MARGIN = { top: 18, right: 30, bottom: 30, left: 30 };
const MARK_RADIUS = 2;
class ScatterPlot {
    constructor(view) {
        this.view = view;
        const g = d3
            .select(view.el)
            .append('svg')
            .attr('width', 100)
            .attr('height', 100)
            .append('g')
            .classed('substrate', true)
            .attr('transform', 'translate(' + MARGIN.left + ',' + MARGIN.top + ')');
        // set the scales
        const x = prepareScale([], [0, 100]);
        const y = prepareScale([], [100, 0]);
        // add the X Axis
        g.append('g')
            .attr('class', 'x axis')
            .attr('transform', 'translate(0,' + 100 + ')')
            .call(d3.axisBottom(x));
        // add the Y axis
        g.append('g').attr('class', 'y axis').call(d3.axisLeft(y));
        // add the color legend
        g.append('g')
            .attr('id', 'legend')
            .append('text')
            .classed('label', true)
            .style('text-anchor', 'end');
        this.lensCursor = new lensCursor_1.LensCursor(view, g);
        this.updateSubstrateSize();
        this.view.model.on('change:substrate_width change:substrate_height', () => this.updateSubstrateSize(), this.view);
        this.view.model.on('change:_marks_x change:_marks_y change:_marks_color', this.updateScatterPlotData, this);
    }
    updateSubstrateSize() {
        const substWidth = this.view.model.get('substrate_width');
        const substHeight = this.view.model.get('substrate_height');
        const selSvg = d3
            .select(this.view.el)
            .select('svg')
            .attr('width', substWidth + MARGIN.left + MARGIN.right)
            .attr('height', substHeight + MARGIN.top + MARGIN.bottom);
        selSvg
            .select('.x.axis')
            .attr('transform', 'translate(0,' + substHeight + ')');
        selSvg
            .select('#legend')
            .attr('transform', 'translate(' + (substWidth + MARGIN.right) + ', -2)');
        this.updateScatterPlotData();
    }
    updateScatterPlotData() {
        const substWidth = this.view.model.get('substrate_width');
        const substHeight = this.view.model.get('substrate_height');
        const xValues = this.view.model.get('_marks_x');
        const yValues = this.view.model.get('_marks_y');
        const cValues = this.view.model.get('_marks_color');
        // set the scales
        const xScale = prepareScale(xValues, [0, substWidth]);
        const yScale = prepareScale(yValues, [substHeight, 0]);
        this.lensCursor.transform = (x, y) => {
            return { x: xScale.invert(x), y: yScale.invert(y) };
        };
        // const colorValues = [...new Set(cValues)];
        const colorValues = d3
            .rollups(cValues, (v) => v.length, (d) => d)
            .sort((a, b) => (a[1] < b[1] ? 1 : -1))
            .map((v) => v[0]);
        // console.log(colorValues);
        // a.last_nom.localeCompare(b.last_nom))
        const colorScale = d3.scaleOrdinal(d3.schemeTableau10).domain(colorValues);
        // console.log('%% length x: ' + xValues.length + ' , y: ' + yValues.length);
        const gSubstrate = d3.select(this.view.el).select('g.substrate');
        // add the scatterplot without data transformations
        // <https://stackoverflow.com/a/17872039/1140589>
        gSubstrate
            .selectAll('circle.dot')
            .data(xValues.length < yValues.length ? xValues : yValues)
            .join('circle')
            .classed('dot', true)
            .attr('r', MARK_RADIUS)
            .attr('fill', (d, i) => colorScale(cValues[i]))
            .attr('cx', (d, i) => xScale(xValues[i]))
            .attr('cy', (d, i) => yScale(yValues[i]));
        // update the X Axis
        gSubstrate.select('.x.axis').call(d3.axisBottom(xScale));
        gSubstrate
            .selectAll('.x.label')
            .data([this.view.model.get('x_field')])
            .join('text')
            .attr('class', 'x label')
            // .attr("transform", "rotate(-90)")
            .attr('y', substHeight + 26)
            .attr('x', substWidth + MARGIN.right / 2)
            .style('text-anchor', 'end')
            .text((d) => d);
        // update the Y axis
        gSubstrate.select('.y.axis').call(d3.axisLeft(yScale));
        gSubstrate
            .selectAll('.y.label')
            .data([this.view.model.get('y_field')])
            .join('text')
            .attr('class', 'y label')
            // .attr("transform", "rotate(-90)")
            .attr('y', -8)
            .attr('x', -MARGIN.left)
            .style('text-anchor', 'start')
            .text((d) => d);
        // update the legend
        const gLegend = gSubstrate.select('g#legend');
        gLegend.select('text.label').text(this.view.model.get('color_field'));
        gLegend
            .selectAll('text.axis')
            .data(colorValues)
            .join('text')
            .attr('class', 'axis')
            .text((d) => d)
            .style('text-anchor', 'end')
            .attr('x', '-9')
            .attr('y', (d, i) => i * 14 + 14);
        gLegend
            .selectAll('rect')
            .data(colorValues)
            .join('rect')
            .attr('x', '-7')
            .attr('y', (d, i) => i * 14 + 7)
            .attr('width', '7')
            .attr('height', '7')
            .style('fill', (d) => colorScale(d));
    }
}
exports.ScatterPlot = ScatterPlot;
function prepareScale(values, range) {
    const xMin = d3.min(values) || 0;
    const xMax = d3.max(values) || 1;
    // console.log('%% domain: [' + xMin + ' ,' + xMax + ']');
    const space = (xMax - xMin) * 0.05;
    const xSpacedMin = xMin - space < 0 && xMin >= 0 ? 0 : xMin - space;
    return d3
        .scaleLinear()
        .range(range)
        .domain([xSpacedMin, xMax + space]);
}


/***/ }),

/***/ "./lib/version.js":
/*!************************!*\
  !*** ./lib/version.js ***!
  \************************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

// Copyright (c) Alexander Rind & the SoniVis team.
// Distributed under the terms of the MIT License (see LICENSE.txt).
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.MODULE_NAME = exports.MODULE_VERSION = void 0;
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
// eslint-disable-next-line @typescript-eslint/no-var-requires
const data = __webpack_require__(/*! ../package.json */ "./package.json");
/**
 * The _model_module_version/_view_module_version this package implements.
 *
 * The html widget manager assumes that this is the same as the npm package
 * version number.
 */
exports.MODULE_VERSION = data.version;
/*
 * The current package name.
 */
exports.MODULE_NAME = data.name;


/***/ }),

/***/ "./lib/widget.js":
/*!***********************!*\
  !*** ./lib/widget.js ***!
  \***********************/
/***/ ((__unused_webpack_module, exports, __webpack_require__) => {

"use strict";

// Copyright (c) Alexander Rind & the SoniVis team.
// Distributed under the terms of the MIT License (see LICENSE.txt).
Object.defineProperty(exports, "__esModule", ({ value: true }));
exports.LensView = exports.LensModel = void 0;
const base_1 = __webpack_require__(/*! @jupyter-widgets/base */ "webpack/sharing/consume/default/@jupyter-widgets/base");
const version_1 = __webpack_require__(/*! ./version */ "./lib/version.js");
// Import the CSS
__webpack_require__(/*! ../css/widget.css */ "./css/widget.css");
const scatterPlot_1 = __webpack_require__(/*! ./scatterPlot */ "./lib/scatterPlot.js");
class LensModel extends base_1.DOMWidgetModel {
    defaults() {
        return Object.assign(Object.assign({}, super.defaults()), { _model_name: LensModel.model_name, _model_module: LensModel.model_module, _model_module_version: LensModel.model_module_version, _view_name: LensModel.view_name, _view_module: LensModel.view_module, _view_module_version: LensModel.view_module_version, x_field: '', y_field: '', _marks_x: [], _marks_y: [], size: 0.1, shape: 'circle', width: 500, height: 500 });
    }
}
exports.LensModel = LensModel;
LensModel.serializers = Object.assign({}, base_1.DOMWidgetModel.serializers);
LensModel.model_name = 'LensModel';
LensModel.model_module = version_1.MODULE_NAME;
LensModel.model_module_version = version_1.MODULE_VERSION;
LensModel.view_name = 'LensView'; // Set to null if no view
LensModel.view_module = version_1.MODULE_NAME; // Set to null if no view
LensModel.view_module_version = version_1.MODULE_VERSION;
class LensView extends base_1.DOMWidgetView {
    // private scatterPlot: ScatterPlot;
    render() {
        // this.scatterPlot =
        new scatterPlot_1.ScatterPlot(this);
    }
}
exports.LensView = LensView;


/***/ }),

/***/ "./node_modules/css-loader/dist/runtime/api.js":
/*!*****************************************************!*\
  !*** ./node_modules/css-loader/dist/runtime/api.js ***!
  \*****************************************************/
/***/ ((module) => {

"use strict";


/*
  MIT License http://www.opensource.org/licenses/mit-license.php
  Author Tobias Koppers @sokra
*/
module.exports = function (cssWithMappingToString) {
  var list = [];

  // return the list of modules as css string
  list.toString = function toString() {
    return this.map(function (item) {
      var content = "";
      var needLayer = typeof item[5] !== "undefined";
      if (item[4]) {
        content += "@supports (".concat(item[4], ") {");
      }
      if (item[2]) {
        content += "@media ".concat(item[2], " {");
      }
      if (needLayer) {
        content += "@layer".concat(item[5].length > 0 ? " ".concat(item[5]) : "", " {");
      }
      content += cssWithMappingToString(item);
      if (needLayer) {
        content += "}";
      }
      if (item[2]) {
        content += "}";
      }
      if (item[4]) {
        content += "}";
      }
      return content;
    }).join("");
  };

  // import a list of modules into the list
  list.i = function i(modules, media, dedupe, supports, layer) {
    if (typeof modules === "string") {
      modules = [[null, modules, undefined]];
    }
    var alreadyImportedModules = {};
    if (dedupe) {
      for (var k = 0; k < this.length; k++) {
        var id = this[k][0];
        if (id != null) {
          alreadyImportedModules[id] = true;
        }
      }
    }
    for (var _k = 0; _k < modules.length; _k++) {
      var item = [].concat(modules[_k]);
      if (dedupe && alreadyImportedModules[item[0]]) {
        continue;
      }
      if (typeof layer !== "undefined") {
        if (typeof item[5] === "undefined") {
          item[5] = layer;
        } else {
          item[1] = "@layer".concat(item[5].length > 0 ? " ".concat(item[5]) : "", " {").concat(item[1], "}");
          item[5] = layer;
        }
      }
      if (media) {
        if (!item[2]) {
          item[2] = media;
        } else {
          item[1] = "@media ".concat(item[2], " {").concat(item[1], "}");
          item[2] = media;
        }
      }
      if (supports) {
        if (!item[4]) {
          item[4] = "".concat(supports);
        } else {
          item[1] = "@supports (".concat(item[4], ") {").concat(item[1], "}");
          item[4] = supports;
        }
      }
      list.push(item);
    }
  };
  return list;
};

/***/ }),

/***/ "./node_modules/css-loader/dist/runtime/sourceMaps.js":
/*!************************************************************!*\
  !*** ./node_modules/css-loader/dist/runtime/sourceMaps.js ***!
  \************************************************************/
/***/ ((module) => {

"use strict";


module.exports = function (item) {
  var content = item[1];
  var cssMapping = item[3];
  if (!cssMapping) {
    return content;
  }
  if (typeof btoa === "function") {
    var base64 = btoa(unescape(encodeURIComponent(JSON.stringify(cssMapping))));
    var data = "sourceMappingURL=data:application/json;charset=utf-8;base64,".concat(base64);
    var sourceMapping = "/*# ".concat(data, " */");
    return [content].concat([sourceMapping]).join("\n");
  }
  return [content].join("\n");
};

/***/ }),

/***/ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js":
/*!****************************************************************************!*\
  !*** ./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js ***!
  \****************************************************************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

"use strict";


var isOldIE = function isOldIE() {
  var memo;
  return function memorize() {
    if (typeof memo === 'undefined') {
      // Test for IE <= 9 as proposed by Browserhacks
      // @see http://browserhacks.com/#hack-e71d8692f65334173fee715c222cb805
      // Tests for existence of standard globals is to allow style-loader
      // to operate correctly into non-standard environments
      // @see https://github.com/webpack-contrib/style-loader/issues/177
      memo = Boolean(window && document && document.all && !window.atob);
    }

    return memo;
  };
}();

var getTarget = function getTarget() {
  var memo = {};
  return function memorize(target) {
    if (typeof memo[target] === 'undefined') {
      var styleTarget = document.querySelector(target); // Special case to return head of iframe instead of iframe itself

      if (window.HTMLIFrameElement && styleTarget instanceof window.HTMLIFrameElement) {
        try {
          // This will throw an exception if access to iframe is blocked
          // due to cross-origin restrictions
          styleTarget = styleTarget.contentDocument.head;
        } catch (e) {
          // istanbul ignore next
          styleTarget = null;
        }
      }

      memo[target] = styleTarget;
    }

    return memo[target];
  };
}();

var stylesInDom = [];

function getIndexByIdentifier(identifier) {
  var result = -1;

  for (var i = 0; i < stylesInDom.length; i++) {
    if (stylesInDom[i].identifier === identifier) {
      result = i;
      break;
    }
  }

  return result;
}

function modulesToDom(list, options) {
  var idCountMap = {};
  var identifiers = [];

  for (var i = 0; i < list.length; i++) {
    var item = list[i];
    var id = options.base ? item[0] + options.base : item[0];
    var count = idCountMap[id] || 0;
    var identifier = "".concat(id, " ").concat(count);
    idCountMap[id] = count + 1;
    var index = getIndexByIdentifier(identifier);
    var obj = {
      css: item[1],
      media: item[2],
      sourceMap: item[3]
    };

    if (index !== -1) {
      stylesInDom[index].references++;
      stylesInDom[index].updater(obj);
    } else {
      stylesInDom.push({
        identifier: identifier,
        updater: addStyle(obj, options),
        references: 1
      });
    }

    identifiers.push(identifier);
  }

  return identifiers;
}

function insertStyleElement(options) {
  var style = document.createElement('style');
  var attributes = options.attributes || {};

  if (typeof attributes.nonce === 'undefined') {
    var nonce =  true ? __webpack_require__.nc : 0;

    if (nonce) {
      attributes.nonce = nonce;
    }
  }

  Object.keys(attributes).forEach(function (key) {
    style.setAttribute(key, attributes[key]);
  });

  if (typeof options.insert === 'function') {
    options.insert(style);
  } else {
    var target = getTarget(options.insert || 'head');

    if (!target) {
      throw new Error("Couldn't find a style target. This probably means that the value for the 'insert' parameter is invalid.");
    }

    target.appendChild(style);
  }

  return style;
}

function removeStyleElement(style) {
  // istanbul ignore if
  if (style.parentNode === null) {
    return false;
  }

  style.parentNode.removeChild(style);
}
/* istanbul ignore next  */


var replaceText = function replaceText() {
  var textStore = [];
  return function replace(index, replacement) {
    textStore[index] = replacement;
    return textStore.filter(Boolean).join('\n');
  };
}();

function applyToSingletonTag(style, index, remove, obj) {
  var css = remove ? '' : obj.media ? "@media ".concat(obj.media, " {").concat(obj.css, "}") : obj.css; // For old IE

  /* istanbul ignore if  */

  if (style.styleSheet) {
    style.styleSheet.cssText = replaceText(index, css);
  } else {
    var cssNode = document.createTextNode(css);
    var childNodes = style.childNodes;

    if (childNodes[index]) {
      style.removeChild(childNodes[index]);
    }

    if (childNodes.length) {
      style.insertBefore(cssNode, childNodes[index]);
    } else {
      style.appendChild(cssNode);
    }
  }
}

function applyToTag(style, options, obj) {
  var css = obj.css;
  var media = obj.media;
  var sourceMap = obj.sourceMap;

  if (media) {
    style.setAttribute('media', media);
  } else {
    style.removeAttribute('media');
  }

  if (sourceMap && typeof btoa !== 'undefined') {
    css += "\n/*# sourceMappingURL=data:application/json;base64,".concat(btoa(unescape(encodeURIComponent(JSON.stringify(sourceMap)))), " */");
  } // For old IE

  /* istanbul ignore if  */


  if (style.styleSheet) {
    style.styleSheet.cssText = css;
  } else {
    while (style.firstChild) {
      style.removeChild(style.firstChild);
    }

    style.appendChild(document.createTextNode(css));
  }
}

var singleton = null;
var singletonCounter = 0;

function addStyle(obj, options) {
  var style;
  var update;
  var remove;

  if (options.singleton) {
    var styleIndex = singletonCounter++;
    style = singleton || (singleton = insertStyleElement(options));
    update = applyToSingletonTag.bind(null, style, styleIndex, false);
    remove = applyToSingletonTag.bind(null, style, styleIndex, true);
  } else {
    style = insertStyleElement(options);
    update = applyToTag.bind(null, style, options);

    remove = function remove() {
      removeStyleElement(style);
    };
  }

  update(obj);
  return function updateStyle(newObj) {
    if (newObj) {
      if (newObj.css === obj.css && newObj.media === obj.media && newObj.sourceMap === obj.sourceMap) {
        return;
      }

      update(obj = newObj);
    } else {
      remove();
    }
  };
}

module.exports = function (list, options) {
  options = options || {}; // Force single-tag solution on IE6-9, which has a hard limit on the # of <style>
  // tags it will allow on a page

  if (!options.singleton && typeof options.singleton !== 'boolean') {
    options.singleton = isOldIE();
  }

  list = list || [];
  var lastIdentifiers = modulesToDom(list, options);
  return function update(newList) {
    newList = newList || [];

    if (Object.prototype.toString.call(newList) !== '[object Array]') {
      return;
    }

    for (var i = 0; i < lastIdentifiers.length; i++) {
      var identifier = lastIdentifiers[i];
      var index = getIndexByIdentifier(identifier);
      stylesInDom[index].references--;
    }

    var newLastIdentifiers = modulesToDom(newList, options);

    for (var _i = 0; _i < lastIdentifiers.length; _i++) {
      var _identifier = lastIdentifiers[_i];

      var _index = getIndexByIdentifier(_identifier);

      if (stylesInDom[_index].references === 0) {
        stylesInDom[_index].updater();

        stylesInDom.splice(_index, 1);
      }
    }

    lastIdentifiers = newLastIdentifiers;
  };
};

/***/ }),

/***/ "./css/widget.css":
/*!************************!*\
  !*** ./css/widget.css ***!
  \************************/
/***/ ((module, __unused_webpack_exports, __webpack_require__) => {

var api = __webpack_require__(/*! !../node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js */ "./node_modules/style-loader/dist/runtime/injectStylesIntoStyleTag.js");
            var content = __webpack_require__(/*! !!../node_modules/css-loader/dist/cjs.js!./widget.css */ "./node_modules/css-loader/dist/cjs.js!./css/widget.css");

            content = content.__esModule ? content.default : content;

            if (typeof content === 'string') {
              content = [[module.id, content, '']];
            }

var options = {};

options.insert = "head";
options.singleton = false;

var update = api(content, options);



module.exports = content.locals || {};

/***/ }),

/***/ "./package.json":
/*!**********************!*\
  !*** ./package.json ***!
  \**********************/
/***/ ((module) => {

"use strict";
module.exports = JSON.parse('{"name":"soniscope-jupyter","version":"0.1.6","description":"jupyter notebook widget with a scatter plot and an interactive lens to enable interactive sonification","keywords":["jupyter","jupyterlab","jupyterlab-extension","widgets"],"files":["lib/**/*.js","dist/*.js","css/*.css"],"homepage":"https://github.com/fhstp/soniscope-jupyter","bugs":{"url":"https://github.com/fhstp/soniscope-jupyter/issues"},"license":"MIT","author":{"name":"Alexander Rind","url":"https://github.com/alex-rind/"},"contributors":["Kajetan Enge","SoniVis project (https://research.fhstp.ac.at/en/projects/sonivis-data-analytics-using-sonification-and-visualization)"],"main":"lib/index.js","types":"./lib/index.d.ts","repository":{"type":"git","url":"https://github.com/fhstp/soniscope-jupyter"},"scripts":{"build":"npm run build:lib && npm run build:nbextension:dev && npm run build:labextension:dev","build:prod":"npm run build:lib && npm run build:nbextension && npm run build:labextension","build:labextension":"jupyter labextension build .","build:labextension:dev":"jupyter labextension build --development True .","build:lib":"tsc","build:nbextension":"webpack --mode=production","build:nbextension:dev":"webpack --mode=development","clean":"npm run clean:lib && npm run clean:nbextension && npm run clean:labextension","clean:lib":"rimraf lib","clean:labextension":"rimraf soniscope_jupyter/labextension","clean:nbextension":"rimraf soniscope_jupyter/nbextension/static/index.js","lint":"eslint . --ext .ts,.tsx --fix","lint:check":"eslint . --ext .ts,.tsx","prepack":"npm run build:lib","test":"jest","watch":"npm-run-all -p watch:*","watch:lib":"tsc -w","watch:nbextension":"webpack --watch --mode=development","watch:labextension":"jupyter labextension watch ."},"dependencies":{"@jupyter-widgets/base":"^1.1.10 || ^2.0.0 || ^3.0.0 || ^4.0.0","d3":"^7.2.1"},"devDependencies":{"@babel/core":"^7.5.0","@babel/preset-env":"^7.5.0","@jupyterlab/builder":"^3.6.5","@lumino/application":"^1.6.0","@lumino/widgets":"^1.6.0","@types/d3":"^7.1.0","@types/jest":"^26.0.0","@types/webpack-env":"^1.13.6","@typescript-eslint/eslint-plugin":"^3.6.0","@typescript-eslint/parser":"^3.6.0","acorn":"^7.2.0","css-loader":"^6.5.1","eslint":"^7.4.0","eslint-config-prettier":"^6.11.0","eslint-plugin-prettier":"^3.1.4","fs-extra":"^7.0.0","identity-obj-proxy":"^3.0.0","jest":"^26.0.0","mkdirp":"^0.5.1","npm-run-all":"^4.1.3","prettier":"^2.0.5","rimraf":"^2.6.2","source-map-loader":"^1.1.3","style-loader":"^1.0.0","ts-jest":"^26.0.0","ts-loader":"^8.0.0","typescript":"~4.1.3","webpack":"^5.0.0","webpack-cli":"^4.0.0"},"jupyterlab":{"extension":"lib/plugin","outputDir":"soniscope_jupyter/labextension/","sharedPackages":{"@jupyter-widgets/base":{"bundled":false,"singleton":true}}}}');

/***/ })

}]);
//# sourceMappingURL=lib_widget_js.b85532dd416c2b73b29b.js.map