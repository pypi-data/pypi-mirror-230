
/* Chrysalide - Outil d'analyse de fichiers binaires
 * strsym.c - gestion des chaînes dans un binaire
 *
 * Copyright (C) 2018-2019 Cyrille Bagard
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


#include "strsym.h"


#include <assert.h>
#include <ctype.h>
#include <malloc.h>
#include <string.h>


#include "symbol-int.h"
#include "../arch/operands/feeder-int.h"
#include "../common/alloc.h"
#include "../core/columns.h"



/* ----------------------- VITRINE POUR CHAINES DE CARACTERES ----------------------- */


/* Symbole pour chaîne de caractères (instance) */
struct _GStrSymbol
{
    GBinSymbol parent;                      /* A laisser en premier        */

    bool structural;                        /* Nature d'emploi de la chaîne*/

    StringEncodingType encoding;            /* Encodage de la chaîne liée  */

    union
    {
        GBinContent *content;               /* Conteneur d'origine         */
        char *string;                       /* Données utilisables         */

    };

    bool has_content;                       /* Choix dans l'union          */

};

/* Symbole pour chaîne de caractères (classe) */
struct _GStrSymbolClass
{
    GBinSymbolClass parent;                 /* A laisser en premier        */

};


/* Initialise la classe des chaînes de caractères. */
static void g_string_symbol_class_init(GStrSymbolClass *);

/* Initialise une instance de chaîne de caractères. */
static void g_string_symbol_init(GStrSymbol *);

/* Procède à l'initialisation de l'interface de fourniture. */
static void g_string_symbol_feeder_interface_init(GProxyFeederInterface *);

/* Supprime toutes les références externes. */
static void g_string_symbol_dispose(GStrSymbol *);

/* Procède à la libération totale de la mémoire. */
static void g_string_symbol_finalize(GStrSymbol *);

/* Vérifie la pertinence de l'encodage attribué à une chaîne. */
static void g_string_symbol_check_encoding(GStrSymbol *);



/* ------------------------- FONCTIONNALITES DE FOURNITURES ------------------------- */


/* Compare un fournisseur avec un autre. */
int g_string_symbol_compare(const GStrSymbol *, const GStrSymbol *);

/* Traduit un fournisseur en version humainement lisible. */
void g_string_symbol_print(const GStrSymbol *, GBufferLine *);

/* Charge un fournisseur depuis une mémoire tampon. */
bool g_string_symbol_unserialize(GStrSymbol *, GBinFormat *, packed_buffer_t *);

/* Sauvegarde un fournisseur dans une mémoire tampon. */
bool g_string_symbol_serialize(const GStrSymbol *, packed_buffer_t *);



