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
            initial_xaxis.push(-i);
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


last_results();



function requestChartVar() {
    $.ajax({
        url: '/live-data',
        success: function(point) {

            if(chart_pressure.data.datasets[0].data.length > 30){
                chart_pressure.data.labels.shift();
                chart_pressure.data.datasets[0].data.shift();
            }

            if(chart_flow.data.datasets[0].data.length > 30){
                //chart_flow.data.labels.shift();
                chart_flow.data.datasets[0].data.shift();
            }

 
            if(chart_volume.data.datasets[0].data.length > 30){
                //chart_volume.data.labels.shift();
                chart_volume.data.datasets[0].data.shift();
            }

            for (var i=0; i<30; i++) {
                chart_pressure.data.labels[i] -= 1 ;
           }


            // add the point           
            chart_pressure.data.labels.push(0);
            chart_pressure.data.datasets[0].data.push(point["pressure_buffer"]);

            // add the point
            //chart_pressure.data.labels.push(0);
            chart_flow.data.datasets[0].data.push(point["pressure_inhale"]);

            // add the point
            //chart_pressure.data.labels.push(0);
            chart_volume.data.datasets[0].data.push(point["temperature_buffer"]);
            
            chart_pressure.update();
            chart_flow.update();
            chart_volume.update();

            
        },
        cache: false
    });
    // call it again after one second
    setTimeout(requestChartVar, 1000);
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
                borderColor: "#3e95cd",
                fill: false
              }
            ]
          },
          options: {
            responsive: true,
            stroke: {
                curve: 'smooth'
              },
            title: {
                display: true,
                text: 'Pressure [mbar]',
                fontSize: 25
              },            
            scales: {
            xAxes: [{
                ticks: {
                    fontSize: 25,
                    beginAtZero: true
                },
                //type: 'time',
                time: {
                    unit: 'second',
                    displayFormat: 'second'
                }
            }],
			yAxes: [{
                ticks: {
                    fontSize: 25,
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
                borderColor: "#3e95cd",
                fill: false
              }
            ]
          },
          options: {
            responsive: true,
            stroke: {
                curve: 'smooth'
              },
            title: {
              display: true,
              text: 'Flow [mL/min]',
              fontSize: 25
            },
            scales: {
            xAxes: [{
                ticks: {
                    fontSize: 25,
                    beginAtZero: true
                },
                //type: 'time',
                time: {
                    unit: 'second',
                    displayFormat: 'second'
                }
            }],
			yAxes: [{
                ticks: {
                    fontSize: 25,
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
                    display: false}
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
                borderColor: "#3e95cd",
                fill: false
              }
            ]
          },
          options: {
            responsive: true,
            stroke: {
                curve: 'smooth'
              },
            title: {
              display: true,
              text: 'Volume [mL]',
              fontSize: 25
            },
            scales: {
            xAxes: [{
                ticks: {
                    fontSize: 25,
                    beginAtZero: true
                },
                //type: 'time',
                time: {
                    unit: 'second',
                    displayFormat: 'second'
                }
            }],
			yAxes: [{
                ticks: {
                    fontSize: 25,
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
                    display: false}
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



