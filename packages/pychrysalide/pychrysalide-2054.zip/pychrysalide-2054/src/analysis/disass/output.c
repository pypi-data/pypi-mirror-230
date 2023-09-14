
/* Chrysalide - Outil d'analyse de fichiers binaires
 * output.h - prototypes pour l'impression des instructions désassemblées
 *
 * Copyright (C) 2010-2019 Cyrille Bagard
 *
 *  This file is part of Chrysalide.
 *
 *  Chrysalide is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  Chrysalide is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with Chrysalide.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "output.h"


#include <assert.h>


#include <i18n.h>


#include "../../core/logs.h"
#include "../../format/known.h"
#include "../../format/format.h"
#include "../../format/symiter.h"
#include "../../glibext/generators/rborder.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : cache  = tampon de récueil des résultats d'impression.       *
*                lang   = langage de haut niveau préféré pour l'impression.   *
*                binary = tampon de récueil des résultats d'impression.       *
*                info   = informations complémentaires à intégrer.            *
*                status = barre de statut avec progression à mettre à jour.   *
*                                                                             *
*  Description : Transcrit du code désassemblé en texte humainement lisible.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void print_disassembled_instructions(GBufferCache *cache, GCodingLanguage *lang, GLoadedBinary *binary, GPreloadInfo *info, GtkStatusStack *status)
{
    GExeFormat *format;                     /* Format associé au binaire   */
    GArchProcessor *proc;                   /* Processeur de l'architecture*/
    GBinPortion *root;                      /* Couche première de portions */
    GBinPortion **portions;                 /* Morceaux d'encadrement      */
    size_t portions_count;                  /* Taille de cette liste       */
    size_t portion_index;                   /* Prochaine portion à traiter */
    sym_iter_t *siter;                      /* Parcours des symboles       */
    GBinSymbol *symbol;                     /* Symbole manipulé            */
    MemoryDataSize msize;                   /* Taille du bus d'adresses    */
    const GBinContent *content;             /* Contenu binaire global      */
    size_t count;                           /* Nombre total d'instructions */
    activity_id_t id;                       /* Identifiant de progression  */
    bool expect_outro;                      /* Fin de zone de code définie */


    size_t comment_count;                   /* Quantité de commentaires    */
    size_t comment_index;                   /* Indice du commantaire actif */
    GDbComment *comment;                    /* Commentaire à ajouter       */
    const vmpa2t *caddr;                    /* Localisation du commentaire */

    size_t i;                               /* Boucle de parcours          */
    GArchInstruction *instr;                /* Instruction à traiter       */
    const vmpa2t *iaddr;                    /* Adresse d'instruction       */
    GBorderGenerator *border;               /* Délimitation de routine     */
    const vmpa2t *paddr;                    /* Adresse de portion          */
    GLineGenerator *generator;              /* Générateur de contenu ajouté*/
    const vmpa2t *saddr;                    /* Adresse de symbole          */
    int compared;                           /* Bilan d'une comparaison     */
    char *label;                            /* Etiquette de symbole        */
    char *errmsg;                           /* Description d'une erreur    */
    SymbolType stype;                       /* Type de symbole trouvé      */
    vmpa2t intro_addr;                      /* Adresse de début de code    */
    vmpa2t outro_addr;                      /* Adresse de fin de code      */
    BufferLineFlags flags;                  /* Propriétés pour la ligne    */
    //mrange_t range;                         /* Couverture sans surface     */



    format = g_loaded_binary_get_format(binary);
    proc = g_loaded_binary_get_processor(binary);

    bool collect_all_portions(GBinPortion *portion, GBinPortion *parent, BinaryPortionVisit visit, void *unused)
    {
        if (visit == BPV_ENTER || visit == BPV_SHOW)
        {
            portions = (GBinPortion **)realloc(portions, ++portions_count * sizeof(GBinPortion *));
            portions[portions_count - 1] = portion;
        }

        return true;

    }

    portions = NULL;
    portions_count = 0;

    portion_index = 0;

    root = g_exe_format_get_portions(format);

    g_binary_portion_visit(root, (visit_portion_fc)collect_all_portions, NULL);

    g_object_unref(G_OBJECT(root));

    siter = create_symbol_iterator(G_BIN_FORMAT(format), 0);

    symbol = get_symbol_iterator_current(siter);

    msize = g_arch_processor_get_memory_size(proc);

    content = g_known_format_get_content(G_KNOWN_FORMAT(format));

    g_arch_processor_lock(proc);

    count = g_arch_processor_count_instructions(proc);

    id = gtk_status_stack_add_activity(status, _("Printing all disassebled parts..."), count);

    expect_outro = false;

    g_preload_info_lock_comments(info);

    comment_count = _g_preload_info_count_comments(info);
    comment_index = 0;

    if (comment_index < comment_count)
    {
        comment = _g_preload_info_grab_comment(info, comment_index);
        caddr = g_db_comment_get_address(comment);

        comment_index++;

    }

    else
        comment = NULL;

    /*
    if (comment != NULL)
        log_variadic_message(LMT_BAD_BINARY,
                             _("Got comment '%s' @ 0x%08x"),
                             g_db_comment_get_text(comment), get_phy_addr(caddr));
    */


    for (i = 0; i < count; i++)
    {
        instr = g_arch_processor_get_instruction(proc, i);

        iaddr = get_mrange_addr(g_arch_instruction_get_range(instr));

        /* Fin d'une portion de code précédente ? */

        if (expect_outro && cmp_vmpa(iaddr, &outro_addr) >= 0)
        {
            expect_outro = false;

            border = g_border_generator_new(lang, iaddr, false, msize);
            g_buffer_cache_append(cache, G_LINE_GENERATOR(border), BLF_NONE);

        }

        /* Début d'une nouvelle portion ? */

        while (portion_index < portions_count)
        {
            paddr = get_mrange_addr(g_binary_portion_get_range(portions[portion_index]));

            if (cmp_vmpa_by_phy(iaddr, paddr) != 0)
                break;

            generator = G_LINE_GENERATOR(portions[portion_index]);

            /* Si elle comporte une description ! */
            if (g_line_generator_count_lines(generator) > 0)
                g_buffer_cache_append(cache, generator, BLF_NONE);

            portion_index++;

        }

        /* Début d'un nouveau symbole ? */

        compared = -1;

        if (symbol != NULL)
        {
            iaddr = get_mrange_addr(g_arch_instruction_get_range(instr));

            for ( ; symbol != NULL; symbol = get_symbol_iterator_next(siter))
            {
                saddr = get_mrange_addr(g_binary_symbol_get_range(symbol));

                compared = cmp_vmpa(iaddr, saddr);

                if (compared <= 0)
                    break;

                label = g_binary_symbol_get_label(symbol);

                if (label == NULL)
                    asprintf(&errmsg, _("Unable to find a proper location for symbol"));

                else
                {
                    asprintf(&errmsg, _("Unable to find a proper location for symbol '%s'"), label);
                    free(label);
                }

                g_arch_processor_add_error(proc, APE_LABEL, saddr, errmsg);

                free(errmsg);

                g_object_unref(G_OBJECT(symbol));

            }

            if (symbol == NULL)
                goto no_more_symbol_finally;

            if (compared == 0)
            {
                /* Coupure pour une nouvelle routine */

                stype = g_binary_symbol_get_stype(symbol);

                if (stype == STP_ROUTINE || stype == STP_ENTRY_POINT)
                {
                    /* Impression de la marque de début */

                    copy_vmpa(&intro_addr, get_mrange_addr(g_binary_symbol_get_range(symbol)));

                    border = g_border_generator_new(lang, &intro_addr, true, msize);
                    g_buffer_cache_append(cache, G_LINE_GENERATOR(border), BLF_NONE);

                    /* Mémorisation de la fin */

                    /**
                     * On ne peut pas utiliser l'adresse obtenue dans outro_addr
                     * comme localisation de la marque de clôture. En effet, en
                     * fin du contenu ou de segment, l'adresse générée peut être
                     * inexistante.
                     *
                     * On utilise donc l'adresse de l'instruction suivante.
                     *
                     * On est cependant bien conscient qu'une instruction suivante
                     * est nécessaire pour imprimer cette marque de clôture.
                     */

                    compute_mrange_end_addr(g_binary_symbol_get_range(symbol), &outro_addr);

                    expect_outro = true;

                }

                /* Etiquette ? */

                generator = g_binary_symbol_produce_label(symbol);

                if (generator != NULL)
                    g_buffer_cache_append(cache, generator, BLF_NONE);

            }

        }

 no_more_symbol_finally:

        flags = BLF_NONE;

        if (compared == 0)
        {
            /* Point d'entrée ? */

            if (stype == STP_ENTRY_POINT)
                flags |= BLF_ENTRYPOINT;

            /**
             * Début d'un groupe bien cohérent avec les alignements ?
             *
             * On décide que, à partir du moment où il y a un symbole, il y a
             * là le début d'un nouveau bloc avec sa propre nouvelle gestion
             * des largeurs, quelque soit le type du symbole en question !
             *
             * Seule exception : les symboles créés de toute pièce, qui
             * n'interviennent que comme opérandes, et qui ne peuvent donc
             * pas couper le rendu du flot d'exécution.
             */

            if (stype != STP_DYN_STRING)
                flags |= BLF_WIDTH_MANAGER;

            g_object_unref(G_OBJECT(symbol));
            symbol = get_symbol_iterator_next(siter);

        }

        g_buffer_cache_append(cache, G_LINE_GENERATOR(instr), flags);

        /* Commentaire en bout de ligne ? */

        if (comment != NULL)
        {
            compared = cmp_vmpa(iaddr, caddr);

            if (compared >= 0)
            {
                if (compared == 0)
                    /* FIXME *** g_db_item_apply(G_DB_ITEM(comment), binary) */;

                else
                    log_variadic_message(LMT_BAD_BINARY,
                                         _("Unable to find a proper location for comment '%s' @ 0x%08x"),
                                         g_db_comment_get_text(comment), get_phy_addr(caddr));

                g_object_unref(G_OBJECT(comment));

                if (comment_index < comment_count)
                {
                    comment = _g_preload_info_grab_comment(info, comment_index);
                    caddr = g_db_comment_get_address(comment);

                    comment_index++;

                }

                else
                    comment = NULL;

            }

        }

        g_object_unref(G_OBJECT(instr));

        gtk_status_stack_update_activity_value(status, id, 1);

    }

    assert(comment_index == comment_count);

    _g_preload_info_drain_comments(info);

    g_preload_info_unlock_comments(info);

    gtk_status_stack_remove_activity(status, id);

    g_arch_processor_unlock(proc);

    g_object_unref(G_OBJECT(content));

    if (symbol != NULL)
        g_object_unref(G_OBJECT(symbol));

    delete_symbol_iterator(siter);

    if (portions != NULL)
        free(portions);

    g_object_unref(G_OBJECT(proc));
    g_object_unref(G_OBJECT(format));

}
