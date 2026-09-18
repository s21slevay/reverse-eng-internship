#include <stdio.h>

int main(void){
    int x = 42;
    int *p = &x; // p holds the ADDRESS of x

    printf("&x = %p p= %p\n", (void*)&x, (void*)p); // predict: smae or different? 
    printf("*p = %d\n", *p); // predict

    *p=99; //write throught the pointer
    printf("x = %d\n", x); // Predict: what is x now and why?

    printf("sizeof(int)=%zu sizeof(int*)=%zu sizeof(char)=%zu sizeof(double)=%zu\n",
            sizeof(int), sizeof(int*), sizeof(char), sizeof(double));
    
    return 0;
}



