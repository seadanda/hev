#include "BreathingLoop.h"
#include "common.h"
/*
The Idea of this code is to unfold the FSM in two: one to assign the transitions and the second one to program the states.
*/

BreathingLoop::BreathingLoop()
{
    uint32_t tnow = static_cast<uint32_t>(millis());
    _calib_time = tnow;
    _fsm_time = tnow;
    _fsm_timeout = 1000;
    _ventilation_mode = VENTILATION_MODE::LAB_MODE_BREATHE;
    _bl_state = BL_STATES::IDLE;
    _running = false;
    _reset = false;
    _safe  = true;

    _peep = 5.0;

    initCalib();
    resetReadingSums();

    _total_cycle_duration[0] = _states_durations.buff_loaded
                       +_states_durations.buff_pre_inhale
                       +_states_durations.inhale
                       +_states_durations.pause
                       +_states_durations.exhale_fill
                       +_states_durations.exhale;
    _total_cycle_duration[2] = _total_cycle_duration[1] = _total_cycle_duration[0];

    _flow = 0;
    _volume = 0;
    _airway_pressure = 0;

    _pid.Kp = 0.004; // proportional factor
    _pid.Ki = 0.0010;   // integral factor
    _pid.Kd = 0.;   // derivative factor

    _pid.integral   = 0.;
    _pid.derivative = 0.;

    _pid.process_pressure = 0.;// Variable used to build the target pressure profile
    _pid.target_pressure = 0.;// Variable used to build the target pressure profile
    _pid.target_final_pressure = 10.; // Final pressure after the inhale pressure ramp up
    _pid.nsteps = 3; // Final pressure after the inhale pressure ramp up

    for(int i=0; i<RUNNING_AVG_READINGS; i++){
        _running_flows[i] = 0.0;
    }
    _running_index = 0;

    _inhale_trigger_threshold = 0.0005;  // abs flow ml/s
    _exhale_trigger_threshold = 0.1;  // 30% of peak

    _min_inhale_time = 150;
    _min_exhale_time = 300;
    _max_exhale_time = 30000;  // for mandatory cycle - changed to 30s for the sponteneous breath testing
}

BreathingLoop::~BreathingLoop()
{
;
}

uint8_t BreathingLoop::getFsmState()
{
    return static_cast<uint8_t>(_bl_state);
}

