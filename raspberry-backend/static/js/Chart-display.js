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

var rowid = 0;
function requestData() {
    $.ajax({
        url: '/last-data/'+rowid,
        success: function(data) {
            if (data.length == 0) {
                // we're not getting any new data from the hevserver
                console.log("Got no new data");
            } else
            {
                /*
                // we have some data, let's fill first our readings with last point
                */

                //first point is last time in terms of time
                var point = data[0];
                rowid = point["ROWID"];
                //var fio_reading = (point["airway_pressure"]).toFixed(0) ;
                //var p_plateau_reading = (point["volume"]).toFixed(0) ;
                //if ("fio_gauge" in obj) obj["fio_gauge"].data.datasets[0].gaugeData['value'] = fio_reading;
                //if ("p_plateau_gauge" in obj) obj["p_plateau_gauge"].data.datasets[0].gaugeData['value'] = p_plateau_reading; 
                // if any of these elements exist in html file, we update continuously with data
                var readings = [ "pressure_buffer", "pressure_inhale","pressure_air_supply","pressure_air_regulated",
                            "pressure_o2_supply", "pressure_o2_regulated", "pressure_patient", "pressure_diff_patient", "fsm_state",
                            "fio2_percent", "inhale_exhale_ratio", "peak_inspiratory_pressure", "plateau_pressure",
                            "mean_airway_pressure", "peep", "inhaled_tidal_volume", "exhaled_tidal_volume",
                            "inhaled_minute_volume", "exhaled_minute_volume", "flow", "volume"];
                for (let i = 0 ; i < readings.length; i++){
                    var gauge = document.getElementById("gauge_"+readings[i]);
                    var el = document.getElementById(readings[i]);
                    var val = -1.0;
                    if (readings[i] in point) {
                        val = point[readings[i]];
                        if ( gauge && val != -1 && ("gauge_"+readings[i]) in obj ) {
                            obj["gauge_" + readings[i]] = val.toFixed(0);
                        }
                        if (el && val != -1){
                            el.innerHTML = val.toPrecision(5);
                        }
                    }
                }
                
                // get our current time stamp
                // get difference between it and last received to update plots
                var last_timestamp = point["timestamp"]/1000.0;
                var diff = last_timestamp;
                // this is just for cycling test data
                if ( last_timestamp < current_timestamp ) current_timestamp = last_timestamp - 1.00;
                
                if (current_timestamp != -1) diff = last_timestamp - current_timestamp;

                /*
                // if charts exist we now update with all points received
                */

                if (chart_pressure && chart_flow && chart_volume){
                    //update current plots with difference
                    for ( let i = 0 ; i < chart_pressure.data.datasets[0].data.length; i++){
                        chart_pressure.data.datasets[0].data[i]['x'] = chart_pressure.data.datasets[0].data[i]['x'] - diff;
                        chart_flow.data.datasets[0].data[i]['x'] = chart_flow.data.datasets[0].data[i]['x'] - diff;
                        chart_volume.data.datasets[0].data[i]['x'] = chart_volume.data.datasets[0].data[i]['x'] - diff;
                    }
                
                    //add new points
                    //keep track of timestamp to make sure we're not mixing it up
                    var running_timestamp = -1;
                    var running_rowid = 0;
                    for (let ip = data.length-1 ; ip >= 0; ip--){
                        var point = data[ip];
                        var seconds = point["timestamp"]/1000;
                        if (seconds < current_timestamp) continue;
                	    // this is a hack for the test data so that we can cycle data
                        //if ( seconds - current_timestamp > 1.0) { console.log("Current Timestamp: ",current_timestamp, " against ",seconds);}
                	    //protect against bogus timestamps, skip those that are earlier than we already have
                	    if (running_timestamp == -1 || seconds > running_timestamp  )
                	    {
                    		// get difference between last time stamp and this and apply to existing points
                    		chart_pressure.data.datasets[0].data.push({x : seconds - last_timestamp, y : point["pressure_patient"]});
                    		chart_flow.data.datasets[0].data.push({ x : seconds - last_timestamp, y : point["flow"]});
                    		chart_volume.data.datasets[0].data.push({ x : seconds - last_timestamp, y : point["volume"]});
                            running_timestamp = seconds;
                            running_rowid = point['ROWID'];
                        }
                    }
                  	while(chart_pressure.data.datasets[0].data.length > 1000) chart_pressure.data.datasets[0].data.shift();
                   	while(chart_flow.data.datasets[0].data.length > 1000) chart_flow.data.datasets[0].data.shift();
                    while(chart_volume.data.datasets[0].data.length > 1000) chart_volume.data.datasets[0].data.shift();

                    current_timestamp = last_timestamp;

    		        chart_pressure.update(0);
            		chart_flow.update(0);
            		chart_volume.update(0);
                }
                if ("fio_gauge" in obj) obj["fio_gauge"].update();
                if ("p_plateau_gauge" in obj) obj["p_plateau_gauge"].update();
            }
        },
        cache: false
    });
    // call it again after time in ms
    chart_display_interval = setTimeout(requestData, 200);
}

