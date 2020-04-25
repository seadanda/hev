var chart_pressure;
var chart_flow;
var chart_volume;

var size_data;
var initial_xaxis = [];
var initial_yaxis_pressure = [];
var initial_yaxis_volume = [];
var initial_yaxis_flow = [];

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */

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

// Calling the function here to retrive 
// the initial values to be plotted on the charts
last_results();



function requestChartVar() {
    $.ajax({
        url: '/live-data',
        success: function(point) {

            if(chart_pressure.data.datasets[0].data.length > 300){
                chart_pressure.data.labels.shift();
                chart_pressure.data.datasets[0].data.shift();
            }

            if(chart_flow.data.datasets[0].data.length > 300){
                //chart_flow.data.labels.shift();
                chart_flow.data.datasets[0].data.shift();
            }

 
            if(chart_volume.data.datasets[0].data.length > 300){
                //chart_volume.data.labels.shift();
                chart_volume.data.datasets[0].data.shift();
            }

            for (var i=0; i<300; i++) {
                var x = chart_pressure.data.labels[i] - 0.20 ;
                chart_pressure.data.labels[i] = x.toFixed(1);
            }


            // add the point           
            chart_pressure.data.labels.push(0);
            //chart_pressure.data.labels.push(point["timestamp"]);
            chart_pressure.data.datasets[0].data.push(point["pressure_buffer"]);

            // add the point
            //chart_pressure.data.labels.push(0);
            chart_flow.data.datasets[0].data.push(point["temperature_buffer"]);

            // add the point
            //chart_pressure.data.labels.push(0);
            chart_volume.data.datasets[0].data.push(point["pressure_inhale"]);
            
            chart_pressure.update();
            chart_flow.update();
            chart_volume.update();
            
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
        type: 'line',
        data: {
            labels: initial_xaxis,
            datasets: [{
                data: initial_yaxis_pressure,
                label: "Var1",
                borderColor: "#0049b8",
                borderWidth: 4,
                fill: false
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
                    beginAtZero: true,
		    maxTicksLimit: 12,
		    maxRotation: 0,
                },
                //type: 'time',
                time: {
                    unit: 'second',
                    displayFormat: 'second'
                }
            }],
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
        type: 'line',
        data: {
            labels: initial_xaxis,
            datasets: [{
                data: initial_yaxis_flow,
                label: "Var1",
                //borderColor: "#3e95cd",
                borderColor: "#000000",
                borderWidth: 4,
                fill: false
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
                    beginAtZero: true,
		    maxTicksLimit: 12,
		    maxRotation: 0,

                },
                //type: 'time',
                time: {
                    unit: 'second',
                    displayFormat: 'second'
                }
            }],
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
        type: 'line',
        data: {
            labels: initial_xaxis,
            datasets: [{
                data: initial_yaxis_volume,
                label: "Var1",
                borderColor: "#ba0202",
                borderWidth: 4,
                fill: false
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
                    beginAtZero: true,
		    maxTicksLimit: 12,
		    maxRotation: 0,
                },
                //type: 'time',
                time: {
                    unit: 'second',
                    displayFormat: 'second'
                }
            }],
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
                //onRefresh:     requestChartVar3()
            }
        }
    });
});



