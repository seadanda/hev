// © Copyright CERN, Riga Technical University and University of Liverpool 2020.
// All rights not expressly granted are reserved. 
// 
// This file is part of hev-sw.
// 
// hev-sw is free software: you can redistribute it and/or modify it under
// the terms of the GNU General Public Licence as published by the Free
// Software Foundation, either version 3 of the Licence, or (at your option)
// any later version.
// 
// hev-sw is distributed in the hope that it will be useful, but WITHOUT
// ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
// FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public Licence
// for more details.
// 
// You should have received a copy of the GNU General Public License along
// with hev-sw. If not, see <http://www.gnu.org/licenses/>.
// 
// The authors would like to acknowledge the much appreciated support
// of all those involved with the High Energy Ventilator project
// (https://hev.web.cern.ch/).


var chart;
var refreshIntervalId;
var updateRefreshIntervalId;

var initial_yaxis_var1 = [];
var updated_yaxis_var1 = [];


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
          initial_yaxis_var1.push({x : seconds, y : data[i]["pressure_patient"]});
        }
        //reverse because data is read from the other way
        initial_yaxis_var1.reverse();
        console.log('init results, timestamp: ',timestamp);
        for ( let i = 0 ; i < initial_yaxis_var1.length; i++){
          console.log('filling up with ',initial_yaxis_var1[i]['x'], ' - ',timestamp);
          initial_yaxis_var1[i]['x'] = initial_yaxis_var1[i]['x'] - timestamp;
        }        
    },
    cache: false
  });
}

/*
document.getElementById("pressure_buffer").innerHTML = (data.pressure_buffer).toFixed(2);
document.getElementById("pressure_inhale").innerHTML = (data.pressure_inhale).toFixed(2);
//document.getElementById("temperature_buffer").innerHTML = (data.temperature_buffer).toFixed(2);
document.getElementById("pressure_air_supply").innerHTML = (data.pressure_air_supply).toFixed(2);
document.getElementById("pressure_air_regulated").innerHTML = (data.pressure_air_regulated).toFixed(2);
document.getElementById("pressure_o2_supply").innerHTML = (data.pressure_o2_supply).toFixed(2);
document.getElementById("pressure_o2_regulated").innerHTML = (data.pressure_o2_regulated).toFixed(2);
document.getElementById("pressure_patient").innerHTML = (data.pressure_patient).toFixed(2);
document.getElementById("pressure_diff_patient").innerHTML = (data.pressure_diff_patient).toFixed(2);	
document.getElementById("fsm_state").innerHTML = data.fsm_state;
document.getElementById("airway_pressure").innerHTML = (data.airway_pressure).toFixed(2);	
document.getElementById("volume").innerHTML = (data.volume).toFixed(2);	
document.getElementById("flow").innerHTML = (data.flow).toFixed(2);	
document.getElementById("data_type").innerHTML = data.data_type;
document.getElementById("timestamp").innerHTML = (data.timestamp/1000).toFixed(2);
document.getElementById("version").innerHTML = data.version; 
//document.getElementById("version").innerHTML = (data.version).toFixed(2); //Commented because not included in the html part
*/
function requestDataVar1(var1) {
  $.ajax({
      url: '/last-data',
      success: function(point) {
        var readings = [ "pressure_buffer", "pressure_inhale","pressure_air_supply","pressure_air_regulated",
        "pressure_o2_supply", "pressure_o2_regulated", "pressure_patient", "pressure_diff_patient", "fsm_state", "volume", "flow", "airway_pressure","fsm_state",
        "version","data_type","timestamp"];
        for (let i = 0 ; i < readings.length; i++){
          var el = document.getElementById(readings[i]);
          var val = point[readings[i]];
          if (el && val){
            if(readings[i] == "timestamp") el.innerHTML = (val/1000).toFixed(2);
            else if (readings[i] == "version" ) el.innerHTML = val;
            else if (readings[i] == "fsm_state") el.innerHTML = "<small>" + val + "</small>";
            else el.innerHTML = val.toFixed(2);
              }
          }

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
              diff = seconds - current_timestamp; 
          }
          current_timestamp = seconds;
          if(chart.data.datasets[0].data.length > 300){
                          chart.data.datasets[0].data.shift();
          }

          
          for ( let i = 0 ; i < initial_yaxis_var1.length; i++){
              chart.data.datasets[0].data[i]['x'] = chart.data.datasets[0].data[i]['x'] - diff;
          }
  
          chart.data.datasets[0].data.push({x : 0, y : point[var1]});
          
          chart.update();
        }

      },
      cache: false
  });
  // call it again after time in ms
  refreshIntervalId = setTimeout(requestDataVar1, 200, var1);
}




