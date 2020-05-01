var chart_pressure;
var chart_flow;
var chart_volume;

var size_data;
var initial_xaxis = [];
var initial_yaxis_pressure = [];
var initial_yaxis_volume = [];
var initial_yaxis_flow = [];

var fio_reading;

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */

var current_timestamp = -1;

function setChartXaxisRange(min,max){
    chart_volume.options.scales.xAxes[0].ticks.min = min;
    chart_volume.options.scales.xAxes[0].ticks.max = max;
    chart_flow.options.scales.xAxes[0].ticks.min = min;
    chart_flow.options.scales.xAxes[0].ticks.max = max;
    chart_pressure.options.scales.xAxes[0].ticks.min = min;
    chart_pressure.options.scales.xAxes[0].ticks.max = max;

    
}


function init_results(){
    $.getJSON({
        url: '/last_N_data',
        success: function(data) {
	    var timestamp = 0;
            for (i=0; i<data.length; i++) {
		var seconds = data[i]["timestamp"]/1000;
		if (i==data.length-1) timestamp = seconds;
		if ( seconds == "" ) continue;
		initial_yaxis_pressure.push({x : seconds, y : data[i]["airway_pressure"]});
		initial_yaxis_volume.push({x : seconds, y : data[i]["volume"]});
		initial_yaxis_flow.push({x : seconds, y : data[i]["flow"]});
            }
            //reverse because data is read from the other way
            initial_xaxis.reverse();
            initial_yaxis_pressure.reverse();
            initial_yaxis_volume.reverse();
            initial_yaxis_flow.reverse();

	    console.log('init results, timestamp: ',timestamp);
	    for ( let i = 0 ; i < initial_yaxis_pressure.length; i++){
		console.log('filling up with ',initial_yaxis_pressure[i]['x'], ' - ',timestamp);
		initial_yaxis_pressure[i]['x'] = initial_yaxis_pressure[i]['x'] - timestamp;
		initial_yaxis_volume[i]['x']   = initial_yaxis_volume[i]['x']   - timestamp;
		initial_yaxis_flow[i]['x']     = initial_yaxis_flow[i]['x']     - timestamp;
        }
        },
        cache: false
    });
}

/*
function last_results() {
    $.getJSON({
        url: '/last_N_data',
        success: function(data) {
          for (i=0; i<data.length; i++) {
            size_data = data.length
            var date = new Date(data[i]["created_at"]);
            var seconds = date.getSeconds();
            // terrible hack to show the time in reverse order
            var time_x = (-i/5).toFixed(2)
            initial_xaxis.push(time_x);
            //initial_xaxis.push(data[i]["timestamp"]);
            initial_yaxis_pressure.push(data[i]["airway_pressure"]);
            initial_yaxis_volume.push(data[i]["volume"]);
            initial_yaxis_flow.push(data[i]["flow"]);
          }
          //reverse because data is read from the other way
          initial_xaxis.reverse();
          initial_yaxis_pressure.reverse();
          initial_yaxis_volume.reverse();
          initial_yaxis_flow.reverse();
        },
        cache: false
    });
}
*/
// Calling the function here to retrive 
// the initial values to be plotted on the charts
//last_results();
//Leave this out for now as there seems to be an issue with timestamps in the last data
//init_results();

function setGaugeValue(name, value){
    obj[name].data.datasets[0].gaugeData['setvalue'] = value;
}

