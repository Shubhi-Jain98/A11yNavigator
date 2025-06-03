'use strict';

/******************************************************************************
Copyright (c) Microsoft Corporation.

Permission to use, copy, modify, and/or distribute this software for any
purpose with or without fee is hereby granted.

THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH
REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY
AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT,
INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM
LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR
OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR
PERFORMANCE OF THIS SOFTWARE.
***************************************************************************** */
/* global Reflect, Promise, SuppressedError, Symbol */
var __assign=function(){return __assign=Object.assign||function(e){for(var t,r=1,n=arguments.length;r<n;r++)for(var o in t=arguments[r])Object.prototype.hasOwnProperty.call(t,o)&&(e[o]=t[o]);return e},__assign.apply(this,arguments)};function __awaiter(e,t,r,n){return new(r||(r=Promise))((function(o,a){function i(e){try{s(n.next(e));}catch(e){a(e);}}function c(e){try{s(n.throw(e));}catch(e){a(e);}}function s(e){var t;e.done?o(e.value):(t=e.value,t instanceof r?t:new r((function(e){e(t);}))).then(i,c);}s((n=n.apply(e,t||[])).next());}))}function __generator(e,t){var r,n,o,a,i={label:0,sent:function(){if(1&o[0])throw o[1];return o[1]},trys:[],ops:[]};return a={next:c(0),throw:c(1),return:c(2)},"function"==typeof Symbol&&(a[Symbol.iterator]=function(){return this}),a;function c(c){return function(s){return function(c){if(r)throw new TypeError("Generator is already executing.");for(;a&&(a=0,c[0]&&(i=0)),i;)try{if(r=1,n&&(o=2&c[0]?n.return:c[0]?n.throw||((o=n.return)&&o.call(n),0):n.next)&&!(o=o.call(n,c[1])).done)return o;switch(n=0,o&&(c=[2&c[0],o.value]),c[0]){case 0:case 1:o=c;break;case 4:return i.label++,{value:c[1],done:!1};case 5:i.label++,n=c[1],c=[0];continue;case 7:c=i.ops.pop(),i.trys.pop();continue;default:if(!(o=i.trys,(o=o.length>0&&o[o.length-1])||6!==c[0]&&2!==c[0])){i=0;continue}if(3===c[0]&&(!o||c[1]>o[0]&&c[1]<o[3])){i.label=c[1];break}if(6===c[0]&&i.label<o[1]){i.label=o[1],o=c;break}if(o&&i.label<o[2]){i.label=o[2],i.ops.push(c);break}o[2]&&i.ops.pop(),i.trys.pop();continue}c=t.call(e,i);}catch(e){c=[6,e],n=0;}finally{r=o=0;}if(5&c[0])throw c[1];return {value:c[0]?c[1]:void 0,done:!0}}([c,s])}}}"function"==typeof SuppressedError?SuppressedError:function(e,t,r){var n=new Error(r);return n.name="SuppressedError",n.error=e,n.suppressed=t,n};

var getCookieObject=function(t){for(var e="".concat(t,"="),o=0,r=decodeURIComponent(document.cookie).split(";");o<r.length;o++){for(var n=r[o];n.startsWith(" ");)n=n.slice(1);if(n.startsWith(e))return n.substring(e.length,n.length)}return null};var getCookieObjectStartWith=function(t){for(var e=t,o=0,r=decodeURIComponent(document.cookie).split(";");o<r.length;o++){for(var n=r[o];n.startsWith(" ");)n=n.slice(1);if(n.startsWith(e))return null==n?void 0:n.split("=")}return null};

var _getAnonymousId=function(t){var e;if(!t)return "";var r="_evga_";var o=getCookieObjectStartWith(r);return !o||o.length<=1?"":null!==(e=JSON.parse(o[1]).uuid)&&void 0!==e?e:""};

var parseJwt=function(e){var r=e.split(".")[1];if(!r)return {persistentId:""};var t=r.replace(/-/g,"+").replace(/_/g,"/"),n=decodeURIComponent(window.atob(t).split("").map((function(e){return "%"+("00"+e.charCodeAt(0).toString(16)).slice(-2)})).join(""));return JSON.parse(n)};

var _getPersistentId=function(e){if(!e)return "";var t=getCookieObject("mc_token");if(e&&t){var r=parseJwt(t);return null==r?void 0:r.persistentId}return ""};

