#include <iostream>
#include <vector>
#include <set>
#include <fstream>
#include <cmath>
#include <limits>
#include <chrono>
#include <thread>
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
        char delimiter;
        ss >> x >> delimiter >> y >> delimiter >> z;
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


void greedy_path_threaded(const vector<vector<double>>& coordinates, double s, int start_index, int end_index, vector<int>& path) {
    set<int> unvisited;
    for (int i = start_index; i < end_index; ++i) {
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
    int heiretu = 1;

    vector<vector<double>> coordinates = read_coordinates_from_file("output_vertex.txt");

    steady_clock::time_point start_time = steady_clock::now();

    int increment = coordinates.size() / heiretu;
    vector<vector<int>> paths(heiretu);
    vector<thread> threads;

    for (int i = 0; i < heiretu; ++i) {
        int start_index = i * increment;
        int end_index = (i == heiretu - 1) ? coordinates.size() : start_index + increment;
        threads.push_back(thread(greedy_path_threaded, ref(coordinates), s, start_index, end_index, ref(paths[i])));
    }

    for (auto& t : threads) {
        t.join();
    }

    // Concatenate the paths
    vector<int> final_path;
    for (auto& path : paths) {
        final_path.insert(final_path.end(), path.begin(), path.end());
    }

    steady_clock::time_point end_time = steady_clock::now();
    duration<double> elapsed_time = duration_cast<duration<double>>(end_time - start_time);

    output_path_to_file(final_path, "path_output.txt");

    cout << "Execution time: " << elapsed_time.count() << " seconds" << endl;

    return 0;
}