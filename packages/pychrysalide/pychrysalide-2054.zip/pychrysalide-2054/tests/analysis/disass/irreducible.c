
static void argstr(char *p, int flags)
{
    if (flags)
    {
 tilde:
        p++;
    }

    for (;;)
    {
        switch (*p)
        {
            case '\0':
                goto breakloop;

            case ':':
                if (*--p == '~')
                    goto tilde;
                continue;
        }

    }

 breakloop:

    ;

}

int main(int argc, char **argv)
{
    argstr(argv[0], 0);

    return 0;

}
