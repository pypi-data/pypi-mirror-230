
/* Chrysalide - Outil d'analyse de fichiers binaires
 * goto.c - boîte de dialogue pour les sauts à une adresse donnée
 *
 * Copyright (C) 2015-2019 Cyrille Bagard
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


#include "gotox.h"


#include <cairo-gobject.h>
#include <malloc.h>


#include <i18n.h>


#include "../../core/columns.h"
#include "../../core/paths.h"
#include "../../format/format.h"
#include "../../format/symiter.h"
#include "../../glibext/gbinarycursor.h"
#include "../../gtkext/easygtk.h"
#include "../../gtkext/gtkblockdisplay.h"



/* Colonnes de la liste des symboles */
typedef enum _GotoXColumn
{
    GXC_PHYSICAL,                           /* Correspondance physique     */
    GXC_VIRTUAL,                            /* Correspondance virtuelle    */

    GXC_PICTURE,                            /* Image de représentation     */
    GXC_ADDRESS,                            /* Adresse mémoire du symbole  */
    GXC_NAME,                               /* Désignation humaine         */
    GXC_CONTENT,                            /* Contenu de la ligne visée   */

    GXC_COUNT                               /* Nombre de colonnes          */

} GotoXColumn;


/* Réagit à une validation d'une ligne affichée. */
static void on_gotox_row_activated(GtkTreeView *, GtkTreePath *, GtkTreeViewColumn *, GtkDialog *);

/* Construit la fenêtre de sélection d'adresses. */
static GtkWidget *create_gotox_dialog(GtkWindow *, GtkTreeStore **);

/* Ajoute une nouvelle localisation de destination. */
static void add_new_location_to_list(GtkTreeStore *, GLoadedBinary *, const vmpa2t *, GBinSymbol *);



