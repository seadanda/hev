#ifndef LINEARFITTER_H
#define LINEARFITTER_H

#include <Arduino.h>
#include <limits>
#include "RingBuf.h"

// just absolute maximum of entries
#define MAX_FIT_ENTRIES 1024

class LinearFitter
{
private:
    void resetSums() { _entries = 0; _sum_x  = 0; _sum_x2 = 0; _sum_y  = 0; _sum_xy = 0; }
    void calculateSums(uint32_t &x, float &y, int8_t sign = 1) {
        _sum_x  += sign * (x         );
        _sum_x2 += sign * (x * x     );
        _sum_y  += sign * (        y );
        _sum_xy += sign * (x     * y );
    }
    void calculateSums() {
        resetSums();
        for (uint8_t idx = 0; idx < _x.size(); idx++) {
            if (_x[idx] - _x[0] >= _duration) {
                break;
            }
            _entries++;
            calculateSums(_x[idx], _y[idx]);
        }
    }

public:
    LinearFitter(uint32_t duration, uint32_t delay) : _duration(duration), _delay(delay) {;}
    void setDuration(uint32_t duration) { _duration = duration; calculateSums();}
    void setDelay   (uint32_t delay   ) { _delay    = delay   ; calculateSums();}

    void resetCalculation(uint32_t reset_time = 0) { _x_zero = reset_time; _x.clear(); _y.clear(); }

    void appendPoints(uint32_t x, float y) {
        x -= _x_zero;

        // remove entry if buffer full or if _duration (in ms) longer than defined
        while ((!_x.isEmpty() && ((x - _x[0]) >= (_duration + _delay)) ) || (_x.isFull() && _y.isFull())) {
            uint32_t x_tmp;
            float    y_tmp;
            _x.pop(x_tmp);
            _y.pop(y_tmp);
        }

        _x.push(x);
        _y.push(y);
        calculateSums();
    }

    bool linearRegression(float &slope, float &offset) {
        if (_x.isEmpty() || _y.isEmpty())               return false;
        if ((_x[_entries - 1] - _x[0]) < _duration )    return false;
        if ((_entries * _sum_x2) == (_sum_x * _sum_x))  return false;

        // results
        slope  = ((_entries * _sum_xy) - (_sum_x * _sum_y)) / ((_entries * _sum_x2) - (_sum_x * _sum_x));
        offset = (_sum_y - (slope * _sum_x)) / _entries;
        return true;
    }
    float extrapolate(uint32_t x) {
        x -= _x_zero;
        float slope, offset;
        if (linearRegression(slope, offset)) {
            return (x*slope + offset);
        }

        return std::numeric_limits<float>::max(); // max float value
    }

private:
    uint32_t _x_zero   = 0;
    uint8_t  _entries  = 0;
    uint32_t _duration = 0;
    uint32_t _delay    = 0;

    // linear regression
    RingBuf<uint32_t, MAX_FIT_ENTRIES> _x;
    RingBuf<   float, MAX_FIT_ENTRIES> _y;

    float _sum_x  = 0;
    float _sum_x2 = 0;
    float _sum_y  = 0;
    float _sum_xy = 0;
};

#endif // LINEARFITTER_H
