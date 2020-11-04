// © Copyright CERN, Riga Technical University and University of Liverpool 2020.
// All rights not expressly granted are reserved. 
// 
// This file is part of hev-sw.
// 
// hev-sw is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public Licence as published by the Free
// Software Foundation, either version 3 of the Licence, or (at your option)
// any later version.
// 
// hev-sw is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence
// for more details.
// 
// You should have received a copy of the GNU General Public License along
// with hev-sw. If not, see <http://www.gnu.org/licenses/>.
// 
// The authors would like to acknowledge the much appreciated support
// of all those involved with the High Energy Ventilator project
// (https://hev.web.cern.ch/).


// place to hard code chart parameters (can not make a separate .js as import of js not supported)

function chartParam(chartName) {
    // values for all plots
    let gridColor     = "hsla(0, 0%, 75%, 0.4)"; 
    let zeroGridColor = "hsla(0, 0%, 90%, 1.0)"; 

    // values for specific plots
    let plotColor;    
    // chosen to have the same saturation and luminosity, tweak to taste
    if( chartName == "pressure" ) plotColor = "hsla(240, 100%, 75%, 1)";
    if( chartName == "flow" )     plotColor = "hsla(114, 100%, 75%, 1)";
    if( chartName == "volume" )   plotColor = "hsla(  0, 100%, 75%, 1)";

    // start with global params for all plots
    let params = {
	dataset : {
	    borderColor          : plotColor,
	    backgroundColor      : plotColor,
	    borderWidth          : 4,
	    fill                 : false,
	    showLine             : true
	},
	gridLines : {
	    display       : true,
	    color         : gridColor,
	    zeroLineColor : zeroGridColor
	}
    };

    return params;
}

var chart_pressure;
var chart_flow;
var chart_volume;

var size_data;

var fio_reading;
var p_plateau_reading;

var current_timestamp = -1;

function setChartXaxisRange(min,max){
    chart_volume.options.scales.xAxes[0].ticks.min = min;
    chart_volume.options.scales.xAxes[0].ticks.max = max;
    chart_flow.options.scales.xAxes[0].ticks.min = min;
    chart_flow.options.scales.xAxes[0].ticks.max = max;
    chart_pressure.options.scales.xAxes[0].ticks.min = min;
    chart_pressure.options.scales.xAxes[0].ticks.max = max;
}

function setGaugeValue(name, value){
    obj[name].data.datasets[0].gaugeData['setvalue'] = value;
}
function getGaugeValue(name){
    return obj[name].data.datasets[0].gaugeData['setvalue'];
}
function getGaugeMinValue(name){
    return obj[name].data.datasets[0].gaugeLimits[0];
}
function getGaugeMaxValue(name){
    return obj[name].data.datasets[0].gaugeLimits[obj[name].data.datasets[0].gaugeLimits.length-1];
}

/*
// Store the original Draw function
var originalLineDraw = Chart.controllers.scatter.prototype.draw;
var originalElementsDraw = Chart.controllers.scatter.prototype.addElements;
var originalElementResetDraw = Chart.controllers.scatter.prototype.addElementAndReset;
// extend the new type
Chart.helpers.extend(Chart.controllers.scatter.prototype, {
    addElements: function() {
        originalElementsDraw.apply(this,arguments);
    },
    addElementAndReset: function() {
        originalElementResetDraw.apply(this,arguments);
    },

    draw: function () {
    // use the base draw function
    originalLineDraw.apply(this, arguments);
    // draw the line
    }
});
*/

