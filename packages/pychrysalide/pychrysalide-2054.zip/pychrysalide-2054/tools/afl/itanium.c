
#include <malloc.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>


#include <common/io.h>
#include <plugins/itanium/demangler.h>



/* Tampon d'entrée */
static char _input_buffer[4096];



/******************************************************************************
*                                                                             *
*  Paramètres  : argc = nombre d'arguments dans la ligne de commande.         *
*                argv = arguments de la ligne de commande.                    *
*                                                                             *
*  Description : Point d'entrée du programme.                                 *
*                                                                             *
*  Retour      : EXIT_SUCCESS si le prgm s'est déroulé sans encombres.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int main(int argc, char **argv)
{
    int result;                             /* Bilan de l'exécution        */
    ssize_t got;                            /* Quantité de données lues    */
    GCompDemangler *demangler;              /* Décodeur à solliciter       */
    GBinRoutine *routine;                   /* Routine obtenue par décodage*/
    char *desc;                             /* Description finale obtenue  */

    result = EXIT_FAILURE;

    got = safe_read_partial(STDIN_FILENO, _input_buffer, sizeof(_input_buffer));
    if (got <= 0) goto exit;

    printf("input: %zd bytes ('%s')\n", got, _input_buffer);

    demangler = g_itanium_demangler_new();

    routine = g_compiler_demangler_decode_routine(demangler, _input_buffer);
    if (routine == NULL) goto demangling_exit;

    desc = g_binary_routine_to_string(routine, true);

    g_object_unref(G_OBJECT(routine));

    printf("routine: %s\n", desc);

    free(desc);

    result = EXIT_SUCCESS;

 demangling_exit:

    g_object_unref(G_OBJECT(demangler));

 exit:

    return result;

}
