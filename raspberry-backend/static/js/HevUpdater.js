var pause_charts = false;
var current_timestamp = -1;

var paused_pressure_data = Array(0);
var paused_flow_data = Array(0);
var paused_volume_data = Array(0);

function togglePause(){
    if ( pause_charts ) {
	pause_charts = false;
	// update charts from buffered data 
	if( paused_pressure_data.length > 0 ){
	    // .slice() to make shallow copy, rather than copy reference only
	    chart_pressure.data.datasets[0].data = paused_pressure_data.slice(); 
	    chart_flow.data.datasets[0].data = paused_flow_data.slice();
	    chart_volume.data.datasets[0].data = paused_volume_data.slice();
	    paused_pressure_data.length = 0;
	    paused_volume_data.length = 0;
	    paused_flow_data.length = 0;	    
	}
	chart_pressure.update()
	chart_flow.update()
	chart_volume.update()

	// turn off tooltips while running
	chart_pressure.options.tooltips.enabled = false;
	chart_flow.options.tooltips.enabled = false;	
	chart_volume.options.tooltips.enabled = false;
    } else {
	pause_charts = true;
	// copy charts to buffered data 
	// .slice() to make shallow copy, rather than copy reference only
	paused_pressure_data = chart_pressure.data.datasets[0].data.slice();
	paused_flow_data = chart_flow.data.datasets[0].data.slice();
	paused_volume_data = chart_volume.data.datasets[0].data.slice();

	// turn on tooltips while not running
	chart_pressure.options.tooltips.enabled = true;
	chart_flow.options.tooltips.enabled = true;
	chart_volume.options.tooltips.enabled = true;
    }
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
                var battery_point_idx = -1;
                var target_point_idx = -1;
                var personal_point_idx = -1;
                rowid = point["ROWID"];

                for (let j = data.length -1 ; j >=0; j-- ){
                    if ( data[j]["payload_type"] == "DATA" ) data_point_idx = j;
                    if ( data[j]["payload_type"] == "CYCLE" ) cycle_point_idx = j;
                    if ( data[j]["payload_type"] == "READBACK" ) readback_point_idx = j;
                    if ( data[j]["payload_type"] == "BATTERY" ) battery_point_idx = j;
                    if ( data[j]["payload_type"] == "TARGET" ) target_point_idx = j;
                    if ( data[j]["payload_type"] == "PERSONAL" ) personal_point_idx = j;

                }
                var data_point = data_point_idx >= 0 ? data[data_point_idx] : null;
                var cycle_point = cycle_point_idx >= 0 ? data[cycle_point_idx] : null;
                var readback_point = readback_point_idx >= 0 ? data[readback_point_idx] : null;
                var battery_point = battery_point_idx >= 0 ? data[battery_point_idx] : null;
                var target_point = target_point_idx >= 0 ? data[target_point_idx] : null;
                var personal_point = personal_point_idx >= 0 ? data[personal_point_idx] : null;

                if (battery_point != null) {
                    //get our elements
                    var powered = document.getElementById("powered");
                    powered.classList.add("transparent");
                      var full = document.getElementById("battery-full");
                    full.classList.add("transparent");
                      three_qtr = document.getElementById("battery-three-quarter");
                    three_qtr.classList.add("transparent");
                      var half = document.getElementById("battery-half");
                    half.classList.add("transparent");
                    var one_qtr = document.getElementById("battery-one-quarter");
                    one_qtr.classList.add("transparent");
                      var empty = document.getElementById("battery-empty");
                    empty.classList.add("transparent");
	            //console.log(battery_point);
                    // find the one to show
                    if (battery_point['ok']) { powered.classList.remove("transparent"); }
                    else if ( battery_point["bat"] && battery_point["bat85"] ) {full.classList.remove("transparent");}
                    else if ( battery_point["bat"] ) { three_qtr.classList.remove("transparent"); }
                    else  { empty.classList.remove("transparent"); }
                }

                var readings = [ "pressure_buffer", "pressure_inhale","pressure_air_supply",                "pressure_air_regulated",
                            "pressure_o2_supply", "pressure_o2_regulated", "pressure_patient", "pressure_diff_patient", "fsm_state",
                            "fiO2_percent", "inhale_exhale_ratio", "peak_inspiratory_pressure", "plateau_pressure",
                            "mean_airway_pressure", "peep", "inhaled_tidal_volume", "exhaled_tidal_volume",
                            "inhaled_minute_volume", "exhaled_minute_volume", "flow", "volume", "respiratory_rate"];
                //var targets = [ "peep", "fiO2_percent"];
		var targets = ["mode", "inspiratory_pressure", "ie_ratio", "volume", "respiratory_rate", "peep", "fiO2_percent", "inhale_time", "inhale_trigger_threshold", "exhale_trigger_threshold", "buffer_upper_pressure", "buffer_lower_pressure", "pid_gain"]
		var personals = ["name", "age", "sex", "height", "weight"]

		if (target_point != null){
		        for (let i = 0 ; i < targets.length; i++){
                    var el = document.getElementById("setting_"+targets[i]);
		    	    var val = null;
		    	    if ( target_point != null && targets[i] in target_point){
		    		    val = target_point[targets[i]];
		    	    }
		    	    if (el && val) {
                        el.classList.remove('text-red');
                        el.value = val.toPrecision(4);
                    }
		        }
		}

		if (personal_point != null){
			var name, age, sex, height, weight
		        for (let i = 0 ; i < personals.length; i++){
		    	    var el = document.getElementById("personal_"+personals[i]);
		    	    var val = null;
		    	    if ( personal_point != null && personals[i] in personal_point){
		    		    val = personal_point[personals[i]];
				    if (personals[i] == "name") name = val;
				    else if (personals[i] == "age") age = val;
				    else if (personals[i] == "sex") sex = val;
				    else if (personals[i] == "height") height = val;
				    else if (personals[i] == "weight") weight = val;
		    	    }
		    	    if (el && val) {
				    el.value = val;
			    }
		        }
		    	var el = document.getElementById("patient_info_top");
			el.innerHTML = name + ", "+age+", "+sex+", "+height+"cm, "+weight+"kg"; 
		}

        if (readback_point != null)
            {
                var vent_mode = document.getElementById("vent_mode");
        		$('.select-container').removeClass('text-red');
        		$('.select-container').addClass('text-white');
                var mode = readback_point['ventilation_mode'];
                vent_mode.value = mode;
                pickout.updated('.pickout');
            }
                
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
                
                // if we have no data point, we can just return now, no need to fill
                if (!data_point) return;
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
                
		// captive function to update either chart or paused data
		function updateChartData(pressure_data, flow_data, volume_data, diff, data, last_timestamp){
		    for ( let i = 0 ; i < pressure_data.length; i++){
                        pressure_data[i]['x'] -= diff;
                        flow_data[i]['x'] -= diff;
                        volume_data[i]['x'] -= diff;
                    }
		    for (let ip = data.length-1 ; ip >= 0; ip--){
			var point = data[ip];
			if (point["payload_type"] != "DATA") {
                            continue;
                        }
			var seconds = point["timestamp"]/1000;
                        //must be greater than our last stopped point
                        if (seconds < current_timestamp) continue;
                	// this is a hack for the test data so that we can cycle data
                	//protect against bogus timestamps, skip those that are earlier than we already have
                	if (running_timestamp == -1 || seconds > running_timestamp  ) {
                    	    // get difference between last time stamp and this and apply to existing points
                    	    pressure_data.push({x : seconds - last_timestamp, y : point["pressure_patient"]});
                    	    flow_data.push({ x : seconds - last_timestamp, y : point["flow"]});
                    	    volume_data.push({ x : seconds - last_timestamp, y : point["volume"]});
			    running_timestamp = seconds;
                        }
                    }
		    var maxLen = 10000; // probably can be smaller 
                    while( pressure_data.length > maxLen ) {
			pressure_data.shift();
			flow_data.shift();
			volume_data.shift();
		    }
		    return;
		}

                if (fillTrends){
                    //keep track of timestamp to make sure we're not mixing it up
                    var running_timestamp = -1;
                    var running_rowid = 0;

		    if ( pause_charts ){
			updateChartData(paused_pressure_data, 
					paused_flow_data, 
					paused_volume_data, 
					diff, data, last_timestamp);
		    } else {
			updateChartData(chart_pressure.data.datasets[0].data, 
					chart_flow.data.datasets[0].data, 
					chart_volume.data.datasets[0].data,
					diff, data, last_timestamp);
			// running so redraw now
        		chart_pressure.update();
                	chart_flow.update();
                	chart_volume.update();
		    }
                    current_timestamp = last_timestamp;
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
                
                if (typeof obj != 'undefined' && "fiO2_percent_gauge" in obj) obj["fiO2_percent_gauge"].update();
                if (typeof obj != 'undefined' && "p_plateau_gauge" in obj) obj["p_plateau_gauge"].update();
            }
        },
        cache: false
    });
    // call it again after time in ms
    chart_display_interval = setTimeout(requestData, 200);
}

requestData();
