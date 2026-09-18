#include <stdio.h>
#include <stddef.h>  // for offsetof

// PREDICT: sizeof(struct telemetry) — naive sum is 1+4+1+8 = 14.
// My prediction: ___ (fill in before compiling — think about alignment/padding)

struct telemetry {
    char id;
    int count;
    char flag;
    double value;
};

void bump(struct telemetry *t) {
    t->count = t->count + 1;
}

int main(void) {
    printf("sizeof(struct telemetry) = %zu\n", sizeof(struct telemetry));

    printf("offset of id    = %zu\n", offsetof(struct telemetry, id));
    printf("offset of count = %zu\n", offsetof(struct telemetry, count));
    printf("offset of flag  = %zu\n", offsetof(struct telemetry, flag));
    printf("offset of value = %zu\n", offsetof(struct telemetry, value));

    // EXPLAIN GAPS HERE once you see the actual offsets — fill in after running.

    struct telemetry t = {.id = 'A', .count = 8, .flag = 'Y', .value = 0};

    printf("count before bump = %d\n", t.count);
    bump(&t);
    printf("count after bump  = %d\n", t.count);

    return 0;
}