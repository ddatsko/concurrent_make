CXX = g++
COMPILE_FLAGS = -O3
OBJECT_FILES = main.o IntegralCalculator.o TimeCounter.o utils.o


lab_integral: main.o IntegralCalculator.h Function.h IntegralCalculator.o TimeCounter.o TimeCounter.h utils.h utils.o
	${CXX} -o $@ ${OBJECT_FILES} /lib/x86_64-linux-gnu/libpthread-2.30.so


main.o: main.cpp Function.h TimeCounter.h IntegralCalculator.h
	${CXX} -c -o $@ main.cpp ${COMPILE_FLAGS} 

IntegralCalculator.o: IntegralCalculator.cpp IntegralCalculator.h Function.h
	${CXX} -c -o $@ IntegralCalculator.cpp ${COMPILE_FLAGS}

TimeCounter.o: TimeCounter.cpp TimeCounter.h
	${CXX} -c -o $@ TimeCounter.cpp ${COMPILE_FLAGS}

utils.o: utils.cpp utils.h
	${CXX} -c -o $@ utils.cpp ${COMPILE_FLAGS}






