//
// Created by kumquat on 02.03.20.
//

#ifndef LAB_INTEGRALS_TIMECOUNTER_H
#define LAB_INTEGRALS_TIMECOUNTER_H


#include <chrono>

class TimeCounter {
public:
    TimeCounter();
    void startCount();
    double timeElapsed();

private:
    std::chrono::high_resolution_clock::time_point startTime;
    static std::chrono::high_resolution_clock::time_point getTime();
};


#endif //LAB_INTEGRALS_TIMECOUNTER_H
