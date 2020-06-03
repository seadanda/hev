var pause_charts = false;
var current_timestamp = -1;

function togglePause(){
    if (pause_charts) pause_charts = false;
    else pause_charts = true;
}

function setChartXaxisRange(min,max){
    chart_volume.options.scales.xAxes[0].ticks.min = min;
    chart_volume.options.scales.xAxes[0].ticks.max = max;
    chart_flow.options.scales.xAxes[0].ticks.min = min;
    chart_flow.options.scales.xAxes[0].ticks.max = max;
    chart_pressure.options.scales.xAxes[0].ticks.min = min;
    chart_pressure.options.scales.xAxes[0].ticks.max = max;
}

function setGaugeValue(name, value){
    if (typeof obj != 'undefined') obj[name].data.datasets[0].gaugeData['setvalue'] = value;
}
function getGaugeValue(name){
    if (typeof obj != 'undefined') return obj[name].data.datasets[0].gaugeData['setvalue'];
    else return -1;
}
function getGaugeMinValue(name){
    if (typeof obj != 'undefined') return obj[name].data.datasets[0].gaugeLimits[0];
    else return 0;
}
function getGaugeMaxValue(name){
    if (typeof obj != 'undefined') return obj[name].data.datasets[0].gaugeLimits[obj[name].data.datasets[0].gaugeLimits.length-1];
    else return 0;
}

