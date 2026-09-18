#include <stdio.h>
int *make_number(void) {
    int n = 42;
    return &n;
}
int main(void) {
    int *p = make_number();
    printf("%d\n", *p);
    return 0;
}