//
// Created by kumquat on 02.03.20.
//

#include "IntegralCalculator.h"
#include "Function.h"
#include <vector>
#include <thread>
#include <mutex>

std::mutex mut;

IntegralCalculator::IntegralCalculator(double xStart, double xEnd, double yStart, double yEnd, Function &function) {
    this->xStart = xStart;
    this->xEnd = xEnd;
    this->yStart = yStart;
    this->yEnd = yEnd;
    this->function = function;
}

double IntegralCalculator::calculate(int numOfIntervals, int numOfThreads) {
    if (numOfThreads == 1)
        return calculateOneThread(numOfIntervals);
    return calculate_multiple_threads(numOfIntervals, numOfThreads);
}

double IntegralCalculator::calculateOneThread(int numOfIntervals) {
    return calculateOnInterval(xStart, xEnd, yStart, yEnd, numOfIntervals, numOfIntervals);
}


double IntegralCalculator::calculateOnInterval(double xFirst, double xLast, double yFirst, double yLast,
                                               int numOfIntervalsX, int numOfIntervalsY) {
    double xStep = (xLast - xFirst) / numOfIntervalsX;
    double yStep = (yLast - yFirst) / numOfIntervalsY;

    double res = 0, x = xFirst, y;
    for (int i = 0; i < numOfIntervalsX; i++) {
        y = yFirst;
        for (int j = 0; j < numOfIntervalsY; j++) {
            res += function.valueAt(x, y);
            y += yStep;
        }
        x += xStep;
    }
    double area = xStep * yStep;
    return res * area;
}

double IntegralCalculator::calculate_multiple_threads(int numOfIntervals, int numOfThreads) {
    std::vector<std::thread> threads;
    std::vector<double> resVector;
    resVector.reserve(numOfThreads);



    double result = 0, step = (yEnd - yStart) / numOfThreads, y = yStart;
    for (int i = 0; i < numOfThreads; i++) {
        threads.emplace_back(&IntegralCalculator::calculateEveryThread, this, xStart, xEnd, y, y + step, numOfIntervals,
                             numOfIntervals / numOfThreads, std::ref(resVector));
        y += step;
    }

    for (auto &th : threads) {
        th.join();
    }
    for (auto &localRes : resVector) result += localRes;
    return result;
}

void IntegralCalculator::calculateEveryThread(double xFirst, double xLast, double yFirst, double yLast,
                                              int numOfIntervalsX, int numOfIntervalsY, std::vector<double> &res) {
    double integralValue = calculateOnInterval(xFirst, xLast, yFirst, yLast, numOfIntervalsX, numOfIntervalsY);
    mut.lock();
    res.push_back(integralValue);
    mut.unlock();
}