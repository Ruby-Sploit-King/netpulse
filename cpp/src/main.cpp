#include <filesystem>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <map>
#include <sstream>
#include <string>
#include <sys/types.h>

int main(int argc, char* argv[]) {
    if (argc != 2 || std::string(argv[1]) != "--json") {
        std::cerr << "Usage: netpulse-core --json\n";
        return 2;
    }

    std::ifstream memory_file("/proc/meminfo");
    std::ifstream uptime_file("/proc/uptime");
    std::ifstream load_file("/proc/loadavg");

    if (!memory_file || !uptime_file || !load_file) {
        std::cerr << "Unable to read Linux system metrics.\n";
        return 1;
    }

    std::map<std::string, long long> memory;
    std::string line;

    while (std::getline(memory_file, line)) {
        std::istringstream fields(line);
        std::string key;
        long long value = 0;

        if (fields >> key >> value) {
            if (!key.empty() && key.back() == ':') {
                key.pop_back();
            }
            memory[key] = value;
        }
    }

    double uptime = 0.0;
    double idle = 0.0;
    double load1 = 0.0;
    double load5 = 0.0;
    double load15 = 0.0;

    if (!(uptime_file >> uptime >> idle) ||
        !(load_file >> load1 >> load5 >> load15)) {
        std::cerr << "Unable to parse Linux system metrics.\n";
        return 1;
    }

    const auto total = memory["MemTotal"] * 1024LL;
    const auto available = memory["MemAvailable"] * 1024LL;
    const auto disk = std::filesystem::space("/");

    if (total <= 0 || available < 0 || available > total ||
        disk.capacity == 0) {
        std::cerr << "System metrics are outside expected ranges.\n";
        return 1;
    }

    std::cout << std::fixed << std::setprecision(2)
              << "{"
              << "\"load_1m\":" << load1 << ","
              << "\"load_5m\":" << load5 << ","
              << "\"load_15m\":" << load15 << ","
              << "\"memory_total\":" << total << ","
              << "\"memory_available\":" << available << ","
              << "\"disk_total\":" << disk.capacity << ","
              << "\"disk_free\":" << disk.available << ","
              << "\"uptime_seconds\":" << static_cast<long long>(uptime)
              << "}\n";

    return 0;
}
