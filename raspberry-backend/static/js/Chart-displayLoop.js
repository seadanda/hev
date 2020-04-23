//3 loop displays: Pressure-Volume, Flow-Volume and Pressure-Flow.
var chart_PV;
var chart_FV;
var chart_PF;

/**
 * Request data from the server, add it to the graph and set a timeout
 * to request again
 */
function requestChartVar() {
    $.ajax({
        url: '/live-data',
        success: function(point) {
	    if( chart_PV.data.datasets[0].data.length > 100 ){
		chart_PV.data.datasets[0].data.shift();
		chart_FV.data.datasets[0].data.shift();
		chart_PF.data.datasets[0].data.shift();
	    }
	    // point labelled as: (stealing definitions from Chart-display.js)
	    // Pressure = pressure_buffer
	    // Flow = pressure_inhale ??
	    // Volume = temperature_buffer !!?
	    chart_PV.data.datasets[0].data.push({x: point["temperature_buffer"],
						 y: point["pressure_buffer"]});
	    chart_FV.data.datasets[0].data.push({x: point["temperature_buffer"],
						 y: point["pressure_inhale"]});
	    chart_PF.data.datasets[0].data.push({x: point["pressure_inhale"],
						 y: point["pressure_buffer"]});
	    chart_PV.update();
	    chart_FV.update();
	    chart_PF.update();
	    
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
			   label: "Loop Pressure:Volme",
			   borderColor: "rgb(51,99,255)",
			   fill: false }]}
	,options: {scales: {xAxes: [{type: 'linear',
				     position: 'bottom',
				     lablelString: 'temperature_buffer??',
				     display: true,
				     ticks: {min: -1000, max: 1500, 
					     stepSize: 500 }}],
			    yAxes: [{type: 'linear',
				     position: 'left',
				     lablelString: 'pressure_buffer??',
				     display: true,
				     ticks: {min: 0, max: 25, 
					     stepSize: 5 }}]}}
    });

    var ctx_FV = document.getElementById('flow_volume_chart');
    chart_FV = new Chart(ctx_FV, {
        type: 'scatter',
        data: {datasets: [{data: [],
			   label: "Loop Flow:Volme",
			   borderColor: "rgb(51,99,255)",
			   fill: false }]}
	,options: {scales: {xAxes: [{type: 'linear',
				     position: 'bottom',
				     lablelString: 'temperature_buffer??',
				     display: true,
				     ticks: {min: -1000, max: 1500, 
					     stepSize: 500 }}],
			    yAxes: [{type: 'linear',
				     position: 'left',
				     lablelString: 'pressure_inhale??',
				     display: true,
				     ticks: {min: 0, max: 300, 
					     stepSize: 100 }}]}}
    });
	
    var ctx_PF = document.getElementById('pressure_flow_chart');
    chart_PF = new Chart(ctx_PF, {
        type: 'scatter',
        data: {datasets: [{data: [],
			   label: "Loop Pressure:Flow",
			   borderColor: "rgb(51,99,255)",
			   fill: false }]}
	,options: {scales: {xAxes: [{type: 'linear',
				     position: 'bottom',
				     lablelString: 'pressure_inhale??',
				     display: true,
				     ticks: {min: 0, max: 300, 
					     stepSize: 100 }}],
			    yAxes: [{type: 'linear',
				     position: 'left',
				     lablelString: 'pressure_buffer??',
				     display: true,
				     ticks: {min: 0, max: 25, 
					     stepSize: 5 }}]}}
    });
});


