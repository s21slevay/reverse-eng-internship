#include "mathutils.h"

int clamp(int v, int lo, int hi) {
    if (v < lo) return lo;
    if (v > hi) return hi;
    return v;
}

unsigned int checksum(const unsigned char *data, int n) {
    unsigned int acc = 0;
    for (int i = 0; i < n; i++) {
        acc = acc * 31 + data[i];
    }
    return acc;
}