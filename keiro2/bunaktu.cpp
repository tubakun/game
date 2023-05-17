#include <iostream>
#include <vector>
#include <set>
#include <fstream>
#include <sstream>
#include <cmath>
#include <limits>
#include <chrono>
#include <omp.h>

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
    ofstream outfile(filename, ios_base::app);  // Append mode
    for (const int& p : path) {
        outfile << p << endl;
    }
    outfile.close();
}

int get_region(const vector<double>& point, const vector<double>& mid) {
    return (point[0] > mid[0]) + 2 * (point[1] > mid[1]) + 4 * (point[2] > mid[2]);
}

int main() {
    int n = 100;
    double s = 1.0;
    steady_clock::time_point start_time = steady_clock::now();

    vector<vector<double>> coordinates = read_coordinates_from_file("rippou.txt");

    vector<double> min_coord = coordinates[0];
    vector<double> max_coord = coordinates[0];
    for (const auto& coord : coordinates) {
        for (int i = 0; i < 3; ++i) {
            min_coord[i] = min(min_coord[i], coord[i]);
            max_coord[i] = max(max_coord[i], coord[i]);
        }
    }

    vector<double> mid_coord = { 
        (min_coord[0] + max_coord[0]) / 2, 
        (min_coord[1] + max_coord[1]) / 2, 
        (min_coord[2] + max_coord[2]) / 2
    };

    vector<vector<vector<double>>> regions(8);
    for (const auto& coord : coordinates) {
        regions[get_region(coord, mid_coord)].push_back(coord);
    }

    vector<vector<int>> paths(8);

    #pragma omp parallel for
    for (int i = 0; i < 8; ++i) {
        paths[i] = greedy_path(regions[i], s);
    }

    output_path_to_file(paths[0], "path_output_rippou.txt");  // Clear the file first

    for (int i = 1; i < 8; ++i) {
        output_path_to_file(paths[i], "path_output_rippou.txt");  // Append subsequent paths
    }

    steady_clock::time_point end_time = steady_clock::now();
    duration<double> elapsed_time = duration_cast<duration<double>>(end_time - start_time);

    cout << "Execution time: " << elapsed_time.count() << " seconds" << endl;

    return 0;
}

