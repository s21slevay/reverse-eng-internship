// tiny.c — small on purpose: every instruction will be accountable to a line you wrote.
int add3(int a, int b, int c) { return a + b + c; }

int sum_to(int n) {
    int total = 0;
    for (int i = 1; i <= n; i++) total += i;
    return total;
}

int main(void) { return add3(1, 2, 3) + sum_to(10); }