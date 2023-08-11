#include <iostream>
#include <vector>
#include <fstream>
#include <sstream>
#include <limits>
#include <algorithm>
#include <cmath>

using namespace std;

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

vector<vector<double>> find_shortest_path(vector<vector<double>>& coordinates) {
    vector<vector<double>> shortestPath;
    vector<bool> visited(coordinates.size(), false);

    // start from the first point
    int currentIndex = 0;
    visited[currentIndex] = true;
    shortestPath.push_back(coordinates[currentIndex]);

    size_t total = coordinates.size();
    for (size_t i = 1; i < total; ++i) {
        double minDist = numeric_limits<double>::max();
        int minIndex = -1;

        for (size_t j = 0; j < total; ++j) {
            if (!visited[j]) {
                double dist = distance(coordinates[currentIndex], coordinates[j]);
                if (dist == 1) {
                    minDist = dist;
                    minIndex = j;
                    break;
                }
                else if (dist < minDist) {
                    minDist = dist;
                    minIndex = j;
                }
            }
        }

        currentIndex = minIndex;
        visited[currentIndex] = true;
        shortestPath.push_back(coordinates[currentIndex]);

        // progress
        cout << "\rProgress: " << static_cast<int>(static_cast<double>(i) / total * 100) << "%";
        cout.flush();
    }

    cout << "\rProgress: 100%\n";
    return shortestPath;
}

void write_coordinates_to_file(const string& filename, const vector<vector<double>>& coordinates) {
    ofstream outfile(filename);

    for (const auto& coordinate : coordinates) {
        outfile << coordinate[0] << ", " << coordinate[1] << ", " << coordinate[2] << "\n";
    }

    outfile.close();
}

int main() {
    string inputFilename = "output_vertex.txt"; // replace with your file name
    string outputFilename = "path_vertex.txt"; // output file name

    auto coordinates = read_coordinates_from_file(inputFilename);
    auto shortestPath = find_shortest_path(coordinates);

    // write coordinates in the shortest path to file
    write_coordinates_to_file(outputFilename, shortestPath);

    return 0;
}
