//
// Created by kumquat on 02.03.20.
//

#ifndef LAB_INTEGRALS_FUNCTION_H
#define LAB_INTEGRALS_FUNCTION_H

#include <cmath>
class Function {
public:
    virtual double valueAt(double x, double y) {
        double a = 20, b = 0.2, c = 2 * M_PI;
        return -a * exp(-b * sqrt(0.5 * (x * x + y * y))) - exp(0.5 * (cos(c * x) + cos(c * y))) + a + exp(1);
    }
};


#endif //LAB_INTEGRALS_FUNCTION_H