//User defined scale, using afterFit callbacks instead
/*


var UserDefinedScaleDefaults = Chart.scaleService.getScaleDefaults("linear");
var MyScale = Chart.scaleService.getScaleConstructor("linear").extend({
    
    initialize: function() {
      Chart.Scale.prototype.initialize.call(this);
    },
    
    fit: function(){
     Chart.Scale.prototype.fit.call(this,arguments);
     //Chart.scaleService.getScaleConstructor("linear").fit.call(this,arguments);
     //originalFit.apply(this,arguments)
     this.margins.left = 500000;
     this.margins.right = 500000;
     console.log(this.margins);
     console.log(this);
    },
    
    // Determines the data limits. Should set this.min and this.max to be the data max/min
    determineDataLimits: function() { Chart.Scale.prototype.determineDataLimits.call(this,arguments);},
    // Generate tick marks. this.chart is the chart instance. The data object can be accessed as this.chart.data
    // buildTicks() should create a ticks array on the axis instance, if you intend to use any of the implementations from the base class
    buildTicks: function() {Chart.Scale.prototype.buildTicks.call(this,arguments);},

    // Get the value to show for the data at the given index of the the given dataset, ie this.chart.data.datasets[datasetIndex].data[index]
    getLabelForIndex: function(index, datasetIndex) { Chart.Scale.prototype.getLabelForIndex.call(index,datasetIndex);},

    // Get the pixel (x coordinate for horizontal axis, y coordinate for vertical axis) for a given value
    // @param index: index into the ticks array
    getPixelForTick: function(index) { Chart.Scale.prototype.getPixelForTick.call(index);},

    // Get the pixel (x coordinate for horizontal axis, y coordinate for vertical axis) for a given value
    // @param value : the value to get the pixel for
    // @param index : index into the data array of the value
    // @param datasetIndex : index of the dataset the value comes from
    getPixelForValue: function(value, index, datasetIndex) { Chart.Scale.prototype.getPixelForValue.call(value,index,datasetIndex);},

    // Get the value for a given pixel (x coordinate for horizontal axis, y coordinate for vertical axis)
    // @param pixel : pixel value
    getValueForPixel: function(pixel) { Chart.Scale.prototype.getValueForPixel.call(pixel); }


    
});

Chart.scaleService.registerScaleType('myScale', MyScale, UserDefinedScaleDefaults);
*/

$(document).ready(function() {
    var ctx_pressure = document.getElementById('pressure_chart');
    if ( ctx_pressure ) {
	let params = chartParam("pressure");
        chart_pressure = new Chart.Scatter(ctx_pressure, {
            data: {
                datasets: [{
                    data: [],
                    label: "Var1",
		    borderColor         : params.dataset.borderColor,
		    backgroundColor     : params.dataset.backgroundColor,
		    borderWidth         : params.dataset.borderWidth,
		    fill                : params.dataset.fill,
		    showLine            : params.dataset.showLine
                  } 
                ]
            },
            options: {
                layout: {
                    padding:{
                        top:0,
                        bottom:0,
                        //padding of slightly less (trial and error) than half of our tick font size added to top and middle charts
                        // to make up for extra padding added by displaying x ticks in bottom plot
                        right:0.6*parseFloat(getComputedStyle(document.documentElement).fontSize)*0.455,
                    }
                },
                elements: {
                    point: { 
                        radius: 0
                    },
                    line: {
                        tension: 0
                    },
                },            
                responsive: true,
        	maintainAspectRatio: false,
                bezierCurve : false,
                stroke: {
                },
                tooltips: {
                    enabled: false,
                    intersect: false,
		    mode: 'nearest',
		    callbacks: {
			label: function(tooltipItem) {
			    var pointPressure = chart_pressure.data.datasets[0].data[tooltipItem.index]['y'];
			    var pointFlow = chart_flow.data.datasets[0].data[tooltipItem.index]['y'];
			    var pointVolume = chart_volume.data.datasets[0].data[tooltipItem.index]['y'];
			    var label = 'Pres ' + Math.round(pointPressure*10)/10 + ' mbar, '
			    label += 'Flow ' + Math.round(pointFlow) + ' l/min, ';
			    label += 'Vol ' + Math.round(pointVolume) + ' ml';
			    return label;
			}
		    },
		    bodyFontSize: 18
                },
                title: {
                    display: false,
                    text: 'Pressure [cmH2O]',
            		fontSize: 0.7*parseFloat(getComputedStyle(document.documentElement).fontSize),
			fontColor: "#cccccc",
                },            
                scales: {
                    xAxes: [{
                        gridLines : {
                            display:       params.gridLines.display,
                            color:         params.gridLines.color,
                            zeroLineColor: params.gridLines.zeroLineColor
                        },
                        ticks: {
                            display:false,
            		        maxTicksLimit: 13,
                		    maxRotation: 0,
                            min: -60,
                            max: 0,
            	    	    fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),fontColor: "#cccccc"}}],
            		yAxes: [{
                        /*type: "myScale",*/
                        gridLines : {
                            display:       params.gridLines.display,
                            color:         params.gridLines.color,
                            zeroLineColor: params.gridLines.zeroLineColor,
                        },
                        ticks: {
                            beginAtZero: true,
                            suggestedMax: 25,
            	    	    fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),fontColor: "#cccccc",
                            maxTicksLimit: 8,
                        },
        				scaleLabel: {
    					display: true,
                        labelString: 'Pressure [mbar]',
                        fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),
                        fontColor: "#cccccc",
        				},
                        afterFit : function(axis){
                            axis.width = 70.0;
                            },
		        	}]            
                },
                legend : {
                    display: false
                }
            },
            plugins: {
                streaming: {
                    duration: 20000,
                    refresh: 1000,
                    delay: 2000
                    // onRefresh:     requestChartVar()
                }
            }
        });
    }
});


