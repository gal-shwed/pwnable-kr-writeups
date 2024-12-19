#include <time.h>
#include <stdio.h>
#include <stdlib.h>


int main(void)
{
    srand(time(0));
    printf("%d", rand()*0 + rand() + rand() - rand() + rand() + rand() - rand() + rand());
    return 0;
}