void BreathingLoop::updateReadings()
{
    // calc pressure every 1ms
    // create averages every 10ms
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _readings_time > _readings_timeout) {
        _readings_time = tnow;
        _readings_N++;

        _readings_sums.timestamp                = tnow;
#ifdef CHIP_ESP32
        _readings_sums.pressure_air_supply      += static_cast<float>(analogRead(pin_pressure_air_supply)    );
        _readings_sums.pressure_o2_supply       += static_cast<float>(analogRead(pin_pressure_o2_supply)     );
#endif
        _readings_sums.pressure_air_regulated   += static_cast<float>(analogRead(pin_pressure_air_regulated) );
        _readings_sums.pressure_buffer          += static_cast<float>(analogRead(pin_pressure_buffer)        );
        _readings_sums.pressure_inhale          += static_cast<float>(analogRead(pin_pressure_inhale)        );
        _readings_sums.pressure_patient         += static_cast<float>(analogRead(pin_pressure_patient)       );
        _readings_sums.temperature_buffer       += static_cast<float>(analogRead(pin_temperature_buffer)     );
        _readings_sums.pressure_o2_regulated    += static_cast<float>(analogRead(pin_pressure_o2_regulated)  );
        _readings_sums.pressure_diff_patient    += static_cast<float>(analogRead(pin_pressure_diff_patient)  );
 

    }

    // to make sure the readings correspond only to the same fsm mode
    if (_readings_reset) {
        resetReadingSums();
    } else if (tnow - _readings_avgs_time > _readings_avgs_timeout) {
        _readings_avgs.timestamp                = static_cast<uint32_t>(_readings_sums.timestamp);
        _readings_avgs.pressure_air_supply      = adcToMillibarFloat((_readings_sums.pressure_air_supply      / _readings_N));
        _readings_avgs.pressure_air_regulated   = adcToMillibarFloat((_readings_sums.pressure_air_regulated   / _readings_N));
        _readings_avgs.pressure_buffer          = adcToMillibarFloat((_readings_sums.pressure_buffer          / _readings_N), _calib_avgs.pressure_buffer       );
        _readings_avgs.pressure_inhale          = adcToMillibarFloat((_readings_sums.pressure_inhale          / _readings_N), _calib_avgs.pressure_inhale       );
        _readings_avgs.pressure_patient         = adcToMillibarFloat((_readings_sums.pressure_patient         / _readings_N), _calib_avgs.pressure_patient      );
        _readings_avgs.temperature_buffer       = adcToMillibarFloat((_readings_sums.temperature_buffer       / _readings_N), _calib_avgs.temperature_buffer    );
#ifdef HEV_FULL_SYSTEM                                         
        _readings_avgs.pressure_o2_supply       = adcToMillibarFloat((_readings_sums.pressure_o2_supply       / _readings_N));
        _readings_avgs.pressure_o2_regulated    = adcToMillibarFloat((_readings_sums.pressure_o2_regulated    / _readings_N));
        _readings_avgs.pressure_diff_patient    = adcToMillibarDPFloat((_readings_sums.pressure_diff_patient    / _readings_N),_calib_avgs.pressure_diff_patient) ;
#endif


        // add Oscar code here:
        if (getFsmState() == BL_STATES::INHALE){

                //TODO

                float _pressure_inhale = adcToMillibarFloat((_readings_sums.pressure_inhale          / _readings_N), _calib_avgs.pressure_inhale     );

                doPID(3, _pid.target_final_pressure, _pressure_inhale, _valve_inhale_PID_percentage, _airway_pressure, _volume, _flow);
		//_volume = _valve_inhale_PID_percentage;

		//_valve_inhale_PID_percentage /= 10.; // In the Labview code the output was defined from 0-10V. It is a simple rescale to keep the same parameters
                //Lazy approach
                _airway_pressure = _pid.proportional;
                _volume = _pid.integral;
                //_flow = (_pid.Kd*_pid.derivative);
                //_flow = _valves_controller.calcValveDutyCycle(pwm_resolution,_valve_inhale_PID_percentage);

                _valves_controller.setPIDoutput(_pid.valve_duty_cycle);
                _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::PID, VALVE_STATE::FULLY_CLOSED, VALVE_STATE::CLOSED);

        }
        runningAvgs();

        _flow = _readings_avgs.pressure_diff_patient;
        _pid.previous_process_pressure = adcToMillibarFloat((_readings_sums.pressure_inhale / _readings_N), _calib_avgs.pressure_inhale);

        resetReadingSums();

    }
}

void BreathingLoop::updateRawReadings()
{
    // calc pressure every 1ms
    // create averages every 10ms
    uint32_t tnow = static_cast<uint32_t>(millis());

    // to make sure the readings correspond only to the same fsm mode
    if (tnow - _readings_avgs_time > _readings_avgs_timeout) {
        _readings_raw.timestamp                = static_cast<uint32_t>(_readings_sums.timestamp);
#ifdef CHIP_ESP32
        _readings_raw.pressure_air_supply      =analogRead(pin_pressure_air_supply)    ;
        _readings_raw.pressure_o2_supply       =analogRead(pin_pressure_o2_supply)     ;
#endif
        _readings_raw.pressure_air_regulated   =analogRead(pin_pressure_air_regulated) ;
        _readings_raw.pressure_buffer          =analogRead(pin_pressure_buffer)        ;
        _readings_raw.pressure_inhale          =analogRead(pin_pressure_inhale)        ;
        _readings_raw.pressure_patient         =analogRead(pin_pressure_patient)       ;
        _readings_raw.temperature_buffer       =analogRead(pin_temperature_buffer)     ;
        _readings_raw.pressure_o2_regulated    =analogRead(pin_pressure_o2_regulated)  ;
        _readings_raw.pressure_diff_patient    =analogRead(pin_pressure_diff_patient)  ;
    }

}

