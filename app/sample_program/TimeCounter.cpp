//
// Created by kumquat on 02.03.20.
//

#include <atomic>
#include "TimeCounter.h"

TimeCounter::TimeCounter(){
    startTime = getTime();
}

std::chrono::high_resolution_clock::time_point TimeCounter::getTime() {
    std::atomic_thread_fence(std::memory_order_seq_cst);
    auto resTime = std::chrono::high_resolution_clock::now();
    std::atomic_thread_fence(std::memory_order_seq_cst);
    return resTime;
}

double TimeCounter::timeElapsed() {
    auto now = getTime();
    auto finishTime = getTime();

    auto intNs = std::chrono::duration_cast<std::chrono::nanoseconds>(finishTime - startTime);
    std::chrono::duration<long long, std::nano> longSec = intNs;
    return longSec.count();
}

void TimeCounter::startCount() {
    startTime = getTime();
}
