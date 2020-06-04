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
					    stepSize: 100, fontSize:25 }}]},
		  tooltips: {
		      callbacks: {
			  label: function(tooltipItem) {
			      //console.info(tooltipItem)
			      var label = 'Pressure ' + Math.round(tooltipItem.xLabel*10)/10 + ' [mbar]';
			      label += ' Volume ' + Math.round(tooltipItem.yLabel) + ' [ml]';
			      return label;
			  }
		      },
		      bodyFontSize: 18
		  }
		 }
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
					     stepSize: 100, fontSize: 25 }}]},
		   tooltips: {
		       callbacks: {
			   label: function(tooltipItem) {
			       //console.info(tooltipItem)
			       var label = 'Volume ' + Math.round(tooltipItem.xLabel) + ' [ml]';
			       label += ' Flow ' + Math.round(tooltipItem.yLabel) + ' [ml/min]';
			       return label;
			   }
		       },
		       bodyFontSize: 18
		   }
		  }
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
					     stepSize: 100, fontSize: 25 }}]},
		   tooltips: {
		       callbacks: {
			   label: function(tooltipItem) {
			       //console.info(tooltipItem)
			       var label = 'Pressure ' + Math.round(tooltipItem.xLabel*10)/10 + ' [mbar]';
			       label += ' Flow ' + Math.round(tooltipItem.yLabel) + ' [ml/min]';
			       return label;
			   }
		       },
		       bodyFontSize: 18
		   }
		  }
    });
});