void BreathingLoop::setVentilationMode(VENTILATION_MODE mode)
{
    _ventilation_mode = mode;
}

VENTILATION_MODE BreathingLoop::getVentilationMode()
{
    return _ventilation_mode;
}


readings<float> BreathingLoop::getReadingAverages()
{
    return _readings_avgs;

}

readings<float> BreathingLoop::getRawReadings()
{
    return _readings_raw;

}

float BreathingLoop::getRespiratoryRate(){
    // 60*1000ms / total time for a full cycle
    float avg = (_total_cycle_duration[0]+_total_cycle_duration[1]+_total_cycle_duration[2])/3.0;
    return 60000.0/avg;
}

/*
float BreathingLoop::getFlow(){
    float normal_volume = 1;
    float si_volume = (_readings_avgs.temperature_buffer / _readings_avgs.pressure_patient ) * (1013.25/273.15) * normal_volume;
    // conversion from V to dp from dp-sensor manual: https://docs.rs-online.com/7d77/0900766b81568899.pdf (500 Pa range?) [Pa -> mbar => 525 -> 5.25]
    float dp_raw = _readings_avgs.pressure_diff_patient / 4096.0 ; // assuming 12bit ADC
    int sign = (dp_raw -0.5) < 0 ? -1 : 1;
    if ((dp_raw -0.5) == 0.000) 
        sign = 0.0;
    float dp = sign*pow(((dp_raw/0.4)-1.25),2) * 5.25; 
    // 
    float flow = dp;


    // NLPM - normal litres per minute = 1 Si Litre per minute * (293.15/T)*(P/1013.25)
    float T = 25+273.15; //_readings_avgs.temperature_buffer;
    float P = _readings_avgs.pressure_patient;
    float nlpm_factor = (293.15/T)*(P/1013.25); 
    return flow;
    /*
    float R = 0.08206 * 1/0.98692 *1000; // mbar *l * mol-1 *K-1
    float T = 25+273.15; //_readings_avgs.temperature_buffer;
    float V_buffer = 10.0 ; //l 
    float V_tube = 1.4 ; //l
    float P_tube = _readings_avgs.pressure_inhale;
    
    float n1 = _readings_avgs.pressure_buffer * V_buffer/(R*T);
    float n2 = _readings_avgs.pressure_inhale * V_tube/(R*T);
    float M = 15.99; // molar mass O2 g.mol-1
    float rho = 1.42 * 1000; // density  1.2kg/m3 @ 25 deg
    */

//}

float    BreathingLoop::getIERatio(){
    // TODO : check with Oscar/Xavier
    float total_inhale_time = _states_durations.inhale + _states_durations.pause;
    float total_exhale_time = _states_durations.exhale_fill + _states_durations.exhale;
    return total_inhale_time/total_exhale_time;
}

float BreathingLoop::getPEEP()
{
    return _peep;
}

float BreathingLoop::getMinuteVolume(){

    return 0;
}

void BreathingLoop::resetReadingSums()
{
    _readings_reset = false;

    uint32_t tnow = static_cast<uint32_t>(millis());
    _readings_time = tnow;
    _readings_avgs_time = tnow;
    _readings_timeout = 1; //ms
    _readings_avgs_timeout = 10; //ms
    _readings_N = 0;
    
    _readings_sums.timestamp                = 0;
    _readings_sums.pressure_air_supply      = 0;
    _readings_sums.pressure_air_regulated   = 0;
    _readings_sums.pressure_buffer          = 0;
    _readings_sums.pressure_inhale          = 0;
    _readings_sums.pressure_patient         = 0;
    _readings_sums.temperature_buffer       = 0;
    _readings_sums.pressure_o2_supply       = 0;
    _readings_sums.pressure_o2_regulated    = 0;
    _readings_sums.pressure_diff_patient    = 0;
}

