
#include <stdio.h>

int main(int argc, char **argv)
{
    int i;

    for (i = 0; i < argc; i++)
    {
        printf("arg[%d]: %s\n", i, argv[i]);

        if (argc > 2)
            printf("!");
        else
            printf("#");

        printf(".");

    }

    printf("Hello\n");

    return 0;

}
