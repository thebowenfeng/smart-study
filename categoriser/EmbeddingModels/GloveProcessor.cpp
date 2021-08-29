#include <iostream>
#include <string>
#include <stdio.h>
using namespace std;

const int VECTOR_SIZE = 50;

int main() {
    freopen("glove.6B.50d.txt","r",stdin);
    FILE * corpusFile, * weightsFile;
    corpusFile = fopen("glove50Words.txt","w");
    weightsFile = fopen("glove50Weights.txt","w");
    while (true) {

        string s;
        if (not (cin >> s)) {
            break;
        }
        fputs((s+"\n").c_str(), corpusFile);
        for (int i=0; i<VECTOR_SIZE; i++) {
            float x;
            cin >> x;
            fputs(to_string(x).c_str(), weightsFile);
            fputs(" ", weightsFile);
        }
        fputs("\n", weightsFile);
    }
    fclose(weightsFile);
    fclose(corpusFile);
}