//This is used to assign the transitions of the fsm
void BreathingLoop::FSM_assignment( ) {
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _fsm_time > _fsm_timeout) {
        BL_STATES next_state;
        switch (_bl_state)
        {
        case BL_STATES::IDLE:
            if (_running == true) {
                // FSM_time = millis();
                next_state = BL_STATES::CALIBRATION;
            } else {
                next_state = BL_STATES::IDLE;
            }
            _reset = false;
            break;
        case BL_STATES::CALIBRATION:
            next_state = BL_STATES::BUFF_PREFILL;
            break;
        case BL_STATES::BUFF_PREFILL:
            next_state = BL_STATES::BUFF_FILL;
            break;
        case BL_STATES::BUFF_FILL:
            next_state = BL_STATES::BUFF_LOADED;
            break;
        case BL_STATES::BUFF_LOADED:
            switch (_ventilation_mode)
            {
            case LAB_MODE_FLUSH:
                next_state = BL_STATES::BUFF_FLUSH;
                break;
            case LAB_MODE_PURGE:
                next_state = BL_STATES::BUFF_PURGE;
                break;
            default:
                next_state = BL_STATES::BUFF_PRE_INHALE;
            }
            break;
        case BL_STATES::BUFF_PRE_INHALE:
            next_state = BL_STATES::INHALE;
            break;
        case BL_STATES::INHALE:
            next_state = BL_STATES::PAUSE;
            break;
        case BL_STATES::PAUSE:
            next_state = BL_STATES::EXHALE_FILL;
            break;
        case BL_STATES::EXHALE_FILL:
            next_state = BL_STATES::EXHALE;
            break;
        case BL_STATES::EXHALE:
            if (_running == false) {
                next_state = BL_STATES::STOP;
            } else {
                next_state = BL_STATES::BUFF_LOADED;
            }
            break;
        case BL_STATES::BUFF_PURGE:
            if (_reset == true ){
                next_state = BL_STATES::IDLE;
            } else if (_safe == false ){
                next_state = BL_STATES::BUFF_PURGE;
            } else if (_running == false) {
                next_state = BL_STATES::IDLE;
            } else {
                next_state = BL_STATES::BUFF_PREFILL;
            }
            break;
        case BL_STATES::BUFF_FLUSH:
            next_state = BL_STATES::IDLE;
            break;
        case BL_STATES::STOP:
            if (_reset == true or _running == true) {
                next_state = BL_STATES::IDLE;
            } else {
                next_state = BL_STATES::STOP;
            }
            break;
        default:
            next_state = _bl_state;
        }
        _bl_state = next_state;
        _fsm_time = tnow;
        // set flag to discard readings due to the mode change
        _readings_reset = true;
    }
    // safety check
    if (tnow - _fsm_time > 10) {
        if (_safe == false){
            _bl_state = BL_STATES::BUFF_PURGE;
            // TODO RAISE ALARM
            _fsm_timeout = 0;
        }
    }
}