/******************************************************************************
*                                                                             *
*  Paramètres  : treeview = composant graphique manipulé par l'utilisateur.   *
*                path     = chemin d'accès à la ligne activée.                *
*                column   = colonne impactée par l'action.                    *
*                dialog   = boîte de dialogue affichant la liste éditée.      *
*                                                                             *
*  Description : Réagit à une validation d'une ligne affichée.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_gotox_row_activated(GtkTreeView *treeview, GtkTreePath *path, GtkTreeViewColumn *column, GtkDialog *dialog)
{
    gtk_dialog_response(dialog, GTK_RESPONSE_OK);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = fenêtre parente à surpasser.                        *
*                store  = modèle de gestion pour les éléments de liste. [OUT] *
*                                                                             *
*  Description : Construit la fenêtre de sélection d'adresses.                *
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *create_gotox_dialog(GtkWindow *parent, GtkTreeStore **store)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkWidget *dlgvbox;                     /* Zone principale de la boîte */
    GtkWidget *vbox;                        /* Support à construire #1     */
    GtkWidget *scrollwnd;                   /* Support défilant            */
    GtkWidget *treeview;                    /* Affichage de la liste       */
    GtkCellRenderer *renderer;              /* Moteur de rendu de colonne  */
    GtkTreeViewColumn *column;              /* Colonne de la liste         */

    result = gtk_dialog_new();
    gtk_window_set_default_size(GTK_WINDOW(result), 600, 350);
    gtk_window_set_position(GTK_WINDOW(result), GTK_WIN_POS_CENTER);
    gtk_window_set_type_hint(GTK_WINDOW(result), GDK_WINDOW_TYPE_HINT_DIALOG);

    gtk_window_set_modal(GTK_WINDOW(result), TRUE);
    gtk_window_set_transient_for(GTK_WINDOW(result), parent);

    dlgvbox = gtk_dialog_get_content_area(GTK_DIALOG(result));
    gtk_widget_show(dlgvbox);

    vbox = gtk_box_new(GTK_ORIENTATION_VERTICAL, 8);
    gtk_widget_show(vbox);
    gtk_box_pack_start(GTK_BOX(dlgvbox), vbox, TRUE, TRUE, 0);
    gtk_container_set_border_width(GTK_CONTAINER(vbox), 8);

    /* Liste arborescente ou linéaire */

    scrollwnd = gtk_scrolled_window_new(NULL, NULL);
    gtk_widget_show(scrollwnd);
    gtk_box_pack_start(GTK_BOX(vbox), scrollwnd, TRUE, TRUE, 0);

    gtk_scrolled_window_set_policy(GTK_SCROLLED_WINDOW(scrollwnd), GTK_POLICY_AUTOMATIC, GTK_POLICY_AUTOMATIC);
    gtk_scrolled_window_set_shadow_type(GTK_SCROLLED_WINDOW(scrollwnd), GTK_SHADOW_IN);

    *store = gtk_tree_store_new(GXC_COUNT,
                                G_TYPE_UINT64, G_TYPE_UINT64,
                                CAIRO_GOBJECT_TYPE_SURFACE,
                                G_TYPE_STRING, G_TYPE_STRING, G_TYPE_STRING);

    treeview = gtk_tree_view_new_with_model(GTK_TREE_MODEL(*store));
    gtk_tree_view_set_headers_visible(GTK_TREE_VIEW(treeview), TRUE);
    gtk_tree_view_set_enable_tree_lines(GTK_TREE_VIEW(treeview), TRUE);

    g_signal_connect(treeview, "row-activated", G_CALLBACK(on_gotox_row_activated), result);

    g_object_set_data(G_OBJECT(result), "treeview", treeview);

    gtk_widget_show(treeview);
    gtk_container_add(GTK_CONTAINER(scrollwnd), treeview);

    /* Cellules d'affichage */

    renderer = gtk_cell_renderer_text_new();
    column = gtk_tree_view_column_new_with_attributes(_("Address"), renderer,
                                                      "markup", GXC_ADDRESS,
                                                      NULL);
    gtk_tree_view_column_set_sort_column_id(column, GXC_ADDRESS);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    column = gtk_tree_view_column_new();

    gtk_tree_view_column_set_title(column, _("Name"));

    renderer = gtk_cell_renderer_pixbuf_new();
    gtk_tree_view_column_pack_start(column, renderer, FALSE);
    gtk_tree_view_column_set_attributes(column, renderer,
                                        "surface", GXC_PICTURE,
                                        NULL);

    g_object_set(G_OBJECT(renderer), "xpad", 4, NULL);

    renderer = gtk_cell_renderer_text_new();
    gtk_tree_view_column_pack_start(column, renderer, TRUE);
    gtk_tree_view_column_set_attributes(column, renderer,
                                        "text", GXC_NAME,
                                        NULL);

    gtk_tree_view_column_set_sort_column_id(column, GXC_NAME);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    renderer = gtk_cell_renderer_text_new();
    column = gtk_tree_view_column_new_with_attributes(_("Content"), renderer,
                                                      "markup", GXC_CONTENT,
                                                      NULL);
    gtk_tree_view_column_set_sort_column_id(column, GXC_CONTENT);
    gtk_tree_view_append_column(GTK_TREE_VIEW(treeview), column);

    /* Zone de validation */

    gtk_dialog_add_button(GTK_DIALOG(result), _("_Cancel"), GTK_RESPONSE_CANCEL);
    gtk_dialog_add_button(GTK_DIALOG(result), _("_Go"), GTK_RESPONSE_OK);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = fenêtre parente à surpasser.                        *
*                binary = binaire dont les points d'entrée sont à afficher.   *
*                                                                             *
*  Description : Construit la fenêtre de sélection des points d'entrée.       *
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_gotox_dialog_for_entry_points(GtkWindow *parent, GLoadedBinary *binary)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkTreeStore *store;                    /* Modèle de gestion           */
    GBinFormat *format;                     /* Format associé au binaire   */
    sym_iter_t *siter;                      /* Parcours des symboles       */
    GBinSymbol *symbol;                     /* Symbole manipulé            */
    bool has_entry_points;                  /* Présences d'insertions ?    */
    vmpa2t addr;                            /* Localisation de symbole     */

    /* Mise en place de la boîte de dialogue */

    result = create_gotox_dialog(parent, &store);

    gtk_window_set_title(GTK_WINDOW(result), _("Binary's entry points"));

    /* Affichage de tous les points d'entrées */

    format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));

    siter = create_symbol_iterator(format, 0);

    has_entry_points = false;

    for (symbol = get_symbol_iterator_current(siter);
         symbol != NULL;
         symbol = get_symbol_iterator_next(siter))
    {
        if (g_binary_symbol_get_stype(symbol) != STP_ENTRY_POINT)
            goto cgdfep_next;

        copy_vmpa(&addr, get_mrange_addr(g_binary_symbol_get_range(symbol)));

        add_new_location_to_list(store, binary, &addr, symbol);

        has_entry_points = true;

 cgdfep_next:

        g_object_unref(G_OBJECT(symbol));

    }

    delete_symbol_iterator(siter);

    g_object_unref(G_OBJECT(format));

    g_object_unref(G_OBJECT(store));

    gtk_dialog_set_response_sensitive(GTK_DIALOG(result), GTK_RESPONSE_OK, has_entry_points);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : parent = fenêtre parente à surpasser.                        *