var rowid = 0;
function requestData() {
    $.ajax({
        url: '/last-data/'+rowid,
        success: function(data) {
            if (data.length == 0) {
                // we're not getting any new data from the hevserver
                console.log("Got no new data");
            } else
            {
                //when we load, we check what elements are present that we should fill
                // we should be doing this just once when we load the script but objects are undefined until this call, not sure why
                var fillTrends = Boolean( typeof chart_pressure != 'undefined' && typeof chart_flow != 'undefined' && typeof chart_volume != 'undefined');
                var fillLoops  = Boolean( typeof chart_PV != 'undefined' && typeof chart_PF != 'undefined' && typeof chart_VF != 'undefined' );
                /*
                // we have some data, let's fill first our readings with last point
                */

                //first point is last time in terms of time
                var point = data[0];
                var data_point_idx = -1;
                var cycle_point_idx = -1;
                var readback_point_idx = -1;
                rowid = point["ROWID"];

                for (let j = data.length -1 ; j >=0; j-- ){
                    if ( data[j]["payload_type"] == "DATA" ) data_point_idx = j;
                    if ( data[j]["payload_type"] == "CYCLE" ) cycle_point_idx = j;
                    if ( data[j]["payload_type"] == "READBACK" ) readback_point_idx = j;

                }
                var data_point = data_point_idx >= 0 ? data[data_point_idx] : null;
                var cycle_point = cycle_point_idx >= 0 ? data[cycle_point_idx] : null;
                var readback_point = readback_point_idx >= 0 ? data[readback_point_idx] : null;
                var readings = [ "pressure_buffer", "pressure_inhale","pressure_air_supply","pressure_air_regulated",
                            "pressure_o2_supply", "pressure_o2_regulated", "pressure_patient", "pressure_diff_patient", "fsm_state",
                            "fi02_percent", "inhale_exhale_ratio", "peak_inspiratory_pressure", "plateau_pressure",
                            "mean_airway_pressure", "peep", "inhaled_tidal_volume", "exhaled_tidal_volume",
                            "inhaled_minute_volume", "exhaled_minute_volume", "flow", "volume", "respiratory_rate"];
                for (let i = 0 ; i < readings.length; i++){
                    var gauge = document.getElementById("gauge_"+readings[i]);
                    var el = document.getElementById(readings[i]);
                    var val = null;
                    if ( data_point != null && readings[i] in data_point ) { val = data_point[readings[i]];}
                    else if ( cycle_point != null && readings[i] in cycle_point ) { val = cycle_point[readings[i]];}
                    else if ( readback_point != null && readings[i] in readback_point ) { val = readback_point[readings[i]];}
                    else continue;
                    if ( typeof obj != 'undefined' && gauge && ((readings[i]+"_gauge") in obj) ) {
                        obj[readings[i]+"_gauge"].data.datasets[0].gaugeData['value'] = val.toPrecision(4);
                    }
                    if (el ){
                        if (readings[i] == "inhale_exhale_ratio") {
                        	//var posColon = val.search(":");
                            var posColon = -1;
                        	if( posColon != -1 ) {
                    	        // already have colon...
                        	    el.innerHTML = val.toPrecision(4);
                        	}else{
                        	    var ratio = val;
                        	    if( ratio < 1 ){
                            		var invRatio = (1/ratio);
                            		invRatio.toFixed(1); // in case of 0.75 -> 1.3333333333333333333:1 formating problems
                            		el.innerHTML = invRatio.toPrecision(3).toString() + ":1";
                	            }else{
                            		el.innerHTML = "1:"+val.toPrecision(2);
                        	    }
                            }
                        }
                        else{           
                            el.innerHTML = val.toPrecision(4);
                        }
                    }
                }
                
                // get our current time stamp
                // get difference between it and last received to update plots
                var last_timestamp = data_point["timestamp"]/1000.0;
                var diff = 0;
                
                if (current_timestamp != -1) {
                    diff = last_timestamp - current_timestamp;
                }
                else{
                    diff = - last_timestamp;
                }
                // this is just for cycling test data
                // if ( last_timestamp < current_timestamp ) current_timestamp = last_timestamp - 1.00;
                

                /*
                // if charts exist we now update with all points received
                */
                
                if (fillTrends){
                    //update current plots with difference
                    for ( let i = 0 ; i < chart_pressure.data.datasets[0].data.length; i++){
                        chart_pressure.data.datasets[0].data[i]['x'] = chart_pressure.data.datasets[0].data[i]['x'] - diff;
                        chart_flow.data.datasets[0].data[i]['x'] = chart_flow.data.datasets[0].data[i]['x'] - diff;
                        chart_volume.data.datasets[0].data[i]['x'] = chart_volume.data.datasets[0].data[i]['x'] - diff;
                    }
                
                    //add new points
                    //keep track of timestamp to make sure we're not mixing it up
                    var running_timestamp = -1;
                    var running_rowid = 0;
                    for (let ip = data.length-1 ; ip >= 0; ip--){
                        var point = data[ip];
                        if (point["payload_type"] != "DATA") {
                            continue;
                        }
                        var seconds = point["timestamp"]/1000;
                        //must be greater than our last stopped point
                        if (seconds < current_timestamp) continue;
                	    // this is a hack for the test data so that we can cycle data
                        //if ( seconds - current_timestamp > 1.0) { console.log("Current Timestamp: ",current_timestamp, " against ",seconds);}
                	    //protect against bogus timestamps, skip those that are earlier than we already have
                	    if (running_timestamp == -1 || seconds > running_timestamp  )
                	    {
                    		// get difference between last time stamp and this and apply to existing points
                    		chart_pressure.data.datasets[0].data.push({x : seconds - last_timestamp, y : point["pressure_patient"]});
                    		chart_flow.data.datasets[0].data.push({ x : seconds - last_timestamp, y : point["flow"]});
                    		chart_volume.data.datasets[0].data.push({ x : seconds - last_timestamp, y : point["volume"]});
                            running_timestamp = seconds;
                        }
                    }
                  	while(chart_pressure.data.datasets[0].data.length > 10000) chart_pressure.data.datasets[0].data.shift();
                   	while(chart_flow.data.datasets[0].data.length > 10000) chart_flow.data.datasets[0].data.shift();
                    while(chart_volume.data.datasets[0].data.length > 10000) chart_volume.data.datasets[0].data.shift();

                    current_timestamp = last_timestamp;
                    if (!pause_charts){
        		        chart_pressure.update(0);
                		chart_flow.update(0);
                		chart_volume.update(0);
                    }
                }
                // fill loop plots
                if ( fillLoops ) {

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
                    // now run chart updates: outside loop (only need to update plot every 0.2s)
                    chart_PV.update();
                    chart_VF.update();
                    chart_PF.update();
                    }
                }
                
                if (typeof obj != 'undefined' && "fi02_percent_gauge" in obj) obj["fi02_percent_gauge"].update();
                if (typeof obj != 'undefined' && "p_plateau_gauge" in obj) obj["p_plateau_gauge"].update();
            }
        },
        cache: false
    });
    // call it again after time in ms
    chart_display_interval = setTimeout(requestData, 200);
}

requestData();
