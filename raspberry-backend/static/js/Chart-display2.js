var chart_pressure;
var chart_flow;
var chart_volume;
var time_value = 0 ;

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */


function requestChartVar() {
    $.ajax({
        url: '/live-data',
        success: function(point) {
            //Convert epoch timestamp into seconds
            var date = new Date(point.created_at);
            var seconds = date.getSeconds();

	    var last = 59;
	    // get last entered point
	    for ( ; last >= 0 ; last-- ){
		if (chart_pressure.data.datasets[0].data[last] != null){
		    break;
		}
	    }

	    if (chart_pressure.data.labels[0] == "0"){
		chart_pressure.data.labels[0] = ""+date.getHours()+':'+date.getMinutes()+':00';
		chart_pressure.data.labels[60] = ""+date.getHours()+':'+(date.getMinutes()+1)+':00';
		chart_flow.data.labels[0] = ""+date.getHours()+':'+date.getMinutes()+':00';
		chart_flow.data.labels[60] = ""+date.getHours()+':'+(date.getMinutes()+1)+':00';
		chart_volume.data.labels[0] = ""+date.getHours()+':'+date.getMinutes()+':00';
		chart_volume.data.labels[60] = ""+date.getHours()+':'+(date.getMinutes()+1)+':00';
		
	    }
	    
	    if ( seconds%60 < last ){
		console.log(chart_pressure.data.datasets[0].data[-1]);
		chart_pressure.data.datasets.unshift(
		    {
			data: [new Array(60)],
			label: "Var1",
			borderColor: "rgb(51, 99, 255)",
			fill: false
		    });
		chart_flow.data.datasets.unshift(
		    {
			data: [new Array(60)],
			label: "Var1",
			borderColor: "rgb(51,99,255)",
			fill: false
		    });
		chart_volume.data.datasets.unshift(
		    {
			data: [new Array(60)],
			label: "Var1",
			borderColor: "rgb(51,99,255)",
			fill: false
		    });

		chart_pressure.data.datasets[1].borderColor = "rgba(51, 99, 255,0.2)";
		chart_pressure.data.datasets[1].pointRadius = 0;
		chart_pressure.data.labels[0] = ""+date.getHours()+':'+date.getMinutes()+':00';
		chart_pressure.data.labels[60] = ""+date.getHours()+':'+(date.getMinutes()+1)+':00';
		if (chart_pressure.data.datasets.length > 2) chart_pressure.data.datasets.pop();

		chart_flow.data.datasets[1].borderColor = "rgba(51, 99, 255,0.2)";
		chart_flow.data.datasets[1].pointRadius = 0;
		chart_flow.data.labels[0] = ""+date.getHours()+':'+date.getMinutes()+':00';
		chart_flow.data.labels[60] = ""+date.getHours()+':'+(date.getMinutes()+1)+':00';
		if (chart_flow.data.datasets.length > 2 )chart_flow.data.datasets.pop();

		chart_volume.data.datasets[1].borderColor = "rgba(51, 99, 255,0.2)";
		chart_volume.data.datasets[1].pointRadius = 0;
		chart_volume.data.labels[0] = ""+date.getHours()+':'+date.getMinutes()+':00';
		chart_volume.data.labels[60] = ""+date.getHours()+':'+(date.getMinutes()+1)+':00';
		if (chart_volume.data.datasets.length > 2) chart_volume.data.datasets.pop();

	    }
	    chart_pressure.data.datasets[0].data[seconds%60] = point["pressure_buffer"];
	    chart_pressure.update();

	    chart_flow.data.datasets[0].data[seconds%60] = point["pressure_inhale"];
	    chart_flow.update();

	    chart_volume.data.datasets[0].data[seconds%60] = point["temperature_buffer"];
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
            datasets: [
		{
                    data: [],
                    label: "Var1",
                    borderColor: "rgb(51,99,255)",
                    fill: false
		},
            ]
          },
          options: {
            responsive: true,
            title: {
              display: true,
              text: 'Pressure [mbar]'
            },
            scales: {
            xAxes: [{
                ticks: {
                    beginAtZero: true,
		    maxTicksLimit: 12,
		    maxRotation: 0,
		    display: true,
		},
		scaleLabel:{
		    display: true,
		    labelString: 'Seconds',
                },
		showTickLabels: 'none'
                //type: 'time',
                //time: {
                //    unit: 'second',
                //    displayFormat: 'second'
                //}
            }],
			yAxes: [{
                ticks: {
                    beginAtZero: false,
                    suggestedMax: 150,
		    suggestedMin: 140,
                  },
				scaleLabel: {
					display: true,
                    labelString: 'Pressure [mbar]'
				}
			}]            
            },
                legend : {
                    display: false},
	      spanGaps: true
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


    var ctx_volume = document.getElementById('volume_chart');
    chart_volume = new Chart(ctx_volume, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                label: "Var1",
                borderColor: "rgb(51,99,255)",
                fill: false
            },
            ]
          },
          options: {
            title: {
              display: true,
              text: 'Volume [mL]'
            },
            scales: {
		xAxes: [{
		    
                ticks: {
                    beginAtZero: true,
		    maxTicksLimit: 12,
		    maxRotation: 0,
		},
		scaleLabel:{
		    display: true,
		    labelString: 'Seconds',
                },
            }],
			yAxes: [{
                ticks: {
                    beginAtZero: true,
                    suggestedMax: 25
                  },
				scaleLabel: {
					display: true,
                    labelString: 'Volume [mL]'
				}
			}]
	    },
              legend : {
		  display: false},
	      spanGaps: true
	  }
    });


    var ctx_flow = document.getElementById('flow_chart');
    chart_flow = new Chart(ctx_flow, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                data: [],
                label: "Var1",
                borderColor: "rgb(51,99,255)",
                fill: false
            },
		       //{
			//   data: [],
			//   label: "Old",
			//   borderColor: "#FFFF00",
			//   fill: false
		       //},
            ]
          },
          options: {
            title: {
              display: true,
              text: 'Flow [mL/min]'
            },
            scales: {
		xAxes: [{
		    
                ticks: {
                    beginAtZero: true,
		    maxTicksLimit: 12,
		    maxRotation: 0,
		    display: true,
		},
		scaleLabel:{
		    display: true,
		    labelString: 'Seconds',
                },
                //ticks: {
                //    beginAtZero: true,
		//    maxTicksLimit: 5,
		//    maxRotation: 0
                //},
            }],
		
			yAxes: [{
                ticks: {
                    beginAtZero: true,
                    suggestedMax: 25
                  },
				scaleLabel: {
					display: true,
                    labelString: 'Flow [mL/min]'
				}
			}]     
            },
                legend : {
                    display: false},
	      spanGaps: true
          }
    });


    

    
    for ( let i = 0 ; i < 61; i++ ) {
	chart_pressure.data.labels.push(i);
	chart_pressure.data.datasets[0].data.push(null);
	//chart_pressure.data.datasets[1].data.push(null);
	
	
	chart_flow.data.labels.push(i);
	chart_flow.data.datasets[0].data.push(null);
	//chart_flow.data.datasets[1].data.push(null);
	
	chart_volume.data.labels.push(i);
	chart_volume.data.datasets[0].data.push(null);
	//chart_volume.data.datasets[1].data.push(null);
	
    }
    //initChartVar();
});