$(document).ready(function() {
    var ctx_flow = document.getElementById('flow_chart');
    if (ctx_flow) {
	let params = chartParam("flow");
        chart_flow = new Chart.Scatter(ctx_flow, {
            data: {
                //labels: initial_xaxis,
                datasets: [{
                    data: [],
                    label: "Var1",
		    borderColor         : params.dataset.borderColor,
		    backgroundColor     : params.dataset.backgroundColor,
		    borderWidth         : params.dataset.borderWidth,
		    fill                : params.dataset.fill,
		    showLine            : params.dataset.showLine
                }]
            },
            options: {

                layout: {
                    padding:{
                        top:0,
                        bottom:0,
                        //padding of slightly less (trial and error) than half of our tick font size added to top and middle charts
                        // to make up for extra padding added by displaying x ticks in bottom plot
                        right:0.6*parseFloat(getComputedStyle(document.documentElement).fontSize)*0.455,
                    }
                },
                elements: {
                    point: { 
                        radius: 0
                    },
                    line: {
                        tension: 0
                    },
                },            
                responsive: true,
    	        maintainAspectRatio: false,
                bezierCurve : false,
                stroke: {
                },
                tooltips: {
                    enabled: false,
                    intersect: false,
		    mode: 'nearest',
		    callbacks: {
			label: function(tooltipItem) {
			    var pointPressure = chart_pressure.data.datasets[0].data[tooltipItem.index]['y'];
			    var pointFlow = chart_flow.data.datasets[0].data[tooltipItem.index]['y'];
			    var pointVolume = chart_volume.data.datasets[0].data[tooltipItem.index]['y'];
			    var label = 'Pres ' + Math.round(pointPressure*10)/10 + ' mbar, '
			    label += 'Flow ' + Math.round(pointFlow) + ' l/min, ';
			    label += 'Vol ' + Math.round(pointVolume) + ' ml';
			    return label;
            }
		    },
		    bodyFontSize: 18
                },
                title: {
                  display: false,
            		text: 'Flow [l/min]',
            		fontSize: 0.7*parseFloat(getComputedStyle(document.documentElement).fontSize),
			fontColor: "#cccccc",
                },
                scales: {
                    xAxes: [{
                        gridLines : {
			    display:       params.gridLines.display,
                            color:         params.gridLines.color,
                            zeroLineColor: params.gridLines.zeroLineColor
                        },
                        ticks: {
                            display:false,
            		        maxTicksLimit: 13,
                		    maxRotation: 0,
                            min: -60,
                            max: 0,
                    		fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),fontColor: "#cccccc",}},],
        			yAxes: [{
                        gridLines : {
            			    display:       params.gridLines.display,
                            color:         params.gridLines.color,
                            zeroLineColor: params.gridLines.zeroLineColor
                        },
                        ticks: {
                            beginAtZero: true,
                            maxTicksLimit: 8,
                            fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),fontColor: "#cccccc",
                        },
        				scaleLabel: {
        					display: true,
                            labelString: 'Flow [l/min]',
                            fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),
                            fontColor: "#cccccc",
        				},
                        afterFit : function(axis){
                            axis.width = 70.0;
                            },
                        },
                ]            
                },
                legend : {
                    display: false
                }
            },
            plugins: {
                streaming: {
                    duration: 20000,
                    refresh: 1000,
                    delay: 2000
                    //onRefresh:     requestChartVar2()
                }
           }
        });
    }
});





