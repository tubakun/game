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
        double x, y, z, r, g, b;
        char delimiter;
        ss >> x >> delimiter >> y >> delimiter >> z >> delimiter >> r >> delimiter >> g >> delimiter >> b;
        coordinates.push_back({ x, y, z, r, g, b });
    }

    infile.close();
    return coordinates;
}


double distance(const vector<double>& p1, const vector<double>& p2) {
    double sum = 0.0;
    for (size_t i = 0; i < 3; ++i) {  // Calculate distance only based on x, y, z
        sum += pow(p1[i] - p2[i], 2);
    }
    return sqrt(sum);
}


void output_path_to_file(const vector<int>& path, const vector<vector<double>>& coordinates, const string& filename) {
    ofstream outfile(filename);
    for (const int& p : path) {
        outfile << coordinates[p][0] << " " << coordinates[p][1] << " " << coordinates[p][2] << " "
            << coordinates[p][3] << " " << coordinates[p][4] << " " << coordinates[p][5] << endl;
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
        }
        current = nearest_neighbor;
        path.push_back(current);
        unvisited.erase(current);
    }
}

int main() {
    double s = 1.0;
    int heiretu = 8;

    vector<vector<double>> coordinates = read_coordinates_from_file("output_vertex_color.txt");

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

    output_path_to_file(final_path, coordinates, "path_output_zahyou_colors.txt");

    cout << "Execution time: " << elapsed_time.count() << " seconds" << endl;

    return 0;
}
