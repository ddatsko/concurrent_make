//
// Created by kumquat on 02.03.20.
//

#ifndef LAB_INTEGRALS_INTEGRALCALCULATOR_H
#define LAB_INTEGRALS_INTEGRALCALCULATOR_H


#include <vector>
#include "Function.h"

class IntegralCalculator {
public:
    IntegralCalculator(double xStart, double xEnd, double yStart, double yEnd, Function &function);

    double calculate(int numOfIntervals, int numOfThreads);

    double calculateOnInterval(double xFirst, double xLast, double yFirst, double yLast,
                               int numOfIntervalsX, int numOfIntervalsY);
    void calculateEveryThread(double xFirst, double xLast, double yFirst, double yLast,
                              int numOfIntervalsX, int numOfIntervalsY, std::vector<double> &res);

private:
    double xStart, xEnd, yStart, yEnd;
    Function function;

    double calculateOneThread(int numOfIntervals);

    double calculate_multiple_threads(int numOfIntervals, int numOfThreads);
};


#endif //LAB_INTEGRALS_INTEGRALCALCULATOR_H