requestData();



$(document).ready(function() {
    var ctx_pressure = document.getElementById('pressure_chart');
    if ( ctx_pressure ) {
        chart_pressure = new Chart(ctx_pressure, {
            type: 'scatter',
            data: {
                datasets: [{
                    data: [],
                    label: "Var1",
                    borderColor: "#0049b8",
                    borderWidth: 4,
                    fill: false,
    		showLine: true,
                  }
                ]
            },
            options: {
                elements: {
                    point: { 
                        radius: 0
                    }
                },            
                responsive: true,
        	    maintainAspectRatio: false,
                stroke: {
                    curve: 'smooth'
                },
                tooltips: {
                    enabled: false
                },
                title: {
                    display: true,
                    text: 'Pressure [mbar]',
            		fontSize: 0.7*parseFloat(getComputedStyle(document.documentElement).fontSize),
                },            
                scales: {
                    xAxes: [{
                        ticks: {
            		        maxTicksLimit: 13,
                		    maxRotation: 0,
                            min: -60,
                            max: 0,
            	    	    fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),}}],
            		yAxes: [{
                        ticks: {
                            beginAtZero: true,
                            suggestedMax: 25,
            	    	    fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),
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
        chart_flow = new Chart(ctx_flow, {
            type: 'scatter',
            data: {
                //labels: initial_xaxis,
                datasets: [{
                    data: [],
                    label: "Var1",
                    //borderColor: "#3e95cd",
                    borderColor: "#000000",
                    borderWidth: 4,
                    fill: false,
            		showLine: true,
                }]
            },
            options: {
                elements: {
                    point: { 
                        radius: 0
                    }
                },            
                responsive: true,
    	        maintainAspectRatio: false,
                stroke: {
                    curve: 'smooth'
                },
                tooltips: {
                    enabled: false
                },
                title: {
                  display: true,
            		text: 'Flow [mL/min]',
            		fontSize: 0.7*parseFloat(getComputedStyle(document.documentElement).fontSize),
                },
                scales: {
                    xAxes: [{
                        ticks: {
            		        maxTicksLimit: 13,
                		    fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),
                		    maxRotation: 0,
                            min: -60,
                            max: 0,
                    		fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),}}],
        			yAxes: [{
                        ticks: {
                            beginAtZero: true,
                            maxTicksLimit: 8,
                		    fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),
                        },
        				scaleLabel: {
        					display: false,
                            labelString: 'Flow [mL/min]'
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
        chart_volume = new Chart(ctx_volume, {
            type: 'scatter',
            data: {
                datasets: [{
                    data: [],
                    label: "Var1",
                    borderColor: "#ba0202",
                    borderWidth: 4,
                    fill: false,
            		showLine: true,
                }]
            },
	
            options: {
                elements: {
                    point: { 
                        radius: 0
                    }
                },     
                animation: false,       
                responsive: true,
        	    maintainAspectRatio: false,
                stroke: {
                    curve: 'smooth'
                },
                tooltips: {
                    enabled: false
                },
                title: {
                    display: true,
                    text: 'Volume [mL]',
	            	fontSize: 0.7*parseFloat(getComputedStyle(document.documentElement).fontSize),
                },
                scales: {
                    xAxes: [{
                        ticks: {
                		    maxTicksLimit: 13,
                		    maxRotation: 0,
                            min: -60,
                            max: 0,
                            fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),
                        }
                    }],
                            
            		yAxes: [{
                        ticks: {
                            beginAtZero: true,
            	    		suggestedMax: 25,
                			maxTicksLimit: 8,
                		    fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),
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
function create_gauge_chart(var_name) {
    if (document.getElementById("gauge_"+var_name)){
	var ctx = document.getElementById("gauge_"+var_name).getContext("2d");
	obj[var_name + "_gauge"] = new Chart(ctx, {
            renderTo: 'gauge_' + var_name,
            type: "tsgauge",
            data: {
		datasets: [{
                    backgroundColor: ["red", "rgba(20,20,20,0.2)", "red"],
                    borderWidth: 0,
                    gaugeData: {
            value: 0,
            setvalue: 75,
			valueColor: "black"
                    },
                    gaugeLimits: [0, 10, 90, 100]
		}]
            },
            options: {

	    maintainAspectRatio: true,
		events: []
            }
	});
    }
}


["fi02_percent", "plateau_pressure"].forEach(create_gauge_chart);
