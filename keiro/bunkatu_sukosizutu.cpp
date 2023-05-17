#include <iostream>
#include <vector>
#include <set>
#include <fstream>
#include <cmath>
#include <limits>
#include <chrono>
#include <thread>
#include <atomic>

using namespace std;
using namespace chrono;


vector<vector<double>> generate_coordinates(int cube_size) {
    vector<vector<double>> coordinates;
    double offset = static_cast<double>(cube_size) / 2.0;
    for (int x = 0; x <= cube_size; ++x) {
        for (int y = 0; y <= cube_size; ++y) {
            for (int z = 0; z <= cube_size; ++z) {
                if (x == 0 || x == cube_size || y == 0 || y == cube_size || z == 0 || z == cube_size) {
                    coordinates.push_back({ x - offset, y - offset, z - offset });
                }
            }
        }
    }
    return coordinates;
}

double distance(const vector<double>& p1, const vector<double>& p2) {
    double sum = 0.0;
    for (size_t i = 0; i < p1.size(); ++i) {
        sum += pow(p1[i] - p2[i], 2);
    }
    return sqrt(sum);
}

void output_path_to_file(const vector<int>& path, const string& filename) {
    ofstream outfile(filename);
    for (const int& p : path) {
        outfile << p << endl;
    }
    outfile.close();
}



vector<int> greedy_path_half(const vector<vector<double>>& coordinates, double s, int start_index, int end_index) {
    set<int> unvisited;
    for (int i = start_index; i < end_index; ++i) {
        unvisited.insert(i);
    }
    int current = *unvisited.begin();
    vector<int> path = { current };
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
        }
        current = nearest_neighbor;
        path.push_back(current);
        unvisited.erase(current);
    }
    return path;
}

int main() {
    int n = 100;
    double s = 1.0;

    vector<vector<double>> coordinates = generate_coordinates(n);

    steady_clock::time_point start_time = steady_clock::now();

    int mid = coordinates.size() / 2;
    vector<int> path1 = greedy_path_half(coordinates, s, 0, mid);
    vector<int> path2 = greedy_path_half(coordinates, s, mid, coordinates.size());

    // Concatenate the two paths
    path1.insert(path1.end(), path2.begin(), path2.end());

    output_path_to_file(path1, "path_output.txt");

    steady_clock::time_point end_time = steady_clock::now();
    duration<double> elapsed_time = duration_cast<duration<double>>(end_time - start_time);

    cout << "Execution time: " << elapsed_time.count() << " seconds" << endl;

    return 0;
}
