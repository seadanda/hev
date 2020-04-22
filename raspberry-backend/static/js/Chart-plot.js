var chart;
var refreshIntervalId;
var initial_xaxis = [];
var initial_yaxis_var1 = [];
var initial_yaxis_var2 = [];
var time_x;

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */


function last_results() {
  $.getJSON({
      url: '/last_N_data',
      success: function(data) {
        for (i=0; i<data.length; i++) {
          // terrible hack to show the time in reverse order
          time_x = (-i/5).toFixed(2)
          initial_xaxis.push(time_x);
          //initial_xaxis.push(data[i]["timestamp"]);
          initial_yaxis_var1.push(data[i]["pressure_buffer"]);
          initial_yaxis_var2.push(data[i]["pressure_inhale"]);
        }
        //reverse because data is read from the other way
        initial_xaxis.reverse();
        initial_yaxis_var1.reverse();
        initial_yaxis_var2.reverse();
      },
      cache: false
  });
}

last_results();


function requestDataVar1(var1, var2) {
    $.ajax({
        url: '/live-data',
        success: function(point) {

            if(chart.data.datasets[0].data.length > 300){
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }

            if(chart.data.datasets[1].data.length > 300){
                //chart.data.labels.shift();
                chart.data.datasets[1].data.shift();
            }

            for (var i=0; i<300; i++) {
              var x = chart.data.labels[i] - 0.20 ;
              chart.data.labels[i] = x.toFixed(1);
          }

            // add the point
            //chart.data.labels.push(point.created_at);
            chart.data.labels.push(0);
            chart.data.datasets[0].data.push(point[var1]);
            chart.data.datasets[1].data.push(point[var2]);
            
            chart.update();
        },
        cache: false
    });
    // call it again after one second
    refreshIntervalId = setTimeout(requestDataVar1, 200, var1, var2);
}

/*
function requestDataVar(var1, var2) {
    $.ajax({
        url: '/live-data',
        success: function(point) {

            if(chart_new.data.datasets[0].data.length > 300){
                chart_new.data.labels.shift();
                chart_new.data.datasets[0].data.shift();
            }

            if(chart_new.data.datasets[1].data.length > 300){
                //chart.data.labels.shift();
                chart_new.data.datasets[1].data.shift();
            }

            // add the point
            chart_new.data.labels.push(0);
            chart_new.data.datasets[0].data.push(point[var1]);
            chart_new.data.datasets[1].data.push(point[var2]);
            
            chart_new.update();
        },
        cache: false
    });
    // call it again after one second
    //setTimeout(requestDataVar, 1000, var1, var2);
}
*/




$(document).ready(function() {
    var ctx = document.getElementById('pressure_air_supply');
  chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: initial_xaxis,
            datasets: [{ 
      label: 'A',
      yAxisID: 'A',
                data: initial_yaxis_var1,
                label: "Buffer",
                borderColor: "#0000FF",
                fill: false,
              },{ 
      label: 'B',
      yAxisID: 'B',
                data: initial_yaxis_var2,
                label: "Inhale",
                borderColor: "#000000",
                fill: false,
              } 
            ]
          },
          options: {
            title: {
              display: false,
              text: 'pressure_air_supply'
            },
            scales: {
		xAxes: [{
            //type: 'time',
            time: {
			        unit: 'second',
			        displayFormat: 'second',
              type: 'realtime'
                    },
		    ticks: {
          fontSize: 25,
			    maxTicksLimit: 5,
			    maxRotation: 0
		    }
		}],
                yAxes: [{
                   id: 'A',
                   type: 'linear',
                   position: 'left',
		    ticks: {
                  fontColor: "#0000FF", // this here
                  fontSize: 25,
                },
                }, {
                    id: 'B',
                    type: 'linear',
                    position: 'right',
		    ticks: {
                  fontColor: "#000000", // this here
                  fontSize: 25,
                },
		}
		       ]
	  },
		legend : {
      display: true,
      "labels": {
        "fontSize": 20,
    }        } 
        }
  });
    requestDataVar1("pressure_buffer", "pressure_inhale");
});




// Function to parse the selection from a multiselect
function getSelectValues(select) {
  var result = [];
  var options = select && select.options;
  var opt;

  for (var i=0, iLen=options.length; i<iLen; i++) {
    opt = options[i];

    if (opt.selected) {
      result.push(opt.value || opt.text);
    }
  }
  return result;
}




// Function runs on chart type select update
function updateChartType() {

    
    var selection = document.multiselect('#chart_variables')._item
    var selection_results = getSelectValues(selection)
    console.log("selected variables: ", selection_results);

    //here we destroy/delete the old or previous chart and redraw it again
    clearInterval(refreshIntervalId);
    chart.destroy();
    var ctx = document.getElementById('pressure_air_supply');

  chart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{ 
      label: 'A',
      yAxisID: 'A',
                data: [],
                label: selection_results[0],
                borderColor: "#0000FF",
                fill: false,
              },{ 
      label: 'B',
      yAxisID: 'B',
                data: [],
                label: selection_results[1],
                borderColor: "#000000",
                fill: false,
              } 
            ]
          },
          options: {
            title: {
              display: false,
              text: 'pressure_air_supply'
            },
            scales: {
		xAxes: [{
                    //type: 'time',
                    time: {
			unit: 'second',
			displayFormat: 'second'
                    },
		    ticks: {
			maxTicksLimit: 5,
			maxRotation: 0
		    }
		}],
                yAxes: [{
                   id: 'A',
                   type: 'linear',
                    position: 'left',
		    color: "#0000FF",
		    ticks: {
			fontColor: "#0000FF", // this here
                    },

                }, {
                   id: 'B',
                   type: 'linear',
                    position: 'right',
		    color: "#000000",
		    ticks: {
                  fontColor: "#000000", // this here
                },
                }]
	        },
		legend : {
        display: true,
        "labels": {
          "fontSize": 20,
      }        } 
          }



   });
    requestDataVar1(selection_results[0], selection_results[1]);
}; // ends update button

document.multiselect('#chart_variables')
                        
            .setCheckBoxClick("checkboxAll", function(target, args) {
                    console.log("Checkbox 'Select All' was clicked and got value ", args.checked);})
            .setCheckBoxClick("pressure_buffer", function(target, args) {
                    console.log("Checkbox for item with value '1' was clicked and got value ", args.checked); });

document.multiselect('#chart_variables')
      .deselectAll();

