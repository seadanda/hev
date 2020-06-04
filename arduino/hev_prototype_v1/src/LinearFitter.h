#ifndef LINEARFITTER_H
#define LINEARFITTER_H

#include "RingBuf.h"

// just absolute maximum of entries
#define MAX_FIT_ENTRIES 1024

class LinearFitter
{
public:
    LinearFitter();

    void appendPoints(uint32_t x, float y);
    bool linearRegression(float &slope, float &offset);

    void resetCalculation(uint32_t reset_time = 0);
    void setDuration(uint32_t duration) { _duration = duration; }

private:
    void calculateSums(uint32_t &x, float &y, int8_t sign = 1);

private:
    uint32_t _x_zero = 0;
    uint32_t _duration = 0;

    // linear regression
    RingBuf<uint32_t, MAX_FIT_ENTRIES> _x;
    RingBuf<   float, MAX_FIT_ENTRIES> _y;

    float _sum_x  = 0;
    float _sum_x2 = 0;
    float _sum_y  = 0;
    float _sum_xy = 0;
};


LinearFitter::LinearFitter() {
    ;
}

void LinearFitter::resetCalculation(uint32_t reset_time) {
    _x_zero = reset_time;
    _x.clear();
    _y.clear();
}

void LinearFitter::calculateSums(uint32_t &x, float &y, int8_t sign) {
    _sum_x  += sign * (x         );
    _sum_x2 += sign * (x * x     );
    _sum_y  += sign * (        y );
    _sum_xy += sign * (x     * y );
}

void LinearFitter::appendPoints(uint32_t x, float y) {
    x -= _x_zero;

    // remove entry if buffer full or if _duration (in ms) longer than defined
    if ((_x.isFull() && _y.isFull()) || (!_x.isEmpty() && ((x - _x[0]) >= _duration) )) {
        uint32_t x_tmp;
        float    y_tmp;
        _x.pop(x_tmp);
        _y.pop(y_tmp);
        calculateSums(x_tmp, y_tmp, -1);
    }

    // only calculate if successfully pushed both values
    if (_x.push(x) && _y.push(y) ) calculateSums(x, y);
}

bool LinearFitter::linearRegression(float &slope, float &offset) {
    if (_x.isEmpty() || _y.isEmpty())               return false;
    if ((_x[_x.size() - 1] - _x[0]) < _duration)    return false;
    uint8_t entries;
    if ((entries * _sum_x2) == (_sum_x * _sum_x))  return false;

    // results
    slope  = ((entries * _sum_xy) - (_sum_x * _sum_y)) / ((entries * _sum_x2) - (_sum_x * _sum_x));
    offset = (_sum_y - (slope * _sum_x)) / entries;
    return true;
}

#endif // LINEARFITTER_H
