var chart;
var refreshIntervalId;
var initial_yaxis_var1 = [];
var initial_yaxis_var2 = [];

var updated_xaxis = [];
var updated_yaxis_var1 = [];
var updated_yaxis_var2 = [];


var current_timestamp = -1;


function setChartProtXaxisRange(min,max){
    chart.options.scales.xAxes[0].ticks.min = min;
    chart.options.scales.xAxes[0].ticks.max = max;   
}


/**
 * Request last N data from the server, add it to the graph
 */
function init_results(){
  $.getJSON({
    url: '/last_N_data',
    success: function(data) {
      var timestamp = 0;
        for (i=0; i<data.length; i++) {
          var seconds = data[i]["timestamp"]/1000;
          if (i==data.length-1) timestamp = seconds;
          if ( seconds == "" ) continue;
          initial_yaxis_var1.push({x : seconds, y : data[i]["airway_pressure"]});
          initial_yaxis_var2.push({x : seconds, y : data[i]["volume"]});
        }
        //reverse because data is read from the other way
        initial_yaxis_var1.reverse();
        initial_yaxis_var2.reverse();
        console.log('init results, timestamp: ',timestamp);
        for ( let i = 0 ; i < initial_yaxis_var1.length; i++){
          console.log('filling up with ',initial_yaxis_var1[i]['x'], ' - ',timestamp);
          initial_yaxis_var1[i]['x'] = initial_yaxis_var1[i]['x'] - timestamp;
          initial_yaxis_var2[i]['x']   = initial_yaxis_var2[i]['x']   - timestamp;
        }
    },
    cache: false
  });
}


function requestDataVar1(var1, var2) {
  $.ajax({
      url: '/live-data',
      success: function(point) {

        var seconds = point["timestamp"]/1000;

        // this is a hack for the test data so that we can cycle data
        if ( seconds < current_timestamp ) current_timestamp = seconds - 0.20;
        
        //protect against bogus timestamps, skip those that are earlier than we already have
        if (current_timestamp == -1 || seconds > current_timestamp ) {
          // get difference between last time stamp and this and apply to existing points
          var diff = 0;
          if ( current_timestamp == -1 ){
              diff = seconds;
          }
          else {
              diff = seconds - current_timestamp; //FUTURE: restore this line in case not using simulated data
          }
          current_timestamp = seconds;
          if(chart.data.datasets[0].data.length > 300){
                          chart.data.datasets[0].data.shift();
          }
          
          if(chart.data.datasets[1].data.length > 300){
            chart.data.datasets[1].data.shift();
          }                  
 
          for ( let i = 0 ; i < initial_yaxis_var1.length; i++){
              chart.data.datasets[0].data[i]['x'] = chart.data.datasets[0].data[i]['x'] - diff;
              chart.data.datasets[1].data[i]['x'] = chart.data.datasets[1].data[i]['x'] - diff;
          }
  
          chart.data.datasets[0].data.push({x : 0, y : point[var1]});
          chart.data.datasets[1].data.push({ x : 0, y : point[var2]});
          
          chart.update();
        }

      },
      cache: false
  });
  // call it again after time in ms
  refreshIntervalId = setTimeout(requestDataVar1, 200, var1, var2);
}

requestDataVar1("airway_pressure", "volume");



$(document).ready(function() {
  var ctx = document.getElementById('pressure_air_supply');
  chart = new Chart(ctx, {
    type: 'scatter',
    data: {
      labels: [],
      datasets: [{ 
        label: 'A',
        yAxisID: 'A',
        data: initial_yaxis_var1,
        label: "Pressure",
        borderColor: "#0000FF",
        fill: false,
        showLine: true,
        }, 
      { 
        label: 'B',
        yAxisID: 'B',
        data: initial_yaxis_var2,
        label: "Volume",
        borderColor: "#000000",
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
          updated_yaxis_var1.push(data[i]["airway_pressure"]);
          updated_yaxis_var2.push(data[i]["airway_pressure"]);
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
              fontSize: 25,
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
              fontSize: 25,
            },
          }, 
          {
            id: 'B',
            type: 'linear',
            position: 'right',
		        color: "#000000",
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
   requestDataVar1(selection_results[0], selection_results[1]);
}; // ends update button

document.multiselect('#chart_variables')
                        
            .setCheckBoxClick("checkboxAll", function(target, args) {
                    console.log("Checkbox 'Select All' was clicked and got value ", args.checked);})
            .setCheckBoxClick("pressure_buffer", function(target, args) {
                    console.log("Checkbox for item with value '1' was clicked and got value ", args.checked); });

document.multiselect('#chart_variables')
      .deselectAll();

