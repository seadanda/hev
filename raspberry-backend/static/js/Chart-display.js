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


// Store the original Draw function
var originalLineDraw = Chart.controllers.scatter.prototype.draw;
var originalElementsDraw = Chart.controllers.scatter.prototype.addElements;
var originalElementResetDraw = Chart.controllers.scatter.prototype.addElementAndReset;
// extend the new type
Chart.helpers.extend(Chart.controllers.scatter.prototype, {
    addElements: function() {
        var xaxis = this['chart'].scales['x-axis-0'];
        var yaxis = this['chart'].scales['y-axis-0'];
    
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
                    display: true,
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
                            display:true,
            		        maxTicksLimit: 13,
                		    maxRotation: 0,
                            min: -60,
                            max: 0,
            	    	    fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),fontColor: "#cccccc"}}],
            		yAxes: [{
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
    					display: false,
                        labelString: 'Pressure [mbar]'
        				}
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
                  display: true,
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
                            display:true,
            		        maxTicksLimit: 13,
                		    fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),
                		    maxRotation: 0,
                            min: -60,
                            max: 0,
                    		fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),fontColor: "#cccccc",}}],
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
        					display: false,
                            labelString: 'Flow [l/min]'
        				}
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
                    display: true,
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
                        }
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
        					display: false,
                            labelString: 'Volume [mL]'
        				}
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
