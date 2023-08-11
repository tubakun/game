#include <iostream>
#include <vector>
#include <set>
#include <fstream>
#include <cmath>
#include <limits>
#include <chrono>
#include <atomic>
#include <sstream>


using namespace std;
using namespace chrono;


vector<vector<double>> read_coordinates_from_file(const string& filename) {
    vector<vector<double>> coordinates;
    ifstream infile(filename);

    string line;
    while (getline(infile, line)) {
        stringstream ss(line);
        double x, y, z;
        ss >> x >> y >> z;
        coordinates.push_back({ x, y, z });
    }

    infile.close();
    return coordinates;
}


double distance(const vector<double>& p1, const vector<double>& p2) {
    double maxDiff = 0.0;
    for (size_t i = 0; i < p1.size(); ++i) {
        double diff = fabs(p1[i] - p2[i]);
        if (diff > maxDiff) {
            maxDiff = diff;
        }
    }
    return maxDiff;
}


void output_path_to_file(const vector<int>& path, const string& filename) {
    ofstream outfile(filename);
    for (const int& p : path) {
        outfile << p << endl;
    }
    outfile.close();
}


void greedy_path(const vector<vector<double>>& coordinates, double s, vector<int>& path) {
    set<int> unvisited;
    for (int i = 0; i < coordinates.size(); ++i) {
        unvisited.insert(i);
    }
    int current = *unvisited.begin();
    path.push_back(current);
    unvisited.erase(current);

    while (!unvisited.empty()) {
        double min_distance = numeric_limits<double>::max();
        int nearest_neighbor = *unvisited.begin();
        for (const int& neighbor : unvisited) {
            double dist = distance(coordinates[current], coordinates[neighbor]);
            if (dist <= s) {
                nearest_neighbor = neighbor;
                break;  
            }
            else {
                if (dist < min_distance) {
                    min_distance = dist;
                    nearest_neighbor = neighbor;
                }
            }
        }
        current = nearest_neighbor;
        path.push_back(current);
        unvisited.erase(current);
    }
}

int main() {
    double s = 1;

    vector<vector<double>> coordinates = read_coordinates_from_file("output_vertex.txt");

    steady_clock::time_point start_time = steady_clock::now();

    vector<int> path;

    greedy_path(coordinates, s, path);

    steady_clock::time_point end_time = steady_clock::now();
    duration<double> elapsed_time = duration_cast<duration<double>>(end_time - start_time);

    output_path_to_file(path, "path_output.txt");

    cout << "Execution time: " << elapsed_time.count() << " seconds" << endl;

    return 0;
}