*                binary = binaire dont les points d'entrée sont à afficher.   *
*                instr  = instruction de référence sur laquelle s'appuyer.    *
*                back   = sens de la récupérations des instructions visées.   *
*                                                                             *
*  Description : Construit la fenêtre de sélection des références croisées.   *
*                                                                             *
*  Retour      : Adresse de la fenêtre mise en place.                         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkWidget *create_gotox_dialog_for_cross_references(GtkWindow *parent, GLoadedBinary *binary, GArchInstruction *instr, bool back)
{
    GtkWidget *result;                      /* Fenêtre à renvoyer          */
    GtkTreeStore *store;                    /* Modèle de gestion           */
    size_t count;                           /* Nombre d'éléments présents  */
    size_t i;                               /* Boucle de parcours          */
    const instr_link_t *item;               /* Instruction diverse liée    */
    const vmpa2t *addr;                     /* Adresse à considérer        */

    /* Mise en place de la boîte de dialogue */

    result = create_gotox_dialog(parent, &store);

    if (back)
        gtk_window_set_title(GTK_WINDOW(result), _("List of backward cross references"));
    else
        gtk_window_set_title(GTK_WINDOW(result), _("List of forward cross references"));

    /* Affichage de toutes les instructions référencées */

    if (back)
    {
        g_arch_instruction_lock_src(instr);

        count = g_arch_instruction_count_sources(instr);

        for (i = 0; i < count; i++)
        {
            item = g_arch_instruction_get_source(instr, i);

            addr = get_mrange_addr(g_arch_instruction_get_range(item->linked));

            add_new_location_to_list(store, binary, addr, NULL);

            unref_instr_link(item);

        }

        g_arch_instruction_unlock_src(instr);

    }

    else
    {
        g_arch_instruction_lock_dest(instr);

        count = g_arch_instruction_count_destinations(instr);

        for (i = 0; i < count; i++)
        {
            item = g_arch_instruction_get_destination(instr, i);

            addr = get_mrange_addr(g_arch_instruction_get_range(item->linked));

            add_new_location_to_list(store, binary, addr, NULL);

            unref_instr_link(item);

        }

        g_arch_instruction_unlock_dest(instr);

    }

    g_object_unref(G_OBJECT(store));

    gtk_dialog_set_response_sensitive(GTK_DIALOG(result), GTK_RESPONSE_OK, count > 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : store  = modèle de gestionnaire pour la liste affichée.      *
*                binary = représentation du binaire chargé en mémoire.        *
*                addr   = localisation à venir ajouter à la liste.            *
*                hint   = éventuel symbole à venir retrouver à l'adresse.     *
*                                                                             *
*  Description : Ajoute une nouvelle localisation de destination.             *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void add_new_location_to_list(GtkTreeStore *store, GLoadedBinary *binary, const vmpa2t *addr, GBinSymbol *hint)
{
    GBufferCache *cache;                    /* Tampon de désassemblage     */
    GLineCursor *cursor;                    /* Emplacement dans un tampon  */
    size_t index;                           /* Indice de ligne à traiter   */
    GBufferLine *line;                      /* Ligne présente à l'adresse  */
    char *virtual;                          /* Transcription d'adresse     */
    char *label;                            /* Etiquette de symbole trouvé */
    GBinFormat *format;                     /* Format associé au binaire   */
    GBinSymbol *symbol;                     /* Symbole associé à l'adresse */
    phys_t diff;                            /* Décalage vis à vis du début */
    char *name;                             /* Désignation humaine         */
    gchar *filename;                        /* Chemin d'accès à utiliser   */
    cairo_surface_t *icon;                  /* Image pour les symboles     */
    char *content;                          /* Contenu de la ligne visée   */
    GtkTreeIter iter;                       /* Point d'insertion           */

    /* Détermination de la ligne concernée */

    cache = g_loaded_binary_get_disassembly_cache(binary);

    g_buffer_cache_rlock(cache);

    cursor = g_binary_cursor_new();
    g_binary_cursor_update(G_BINARY_CURSOR(cursor), addr);

    index = g_buffer_cache_find_index_by_cursor(cache, cursor, true);

    g_object_unref(G_OBJECT(cursor));

    index = g_buffer_cache_look_for_flag(cache, index, BLF_HAS_CODE);

    line = g_buffer_cache_find_line_by_index(cache, index);

    g_buffer_cache_runlock(cache);

    g_object_unref(G_OBJECT(cache));

    /* Adresse en mémoire virtuelle */

    if (line != NULL)
        virtual = g_buffer_line_get_text(line, DLC_VIRTUAL, DLC_VIRTUAL + 1, true);
    else
        virtual = strdup(_("<line address not found>"));

    /* Désignation humaine de l'adresse */

    if (hint != NULL)
    {
        symbol = hint;
        g_object_ref(G_OBJECT(symbol));

        label = g_binary_symbol_get_label(hint);

        /**
         * Cf. commentaire suivant.
         */
        if (label == NULL)
            name = strdup(_("<no symbol found>"));

        else
        {
            name = make_symbol_offset(label, 0);
            free(label);
        }

    }
    else
    {
        format = G_BIN_FORMAT(g_loaded_binary_get_format(binary));

        if (g_binary_format_resolve_symbol(format, addr, true, &symbol, &diff))
        {
            label = g_binary_symbol_get_label(symbol);

            /**
             * Un symbole ne possède pas toujours d'étiquette.
             * C'est le cas par exemple pour les valeurs chargées par
             * les instructions ARM de type 'ldr'.
             */
            if (label == NULL)
                name = strdup(_("<no symbol found>"));

            else
            {
                name = make_symbol_offset(label, diff);
                free(label);
            }

        }
        else
        {
            symbol = NULL;

            name = strdup(_("<no symbol found>"));

        }

        g_object_unref(G_OBJECT(format));

    }

    /* Image de représentation */

    if (symbol == NULL)
        filename = NULL;

    else
        switch (g_binary_symbol_get_stype(symbol))
        {
            case STP_ENTRY_POINT:
                filename = find_pixmap_file("entrypoint.png");
                break;

            default:
                filename = NULL;
                break;

        }

    if (filename != NULL)
    {
        icon = cairo_image_surface_create_from_png(filename);
        g_free(filename);
    }
    else
        icon = NULL;

    /* Contenu d'assemblage */

    if (line != NULL)
        content = g_buffer_line_get_text(line, DLC_ASSEMBLY_HEAD, DLC_COUNT, true);
    else
        content = strdup(_("<assembly line not found>"));

    /* Insertion finale */

    gtk_tree_store_append(store, &iter, NULL);

    gtk_tree_store_set(store, &iter,
                       GXC_PHYSICAL, PHYS_CAST(get_phy_addr(addr)),
                       GXC_VIRTUAL, VIRT_CAST(get_virt_addr(addr)),
                       GXC_PICTURE, icon,
                       GXC_ADDRESS, virtual,
                       GXC_NAME, name,
                       GXC_CONTENT, content,
                       -1);

    if (symbol != NULL)
        g_object_unref(G_OBJECT(symbol));

    if (virtual != NULL) free(virtual);
    if (icon != NULL) cairo_surface_destroy(icon);
    free(name);
    if (content != NULL) free(content);

    if (line != NULL)
        g_object_unref(G_OBJECT(line));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : dialog = boîte de dialogue ayant reçu une validation.        *
*                                                                             *
*  Description : Fournit l'adresse obtenue par la saisie de l'utilisateur.    *
*                                                                             *
*  Retour      : Adresse reccueillie par la boîte de dialogue ou NULL si rien.*
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

vmpa2t *get_address_from_gotox_dialog(GtkWidget *dialog)
{
    vmpa2t *result;                         /* Adresse à retourner         */
    GtkTreeView *treeview;                  /* Liste d'adresses à lire     */
    GtkTreeSelection *selection;            /* Sélection courante          */
    GtkTreeModel *model;                    /* Modèle de gestionnaire      */
    GList *selected;                        /* Liste des sélections        */
    GtkTreeIter iter;                       /* Tête de lecture             */
    G_TYPE_PHYS phys;                       /* Position physique           */
    G_TYPE_VIRT virt;                       /* Adresse virtuelle           */

    treeview = GTK_TREE_VIEW(g_object_get_data(G_OBJECT(dialog), "treeview"));

    selection = gtk_tree_view_get_selection(treeview);

    selected = gtk_tree_selection_get_selected_rows(selection, &model);
    if (selected == NULL) return NULL;

    if (!gtk_tree_model_get_iter(model, &iter, (GtkTreePath *)selected->data))
        return NULL;

    gtk_tree_model_get(model, &iter,
                       GXC_PHYSICAL, &phys,
                       GXC_VIRTUAL, &virt,
                       -1);

    result = make_vmpa(phys, virt);

    g_list_free_full(selected, (GDestroyNotify)gtk_tree_path_free);

    return result;

}