void BreathingLoop::FSM_breathCycle()
{
    // basic cycle for testing hardware
    switch (_bl_state) {
        case BL_STATES::IDLE:
            
            if (_running == true) {
                // FSM_time = millis();
            } else {
                _fsm_timeout = 1000;
            }
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::FULLY_CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            initCalib();
            break;
        case BL_STATES::CALIBRATION : 
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::OPEN, VALVE_STATE::OPEN);
            calibrate();
            _fsm_timeout = _states_durations.calibration;
            break;
        case BL_STATES::BUFF_PREFILL:
            // TODO - exhale settable; timeout expert settable
            _calibrated = true;
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _fsm_timeout = _states_durations.buff_prefill;
            break;
        case BL_STATES::BUFF_FILL:
            // TODO - exhale settable; timeout settable
            _valves_controller.setValves(VALVE_STATE::OPEN, VALVE_STATE::OPEN, VALVE_STATE::CLOSED, VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _fsm_timeout = _states_durations.buff_fill;
            break;
        case BL_STATES::BUFF_LOADED:
            // TODO - exhale settable
            // Calc pressure and stay in loaded if not ok
            // pressure settable by expert
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _fsm_timeout = _states_durations.buff_loaded;
            break;
        case BL_STATES::BUFF_PRE_INHALE:
            // TODO spontaneous trigger can be enabled
            // - can be triggered by : 
                // P_inhale ; 
                // P_diff_patient //=flow
                // P_patient and p_diff_patient
                // P_patient or p_diff_patient
                // with thresholds on each
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            switch (_ventilation_mode)
            {
                case LAB_MODE_FLUSH:
                    _fsm_timeout = 100;
                    
                    break;
                case LAB_MODE_PURGE:
                    _fsm_timeout =500;
                    
                    break;
                default:
                    _fsm_timeout = _states_durations.buff_pre_inhale;
            }

	    _pid.integral = 0.;//Resets the integral of the Inhale Valve PID before the inhale cycle starts 
	    _pid.target_pressure = 0.; // Resets the target pressure for the PID target profile 
	    _pid.derivative = 0.; // Resets the derivative for Inhale PID
	    _pid.istep = 0;
        
            break;
        case BL_STATES::INHALE:
            // TODO : spontaneous trigger
            // if p_diff_patient < thresh (def: 25% below nominal)
            // go to exhale fill
            // TODO : spontaneous trigger
            // if p_inhale > max thresh pressure(def: 50?)
            // go to exhale fill
            //_valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::OPEN, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);//Comment this line for the PID control during inhale
            _fsm_timeout = _states_durations.inhale;

            _valley_flow = 100000;  // reset valley after exhale
            
            exhaleTrigger();
            break;
        case BL_STATES::PAUSE:
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            _fsm_timeout = _states_durations.pause;
            break;
        case BL_STATES::EXHALE_FILL:
            _valves_controller.setValves(VALVE_STATE::OPEN, VALVE_STATE::OPEN, VALVE_STATE::CLOSED, VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _peak_flow = -100000;  // reset peak after inhale
            _fsm_timeout = _states_durations.exhale_fill;
            inhaleTrigger();
            break;
        case BL_STATES::EXHALE:
            _states_durations.exhale = calculateDurationExhale();
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _fsm_timeout = _states_durations.exhale;
            //update total cycle time
            updateTotalCycleDuration(_states_durations.buff_loaded
                       +_states_durations.buff_pre_inhale
                       +_states_durations.inhale
                       +_states_durations.pause
                       +_states_durations.exhale_fill
                       +_states_durations.exhale);

            inhaleTrigger();
            
            break;
        case BL_STATES::BUFF_PURGE:
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::OPEN, VALVE_STATE::OPEN);
            _fsm_timeout = _states_durations.buff_purge;
            break;
        case BL_STATES::BUFF_FLUSH:
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::FULLY_OPEN, VALVE_STATE::OPEN, VALVE_STATE::CLOSED);
            _fsm_timeout = _states_durations.buff_flush;
            break;
        case BL_STATES::STOP: 
            // TODO : require a reset command to go back to idle
            _valves_controller.setValves(VALVE_STATE::CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::FULLY_CLOSED, VALVE_STATE::CLOSED, VALVE_STATE::CLOSED);
            _fsm_timeout = 1000;
            break;
    }
    safetyCheck();

}

void BreathingLoop::safetyCheck()
{
    // based on averages or instantaneous values?
    if (_calibrated){
        if (_readings_avgs.pressure_inhale > MAX_PATIENT_PRESSURE)
            _safe = false;
        else if (_readings_avgs.pressure_patient > MAX_PATIENT_PRESSURE)
            _safe = false;
        else 
            _safe = true;
    }
}

void BreathingLoop::doStart()
{
    _running = true;
}

void BreathingLoop::doStop()
{
    _running = false;
}

void BreathingLoop::doReset()
{
    _reset = true;
}

bool BreathingLoop::getRunning()
{
    return _running;
}

