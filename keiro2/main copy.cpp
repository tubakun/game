#include <iostream>
#include <vector>
#include <set>
#include <fstream>
#include <sstream>
#include <cmath>
#include <limits>
#include <chrono>

using namespace std;
using namespace chrono;

vector<vector<double>> read_coordinates_from_file(const string& filename) {
    vector<vector<double>> coordinates;
    ifstream infile(filename);

    string line;
    while (getline(infile, line)) {
        stringstream ss(line);
        double x, y, z;
        char delimiter;
        ss >> x >> delimiter >> y >> delimiter >> z;
        coordinates.push_back({ x, y, z });
    }

    infile.close();
    return coordinates;
}

double distance(const vector<double>& p1, const vector<double>& p2) {
    double sum = 0.0;
    for (size_t i = 0; i < p1.size(); ++i) {
        sum += pow(p1[i] - p2[i], 2);
    }
    return sqrt(sum);
}

vector<int> greedy_path(const vector<vector<double>>& coordinates, double s) {
    set<int> unvisited;
    for (int i = 0; i < coordinates.size(); ++i) {
        unvisited.insert(i);
    }
    int current = 0;
    vector<int> path = { current };
    unvisited.erase(current);

    while (!unvisited.empty()) {
        double min_distance = numeric_limits<double>::infinity();
        int nearest_neighbor = -1;
        for (const int& neighbor : unvisited) {
            double dist = distance(coordinates[current], coordinates[neighbor]);
            if (dist <= s) {
                nearest_neighbor = neighbor;
                break;
            }
            else if (dist < min_distance) {
                min_distance = dist;
                nearest_neighbor = neighbor;
            }
        }
        current = nearest_neighbor;
        path.push_back(current);
        unvisited.erase(current);
    }
    return path;
}

void output_path_to_file(const vector<int>& path, const string& filename) {
    ofstream outfile(filename);
    for (const int& p : path) {
        outfile << p << endl;
    }
    outfile.close();
}

int main() {
    int n = 100;
    double s = 1.0;

    steady_clock::time_point start_time = steady_clock::now();

    vector<vector<double>> coordinates = read_coordinates_from_file("rippou.txt");
    vector<int> path = greedy_path(coordinates, s);
    output_path_to_file(path, "path_output_rippou.txt");

    steady_clock::time_point end_time = steady_clock::now();
    duration<double> elapsed_time = duration_cast<duration<double>>(end_time - start_time);

    cout << "Execution time: " << elapsed_time.count() << " seconds" << endl;

    return 0;
}