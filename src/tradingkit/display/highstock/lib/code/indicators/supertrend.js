/*
 Highstock JS v8.0.4 (2020-03-10)

 Indicator series type for Highstock

 (c) 2010-2019 Wojciech Chmiel

 License: www.highcharts.com/license
*/
(function(c){"object"===typeof module&&module.exports?(c["default"]=c,module.exports=c):"function"===typeof define&&define.amd?define("highcharts/indicators/supertrend",["highcharts","highcharts/modules/stock"],function(l){c(l);c.Highcharts=l;return c}):c("undefined"!==typeof Highcharts?Highcharts:void 0)})(function(c){function l(c,m,B,l){c.hasOwnProperty(m)||(c[m]=l.apply(null,B))}c=c?c._modules:{};l(c,"indicators/supertrend.btx.js",[c["parts/Globals.js"],c["parts/Utilities.js"]],function(c,m){function l(d,
b,n){return{index:b,close:d.yData[b][n],x:d.xData[b]}}var z=m.correctFloat,v=m.merge,C=m.seriesType,D=m.isArray,E=m.objectEach,F=c.seriesTypes.atr,A=c.seriesTypes.sma;C("supertrend","sma",{params:{multiplier:3,period:10},risingTrendColor:"#06B535",fallingTrendColor:"#F21313",changeTrendLine:{styles:{lineWidth:1,lineColor:"#333333",dashStyle:"LongDash"}}},{nameBase:"Supertrend",nameComponents:["multiplier","period"],requiredIndicators:["atr"],init:function(){A.prototype.init.apply(this,arguments);
var d=this.options;d.cropThreshold=this.linkedParent.options.cropThreshold-(d.params.period-1)},drawGraph:function(){var d=this,b=d.options,n=d.linkedParent,c=n?n.points:[],y=d.points,m=d.graph,t=y.length,u=c.length-t;u=0<u?u:0;for(var x={options:{gapSize:b.gapSize}},k={top:[],bottom:[],intersect:[]},w={top:{styles:{lineWidth:b.lineWidth,lineColor:b.fallingTrendColor||b.color,dashStyle:b.dashStyle}},bottom:{styles:{lineWidth:b.lineWidth,lineColor:b.risingTrendColor||b.color,dashStyle:b.dashStyle}},
intersect:b.changeTrendLine},a,h,e,f,g,p,q,r;t--;)a=y[t],h=y[t-1],e=c[t-1+u],f=c[t-2+u],g=c[t+u],p=c[t+u+1],q=a.options.color,r={x:a.x,plotX:a.plotX,plotY:a.plotY,isNull:!1},!f&&e&&n.yData[e.index-1]&&(f=l(n,e.index-1,3)),!p&&g&&n.yData[g.index+1]&&(p=l(n,g.index+1,3)),!e&&f&&n.yData[f.index+1]?e=l(n,f.index+1,3):!e&&g&&n.yData[g.index-1]&&(e=l(n,g.index-1,3)),a&&e&&g&&f&&a.x!==e.x&&(a.x===g.x?(f=e,e=g):a.x===f.x?(e=f,f={close:n.yData[e.index-1][3],x:n.xData[e.index-1]}):p&&a.x===p.x&&(e=p,f=g)),
h&&f&&e?(g={x:h.x,plotX:h.plotX,plotY:h.plotY,isNull:!1},a.y>=e.close&&h.y>=f.close?(a.color=q||b.fallingTrendColor||b.color,k.top.push(r)):a.y<e.close&&h.y<f.close?(a.color=q||b.risingTrendColor||b.color,k.bottom.push(r)):(k.intersect.push(r),k.intersect.push(g),k.intersect.push(v(g,{isNull:!0})),a.y>=e.close&&h.y<f.close?(a.color=q||b.fallingTrendColor||b.color,h.color=q||b.risingTrendColor||b.color,k.top.push(r),k.top.push(v(g,{isNull:!0}))):a.y<e.close&&h.y>=f.close&&(a.color=q||b.risingTrendColor||
b.color,h.color=q||b.fallingTrendColor||b.color,k.bottom.push(r),k.bottom.push(v(g,{isNull:!0}))))):e&&(a.y>=e.close?(a.color=q||b.fallingTrendColor||b.color,k.top.push(r)):(a.color=q||b.risingTrendColor||b.color,k.bottom.push(r)));E(k,function(a,b){d.points=a;d.options=v(w[b].styles,x);d.graph=d["graph"+b+"Line"];A.prototype.drawGraph.call(d);d["graph"+b+"Line"]=d.graph});d.points=y;d.options=b;d.graph=m},getValues:function(d,b){var c=b.period;b=b.multiplier;var l=d.xData,m=d.yData,v=[],t=[],u=[],
x=0===c?0:c-1,k=[],w=[],a;if(!(l.length<=c||!D(m[0])||4!==m[0].length||0>c)){d=F.prototype.getValues.call(this,d,{period:c}).yData;for(a=0;a<d.length;a++){var h=m[x+a];var e=m[x+a-1]||[];var f=k[a-1];var g=w[a-1];var p=u[a-1];0===a&&(f=g=p=0);c=z((h[1]+h[2])/2+b*d[a]);var q=z((h[1]+h[2])/2-b*d[a]);k[a]=c<f||e[3]>f?c:f;w[a]=q>g||e[3]<g?q:g;if(p===f&&h[3]<k[a]||p===g&&h[3]<w[a])var r=k[a];else if(p===f&&h[3]>k[a]||p===g&&h[3]>w[a])r=w[a];v.push([l[x+a],r]);t.push(l[x+a]);u.push(r)}return{values:v,xData:t,
yData:u}}}});""});l(c,"masters/indicators/supertrend.btx.js",[],function(){})});
//# sourceMappingURL=supertrend.js.map