void BreathingLoop::calibrate()
{
    // get pressure_air_regulated over last sec of 10s calc mean
    uint32_t tnow = static_cast<uint32_t>(millis());
    if (tnow - _calib_time > _calib_timeout ) {
        _calib_N++;
        _calib_sums.pressure_air_regulated += static_cast<float>(analogRead(pin_pressure_air_regulated));
        _calib_avgs.pressure_air_regulated  = static_cast<float>(_calib_sums.pressure_air_regulated/ _calib_N);
        _calib_sums.pressure_o2_regulated += static_cast<float>(analogRead(pin_pressure_o2_regulated));
        _calib_avgs.pressure_o2_regulated  = static_cast<float>(_calib_sums.pressure_o2_regulated/ _calib_N);
        _calib_sums.pressure_buffer += static_cast<float>(analogRead(pin_pressure_buffer));
        _calib_avgs.pressure_buffer  = static_cast<float>(_calib_sums.pressure_buffer/ _calib_N);
        _calib_sums.pressure_inhale += static_cast<float>(analogRead(pin_pressure_inhale));
        _calib_avgs.pressure_inhale  = static_cast<float>(_calib_sums.pressure_inhale/ _calib_N);
        _calib_sums.pressure_patient += static_cast<float>(analogRead(pin_pressure_patient));
        _calib_avgs.pressure_patient = static_cast<float>(_calib_sums.pressure_patient/ _calib_N);
        _calib_sums.pressure_diff_patient += static_cast<float>(analogRead(pin_pressure_diff_patient));
        _calib_avgs.pressure_diff_patient = static_cast<float>(_calib_sums.pressure_diff_patient/ _calib_N);

	_calib_time = tnow;
	_calib_timeout = 10;
    }
}


void BreathingLoop::initCalib()
{   // do calibration in last sec of calibration step (normally 10s) or default to 10ms
    _calibrated = false;
    _calib_timeout = 10;  
    if (_states_durations.calibration - 1000 > 10)
        _calib_timeout = _states_durations.calibration - 1000;
    _calib_time = static_cast<uint32_t>(millis());
    _calib_sums.pressure_air_regulated = 0;
    _calib_sums.pressure_o2_regulated  = 0;
    _calib_sums.pressure_buffer = 0;
    _calib_sums.pressure_inhale = 0;
    _calib_sums.pressure_patient = 0;
    _calib_avgs.pressure_air_regulated = 0;
    _calib_avgs.pressure_o2_regulated  = 0;
    _calib_avgs.pressure_buffer = 0;
    _calib_avgs.pressure_inhale = 0;
    _calib_avgs.pressure_patient = 0;
    _calib_avgs.pressure_diff_patient = 0;
    _calib_N = 0;
}


states_durations &BreathingLoop::getDurations() {
    return _states_durations;
}

uint32_t BreathingLoop::calculateDurationExhale() {
    // TODO : should have sane minimum times
    // for now min = 100ms
    uint32_t exhale_duration = (_states_durations.inhale * getIERatio())  - _states_durations.exhale_fill ;
    if (exhale_duration < 100)
        exhale_duration = 100;
    return static_cast<uint32_t>(exhale_duration);
}

ValvesController* BreathingLoop::getValvesController()
{
    return &_valves_controller;
}

void BreathingLoop::updateTotalCycleDuration(uint16_t newtotal)
{
    const uint8_t N = 3;
    for(int i=0; i<N-1; i++){
        _total_cycle_duration[i] = _total_cycle_duration[i+1];

    }
    _total_cycle_duration[N-1] = newtotal;
}

float BreathingLoop::getFlow(){
    return _flow;
}
float BreathingLoop::getVolume(){
    return _volume;
}
float BreathingLoop::getAirwayPressure(){
    return _airway_pressure;
}