/* ---------------------------------------------------------------------------------- */
/*                         VITRINE POUR CHAINES DE CARACTERES                         */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un symbole d'exécutable. */
G_DEFINE_TYPE_WITH_CODE(GStrSymbol, g_string_symbol, G_TYPE_BIN_SYMBOL,
                        G_IMPLEMENT_INTERFACE(G_TYPE_PROXY_FEEDER, g_string_symbol_feeder_interface_init));


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des chaînes de caractères.              *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_symbol_class_init(GStrSymbolClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_string_symbol_dispose;
    object->finalize = (GObjectFinalizeFunc)g_string_symbol_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = instance à initialiser.                             *
*                                                                             *
*  Description : Initialise une instance de chaîne de caractères.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_symbol_init(GStrSymbol *symbol)
{
    symbol->structural = false;

    symbol->encoding = SET_NONE;

    symbol->string = NULL;

    symbol->has_content = false;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : iface = interface GLib à initialiser.                        *
*                                                                             *
*  Description : Procède à l'initialisation de l'interface de fourniture.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_symbol_feeder_interface_init(GProxyFeederInterface *iface)
{
    iface->compare = (compare_proxy_operand_fc)g_string_symbol_compare;

    iface->print = (print_proxy_feeder_fc)g_string_symbol_print;

    //iface->unserialize = (unserialize_proxy_feeder_fc)g_string_symbol_unserialize;
    //iface->serialize = (serialize_proxy_feeder_fc)g_string_symbol_serialize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_symbol_dispose(GStrSymbol *symbol)
{
    if (symbol->has_content)
        g_clear_object(&symbol->content);

    G_OBJECT_CLASS(g_string_symbol_parent_class)->dispose(G_OBJECT(symbol));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = instance d'objet GLib à traiter.                    *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_symbol_finalize(GStrSymbol *symbol)
{
    if (!symbol->has_content)
        free(symbol->string);

    G_OBJECT_CLASS(g_string_symbol_parent_class)->finalize(G_OBJECT(symbol));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : encoding = encodage de la chaîne de caractères à représenter.*
*                format   = format binaire reconnu.                           *
*                range    = espace couvert par le nouveau symbole.            *
*                                                                             *
*  Description : Crée un nouveau symbole pour chaîne de caractères.           *
*                                                                             *
*  Retour      : Adresse de l'instance mise en place ou NULL en cas d'échec.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinSymbol *g_string_symbol_new_read_only(StringEncodingType encoding, GKnownFormat *format, const mrange_t *range)
{
    GStrSymbol *result;                     /* Nouveau symbole à renvoyer  */

    result = g_object_new(G_TYPE_STR_SYMBOL, NULL);

    g_string_symbol_init_read_only(result, encoding, format, range);

    return G_BIN_SYMBOL(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbole  = symbole dont la définition est à initialiser.     *
*                encoding = encodage de la chaîne de caractères à représenter.*
*                format   = format binaire reconnu.                           *
*                range    = espace couvert par le nouveau symbole.            *
*                                                                             *
*  Description : Réalise la complète initialisation d'unsymbole pour chaîne.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_string_symbol_init_read_only(GStrSymbol *symbol, StringEncodingType encoding, GKnownFormat *format, const mrange_t *range)
{
    GBinSymbol *parent;                     /* Type d'instance parent      */

    parent = G_BIN_SYMBOL(symbol);

    g_binary_symbol_set_range(parent, range);
    g_binary_symbol_set_stype(parent, STP_RO_STRING);

    symbol->encoding = encoding;

    symbol->content = g_known_format_get_content(format);
    symbol->has_content = true;

    g_string_symbol_check_encoding(symbol);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : encoding = encodage de la chaîne de caractères à représenter.*
*                string   = contenu de la chaîne de caractères.               *
*                addr     = emplacement de cette chaîne virtuelle.            *
*                                                                             *
*  Description : Crée un nouveau symbole pour chaîne de caractères.           *
*                                                                             *
*  Retour      : Adresse de l'instance mise en place ou NULL en cas d'échec.  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GBinSymbol *g_string_symbol_new_dynamic(StringEncodingType encoding, const char *string, const vmpa2t *addr)
{
    GStrSymbol *result;                     /* Nouveau symbole à renvoyer  */

    result = g_object_new(G_TYPE_STR_SYMBOL, NULL);

    g_string_symbol_init_dynamic(result, encoding, string, addr);

    return G_BIN_SYMBOL(result);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbole  = symbole dont la définition est à initialiser.     *
*                encoding = encodage de la chaîne de caractères à représenter.*
*                string   = contenu de la chaîne de caractères.               *
*                addr     = emplacement de cette chaîne virtuelle.            *
*                                                                             *
*  Description : Réalise la complète initialisation d'unsymbole pour chaîne.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_string_symbol_init_dynamic(GStrSymbol *symbol, StringEncodingType encoding, const char *string, const vmpa2t *addr)
{
    GBinSymbol *parent;                     /* Type d'instance parent      */
    mrange_t range;                         /* Emplacement à constituer    */

    parent = G_BIN_SYMBOL(symbol);

    init_mrange(&range, addr, strlen(string));

    g_binary_symbol_set_range(parent, &range);
    g_binary_symbol_set_stype(parent, STP_DYN_STRING);

    symbol->encoding = encoding;

    symbol->string = strdup(string);
    symbol->has_content = false;

    g_string_symbol_check_encoding(symbol);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                                                                             *
*  Description : Vérifie la pertinence de l'encodage attribué à une chaîne.   *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_string_symbol_check_encoding(GStrSymbol *symbol)
{
    size_t length;                          /* Taille de la chaîne         */
    const char *string;                     /* Données à analyser          */
    size_t i;                               /* Boucle de parcours          */

    switch (symbol->encoding)
    {
        case SET_NONE:
            assert(false);
            break;

        case SET_ASCII:
            break;

        case SET_UTF_8:
        case SET_MUTF_8:

            string = g_string_symbol_get_utf8(symbol, &length);

            if (!g_utf8_validate(string, length, NULL))
                symbol->encoding = SET_ASCII;

            break;

        case SET_GUESS:

            string = g_string_symbol_get_utf8(symbol, &length);

            /**
             * Afin de ne pas réaliser d'allocation avec strndup(), on simule
             * un appel à g_str_is_ascii() :
             *
             *    gboolean g_str_is_ascii (const gchar *str);
             *
             *    """
             *    Determines if a string is pure ASCII. A string is pure ASCII
             *    if it contains no bytes with the high bit set.
             *    """"
             */

            symbol->encoding = SET_ASCII;

            for (i = 0; i < length; i++)
                if (string[i] & 0x80)
                {
                    symbol->encoding = SET_GUESS;
                    break;
                }

            if (symbol->encoding == SET_GUESS)
            {
                if (g_utf8_validate(string, -1, NULL))
                    symbol->encoding = SET_UTF_8;

                else
                    symbol->encoding = SET_ASCII;

            }

            break;

    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir actualiser.                         *
*                                                                             *
*  Description : Définit si une chaîne de caractères est liée au format.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_string_symbol_set_structural(GStrSymbol *symbol, bool status)
{
    symbol->structural = status;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                                                                             *
*  Description : Indique si une chaîne de caractères est liée au format.      *
*                                                                             *
*  Retour      : Indication sur l'emploi de la chaîne.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_string_symbol_is_structural(const GStrSymbol *symbol)
{
    bool result;                            /* Statut à retourner          */

    result = symbol->structural;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                                                                             *
*  Description : Fournit l'encodage d'une chaîne de caractères.               *
*                                                                             *
*  Retour      : Type d'encodage utilisé.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

StringEncodingType g_string_symbol_get_encoding(const GStrSymbol *symbol)
{
    StringEncodingType result;              /* Type à retourner            */

    result = symbol->encoding;

    assert(result != SET_GUESS);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                                                                             *
*  Description : Fournit la chaîne brute de caractères du symbole.            *
*                                                                             *
*  Retour      : Chaîne de caractères d'origine.                              *
*                                                                             *
*  Remarques   : Cf. fonction g_string_symbol_get_utf8() pour l'existence     *
*                du paramètre length.                                         *
*                                                                             *
******************************************************************************/

const char *g_string_symbol_get_raw(const GStrSymbol *symbol, size_t *length)
{
    const char *result;                     /* Données à retourner         */
    const mrange_t *range;                  /* Couverture du symbole       */
    vmpa2t pos;                             /* Tête de lecture modifiable  */
    phys_t len;                             /* Taille de la chaîne         */

    if (symbol->has_content)
    {
        range = g_binary_symbol_get_range(G_BIN_SYMBOL(symbol));

        copy_vmpa(&pos, get_mrange_addr(range));

        len = get_mrange_length(range);

        result = (const char *)g_binary_content_get_raw_access(symbol->content, &pos, len);

        *length = len;

    }

    else
    {
        result = symbol->string;
        *length = strlen(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = symbole à venir consulter.                          *
*                length = taille de la chaîne renvoyée. [OUT]                 *
*                                                                             *
*  Description : Fournit la chaîne de caractères du symbole.                  *
*                                                                             *
*  Retour      : Chaîne de caractères, à priori en UTF-8.                     *
*                                                                             *
*  Remarques   : Lorsque la chaîne est lue à partir du contenu brut, elle     *
*                peut ne pas être terminée par un octet nul (c'est le cas     *
*                avec le fichier strings.asm par exemple, dans la suite de    *
*                tests, où la séparation est marquée par un simple retour     *
*                chariot).                                                    *
*                                                                             *
*                Un appel à strlen() sur le résultat renvoyé n'est donc pas   *
*                fiable à posteriori, donc on renseigne la taille ici.        *
*                                                                             *
******************************************************************************/

const char *g_string_symbol_get_utf8(const GStrSymbol *symbol, size_t *length)
{
    const char *result;                     /* Données à retourner         */
    const mrange_t *range;                  /* Couverture du symbole       */
    vmpa2t pos;                             /* Tête de lecture modifiable  */
    phys_t len;                             /* Taille de la chaîne         */

    if (symbol->has_content)
    {
        range = g_binary_symbol_get_range(G_BIN_SYMBOL(symbol));

        copy_vmpa(&pos, get_mrange_addr(range));

        len = get_mrange_length(range);

        result = (const char *)g_binary_content_get_raw_access(symbol->content, &pos, len);

        *length = len;

    }

    else
    {
        result = symbol->string;
        *length = strlen(result);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = chaîne de caractères à consulter.                   *
*                format = informations chargées à consulter.                  *
*                                                                             *
*  Description : Construit une désignation pour chaîne de caractères.         *
*                                                                             *
*  Retour      : Bilan de l'opération de mise en place.                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_string_symbol_build_label(GStrSymbol *symbol, GBinFormat *format)
{
    const char *base;                       /* Contenu complet et original */
    size_t length;                          /* Taille de la chaîne         */
    size_t allocated;                       /* Taille réservée             */
    char *label;                            /* Etiquette à constituer      */
    size_t cur;                             /* Point d'écriture courant    */
    unsigned int wc;                        /* Nombre de mots rencontrés   */
    size_t i;                               /* Boucle de parcours #1       */
    char *iter;                             /* Boucle de parcours #2       */
    gunichar c;                             /* Caractère unicode           */
    gchar *converted;                       /* Caractère converti          */
    glong size;                             /* Taille du caractère         */
    bool empty;                             /* Base de l'étiquette vide ?  */
    GBinSymbol *found;                      /* Symbole similaire trouvé    */
    const mrange_t *range;                  /* Couverture du symbole       */
    vmpa2t pos;                             /* Tête de lecture modifiable  */
    VMPA_BUFFER(last_sfx);                  /* Dernier suffixe à intégrer  */

    /* Base de décision */

    base = g_string_symbol_get_utf8(symbol, &length);

    if (base == NULL)
        return false;

    /* Phase de constitution */

    allocated = length + 5 + VMPA_MAX_LEN + 1;
    label = (char *)malloc(allocated * sizeof(char));

    cur = 0;

    wc = 0;

    /**
     * Version simple et rapide.
     */
    if (symbol->encoding == SET_ASCII || g_str_is_ascii(base))
    {
        for (i = 0; i < length; i++)
        {
            if (isalnum(base[i])) label[cur++] = tolower(base[i]);

            else if (cur > 0)
            {
                if (label[cur - 1] != '_') wc++;

                if (wc == 3) break;

                if (label[cur - 1] != '_') label[cur++] = '_';

            }

        }

    }

    /**
     * Version complète.
     */
    else
    {
        for (iter = g_utf8_offset_to_pointer(base, 0);
             iter != NULL;
             iter = g_utf8_find_next_char(iter, NULL))
        {
            c = g_utf8_get_char_validated(iter, -1);

            /**
             * Si le caractère n'est pas valide (chaîne chiffrée ?)...
             */
            if (c == (gunichar)-1 || c == (gunichar)-2)
                break;

            if (c == '\0')
                break;

            else if (g_unichar_isalnum(c))
            {
                c = g_unichar_tolower(c);

                converted = g_ucs4_to_utf8(&c, 1, NULL, &size, NULL);

                label = ensure_allocation_size(label, &allocated, cur + size);

                memcpy(label + cur, converted, size);

                g_free(converted);

                cur += size;

            }

            else if (cur > 0)
            {
                if (label[cur - 1] != '_') wc++;

                if (wc == 3) break;

                if (label[cur - 1] != '_')
                {
                    label = ensure_allocation_size(label, &allocated, cur + 1);
                    label[cur++] = '_';
                }

            }

        }

    }

    empty = (cur == 0);

    if (!empty && label[cur - 1] != '_')
    {
        label = ensure_allocation_size(label, &allocated, cur + 1);
        label[cur++] = '_';
    }

    label = ensure_allocation_size(label, &allocated, cur + 4);

    strcpy(label + cur, "str");
    cur += 3;

    /* Détermination du suffixe suffisant */

    found = NULL;

    if (empty || g_binary_format_find_symbol_by_label(format, label, &found))
    {
        if (found != NULL)
            g_object_unref(G_OBJECT(found));

        if (label[cur - 1] != '_')
        {
            label = ensure_allocation_size(label, &allocated, cur + 1);
            label[cur++] = '_';
        }

        range = g_binary_symbol_get_range(G_BIN_SYMBOL(symbol));

        copy_vmpa(&pos, get_mrange_addr(range));

        assert(has_phys_addr(&pos) || has_virt_addr(&pos));

        if (has_virt_addr(&pos))
            vmpa2_virt_to_string(&pos, MDS_UNDEFINED, last_sfx, NULL);
        else
            vmpa2_phys_to_string(&pos, MDS_UNDEFINED, last_sfx, NULL);

        label = ensure_allocation_size(label, &allocated, cur + strlen(last_sfx) + 1);

        strcpy(label + cur, last_sfx);

    }

    /* Application */

    g_binary_symbol_set_alt_label(G_BIN_SYMBOL(symbol), label);

    free(label);

    return true;

}



/* ---------------------------------------------------------------------------------- */
/*                           FONCTIONNALITES DE FOURNITURES                           */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : a = premier fournisseur à consulter.                         *
*                b = second fournisseur à consulter.                          *
*                                                                             *
*  Description : Compare un fournisseur avec un autre.                        *
*                                                                             *
*  Retour      : Bilan de la comparaison.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int g_string_symbol_compare(const GStrSymbol *a, const GStrSymbol *b)
{
    int result;                             /* Bilan à retourner           */
    GBinSymbol *sa;                         /* Version parente pour A      */
    GBinSymbol *sb;                         /* Version parente pour B      */

    sa = G_BIN_SYMBOL(a);
    sb = G_BIN_SYMBOL(b);

    result = g_binary_symbol_cmp((const GBinSymbol * const *)&sa, (const GBinSymbol * const *)&sb);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = fournisseur à traiter.                              *
*                line   = ligne tampon où imprimer l'élément donné.           *
*                                                                             *
*  Description : Traduit un fournisseur en version humainement lisible.       *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void g_string_symbol_print(const GStrSymbol *symbol, GBufferLine *line)
{
    const char *string;                     /* Chaîne de caractères        */
    size_t len;                             /* Taille du texte à créer     */

    string = g_string_symbol_get_utf8(symbol, &len);

    g_buffer_line_append_text(line, DLC_ASSEMBLY, "\"", 1, RTT_STRING, NULL);

    if (len > 0)
        g_buffer_line_append_text(line, DLC_ASSEMBLY, string, len, RTT_STRING, NULL);

    g_buffer_line_append_text(line, DLC_ASSEMBLY, "\"", 1, RTT_STRING, NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = fournisseur à constituer.                           *
*                format = format binaire chargé associé à l'architecture.     *
*                pbuf   = zone tampon à remplir.                              *
*                                                                             *
*  Description : Charge un fournisseur depuis une mémoire tampon.             *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_string_symbol_unserialize(GStrSymbol *symbol, GBinFormat *format, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    vmpa2t addr;                            /* Adresse à cibler            */

    result = unpack_vmpa(&addr, pbuf);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : symbol = fournisseur à consulter.                            *
*                pbuf   = zone tampon à remplir.                              *
*                                                                             *
*  Description : Sauvegarde un fournisseur dans une mémoire tampon.           *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool g_string_symbol_serialize(const GStrSymbol *symbol, packed_buffer_t *pbuf)
{
    bool result;                            /* Bilan à retourner           */
    const mrange_t *range;                  /* Emplacement du symbole      */

    range = g_binary_symbol_get_range(G_BIN_SYMBOL(symbol));

    result = pack_vmpa(get_mrange_addr(range), pbuf);

    return result;

}