var getData=function(t){return __awaiter(void 0,[t],void 0,(function(t){var e,a,n,o=t.baseURL,r=t.endPoint,i=t.apiKey,s=t.extraHeaders,c=t.timeout,_=void 0===c?8e3:c;return __generator(this,(function(t){switch(t.label){case 0:return e=__assign({apikey:i,"Content-Type":"application/json"},s),a=parseInt("".concat(_)),[4/*yield*/,fetch("".concat(o).concat(r),{headers:e,method:"POST",body:"{}",signal:AbortSignal.timeout(a)})];case 1:return (n=t.sent()).ok||console.error(n.status,n.statusText),[2/*return*/,n.json()]}}))}))};

var getCookieDomain=function(){var o;return null!==(o="formula1.com")?o:"formula1.com"};

var setCookieObject=function(o,e,t){var n,a=getCookieDomain();// 24h
t?// The 0 there is the key, which sets the date to the epoch
(n=new Date(0)).setUTCSeconds(t):(n=new Date).setTime(n.getTime()+864e5);var c="expires=".concat(n.toUTCString());document.cookie="".concat(o,"=").concat(e,";").concat(c,";Domain=").concat(a,";path=/");};

// TODO: Add time out 
var _createMarketingTokenCookie=function(e,t,r){return __awaiter(void 0,void 0,void 0,(function(){var o,i,n,a,s,k,u,c,m;return __generator(this,(function(g){switch(g.label){case 0:if(!e)return [2/*return*/,""];if(!(o=getCookieObject("login-session")))return [2/*return*/,""];if(i=JSON.parse(o),!(n=null===(m=null==i?void 0:i.data)||void 0===m?void 0:m.subscriptionToken))return [2/*return*/,""];if(!(a="/v1/marketing/marketing-token"))return [2/*return*/,""];s="5000",g.label=1;case 1:return g.trys.push([1,3,,4]),[4/*yield*/,getData({baseURL:t,endPoint:a,apiKey:r,extraHeaders:{Authorization:n},timeout:s})];case 2:return (null==(k=g.sent())?void 0:k.marketingToken)?(u=parseJwt(k.marketingToken),setCookieObject("mk-token",k.marketingToken,null==u?void 0:u.exp),[2/*return*/,u.persistentId]):[2/*return*/,""];case 3:return c=g.sent(),console.error(c),[2/*return*/,""];case 4:return [2/*return*/]}}))}))};

var removeCookieObject=function(o){document.cookie=o+"=;expires=Thu, 01 Jan 1970 00:00:01 GMT;Domain="+getCookieDomain()+";path=/";};

var _clearMarketingTokenCookie=function(){var e="mk-token";removeCookieObject(e);};

var _clearSalesforceCookie=function(){var e="_evga_";var o=getCookieObjectStartWith(e);if(!o||o.length<=1)return "";JSON.parse(o[1]).uuid&&removeCookieObject(o[0]);};

var _getF1Identifiers=function(e,o,t,r,i){return __awaiter(void 0,void 0,void 0,(function(){var t;return __generator(this,(function(n){return t={anonymousID:"",persistentID:""},[2/*return*/,new Promise((function(n){o?t.anonymousID=_getAnonymousId(o):o||_clearSalesforceCookie();var a=getCookieObject("login-session"),s=getCookieObject("mc_token");e&&a&&s?(t.persistentID=_getPersistentId(e),n(t)):e&&a?_createMarketingTokenCookie(e,r,i).then((function(e){t.persistentID=e,n(t);})):(e||_clearMarketingTokenCookie(),n(t));}))]}))}))};

/* @preserve */var MKSDK;!function(e){e.getAnonymousId=function(e){return _getAnonymousId(e)},e.getPersistentId=function(e){return _getPersistentId(e)},e.createMarketingTokenCookie=function(e,r,o){return __awaiter(this,void 0,void 0,(function(){return __generator(this,(function(t){switch(t.label){case 0:return [4/*yield*/,_createMarketingTokenCookie(e,r,o)];case 1:return [2/*return*/,t.sent()]}}))}))},e.clearMarketingTokenCookie=function(){_clearMarketingTokenCookie();},e.clearSalesforceCookie=function(){_clearSalesforceCookie();},e.getF1Identifiers=function(e,r,o,t,n){return _getF1Identifiers(e,r,o,t,n)};}(MKSDK||(MKSDK={}));
