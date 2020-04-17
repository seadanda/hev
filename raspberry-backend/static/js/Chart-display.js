var chart_pressure;
var chart_flow;
var chart_volume;

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */
function requestChartVar() {
    $.ajax({
        url: '/live-data',
        success: function(point) {

            if(chart_pressure.data.datasets[0].data.length > 30){
                chart_pressure.data.labels.shift();
                chart_pressure.data.datasets[0].data.shift();
            }
            if(chart_flow.data.datasets[0].data.length > 30){
                chart_flow.data.labels.shift();
                chart_flow.data.datasets[0].data.shift();
            }
            if(chart_volume.data.datasets[0].data.length > 30){
                chart_volume.data.labels.shift();
                chart_volume.data.datasets[0].data.shift();
            }


            // Convert epoch timestamp into seconds
            var date = new Date(point.created_at);
            var seconds = date.getSeconds();

            // Show the time that has passed 
            chart_pressure.data.labels.push(seconds);
            chart_pressure.data.datasets[0].data.push(point["pressure_buffer"]);

            // add the point
            chart_flow.data.labels.push(point.created_at);
            chart_flow.data.datasets[0].data.push(point["pressure_inhale"]);

            // add the point
            chart_volume.data.labels.push(point.created_at);
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



$(document).ready(function() {
    var ctx_pressure = document.getElementById('pressure_chart');
    chart_pressure = new Chart(ctx_pressure, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                label: "Var1",
                borderColor: "#3e95cd",
                fill: false
              }
            ]
          },
          options: {
            responsive: true,
            title: {
              display: false,
              text: 'Pressure [mbar]'
            },
            scales: {
            xAxes: [{
                ticks: {
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
                    beginAtZero: true,
                    suggestedMax: 25
                  },
				scaleLabel: {
					display: true,
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
                  delay: 2000,
                  onRefresh:     requestChartVar()
              }
          }
    });
});




$(document).ready(function() {
    var ctx_flow = document.getElementById('flow_chart');
    chart_flow = new Chart(ctx_flow, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                label: "Var1",
                borderColor: "#3e95cd",
                fill: false
              }
            ]
          },
          options: {
            title: {
              display: false,
              text: 'Variable 1'
            },
            scales: {
            xAxes: [{
                type: 'time',
                time: {
                    unit: 'second',
                    displayFormat: 'second'
                }
            }]
            },
                legend : {
                    display: false}
          }
    });
    //requestChartVar("pressure_inhale");
});



$(document).ready(function() {
    var ctx_volume = document.getElementById('volume_chart');
    chart_volume = new Chart(ctx_volume, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                label: "Var1",
                borderColor: "#3e95cd",
                fill: false
              }
            ]
          },
          options: {
            title: {
              display: false,
              text: 'Variable 1'
            },
            scales: {
            xAxes: [{
                type: 'time',
                time: {
                    unit: 'second',
                    displayFormat: 'second'
                }
            }]
            },
                legend : {
                    display: false}
          }
    });
    //requestChartVar("temperature_buffer");
});


