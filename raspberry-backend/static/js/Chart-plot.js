var chart;
var refreshIntervalId;
var initial_xaxis = [];
var initial_yaxis_var1 = [];
var initial_yaxis_var2 = [];
var time_x;

var updated_xaxis = [];
var updated_yaxis_var1 = [];
var updated_yaxis_var2 = [];

/**
 * Request last N data from the server, add it to the graph
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

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */

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
  // call it again after 200 ms
  refreshIntervalId = setTimeout(requestDataVar1, 200, var1, var2);
}





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
        }, 
      { 
        label: 'B',
        yAxisID: 'B',
        data: initial_yaxis_var2,
        label: "Inhale",
        borderColor: "#000000",
        fill: false,
      }]
    },
    options: {
      elements: {
        point: { 
            radius: 0
        }
      },       
      responsive: true,
      stroke: {
          curve: 'smooth'
      },
      tooltips: {
        enabled: false
      },
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
          }, 
        {
          id: 'B',
          type: 'linear',
          position: 'right',
		      ticks: {
                  fontColor: "#000000", // this here
                  fontSize: 25,
          },
		    }]
	    },
		  legend : {
        display: true,
        "labels": {
        "fontSize": 20,
        }
      } 
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


function updated_last_results(var1, var2) {
  $.getJSON({
      url: '/last_N_data',
      success: function(data) {
        for (i=0; i<data.length; i++) {
          // terrible hack to show the time in reverse order
          time_x = (-i/5).toFixed(2)
          updated_xaxis.push(time_x);
          //initial_xaxis.push(data[i]["timestamp"]);
          updated_yaxis_var1.push(data[i]["pressure_buffer"]);
          updated_yaxis_var2.push(data[i]["pressure_buffer"]);
        }
        console.log(updated_xaxis);
        //reverse because data is read from the other way
        updated_xaxis.reverse();
        updated_yaxis_var1.reverse();
        updated_yaxis_var2.reverse();
      },
      cache: false
  });
}



// Function runs on chart type select update
function updateChartType() {
  var selection = document.multiselect('#chart_variables')._item
  var selection_results = getSelectValues(selection)
  console.log("selected variables: ", selection_results);
  chart.destroy();
  //chart.data.labels = [];
  //chart.data.datasets[0].data = [];
  //chart.data.datasets[1].data = [];
  //here we destroy/delete the old or previous chart and redraw it again
  updated_xaxis = [];
  updated_yaxis_var1 = [];
  updated_yaxis_var2 = [];
  clearInterval(refreshIntervalId);
  updated_last_results(selection_results[0], selection_results[1]);
  

  var ctx = document.getElementById('pressure_air_supply');
  chart = new Chart(ctx, {
    type: 'line',
    data: {
      labels: updated_xaxis,
      datasets: [{ 
        label: 'A',
        yAxisID: 'A',
        data: updated_yaxis_var1,
        label: selection_results[0],
        borderColor: "#0000FF",
        fill: false,
      },
      { 
        label: 'B',
        yAxisID: 'B',
        data: updated_yaxis_var2,
        label: selection_results[1],
        borderColor: "#000000",
        fill: false,
      }]
    },
      options: {
        elements: {
          point: { 
              radius: 0
          }
        },        
        responsive: true,
        stroke: {
            curve: 'smooth'
        },
        tooltips: {
          enabled: false
        },
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
          }, 
          {
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
          }
        } 
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

