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

//3 loop displays: Pressure-Volume, Flow-Volume and Pressure-Flow.
var chart_PV;
var chart_FV;
var chart_PF;

// last row accessed from the database
var last_row_accessed = 0;

// is the plot in the exhale part of the cycle
var inExhaleFill = false;
var inExhale = false;

var holdLoop = false; // global if loop plot to stop at end of this loop
var stopLoop = false; // global if loop plotting is stopped

// Manage running loop state
function HoldLoop() {
    console.info("Holding loop");
    holdLoop = true;
    stopLoop = false; // run to end of loop
    // toggle button state to allow a start or stop of the loop
    document.getElementById("LoopHoldButton").disabled = true;
    document.getElementById("LoopStartButton").disabled = false;
}
function RunLoop() {
    console.info("Running loop");
    holdLoop = false;
    stopLoop = false; // running again
    // toggle button state to allow a start or stop of the loop
    document.getElementById("LoopHoldButton").disabled = false;
    document.getElementById("LoopStartButton").disabled = true;
    // remove now stale data on plots
    chart_PV.data.datasets[0].data.length = 0;
    chart_VF.data.datasets[0].data.length = 0;
    chart_PF.data.datasets[0].data.length = 0;
    chart_PV.data.datasets[1].data.length = 0;
    chart_VF.data.datasets[1].data.length = 0;
    chart_PF.data.datasets[1].data.length = 0;
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
		    if( point["payload_type"] != "DATA" ) continue; // ignore all other data packets
		    // loop could be INHALE -> PAUSE -> EXHALE_FILL -> INHALE -> EXHALE -> BUFF_PRE_INHALE -> new loop
		    // may miss some of the shorter steps (PAUSE & BUFF_PRE_INHALE)
		    if( point["fsm_state"] == "EXHALE_FILL" ){ 
			inExhaleFill = true;  // in exhale part of loop
		    }
		    if( point["fsm_state"] == "EXHALE" ){ 
			inExhale = true;  // in exhale part of loop
		    }
		    if( point["fsm_state"] == "INHALE" && inExhale ) { // start of loop (exhale->inhale transition)
			inExhale = false;
			inExhaleFill = false;
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

			    chart_PV.data.datasets[1].data.length = 0;
			    chart_VF.data.datasets[1].data.length = 0;
			    chart_PF.data.datasets[1].data.length = 0;
			}
		    }
		    if( chart_PV.data.datasets[0].data.length > 1000 ){ // protect against not seeing a new loop
			chart_PV.data.datasets[0].data.length = 100;
			chart_VF.data.datasets[0].data.length = 100;
			chart_PF.data.datasets[0].data.length = 100;
			console.warning("Too many points to plot in inhale, is loop stopped?")
		    }
		    if( chart_PV.data.datasets[1].data.length > 1000 ){ // protect against not seeing a new loop
			chart_PV.data.datasets[1].data.length = 100;
			chart_VF.data.datasets[1].data.length = 100;
			chart_PF.data.datasets[1].data.length = 100;
			console.warning("Too many points to plot in exhale, is loop stopped?")
		    }
		    if( ! stopLoop ){
			// if the loop is running update the points
			var pressure =  point["pressure_patient"];
			var volume = point["volume"];
			var flow = point["flow"];

			// loops:
			if( (! inExhale) && (!inExhaleFill) ) {
			    // inhale points
			    chart_PV.data.datasets[0].data.push({x: pressure, y: volume});
			    chart_VF.data.datasets[0].data.push({x: volume, y: flow});
			    chart_PF.data.datasets[0].data.push({x: pressure, y: flow});
			}else{
			    // exhale points
			    chart_PV.data.datasets[1].data.push({x: pressure, y: volume});
			    chart_VF.data.datasets[1].data.push({x: volume, y: flow});
			    chart_PF.data.datasets[1].data.push({x: pressure, y: flow});
			}
		    }
		}
		// now run chart updates: outside loop (only need to update plot every 0.2s)
		chart_PV.update();
		chart_VF.update();
		chart_PF.update();
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
			   label: "Inhale",
			   borderColor: "rgb(100,150,255)",
			   pointBackgroundColor : "rgb(100,150,255)",
			   fill: false,
			   showLine: true },
			  {data: [],
			   label: "Exhale : Pressure - Volume",
			   borderColor: "rgb(255,150,100)",
			   pointBackgroundColor : "rgb(255,150,100)",
			   fill: false,
			   showLine: true }
			  ]},
	options: {elements: { point: { radius: 5}},
		  legend: { display: true, labels: {fontSize: 24 } },
		  scales: {xAxes: [{display: true,
				    scaleLabel: { display: true, labelString: 'Pressure [mbar]', fontSize: 24},
                    gridLines : {
                        display: true,
                        color: "rgba(255,255,255,0.2)",
                        zeroLineColor: 'rgba(255,255,255,0.2)',
                        },
				    ticks: {min: 0, max: 35,
					     stepSize: 5, fontSize: 25 }}],
			   yAxes: [{display: true,
				    scaleLabel: { display: true, labelString: 'Volume [ml]', fontSize: 24},
                    gridLines : {
                        display: true,
                        color: "rgba(255,255,255,0.2)",
                        zeroLineColor: 'rgba(255,255,255,0.2)',
                        },
				    ticks: {min: 0, max: 800,
					    stepSize: 100, fontSize:25 }}]}}
    });

    var ctx_VF = document.getElementById('flow_volume_chart');
    chart_VF = new Chart(ctx_VF, {
        type: 'scatter',
        data: {datasets: [{data: [],
			   label: "Inhale",
			   borderColor: "rgb(100,150,255)",
			   pointBackgroundColor : "rgb(100,150,255)",
			   fill: false,
			   showLine: true },
			  {data: [],
			   label: "Exhale : Volume - Flow",
			   borderColor: "rgb(255,150,100)",
			   pointBackgroundColor : "rgb(255,150,100)",
			   fill: false,
			   showLine: true }]}
	,options: {elements: { point: { radius: 5}},
		  legend: { display: true, labels: {fontSize: 24 } },
		scales: {xAxes: [{display: true,
				  scaleLabel: { display: true, labelString: 'Volume [ml]', fontSize: 24},
                    gridLines : {
                        display: true,
                        color: "rgba(255,255,255,0.2)",
                        zeroLineColor: 'rgba(255,255,255,0.2)',
                        },
				  ticks: {min: 0, max: 800,
					  stepSize: 100, fontSize: 25 }}],
			    yAxes: [{display: true,
				     scaleLabel: { display: true, labelString: 'Flow [ml/min]', fontSize: 24},
                    gridLines : {
                        display: true,
                        color: "rgba(255,255,255,0.2)",
                        zeroLineColor: 'rgba(255,255,255,0.2)',
                        },
				     ticks: {min: -300, max: 300,
					     stepSize: 100, fontSize: 25 }}]}}
    });

    var ctx_PF = document.getElementById('pressure_flow_chart');
    chart_PF = new Chart(ctx_PF, {
        type: 'scatter',
        data: {datasets: [{data: [],
			   label: "Inhale",
			   borderColor: "rgb(100,150,255)",
			   pointBackgroundColor : "rgb(100,150,255)",
			   fill: false,
			   showLine: true },
			  {data: [],
			   label: "Exhale : Pressure - Flow",
			   borderColor: "rgb(255,150,100)",
			   pointBackgroundColor : "rgb(255,150,100)",
			   fill: false,
			   showLine: true }]}
	,options: {elements: { point: { radius: 5, fill: true}},
		  legend: { display: true, labels: {fontSize: 24 } },
		   scales: {xAxes: [{display: true,
				     scaleLabel: { display: true, labelString: 'Pressure [mbar]', fontSize: 24},
                    gridLines : {
                        display: true,
                        color: "rgba(255,255,255,0.2)",
                        zeroLineColor: 'rgba(255,255,255,0.2)',
                        },
				     ticks: {min: 0, max: 35 ,
					     stepSize: 5  , fontSize: 25 }}],
			    yAxes: [{display: true,
				     scaleLabel: { display: true, labelString: 'Flow [ml/min]', fontSize: 24},
                    gridLines : {
                        display: true,
                        color: "rgba(255,255,255,0.2)",
                        zeroLineColor: 'rgba(255,255,255,0.2)',
                        },
				     ticks: {min: -300, max: 300,
					     stepSize: 100, fontSize: 25 }}]}}
    });
});


