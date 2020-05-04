#include "AlarmLoop.h"

AlarmLoop::AlarmLoop()
{
    ;
}

AlarmLoop::~AlarmLoop()
{;}

int AlarmLoop::fireAlarm(alarms<bool> &triggered, alarms<ALARM_TYPE> &priority)
{
    return 0;
}

bool AlarmLoop::checkTresholds() {
    _triggered = false;
    _triggered |= COMPARE_THRESHOLD(apnea                           );
    _triggered |= COMPARE_THRESHOLD(check_valve_exhale              );
    _triggered |= COMPARE_THRESHOLD(check_p_patient                 );
    _triggered |= COMPARE_THRESHOLD(expiration_sense_fault_or_leak  );
    _triggered |= COMPARE_THRESHOLD(expiration_valve_leak           );
    _triggered |= COMPARE_THRESHOLD(high_fio2                       );
    _triggered |= COMPARE_THRESHOLD(high_pressure                   );
    _triggered |= COMPARE_THRESHOLD(high_rr                         );
    _triggered |= COMPARE_THRESHOLD(high_vte                        );
    _triggered |= COMPARE_THRESHOLD(low_vte                         );
    _triggered |= COMPARE_THRESHOLD(high_vti                        );
    _triggered |= COMPARE_THRESHOLD(low_vti                         );
    _triggered |= COMPARE_THRESHOLD(intentional_stop                );
    _triggered |= COMPARE_THRESHOLD(low_battery                     );
    _triggered |= COMPARE_THRESHOLD(low_fio2                        );
    _triggered |= COMPARE_THRESHOLD(occlusion                       );
    _triggered |= COMPARE_THRESHOLD(high_peep                       );
    _triggered |= COMPARE_THRESHOLD(low_peep                        );
    _triggered |= COMPARE_THRESHOLD(ac_power_disconnection          );
    _triggered |= COMPARE_THRESHOLD(battery_fault_srvc              );
    _triggered |= COMPARE_THRESHOLD(battery_charge                  );
    _triggered |= COMPARE_THRESHOLD(air_fail                        );
    _triggered |= COMPARE_THRESHOLD(o2_fail                         );
    _triggered |= COMPARE_THRESHOLD(pressure_sensor_fault           );
    _triggered |= COMPARE_THRESHOLD(arduino_fail                    );
    return _triggered;
}

void AlarmLoop::processAlarms() {
    checkTresholds();

    _av_controller.setStyles(AV_STYLE::OSCIL);
    _av_controller.update();
}
