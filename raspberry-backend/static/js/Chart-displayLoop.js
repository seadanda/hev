//3 loop displays: Pressure-Volume, Flow-Volume and Pressure-Flow.
var chart_PV;
var chart_FV;
var chart_PF;

// last row accessed from the database
var last_row_accessed = 0;

var holdLoop = false; // global if loop plot to stop at end of this loop
var stopLoop = false; // global if loop plotting is stopped

// Manage running loop state
function HoldLoop() {
    console.info("Holding loop");
    holdLoop = true;
    stopLoop = false; // run on either to end of loop
    // toggle button state to allow a start or stop of the loop
    document.getElementById("LoopHoldButton").disabled = true;
    document.getElementById("LoopStartButton").disabled = false;
}
function RunLoop() {
    console.info("Running loop");
    holdLoop = false;
    stopLoop = false; // run on either to end of loop
    // toggle button state to allow a start or stop of the loop
    document.getElementById("LoopHoldButton").disabled = false;
    document.getElementById("LoopStartButton").disabled = true;
    // remove now stale data on plots
    chart_PV.data.datasets[0].data.length = 0;
    chart_VF.data.datasets[0].data.length = 0;
    chart_PF.data.datasets[0].data.length = 0;
    // now run chart updates
    chart_PV.update();
    chart_VF.update();
    chart_PF.update();
}


/**
 * Request new data from the server, add it to the graph and set a timeout
 * to request again
 */
function requestChartVar() {
    $.ajax({
        url: '/last-data/'+last_row_accessed,
        success: function(data) {
	    if (data.length > 0 ) {
		last_row_accessed = data[0]['ROWID'];
		if (stopLoop) {
		    return; // nothing to do if stopped
		}
		for ( let i = data.length-1 ; i >= 0; i--) {
		    var point = data[i];
		    if( point["fsm_state"] == 14 ) { // start of loop FIXME
			if( holdLoop ) {
			    stopLoop = true;
			    holdLoop = false;
			    window.createNotification({
				closeOnClick: 1,
				displayCloseButton: 0,
				positionClass: "nfc-bottom-right",
				showDuration: false,
				theme: "info"
			    })({
				title: "Loop plot on hold",
				message: "Loop plot held, press Restart Loop to resume"
			    });
			}else{
			    chart_PV.data.datasets[0].data.length = 0;
			    chart_VF.data.datasets[0].data.length = 0;
			    chart_PF.data.datasets[0].data.length = 0;
			}
		    }else if( chart_PV.data.datasets[0].data.length > 100 ){
			chart_PV.data.datasets[0].data.shift();
			chart_VF.data.datasets[0].data.shift();
			chart_PF.data.datasets[0].data.shift();
		    }
		    if( ! stopLoop ){ // skip updates if loop is stopped
			var pressure =  point["airway_pressure"];
			var volume = point["volume"];
			var flow = point["flow"];

			// to quote the AAMI:
			//For Pressure-Volume loops, the graph
			//is required to use delivered volume on the vertical axis
			//and airway pressure on the horizontal axis. Positive
			//values should increase in up/right directions. Every
			//breath resets the graph, setting the volume back at the
			//origin.

			//For Flow-Volume loops the graph is required to use flow
			//rate on the vertical axis and delivered volume on the
			//horizontal axis. Positive values should increase in the
			//up/right directions.  Every breath resets the graph,
			//setting the volume back at the origin. The document also
			//suggests that there could be another version using
			//exhalation flow, if possible.

			// loops:
			chart_PV.data.datasets[0].data.push({x: pressure, y: volume});
			chart_VF.data.datasets[0].data.push({x: volume, y: flow});
			chart_PF.data.datasets[0].data.push({x: pressure, y: flow});

			// now run chart updates
			chart_PV.update();
			chart_VF.update();
			chart_PF.update();
		    }
		}
	    }
	},
        cache: false
    });
    setTimeout(requestChartVar, 200);
}

requestChartVar()

$(document).ready(function() {
    var ctx_PV = document.getElementById('pressure_volume_chart');
    chart_PV = new Chart(ctx_PV, {
        type: 'scatter',
        data: {datasets: [{data: [],
			   label: "Pressure (x) [mbar]: Volume (y) [ml]",
			   borderColor: "rgb(51,99,255)",
			   pointBackgroundColor : "rgb(51,99,255)",
			   fill: false,
			showLine: true },
			  ]},
	options: {elements: { point: { radius: 5}},
		  scales: {xAxes: [{display: true,
				     ticks: {min: 0, max: 25,
					     stepSize: 5, fontSize: 25 }}],
			    yAxes: [{display: true,
				     ticks: {min: 0, max: 500,
					     stepSize: 100, fontSize:25 }}]}}
    });

    var ctx_VF = document.getElementById('flow_volume_chart');
    chart_VF = new Chart(ctx_VF, {
        type: 'scatter',
        data: {datasets: [{data: [],
			   label: "Volume (x) [ml]: Flow (y) [ml/min]",
			   borderColor: "rgb(51,99,255)",
			   pointBackgroundColor : "rgb(51,99,255)",
			   fill: false,
			showLine: true }]}
	,options: {elements: { point: { radius: 5}},
		scales: {xAxes: [{display: true,
				  ticks: {min: 0, max: 500,
					  stepSize: 100, fontSize: 25 }}],
			    yAxes: [{display: true,
				     ticks: {min: -1000, max: 1500,
					     stepSize: 500, fontSize: 25 }}]}}
    });

    var ctx_PF = document.getElementById('pressure_flow_chart');
    chart_PF = new Chart(ctx_PF, {
        type: 'scatter',
        data: {datasets: [{data: [],
			   label: "Pressure (x) [mbar]: Flow (y) [ml/min]",
			   borderColor: "rgb(51,99,255)",
			   pointBackgroundColor : "rgb(51,99,255)",
			   fill: false,
				showLine: true }]}
	,options: {elements: { point: { radius: 5, fill: true}},
		   scales: {xAxes: [{display: true,
				     ticks: {min: 0, max: 25 ,
					     stepSize: 5  , fontSize: 25 }}],
			    yAxes: [{display: true,
				     ticks: {min: -1000, max: 1500,
					     stepSize: 500, fontSize: 25 }}]}}
    });
});


