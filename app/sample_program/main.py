import sys
import subprocess

config_arguments = {
    "num_of_threads": 1,
    "abs_error": 0.000001,
    "rel_error": 0.00000000001026,
    "x_start": -100,
    "x_end": 100,
    "y_start": -100,
    "y_end": 100
}
arguments = ["num_of_threads", "abs_error", "rel_error", "x_start", "x_end", "y_start", "y_end"]


def main():
    if len(sys.argv) != 4:
        print(
            "Wrong arguments. You need to specify the binary file name, number of threads (or range) and number of runs each time\n"
            "e.g. \n$ python3 main.py ./bin/main 1-3 100  # will run algorithm 300 times: 100 with 1 thread ...\n"
            "$ python3 main.py ./a.out 8 1000  # will run algorithm 1000 times with 8 threads")
        exit()
    bin_file = sys.argv[1]
    num_of_repeats = int(sys.argv[3])
    arg_threads = sys.argv[2]
    if '-' in arg_threads:
        threads_num = arg_threads.split('-')
        if len(threads_num) != 2:
            print("Wrong number of threads argument type")
            exit()
        thread = list(map(int, threads_num))
    else:
        thread = [int(arg_threads)] * 2

    print("Threads, time")
    for threads_num in range(max(1, thread[0]), min(100, thread[1]) + 1):
        print(f"{threads_num}, {calculate_running_time(threads_num, num_of_repeats, bin_file)}")


def calculate_running_time(number_of_threads, number_of_repeats, bin_file):
    conf_file = open("config_tmp.txt", "w")
    config_arguments["num_of_threads"] = number_of_threads
    for arg in arguments:
        print(f"{arg}={config_arguments[arg]}", file=conf_file)
    conf_file.close()

    min_time = float("inf")

    ok = True
    values = []
    for _ in range(number_of_repeats):
        res = list(map(float, subprocess.check_output([bin_file, "config_tmp.txt"]).split()))
        min_time = min(min_time, res[0])
        values.append(res[1])
        for prev_res in values:
            if abs(prev_res - res[1]) > 2 * config_arguments["abs_error"]:
                ok = False
    if not ok:
        print("Result is wrong")
    return min_time


if __name__ == "__main__":
    main()
