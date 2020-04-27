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
            for (i=0; i<data.length; i++) {
		var seconds = data[i]["timestamp"]/1000;
		if ( seconds == "" ) continue;
		initial_yaxis_pressure.push({x : seconds, y : data[i]["pressure_buffer"]});
		initial_yaxis_volume.push({x : seconds, y : data[i]["pressure_inhale"]});
		initial_yaxis_flow.push({x : seconds, y : data[i]["temperature_buffer"]});
            }
            //reverse because data is read from the other way
            initial_xaxis.reverse();
            initial_yaxis_pressure.reverse();
            initial_yaxis_volume.reverse();
            initial_yaxis_flow.reverse();

	    if (initial_yaxis_pressure.length > 0) current_timestamp = initial_yaxis_pressure[0][0];
	    for ( let i = 0 ; i < initial_yaxis_pressure.length; i++){
		initial_yaxis_pressure[i][0] = initial_yaxis_pressure[i][0] - current_timestamp;
		initial_yaxis_volume[i][0]   = initial_yaxis_volume[i][0] - current_timestamp;
		initial_yaxis_flow[i][0]     = initial_yaxis_flow[i][0] - current_timestamp;
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
            initial_yaxis_pressure.push(data[i]["pressure_buffer"]);
            initial_yaxis_volume.push(data[i]["pressure_inhale"]);
            initial_yaxis_flow.push(data[i]["temperature_buffer"]);
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
init_results();



function requestChartVar() {
    $.ajax({
        url: '/live-data',
        success: function(point) {
        fio_reading = (point["pressure_buffer"]).toFixed(0) ;
        //console.log(fio_reading);
        fio_gauge.data.datasets[0].gaugeData['value'] = fio_reading;

	    var seconds = point["timestamp"]/1000;
	    // get difference between last time stamp and this and apply to existing points
	    var diff = 0;
	    if ( current_timestamp == -1 ){
		diff = seconds;
	    }
	    else {
		diff = seconds - current_timestamp;
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
		initial_yaxis_pressure[i]['x'] = initial_yaxis_pressure[i]['x'] - diff;
		initial_yaxis_volume[i]['x']   = initial_yaxis_volume[i]['x']   - diff;
		initial_yaxis_flow[i]['x']     = initial_yaxis_flow[i]['x']     - diff;
	    }
	    
            chart_pressure.data.datasets[0].data.push({x : 0, y : point["pressure_buffer"]});
            chart_flow.data.datasets[0].data.push({ x : 0, y : point["temperature_buffer"]});
            chart_volume.data.datasets[0].data.push({ x : 0, y : point["pressure_inhale"]});
            
            chart_pressure.update();
            chart_flow.update();
            chart_volume.update();
            fio_gauge.update();

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
            },            
            scales: {
		
            xAxes: [{
                ticks: {
		        maxTicksLimit: 13,
		    maxRotation: 0,
                    min: -60,
                    max: 0}}],
		yAxes: [{
                ticks: {
                    beginAtZero: true,
                    suggestedMax: 25
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
            },
            scales: {
		
            xAxes: [{
                ticks: {
		        maxTicksLimit: 13,
		    maxRotation: 0,
                    min: -60,
                    max: 0}}],
			yAxes: [{
                ticks: {
                    beginAtZero: true,
                    suggestedMax: 25
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
            },
            scales: {
		
            xAxes: [{
                ticks: {
		    maxTicksLimit: 13,
		    maxRotation: 0,
                    min: -60,
                    max: 0}}],
		
		yAxes: [{
                    ticks: {
                    beginAtZero: true,
                    suggestedMax: 25
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


var ctx = document.getElementById("example_gauge").getContext("2d");
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

