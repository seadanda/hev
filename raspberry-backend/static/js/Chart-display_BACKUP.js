var chart_pressure;
var chart_flow;
var chart_volume;
var time_value = 0 ;

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */
function requestChartVar1() {
    $.ajax({
        url: '/live-data',
        success: function(point) {

            if(chart_pressure.data.datasets[0].data.length > 10){
                chart_pressure.data.labels.shift();
                chart_pressure.data.datasets[0].data.shift();
            }


            // add the point
            chart_pressure.data.labels.push(point.created_at);
            time_value = point.created_at; 
            console.log(time_value)
            chart_pressure.data.datasets[0].data.push(point[var1]);

            // add the point
            chart_flow.data.labels.push(point.created_at);
            chart_flow.data.datasets[0].data.push(point[var1]);

            
            chart_pressure.update();
        },
        cache: false
    });
    // call it again after one second
    setTimeout(requestChartVar1, 1000);
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
            title: {
              display: false,
              text: 'Variable 1'
            },
            scales: {
            xAxes: [{
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
    requestChartVar1("pressure_buffer");
});


function requestChartVar2(var1) {
    $.ajax({
        url: '/live-data',
        success: function(point) {

            if(chart_flow.data.datasets[0].data.length > 10){
                chart_flow.data.labels.shift();
                chart_flow.data.datasets[0].data.shift();
            }


            // add the point
            chart_flow.data.labels.push(point.created_at);
            chart_flow.data.datasets[0].data.push(point[var1]);

            
            chart_flow.update();
        },
        cache: false
    });
    // call it again after one second
    setTimeout(requestChartVar2, 1000, var1);
}



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
    requestChartVar2("pressure_inhale");
});


function requestChartVar3(var1) {
    $.ajax({
        url: '/live-data',
        success: function(point) {

            if(chart_volume.data.datasets[0].data.length > 10){
                chart_volume.data.labels.shift();
                chart_volume.data.datasets[0].data.shift();
            }


            // add the point
            chart_volume.data.labels.push(point.created_at);
            chart_volume.data.datasets[0].data.push(point[var1]);

            
            chart_volume.update();
        },
        cache: false
    });
    // call it again after one second
    setTimeout(requestChartVar3, 1000, var1);
}



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
    requestChartVar3("temperature_buffer");
});


