#include <iostream>
#include <cmath>
#include <map>
#include <stdexcept>
#include <iomanip>
#include "utils.h"
#include "IntegralCalculator.h"
#include "TimeCounter.h"


int main(int argc, char* argv[]) {
    if (argc != 2) throw std::invalid_argument("Wrong number of arguments");

    std::map<std::string, double> conf;
    int numOfThreads = 0;
    readConfig(conf, numOfThreads, argv[1]);

    Function f;
    IntegralCalculator calculator(conf["x_start"], conf["x_end"], conf["y_start"], conf["y_end"], f);
    TimeCounter timeCounter;

    timeCounter.startCount();

    int intervals = 1000;
    double newRes = calculator.calculate(intervals, numOfThreads);
    double res;
    int iteration = 0;
    do {
        intervals *= 2;
        res = newRes;
        newRes = calculator.calculate(intervals, numOfThreads);

//        std::cout << std::setprecision(20) << newRes << std::endl;

//        std::cout << "rel " << std::setprecision(20) << std::abs(newRes - res) / newRes << std::endl;
        iteration++;
    } while ((std::abs(res - newRes) > conf["abs_error"] ||
              std::abs(newRes - res) / newRes > conf["rel_error"]) &&
             iteration <= 15);

    double timeElapsed = timeCounter.timeElapsed();
    std::cout << std::fixed << timeElapsed << " " << newRes << " " << std::abs(res - newRes) << " " << std::abs(newRes - res) / newRes;
}
