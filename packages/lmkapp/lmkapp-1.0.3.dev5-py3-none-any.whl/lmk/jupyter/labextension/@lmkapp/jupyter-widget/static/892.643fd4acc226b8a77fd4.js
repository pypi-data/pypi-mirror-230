"use strict";(self.webpackChunk_lmkapp_jupyter_widget=self.webpackChunk_lmkapp_jupyter_widget||[]).push([[892],{892:(t,n,e)=>{let r;e.r(n),e.d(n,{NIL:()=>S,parse:()=>g,stringify:()=>l,v1:()=>y,v3:()=>C,v4:()=>R,v5:()=>M,validate:()=>i,version:()=>T});const o=new Uint8Array(16);function c(){if(!r&&(r="undefined"!=typeof crypto&&crypto.getRandomValues&&crypto.getRandomValues.bind(crypto),!r))throw new Error("crypto.getRandomValues() not supported. See https://github.com/uuidjs/uuid#getrandomvalues-not-supported");return r(o)}const s=/^(?:[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}|00000000-0000-0000-0000-000000000000)$/i,i=function(t){return"string"==typeof t&&s.test(t)},u=[];for(let t=0;t<256;++t)u.push((t+256).toString(16).slice(1));function a(t,n=0){return(u[t[n+0]]+u[t[n+1]]+u[t[n+2]]+u[t[n+3]]+"-"+u[t[n+4]]+u[t[n+5]]+"-"+u[t[n+6]]+u[t[n+7]]+"-"+u[t[n+8]]+u[t[n+9]]+"-"+u[t[n+10]]+u[t[n+11]]+u[t[n+12]]+u[t[n+13]]+u[t[n+14]]+u[t[n+15]]).toLowerCase()}const l=function(t,n=0){const e=a(t,n);if(!i(e))throw TypeError("Stringified UUID is invalid");return e};let f,p,d=0,h=0;const y=function(t,n,e){let r=n&&e||0;const o=n||new Array(16);let s=(t=t||{}).node||f,i=void 0!==t.clockseq?t.clockseq:p;if(null==s||null==i){const n=t.random||(t.rng||c)();null==s&&(s=f=[1|n[0],n[1],n[2],n[3],n[4],n[5]]),null==i&&(i=p=16383&(n[6]<<8|n[7]))}let u=void 0!==t.msecs?t.msecs:Date.now(),l=void 0!==t.nsecs?t.nsecs:h+1;const y=u-d+(l-h)/1e4;if(y<0&&void 0===t.clockseq&&(i=i+1&16383),(y<0||u>d)&&void 0===t.nsecs&&(l=0),l>=1e4)throw new Error("uuid.v1(): Can't create more than 10M uuids/sec");d=u,h=l,p=i,u+=122192928e5;const g=(1e4*(268435455&u)+l)%4294967296;o[r++]=g>>>24&255,o[r++]=g>>>16&255,o[r++]=g>>>8&255,o[r++]=255&g;const U=u/4294967296*1e4&268435455;o[r++]=U>>>8&255,o[r++]=255&U,o[r++]=U>>>24&15|16,o[r++]=U>>>16&255,o[r++]=i>>>8|128,o[r++]=255&i;for(let t=0;t<6;++t)o[r+t]=s[t];return n||a(o)},g=function(t){if(!i(t))throw TypeError("Invalid UUID");let n;const e=new Uint8Array(16);return e[0]=(n=parseInt(t.slice(0,8),16))>>>24,e[1]=n>>>16&255,e[2]=n>>>8&255,e[3]=255&n,e[4]=(n=parseInt(t.slice(9,13),16))>>>8,e[5]=255&n,e[6]=(n=parseInt(t.slice(14,18),16))>>>8,e[7]=255&n,e[8]=(n=parseInt(t.slice(19,23),16))>>>8,e[9]=255&n,e[10]=(n=parseInt(t.slice(24,36),16))/1099511627776&255,e[11]=n/4294967296&255,e[12]=n>>>24&255,e[13]=n>>>16&255,e[14]=n>>>8&255,e[15]=255&n,e};function U(t,n,e){function r(t,r,o,c){var s;if("string"==typeof t&&(t=function(t){t=unescape(encodeURIComponent(t));const n=[];for(let e=0;e<t.length;++e)n.push(t.charCodeAt(e));return n}(t)),"string"==typeof r&&(r=g(r)),16!==(null===(s=r)||void 0===s?void 0:s.length))throw TypeError("Namespace must be array-like (16 iterable integer values, 0-255)");let i=new Uint8Array(16+t.length);if(i.set(r),i.set(t,r.length),i=e(i),i[6]=15&i[6]|n,i[8]=63&i[8]|128,o){c=c||0;for(let t=0;t<16;++t)o[c+t]=i[t];return o}return a(i)}try{r.name=t}catch(t){}return r.DNS="6ba7b810-9dad-11d1-80b4-00c04fd430c8",r.URL="6ba7b811-9dad-11d1-80b4-00c04fd430c8",r}function w(t){return 14+(t+64>>>9<<4)+1}function m(t,n){const e=(65535&t)+(65535&n);return(t>>16)+(n>>16)+(e>>16)<<16|65535&e}function v(t,n,e,r,o,c){return m((s=m(m(n,t),m(r,c)))<<(i=o)|s>>>32-i,e);var s,i}function I(t,n,e,r,o,c,s){return v(n&e|~n&r,t,n,o,c,s)}function A(t,n,e,r,o,c,s){return v(n&r|e&~r,t,n,o,c,s)}function b(t,n,e,r,o,c,s){return v(n^e^r,t,n,o,c,s)}function k(t,n,e,r,o,c,s){return v(e^(n|~r),t,n,o,c,s)}const C=U("v3",48,(function(t){if("string"==typeof t){const n=unescape(encodeURIComponent(t));t=new Uint8Array(n.length);for(let e=0;e<n.length;++e)t[e]=n.charCodeAt(e)}return function(t){const n=[],e=32*t.length,r="0123456789abcdef";for(let o=0;o<e;o+=8){const e=t[o>>5]>>>o%32&255,c=parseInt(r.charAt(e>>>4&15)+r.charAt(15&e),16);n.push(c)}return n}(function(t,n){t[n>>5]|=128<<n%32,t[w(n)-1]=n;let e=1732584193,r=-271733879,o=-1732584194,c=271733878;for(let n=0;n<t.length;n+=16){const s=e,i=r,u=o,a=c;e=I(e,r,o,c,t[n],7,-680876936),c=I(c,e,r,o,t[n+1],12,-389564586),o=I(o,c,e,r,t[n+2],17,606105819),r=I(r,o,c,e,t[n+3],22,-1044525330),e=I(e,r,o,c,t[n+4],7,-176418897),c=I(c,e,r,o,t[n+5],12,1200080426),o=I(o,c,e,r,t[n+6],17,-1473231341),r=I(r,o,c,e,t[n+7],22,-45705983),e=I(e,r,o,c,t[n+8],7,1770035416),c=I(c,e,r,o,t[n+9],12,-1958414417),o=I(o,c,e,r,t[n+10],17,-42063),r=I(r,o,c,e,t[n+11],22,-1990404162),e=I(e,r,o,c,t[n+12],7,1804603682),c=I(c,e,r,o,t[n+13],12,-40341101),o=I(o,c,e,r,t[n+14],17,-1502002290),r=I(r,o,c,e,t[n+15],22,1236535329),e=A(e,r,o,c,t[n+1],5,-165796510),c=A(c,e,r,o,t[n+6],9,-1069501632),o=A(o,c,e,r,t[n+11],14,643717713),r=A(r,o,c,e,t[n],20,-373897302),e=A(e,r,o,c,t[n+5],5,-701558691),c=A(c,e,r,o,t[n+10],9,38016083),o=A(o,c,e,r,t[n+15],14,-660478335),r=A(r,o,c,e,t[n+4],20,-405537848),e=A(e,r,o,c,t[n+9],5,568446438),c=A(c,e,r,o,t[n+14],9,-1019803690),o=A(o,c,e,r,t[n+3],14,-187363961),r=A(r,o,c,e,t[n+8],20,1163531501),e=A(e,r,o,c,t[n+13],5,-1444681467),c=A(c,e,r,o,t[n+2],9,-51403784),o=A(o,c,e,r,t[n+7],14,1735328473),r=A(r,o,c,e,t[n+12],20,-1926607734),e=b(e,r,o,c,t[n+5],4,-378558),c=b(c,e,r,o,t[n+8],11,-2022574463),o=b(o,c,e,r,t[n+11],16,1839030562),r=b(r,o,c,e,t[n+14],23,-35309556),e=b(e,r,o,c,t[n+1],4,-1530992060),c=b(c,e,r,o,t[n+4],11,1272893353),o=b(o,c,e,r,t[n+7],16,-155497632),r=b(r,o,c,e,t[n+10],23,-1094730640),e=b(e,r,o,c,t[n+13],4,681279174),c=b(c,e,r,o,t[n],11,-358537222),o=b(o,c,e,r,t[n+3],16,-722521979),r=b(r,o,c,e,t[n+6],23,76029189),e=b(e,r,o,c,t[n+9],4,-640364487),c=b(c,e,r,o,t[n+12],11,-421815835),o=b(o,c,e,r,t[n+15],16,530742520),r=b(r,o,c,e,t[n+2],23,-995338651),e=k(e,r,o,c,t[n],6,-198630844),c=k(c,e,r,o,t[n+7],10,1126891415),o=k(o,c,e,r,t[n+14],15,-1416354905),r=k(r,o,c,e,t[n+5],21,-57434055),e=k(e,r,o,c,t[n+12],6,1700485571),c=k(c,e,r,o,t[n+3],10,-1894986606),o=k(o,c,e,r,t[n+10],15,-1051523),r=k(r,o,c,e,t[n+1],21,-2054922799),e=k(e,r,o,c,t[n+8],6,1873313359),c=k(c,e,r,o,t[n+15],10,-30611744),o=k(o,c,e,r,t[n+6],15,-1560198380),r=k(r,o,c,e,t[n+13],21,1309151649),e=k(e,r,o,c,t[n+4],6,-145523070),c=k(c,e,r,o,t[n+11],10,-1120210379),o=k(o,c,e,r,t[n+2],15,718787259),r=k(r,o,c,e,t[n+9],21,-343485551),e=m(e,s),r=m(r,i),o=m(o,u),c=m(c,a)}return[e,r,o,c]}(function(t){if(0===t.length)return[];const n=8*t.length,e=new Uint32Array(w(n));for(let r=0;r<n;r+=8)e[r>>5]|=(255&t[r/8])<<r%32;return e}(t),8*t.length))})),D={randomUUID:"undefined"!=typeof crypto&&crypto.randomUUID&&crypto.randomUUID.bind(crypto)},R=function(t,n,e){if(D.randomUUID&&!n&&!t)return D.randomUUID();const r=(t=t||{}).random||(t.rng||c)();if(r[6]=15&r[6]|64,r[8]=63&r[8]|128,n){e=e||0;for(let t=0;t<16;++t)n[e+t]=r[t];return n}return a(r)};function E(t,n,e,r){switch(t){case 0:return n&e^~n&r;case 1:case 3:return n^e^r;case 2:return n&e^n&r^e&r}}function _(t,n){return t<<n|t>>>32-n}const M=U("v5",80,(function(t){const n=[1518500249,1859775393,2400959708,3395469782],e=[1732584193,4023233417,2562383102,271733878,3285377520];if("string"==typeof t){const n=unescape(encodeURIComponent(t));t=[];for(let e=0;e<n.length;++e)t.push(n.charCodeAt(e))}else Array.isArray(t)||(t=Array.prototype.slice.call(t));t.push(128);const r=t.length/4+2,o=Math.ceil(r/16),c=new Array(o);for(let n=0;n<o;++n){const e=new Uint32Array(16);for(let r=0;r<16;++r)e[r]=t[64*n+4*r]<<24|t[64*n+4*r+1]<<16|t[64*n+4*r+2]<<8|t[64*n+4*r+3];c[n]=e}c[o-1][14]=8*(t.length-1)/Math.pow(2,32),c[o-1][14]=Math.floor(c[o-1][14]),c[o-1][15]=8*(t.length-1)&4294967295;for(let t=0;t<o;++t){const r=new Uint32Array(80);for(let n=0;n<16;++n)r[n]=c[t][n];for(let t=16;t<80;++t)r[t]=_(r[t-3]^r[t-8]^r[t-14]^r[t-16],1);let o=e[0],s=e[1],i=e[2],u=e[3],a=e[4];for(let t=0;t<80;++t){const e=Math.floor(t/20),c=_(o,5)+E(e,s,i,u)+a+n[e]+r[t]>>>0;a=u,u=i,i=_(s,30)>>>0,s=o,o=c}e[0]=e[0]+o>>>0,e[1]=e[1]+s>>>0,e[2]=e[2]+i>>>0,e[3]=e[3]+u>>>0,e[4]=e[4]+a>>>0}return[e[0]>>24&255,e[0]>>16&255,e[0]>>8&255,255&e[0],e[1]>>24&255,e[1]>>16&255,e[1]>>8&255,255&e[1],e[2]>>24&255,e[2]>>16&255,e[2]>>8&255,255&e[2],e[3]>>24&255,e[3]>>16&255,e[3]>>8&255,255&e[3],e[4]>>24&255,e[4]>>16&255,e[4]>>8&255,255&e[4]]})),S="00000000-0000-0000-0000-000000000000",T=function(t){if(!i(t))throw TypeError("Invalid UUID");return parseInt(t.slice(14,15),16)}}}]);