function requestChartVar() {
    $.ajax({
        url: '/live-data',
        success: function(point) {
        fio_reading = (point["airway_pressure"]).toFixed(0) ;
        p_plateau_reading = (point["volume"]).toFixed(0) ;
        //console.log(fio_reading);
            if ("fio_gauge" in obj) {
                obj["fio_gauge"].data.datasets[0].gaugeData['value'] = fio_reading;
            }
            if ("p_plateau_gauge" in obj) obj["p_plateau_gauge"].data.datasets[0].gaugeData['value'] = p_plateau_reading; 


            var seconds = point["timestamp"]/1000;

	    // this is a hack for the test data so that we can cycle data
	    if ( seconds < current_timestamp ) current_timestamp = seconds - 0.20;
	    
	    //protect against bogus timestamps, skip those that are earlier than we already have
	    if (current_timestamp == -1 || seconds > current_timestamp )
	    {
		// get difference between last time stamp and this and apply to existing points
		var diff = 0;
		if ( current_timestamp == -1 ){
		    diff = seconds;
		}
		else {
		    diff = seconds - current_timestamp; //FUTURE: restore this line in case not using simulated data
		}
		current_timestamp = seconds;
		if(chart_pressure.data.datasets[0].data.length > 300){
                    chart_pressure.data.datasets[0].data.shift();
		}
		
		if(chart_flow.data.datasets[0].data.length > 300){
                    chart_flow.data.datasets[0].data.shift();
		}
		
		if(chart_volume.data.datasets[0].data.length > 300){
                    chart_volume.data.datasets[0].data.shift();
		}
		for ( let i = 0 ; i < initial_yaxis_pressure.length; i++){
		    chart_pressure.data.datasets[0].data[i]['x'] = chart_pressure.data.datasets[0].data[i]['x'] - diff;
		    chart_flow.data.datasets[0].data[i]['x'] = chart_flow.data.datasets[0].data[i]['x'] - diff;
		    chart_volume.data.datasets[0].data[i]['x'] = chart_volume.data.datasets[0].data[i]['x'] - diff;
		}
		
		chart_pressure.data.datasets[0].data.push({x : 0, y : point["airway_pressure"]});
		chart_flow.data.datasets[0].data.push({ x : 0, y : point["flow"]});
		chart_volume.data.datasets[0].data.push({ x : 0, y : point["volume"]});
		
		chart_pressure.update();
		chart_flow.update();
		chart_volume.update();
	    }
	    // we can update these with new value even if there is a timestamp issue
            if ("fio_gauge" in obj) obj["fio_gauge"].update();
            if ("p_plateau_gauge" in obj) obj["p_plateau_gauge"].update();
        },
        cache: false
    });
    // call it again after time in ms
    setTimeout(requestChartVar, 200);
}

requestChartVar();



$(document).ready(function() {
    var ctx_pressure = document.getElementById('pressure_chart');
    chart_pressure = new Chart(ctx_pressure, {
        type: 'scatter',
        data: {
            datasets: [{
                data: initial_yaxis_pressure,
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
                    display: false}
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
});







$(document).ready(function() {
    var ctx_flow = document.getElementById('flow_chart');
    chart_flow = new Chart(ctx_flow, {
        type: 'scatter',
        data: {
            //labels: initial_xaxis,
            datasets: [{
                data: initial_yaxis_flow,
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
});





$(document).ready(function() {
    var ctx_volume = document.getElementById('volume_chart');
    chart_volume = new Chart(ctx_volume, {
        type: 'scatter',
        data: {
            //labels: initial_xaxis,
            datasets: [{
                data: initial_yaxis_volume,
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
		    fontSize: 0.6*parseFloat(getComputedStyle(document.documentElement).fontSize),}}],
		
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
});

/*
var ctx = document.getElementById("gauge_example").getContext("2d");
>>>>>>> 08dee8e2c63b31e8bddfd3efe6c95962465009f0
fio_gauge = new Chart(ctx, {
	type: "tsgauge",
	data: {
		datasets: [{
			backgroundColor: ["#0fdc63", "#fd9704", "#ff7143"],
			borderWidth: 0,
			gaugeData: {
				value: 0,
				valueColor: "#ff7143"
			},
			gaugeLimits: [0, 50, 100]
		}]
	},
	options: {
		events: []
	}
});
*/

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
		events: []
            }
	});
    }
}


["fio", "p_plateau"].forEach(create_gauge_chart);