void BreathingLoop::doPID(int nsteps, float target_pressure, float process_pressure, float &output, float &proportional, float &integral, float &derivative){

    // Set PID profile using the set point
    // nsteps defines the number of intermediate steps
    //
    //

    _pid.istep +=1;

    _pid.process_pressure = process_pressure;

    float _pid_set_point_step = _pid.target_final_pressure/_pid.nsteps;

    _pid.target_pressure += _pid_set_point_step;

    // Slightly ad hoc way of setting the target pressure steps! NB! the number of statements must match the number of steps (_pid.nsteps)
    if (_pid.istep == 1) _pid.target_pressure = 0.1*_pid.target_final_pressure;
    if (_pid.istep == 2) _pid.target_pressure = 0.4*_pid.target_final_pressure;
    if (_pid.istep >= 3) _pid.target_pressure = _pid.target_final_pressure;

    if(_pid.target_pressure > _pid.target_final_pressure) _pid.target_pressure = _pid.target_final_pressure;

    //Calculate the PID error based on the pid set point
    float error = _pid.target_pressure - _pid.process_pressure;

    _pid.proportional       = _pid.Kp*error;
    _pid.integral          += _pid.Ki*error;

    //Derivative calculation

    float _derivative = _pid.previous_process_pressure - _pid.process_pressure ;

    _pid.derivative = 0.7*_pid.derivative + 0.3*_derivative;

    //Checking minium and maximum duty cycle
    
    float minimum_open_frac = 0.52; //Minimum opening to avoid vibrations on the valve control
    float maximum_open_frac = 0.74; //Maximum opening for the PID control

    _pid.valve_duty_cycle = _pid.proportional + _pid.integral + (_pid.Kd * _pid.derivative) + minimum_open_frac;

    if(_pid.valve_duty_cycle > maximum_open_frac) _pid.valve_duty_cycle = maximum_open_frac;
    if(_pid.valve_duty_cycle < minimum_open_frac) _pid.valve_duty_cycle = minimum_open_frac;

}

//void BreathingLoop::PID_process_pressure_derivative(float &_pid_process_pressure_derivative, float process_pressure){
	//process_pressure
//}

pid_variables& BreathingLoop::getPIDVariables()
{
    return _pid;
}


void BreathingLoop::inhaleTrigger()
{
    bool en = _valves_controller.getValveParams().inhale_trigger_enable;
    if(en == true){
        //_fsm_timeout = _max_exhale_time;
        uint32_t tnow = static_cast<uint32_t>(millis());
        if((_flow > _inhale_trigger_threshold) 
            && (tnow - _valley_flow_time > 10)){  // wait 10ms after the valley
            //TODO - check we're past 'valley'
            if (tnow - _fsm_time > _min_exhale_time ) {
                // TRIGGER
                logMsg("inhale trig- " + String(_running_avg_flow) +" "+ String(_inhale_trigger_threshold));
                _fsm_timeout = 0; // go to next state immediately
            }
        } else if (tnow - _fsm_time > _max_exhale_time){
                // TRIGGER
                logMsg("inhale trigger - max exhale time exceeded");
                _fsm_timeout = 0; // go to next state immediately
        }
    } 
}

void BreathingLoop::exhaleTrigger()
{
    bool en = _valves_controller.getValveParams().exhale_trigger_enable;
    if(en == true){
        logMsg("exhale trigger");
        uint32_t tnow = static_cast<uint32_t>(millis());
        if((_running_avg_flow < (_exhale_trigger_threshold * _peak_flow)) 
            && (tnow - _peak_flow_time > 10)){ // wait 10ms after peak
            //TODO - check we're past 'peak'
            logMsg("EXhale trig- " + String(_running_avg_flow) +" "+ String(_exhale_trigger_threshold)+" "+String(_peak_flow));
            if (tnow - _fsm_time > _min_inhale_time ) {
                // TRIGGER
                _fsm_timeout = 0; // go to next state immediately
            }
        }
    } 
}


void BreathingLoop::runningAvgs()
{

    // take the average of the last N flows 
    float sum = 0;
    _running_flows[_running_index] = _flow;
    for(int i=0; i<RUNNING_AVG_READINGS-1; i++){
        // use absolute value to avoid averaging out negative vals
        sum += static_cast<float>(fabs(_running_flows[i]));
    }

    _running_avg_flow = sum/RUNNING_AVG_READINGS;
    _running_index = (_running_index == RUNNING_AVG_READINGS-1 ) ? 0 : _running_index+1;

    if ((_flow > _peak_flow) && (_bl_state == BL_STATES::INHALE)){
        uint32_t tnow = static_cast<uint32_t>(millis());
        _peak_flow_time = tnow;
        _peak_flow = _flow;
    }
    
    if ((_flow < _valley_flow) && ((_bl_state == BL_STATES::EXHALE_FILL ) || (_bl_state == BL_STATES::EXHALE) )){
        uint32_t tnow = static_cast<uint32_t>(millis());
        _valley_flow_time = tnow;
        _valley_flow = _flow;
    }

}
