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

function chartParamLoop(chartName) {
    // values for all plots
    let gridColor     = "hsla(0, 0%, 75%, 0.4)";
    let zeroGridColor = "hsla(0, 0%, 90%, 1.0)";

    // values for specific plots
    let plotColor;
    // chosen to have the same saturation and luminosity, tweak to taste
    if( chartName == "inhale" ) plotColor = "hsla(221, 100%, 70%, 1)";
    if( chartName == "exhale" ) plotColor = "hsla(17, 100%, 70%, 1)";

    // start with global params for all plots
    let params = {
        dataset : {
            borderColor          : plotColor,
            backgroundColor      : plotColor,
            borderWidth          : 4,
            fill                 : false,
            showLine             : true,
        },
        gridLines : {
            display       : true,
            color         : gridColor,
            zeroLineColor : zeroGridColor
        }
    };

    return params;
}


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
    let paramInhale = chartParamLoop("inhale");
    let paramExhale = chartParamLoop("exhale");
    chart_PV = new Chart(ctx_PV, {
        type: 'scatter',
        data: {datasets: [{data: [],
                           label: "Inhale",
                           borderColor         : paramInhale.dataset.borderColor,
                           backgroundColor     : paramInhale.dataset.backgroundColor,
                           borderWidth         : paramInhale.dataset.borderWidth,
                           fill                : paramInhale.dataset.fill,
                           showLine            : paramInhale.dataset.showLine
                          },
                          {data: [],
                           label: "Exhale : Pressure - Volume",
                           borderColor         : paramExhale.dataset.borderColor,
                           backgroundColor     : paramExhale.dataset.backgroundColor,
                           borderWidth         : paramExhale.dataset.borderWidth,
                           fill                : paramExhale.dataset.fill,
                           showLine            : paramExhale.dataset.showLine
                          }
                         ]},
        options: {elements: { point: { radius: 5}},
                  legend: { display: true, labels: {fontSize: 24, fontColor:"#cccccc" } },
                  scales: {xAxes: [{display: true,
                                    scaleLabel: { display: true, labelString: 'Pressure [mbar]', fontSize: 24, fontColor:"#cccccc"},
                                    gridLines : {
                                        display:       paramInhale.gridLines.display,
                                        color:         paramInhale.gridLines.color,
                                        zeroLineColor: paramInhale.gridLines.zeroLineColor
                                    },
                                    ticks: {min: 0, max: 35,
                                            stepSize: 5, fontSize: 25, fontColor:"#cccccc" }}],
                           yAxes: [{display: true,
                                    scaleLabel: { display: true, labelString: 'Volume [ml]', fontSize: 24, fontColor:"#cccccc"},
                                    gridLines : {
                                        display:       paramInhale.gridLines.display,
                                        color:         paramInhale.gridLines.color,
                                        zeroLineColor: paramInhale.gridLines.zeroLineColor
                                    },
                                    ticks: {min: 0, max: 800,
                                            stepSize: 100, fontSize:25, fontColor:"#cccccc" }}]},
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
                           borderColor         : paramInhale.dataset.borderColor,
                           backgroundColor     : paramInhale.dataset.backgroundColor,
                           borderWidth         : paramInhale.dataset.borderWidth,
                           fill                : paramInhale.dataset.fill,
                           showLine            : paramInhale.dataset.showLine
                          },
                          {data: [],
                           label: "Exhale : Volume - Flow",
                           borderColor         : paramExhale.dataset.borderColor,
                           backgroundColor     : paramExhale.dataset.backgroundColor,
                           borderWidth         : paramExhale.dataset.borderWidth,
                           fill                : paramExhale.dataset.fill,
                           showLine            : paramExhale.dataset.showLine
                          }]}
        ,options: {elements: { point: { radius: 5}},
                   legend: { display: true, labels: {fontSize: 24 , fontColor:"#cccccc"} },
                   scales: {xAxes: [{display: true,
                                     scaleLabel: { display: true, labelString: 'Volume [ml]', fontSize: 24, fontColor:"#cccccc"},
                                     gridLines : {
                                         display:       paramInhale.gridLines.display,
                                         color:         paramInhale.gridLines.color,
                                         zeroLineColor: paramInhale.gridLines.zeroLineColor
                                     },
                                     ticks: {min: 0, max: 800,
                                             stepSize: 100, fontSize: 25, fontColor:"#cccccc" }}],
                            yAxes: [{display: true,
                                     scaleLabel: { display: true, labelString: 'Flow [nL/H]', fontSize: 24, fontColor:"#cccccc"},
                                     gridLines : {
                                         display:       paramInhale.gridLines.display,
                                         color:         paramInhale.gridLines.color,
                                         zeroLineColor: paramInhale.gridLines.zeroLineColor
                                     },
                                     ticks: {min: -300, max: 300,
                                             stepSize: 100, fontSize: 25 , fontColor:"#cccccc"}}]},
                   tooltips: {
                       callbacks: {
                           label: function(tooltipItem) {
                               //console.info(tooltipItem)
                               var label = 'Volume ' + Math.round(tooltipItem.xLabel) + ' [ml]';
                               label += ' Flow ' + Math.round(tooltipItem.yLabel) + ' [nL/h]';
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
                           borderColor         : paramInhale.dataset.borderColor,
                           backgroundColor     : paramInhale.dataset.backgroundColor,
                           borderWidth         : paramInhale.dataset.borderWidth,
                           fill                : paramInhale.dataset.fill,
                           showLine            : paramInhale.dataset.showLine
                          },
                          {data: [],
                           label: "Exhale : Pressure - Flow",
                           borderColor         : paramExhale.dataset.borderColor,
                           backgroundColor     : paramExhale.dataset.backgroundColor,
                           borderWidth         : paramExhale.dataset.borderWidth,
                           fill                : paramExhale.dataset.fill,
                           showLine            : paramExhale.dataset.showLine
                          }]}
        ,options: {elements: { point: { radius: 5, fill: true}},
                   legend: { display: true, labels: {fontSize: 24, fontColor:"#cccccc", } },
                   scales: {xAxes: [{display: true,
                                     scaleLabel: { display: true, labelString: 'Pressure [mbar]', fontSize: 24, fontColor:"#cccccc",},
                                     gridLines : {
                                         display:       paramInhale.gridLines.display,
                                         color:         paramInhale.gridLines.color,
                                         zeroLineColor: paramInhale.gridLines.zeroLineColor
                                     },
                                     ticks: {min: 0, max: 35 ,
                                             stepSize: 5  , fontSize: 25, fontColor:"#cccccc" }}],
                            yAxes: [{display: true,
                                     scaleLabel: { display: true, labelString: 'Flow [nL/H]', fontSize: 24, fontColor:"#cccccc",},
                                     gridLines : {
                                         display:       paramInhale.gridLines.display,
                                         color:         paramInhale.gridLines.color,
                                         zeroLineColor: paramInhale.gridLines.zeroLineColor
                                     },
                                     ticks: {min: -300, max: 300,
                                             stepSize: 100, fontSize: 25, fontColor:"#cccccc" }}]},
                   tooltips: {
                       callbacks: {
                           label: function(tooltipItem) {
                               //console.info(tooltipItem)
                               var label = 'Pressure ' + Math.round(tooltipItem.xLabel*10)/10 + ' [mbar]';
                               label += ' Flow ' + Math.round(tooltipItem.yLabel) + ' [nL/H]';
                               return label;
                           }
                       },
                       bodyFontSize: 18
                   }
                  }
    });
});
