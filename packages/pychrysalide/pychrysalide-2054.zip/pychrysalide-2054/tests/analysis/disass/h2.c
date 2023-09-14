
#include <stdio.h>

int main(int argc, char **argv)
{
    int i;
    int j;

    for (i = 0; i < argc; i++)
    {
        printf("arg[%d]: %s\n", i, argv[i]);

        for (j = 0; j < i; j++)
        {
            printf(".");

#if 1
            if (argc > 2)
                printf("!");
            else
                printf("#");

            printf(".");
#endif

        }

        printf("\n");

    }

    printf("Hello\n");

    return 0;

}
