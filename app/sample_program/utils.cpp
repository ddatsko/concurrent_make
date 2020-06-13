#include <string>
#include <fstream>
#include <map>
#include <sstream>


void readConfig(std::map<std::string, double> &conf, int &num_of_threads, char* filename) {
    std::ifstream configFile(filename);
    std::string line, key, value;
    int iteration = 0;

    while (getline(configFile, line)) {
        if (line.empty() || line[0] == '#' || line[0] == ' ')
            continue;
        std::istringstream lineStream(line);
        if (std::getline(lineStream, key, '=')) {
            if (std::getline(lineStream, value)) {
                if (iteration == 0)
                    num_of_threads = std::stoi(value);
                else
                    conf.insert(std::make_pair(key, std::stof(value)));
            }
        }
        iteration++;
    }
    if (conf["x_start"] < conf["x_start"] || conf["y_end"] < conf["y_end"]) {
        throw std::invalid_argument("Wrong integration limits");
    }

    if (num_of_threads <= 0 || conf["abs_error"] <= 0 || conf["rel_error"] <= 0) {
        throw std::invalid_argument("Number of threads or errors in config file are <= 0");
    }
}
