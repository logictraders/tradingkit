/*
 Highstock JS v8.0.4 (2020-03-10)

 Indicator series type for Highstock

 (c) 2010-2019 Pawe Fus

 License: www.highcharts.com/license
*/
(function(a){"object"===typeof module&&module.exports?(a["default"]=a,module.exports=a):"function"===typeof define&&define.amd?define("highcharts/indicators/stochastic",["highcharts","highcharts/modules/stock"],function(d){a(d);a.Highcharts=d;return a}):a("undefined"!==typeof Highcharts?Highcharts:void 0)})(function(a){function d(a,b,w,c){a.hasOwnProperty(b)||(a[b]=c.apply(null,w))}a=a?a._modules:{};d(a,"mixins/reduce-array.js",[a["parts/Globals.js"]],function(a){var b=a.reduce;return{minInArray:function(a,
c){return b(a,function(a,b){return Math.min(a,b[c])},Number.MAX_VALUE)},maxInArray:function(a,c){return b(a,function(a,b){return Math.max(a,b[c])},-Number.MAX_VALUE)},getArrayExtremes:function(a,c,d){return b(a,function(a,b){return[Math.min(a[0],b[c]),Math.max(a[1],b[d])]},[Number.MAX_VALUE,-Number.MAX_VALUE])}}});d(a,"mixins/multipe-lines.js",[a["parts/Globals.js"],a["parts/Utilities.js"]],function(a,b){var d=b.defined,c=b.error,t=b.merge,f=a.each,n=a.seriesTypes.sma;return{pointArrayMap:["top",
"bottom"],pointValKey:"top",linesApiNames:["bottomLine"],getTranslatedLinesNames:function(a){var h=[];f(this.pointArrayMap,function(b){b!==a&&h.push("plot"+b.charAt(0).toUpperCase()+b.slice(1))});return h},toYData:function(a){var h=[];f(this.pointArrayMap,function(b){h.push(a[b])});return h},translate:function(){var a=this,b=a.pointArrayMap,e=[],c;e=a.getTranslatedLinesNames();n.prototype.translate.apply(a,arguments);f(a.points,function(h){f(b,function(b,d){c=h[b];null!==c&&(h[e[d]]=a.yAxis.toPixels(c,
!0))})})},drawGraph:function(){var a=this,b=a.linesApiNames,e=a.points,u=e.length,q=a.options,x=a.graph,y={options:{gapSize:q.gapSize}},l=[],m=a.getTranslatedLinesNames(a.pointValKey),g;f(m,function(a,b){for(l[b]=[];u--;)g=e[u],l[b].push({x:g.x,plotX:g.plotX,plotY:g[a],isNull:!d(g[a])});u=e.length});f(b,function(b,e){l[e]?(a.points=l[e],q[b]?a.options=t(q[b].styles,y):c('Error: "There is no '+b+' in DOCS options declared. Check if linesApiNames are consistent with your DOCS line names." at mixin/multiple-line.js:34'),
a.graph=a["graph"+b],n.prototype.drawGraph.call(a),a["graph"+b]=a.graph):c('Error: "'+b+" doesn't have equivalent in pointArrayMap. To many elements in linesApiNames relative to pointArrayMap.\"")});a.points=e;a.options=q;a.graph=x;n.prototype.drawGraph.call(a)}}});d(a,"indicators/stochastic.btx.js",[a["parts/Globals.js"],a["parts/Utilities.js"],a["mixins/reduce-array.js"],a["mixins/multipe-lines.js"]],function(a,b,d,c){var t=b.isArray,f=b.merge;b=b.seriesType;var n=a.seriesTypes.sma,h=d.getArrayExtremes;
b("stochastic","sma",{params:{periods:[14,3]},marker:{enabled:!1},tooltip:{pointFormat:'<span style="color:{point.color}">\u25cf</span><b> {series.name}</b><br/>%K: {point.y}<br/>%D: {point.smoothed}<br/>'},smoothedLine:{styles:{lineWidth:1,lineColor:void 0}},dataGrouping:{approximation:"averages"}},f(c,{nameComponents:["periods"],nameBase:"Stochastic",pointArrayMap:["y","smoothed"],parallelArrays:["x","y","smoothed"],pointValKey:"y",linesApiNames:["smoothedLine"],init:function(){n.prototype.init.apply(this,
arguments);this.options=f({smoothedLine:{styles:{lineColor:this.color}}},this.options)},getValues:function(a,b){var c=b.periods[0];b=b.periods[1];var d=a.xData,e=(a=a.yData)?a.length:0,f=[],l=[],m=[],g=null,k;if(!(e<c)&&t(a[0])&&4===a[0].length){for(k=c-1;k<e;k++){var p=a.slice(k-c+1,k+1);var v=h(p,2,1);var r=v[0];p=a[k][3]-r;r=v[1]-r;p=p/r*100;l.push(d[k]);m.push([p,null]);k>=c-1+(b-1)&&(g=n.prototype.getValues.call(this,{xData:l.slice(-b),yData:m.slice(-b)},{period:b}),g=g.yData[0]);f.push([d[k],
p,g]);m[m.length-1][1]=g}return{values:f,xData:l,yData:m}}}}));""});d(a,"masters/indicators/stochastic.btx.js",[],function(){})});
//# sourceMappingURL=stochastic.js.map