$(document).ready(function() {
    var ctx_volume = document.getElementById('volume_chart');
    if (ctx_volume) {
	let params = chartParam("volume");
        chart_volume = new Chart.Scatter(ctx_volume, {
            data: {
                datasets: [{
                    data: [],
                    label: "Var1",
		    borderColor         : params.dataset.borderColor,
		    backgroundColor     : params.dataset.backgroundColor,
		    borderWidth         : params.dataset.borderWidth,
		    fill                : params.dataset.fill,
		    showLine            : params.dataset.showLine
                }]
            },
	
            options: {

                layout: {
                    padding:{
                        top:0,
                        bottom:0,
                    }
                },
                elements: {
                    point: { 
                        radius: 0
                    },
                    line: {
                        tension: 0
                    },
                },     
                animation: false,       
                responsive: true,
                bezierCurve : false,
        	    maintainAspectRatio: false,
                stroke: {
                },
                tooltips: {
                    enabled: false,
                    intersect: false,
		    mode: 'nearest',
		    callbacks: {
			label: function(tooltipItem) {
			    var pointPressure = chart_pressure.data.datasets[0].data[tooltipItem.index]['y'];
			    var pointFlow = chart_flow.data.datasets[0].data[tooltipItem.index]['y'];
			    var pointVolume = chart_volume.data.datasets[0].data[tooltipItem.index]['y'];
			    var label = 'Pres ' + Math.round(pointPressure*10)/10 + ' mbar, '
			    label += 'Flow ' + Math.round(pointFlow) + ' l/min, ';
			    label += 'Vol ' + Math.round(pointVolume) + ' ml';
			    return label;
			}
		    },
		    bodyFontSize: 18
                },
                title: {
                    display: false,
                    text: 'Volume [mL]',
	            	fontSize: 0.7*parseFloat(getComputedStyle(document.documentElement).fontSize),
			fontColor: "#cccccc",
                },
                scales: {
                    xAxes: [{
                        gridLines : {
			    display:       params.gridLines.display,
                            color:         params.gridLines.color,
                            zeroLineColor: params.gridLines.zeroLineColor
                        },
                        ticks: {
                            display:true,
                		    maxTicksLimit: 13,
                		    maxRotation: 0,
                            min: -60,
                            max: 0,
                            fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),fontColor: "#cccccc",
                        },
                    }],
                            
            		yAxes: [{
                        gridLines : {
                            display:       params.gridLines.display,
                            color:         params.gridLines.color,
                            zeroLineColor: params.gridLines.zeroLineColor
                        },
                        ticks: {
                            beginAtZero: true,
            	    		suggestedMax: 25,
                			maxTicksLimit: 8,
                		    fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),fontColor: "#cccccc",
		                },
		        		scaleLabel: {
        					display: true,
                            labelString: 'Volume [mL]',
                            fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),
                            fontColor: "#cccccc",
        				},
                        afterFit : function(axis){
                            axis.width = 70.0;
                            },
        			}]            
                },
                legend : {
                    display: false,
                    position: "right",
                }
            },
            plugins: {
                streaming: {
                    duration: 20000,
                    refresh: 1000,
                    delay: 2000
                }
            }
        });
    }
});
var obj = {};
function create_gauge_chart(var_name, setvalue, limits) {
    if (document.getElementById("gauge_"+var_name)){
	var ctx = document.getElementById("gauge_"+var_name).getContext("2d");
	obj[var_name + "_gauge"] = new Chart(ctx, {
            renderTo: 'gauge_' + var_name,
            type: "tsgauge",
            data: {
		datasets: [{
                    backgroundColor: ["red", "rgba(255,255,255,0.2)", "red"],
                    borderWidth: 0,
                    gaugeData: {
            value: 0,
            setvalue: setvalue,
			valueColor: "white"
                    },
                    gaugeLimits: limits
		}]
            },
            options: {
                arrowColor: "white",
	    maintainAspectRatio: true,
		events: []
            }
	});
    }
}

create_gauge_chart("fiO2_percent", 15, [0, 10, 90,100]);
create_gauge_chart("plateau_pressure",10,[0,4,16,20]);
