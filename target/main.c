#include <stdio.h>
#include <string.h>
#include "mathutils.h"

int main(int argc, char *argv[]) {
    if (argc < 2) {
        printf("usage: %s <string>\n", argv[0]);
        return 1;
    }

    unsigned int sum = checksum((const unsigned char *)argv[1], strlen(argv[1]));
    int clamped = clamp((int)sum, 0, 1000);

    printf("checksum=%u clamped=%d\n", sum, clamped);
    return 0;
}