
#include <stdio.h>
#include <string.h>

int main(int argc, char **argv)
{
    int a;
    char cmd[128];

    memcpy(&a, (int []) { 4 }, sizeof(int));

    sprintf(cmd, "cat /proc/%d/maps", getpid());

    system(cmd);

    printf("Hello %d\n", a);

    return 0;

}