$(document).ready(function() {
  var ctx = document.getElementById('pressure_air_supply_chart');
  chart = new Chart(ctx, {
    type: 'scatter',
    data: {
      labels: [],
      datasets: [{ 
        label: 'A',
        yAxisID: 'A',
        data: initial_yaxis_var1,
        label: "Pressure",
        borderColor: "#6496ff",
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
            min: -10,
            max: 0,
            fontSize: 25,
            maxTicksLimit: 5,
			      maxRotation: 0
		      },
                        gridLines : {
                            display: true,
                            color: "rgba(255,255,255,0.2)",
                            zeroLineColor: 'rgba(255,255,255,0.2)',
                        },
		    }],
        yAxes: [{
          id: 'A',
          type: 'linear',
          position: 'left',
		      ticks: {
             fontColor: "#6496ff", // this here
             fontSize: 25,
           },
                        gridLines : {
                            display: true,
                            color: "rgba(255,255,255,0.2)",
                            zeroLineColor: 'rgba(255,255,255,0.2)',
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
  requestDataVar1("pressure_patient");
});






function updated_init_results(var1){
  $.getJSON({
    url: '/last_N_data',
    success: function(data) {
      var timestamp = 0;
        for (i=0; i<data.length; i++) {
          var seconds = data[i]["timestamp"]/1000;
          if (i==data.length-1) timestamp = seconds;
          if ( seconds == "" ) continue;
          updated_yaxis_var1.push({x : seconds, y : data[i][var1]});
        }
        //reverse because data is read from the other way
        updated_yaxis_var1.reverse();
        console.log('init results, timestamp: ',timestamp);
        for ( let i = 0 ; i < updated_yaxis_var1.length; i++){
          console.log('filling up with ',updated_yaxis_var1[i]['x'], ' - ',timestamp);
          updated_yaxis_var1[i]['x'] = updated_yaxis_var1[i]['x'] - timestamp;
        }        
    },
    cache: false
  });
}


function updateRequestDataVar(var1) {
  $.ajax({
    url: '/last-data',
    success: function(point) {
      var readings = [ "pressure_buffer", "pressure_inhale","pressure_air_supply","pressure_air_regulated",
      "pressure_o2_supply", "pressure_o2_regulated", "pressure_patient", "pressure_diff_patient", "fsm_state", "volume", "flow", "airway_pressure","fsm_state",
      "version","data_type","timestamp"];
      for (let i = 0 ; i < readings.length; i++){
        var el = document.getElementById(readings[i]);
        var val = point[readings[i]];
        if (el && val){
          if(readings[i] == "timestamp") el.innerHTML = (val/1000).toFixed(2);
          else if (readings[i] == "version" ) el.innerHTML = val;
          else if (readings[i] == "fsm_state") el.innerHTML = "<small>" + val + "</small>";
          else el.innerHTML = val.toFixed(2);
            }
        }

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
                    
 
          for ( let i = 0 ; i < updated_yaxis_var1.length; i++){
              chart.data.datasets[0].data[i]['x'] = chart.data.datasets[0].data[i]['x'] - diff;
          }
          //console.log('UPDATED value ',point[var1], ' - ',timestamp);

  
          chart.data.datasets[0].data.push({x : 0, y : point[var1]});
          
          chart.update();
        }

      },
      cache: false
  });
  // call it again after time in ms
  updateRefreshIntervalId = setTimeout(updateRequestDataVar, 200, var1);
}



// Function runs on chart type select update
function updateChartType() {
  var selection_results = document.getElementById("chart_variables").value;
  console.log("selected variables: ", selection_results);
  chart.destroy();

  initial_yaxis_var1 = [];
  updated_yaxis_var1 = [];

  clearTimeout(refreshIntervalId);
  clearTimeout(updateRefreshIntervalId);
  //updated_init_results(selection_results);
  //updateRequestDataVar(selection_results);

  $(document).ready(function() {
    var ctx = document.getElementById('pressure_air_supply_chart');
    chart = new Chart(ctx, {
      type: 'scatter',
      data: {
        labels: [],
        datasets: [{ 
          label: 'A',
          yAxisID: 'A',
          data: updated_yaxis_var1,
          label: selection_results,
          borderColor: "#6496ff",
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
               fontColor: "#6496ff", // this here
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
  updateRequestDataVar(selection_results);
}; // ends update button


