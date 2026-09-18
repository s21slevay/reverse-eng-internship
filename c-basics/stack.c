#include <stdio.h>

void dive(int depth) {
    int local = depth;
    printf("depth=%d &local=%p\n", depth, (void*)&local);
    if (depth < 4) {
        dive(depth + 1);
    }
}

int main(void) {
    dive(0);
    return 0;
}