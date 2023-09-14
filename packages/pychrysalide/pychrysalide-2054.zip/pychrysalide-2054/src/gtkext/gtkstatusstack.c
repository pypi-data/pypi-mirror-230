
/* Chrysalide - Outil d'analyse de fichiers binaires
 * gtkstatusstack.c - empilement d'informations de statut
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


#include "gtkstatusstack.h"


#include <assert.h>
#include <inttypes.h>
#include <malloc.h>
#include <string.h>


#include <i18n.h>


#include "easygtk.h"
#include "../gui/agroup.h"
#include "../format/format.h"



/* ------------------------- GESTION EXTERIEURE DE LA BARRE ------------------------- */


/* Navigation au sein d'assemblage */
typedef struct _assembly_info assembly_info;

/* Mémorisation des progressions */
typedef struct _progress_info progress_info;


/* Abstration d'une gestion de barre de statut (instance) */
struct _GtkStatusStack
{
    GtkBox parent;                          /* A laisser en premier        */

    GtkStack *main;                         /* Pile d'informations associée*/

    GSourceFunc def_source;                 /* Appel en fin d'activité     */

    GObject *asm_ref;                       /* Espace de référencements #1 */
    assembly_info *asm_info;                /* Informations courantes #1   */

    GObject *prog_ref;                      /* Espace de référencements #2 */
    progress_info *prog_info;               /* Informations courantes #2   */

};

/* Abstration d'une gestion de barre de statut (classe) */
struct _GtkStatusStackClass
{
    GtkBoxClass parent;                     /* A laisser en premier        */

};


/* Initialise la classe des barres de statut améliorées. */
static void gtk_status_stack_class_init(GtkStatusStackClass *);

/* Initialise une instance de barre de statut améliorée. */
static void gtk_status_stack_init(GtkStatusStack *);

/* Supprime toutes les références externes. */
static void gtk_status_stack_dispose(GtkStatusStack *);

/* Procède à la libération totale de la mémoire. */
static void gtk_status_stack_finalize(GtkStatusStack *);



/* -------------------- STATUT DES INFORMATIONS DE DESASSEMBLAGE -------------------- */


/* Navigation au sein d'assemblage */
struct _assembly_info
{
    bool reset;                             /* Réinitialisation            */

    mrange_t current;                       /* Emplacement correspondant   */

    char *segment;                          /* Segment d'appartenance      */

    VMPA_BUFFER(phys);                      /* Localisation physique       */
    VMPA_BUFFER(virt);                      /* Localisation virtuelle      */

    char *symbol;                           /* Eventuel symbole concerné   */

    const char *encoding;                   /* Encodage de l'instruction   */
    phys_t size;                            /* Taille de l'instruction     */

};


/* Supprime l'empreinte mémoire d'informations d'assemblage. */
static void reset_assembly_info(assembly_info *);

/* Construit une barre d'état pour language d'assemblage. */
static GtkWidget *build_assembly_status_stack(GtkStatusStack *);

/* Réagit à un redimensionnement de la barre de désassemblage. */
static void on_size_allocate_for_asm_status(GtkWidget *, GdkRectangle *, GObject *);

/* Réagit à un clic sur l'icône de zoom. */
static void on_zoom_icon_press(GtkEntry *, GtkEntryIconPosition, GdkEventButton *, GtkStatusStack *);

/* S'assure de l'affichage à jour de la partie "assemblage". */
static gboolean gtk_status_stack_show_current_location(GtkStatusStack *);



/* -------------------------- STATUT DES SUIVIS D'ACTIVITE -------------------------- */


/* Informations de progression */
typedef struct _progress_status
{
    activity_id_t id;                       /* Identifiant unique          */

    char *message;                          /* Indication à faire valoir   */

    unsigned long current;                  /* Position courante           */
    unsigned long max;                      /* Couverture à parcourir      */

    double last_updated;                    /* Dernière valeur poussée     */

} progress_status;

/* Mémorisation des progressions */
struct _progress_info
{
    activity_id_t generator;                /* Générateur de séquence      */

    progress_status *statuses;              /* Statuts de progression      */
    size_t count;                           /* Nombre de ces statuts       */
    GMutex access;                          /* Accès à la pile             */

    guint tag;                              /* Identifiant de mise à jour  */

};


#define PROGRESS_SIZE 200


/* Supprime l'empreinte mémoire d'informations d'activité. */
static void reset_progress_info(progress_info *);

/* Construit une barre d'état pour un suivi d'activité. */
static GtkWidget *build_progress_status_stack(GtkStatusStack *);

/* S'assure de l'affichage à jour de la partie "activité". */
static gboolean gtk_status_stack_show_current_activity(GtkStatusStack *);



/* ---------------------------------------------------------------------------------- */
/*                           GESTION EXTERIEURE DE LA BARRE                           */
/* ---------------------------------------------------------------------------------- */


/* Détermine le type de la barre de statut améliorée. */
G_DEFINE_TYPE(GtkStatusStack, gtk_status_stack, GTK_TYPE_BOX)


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe GTK à initialiser.                            *
*                                                                             *
*  Description : Initialise la classe des barres de statut améliorées.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_status_stack_class_init(GtkStatusStackClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)gtk_status_stack_dispose;
    object->finalize = (GObjectFinalizeFunc)gtk_status_stack_finalize;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = instance GTK à initialiser.                          *
*                                                                             *
*  Description : Initialise une instance de barre de statut améliorée.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_status_stack_init(GtkStatusStack *stack)
{
    GtkWidget *layer;                       /* Couche à empiler            */

    gtk_orientable_set_orientation(GTK_ORIENTABLE(stack), GTK_ORIENTATION_HORIZONTAL);

    stack->main = GTK_STACK(gtk_stack_new());
    gtk_widget_show(GTK_WIDGET(stack->main));
    gtk_box_pack_start(GTK_BOX(stack), GTK_WIDGET(stack->main), TRUE, TRUE, 8);

    stack->def_source = (GSourceFunc)gtk_status_stack_show_current_location;

    layer = build_assembly_status_stack(stack);
    gtk_stack_add_named(stack->main, layer, "asm_info");

    stack->asm_ref = G_OBJECT(layer);
    stack->asm_info = (assembly_info *)calloc(1, sizeof(assembly_info));

    reset_assembly_info(stack->asm_info);

    layer = build_progress_status_stack(stack);
    gtk_stack_add_named(stack->main, layer, "prog_info");

    stack->prog_ref = G_OBJECT(layer);
    stack->prog_info = (progress_info *)calloc(1, sizeof(progress_info));

    reset_progress_info(stack->prog_info);

    gtk_status_stack_reset_current_location(stack);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_status_stack_dispose(GtkStatusStack *stack)
{
    G_OBJECT_CLASS(gtk_status_stack_parent_class)->dispose(G_OBJECT(stack));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : view = instance d'objet GLib à traiter.                      *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void gtk_status_stack_finalize(GtkStatusStack *stack)
{
    reset_assembly_info(stack->asm_info);
    free(stack->asm_info);

    reset_progress_info(stack->prog_info);
    free(stack->prog_info);

    G_OBJECT_CLASS(gtk_status_stack_parent_class)->finalize(G_OBJECT(stack));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une nouvelle instance de barre de statut.               *
*                                                                             *
*  Retour      : Composant GTK mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GtkStatusStack *gtk_status_stack_new(void)
{
    GtkStatusStack *result;                 /* Instance à retourner        */

    result = g_object_new(GTK_TYPE_STATUS_STACK, NULL);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                      STATUT DES INFORMATIONS DE DESASSEMBLAGE                      */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations à réinitialiser.                         *
*                                                                             *
*  Description : Supprime l'empreinte mémoire d'informations d'assemblage.    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void reset_assembly_info(assembly_info *info)
{
    info->reset = true;

    if (info->segment != NULL)
    {
        free(info->segment);
        info->segment = NULL;
    }

    if (info->symbol != NULL)
    {
        free(info->symbol);
        info->symbol = NULL;
    }

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = composant global en cours de construction.           *
*                                                                             *
*  Description : Construit une barre d'état pour language d'assemblage.       *
*                                                                             *
*  Retour      : Composant GTK mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *build_assembly_status_stack(GtkStatusStack *stack)
{
    GtkWidget *result;                      /* Support à retourner         */
    GObject *ref;                           /* Espace de référencements    */
    GtkWidget *hbox;                        /* Sous-division horizontale   */
    GtkWidget *label;                       /* Etiquette pour impression   */
    GtkWidget *zoom;                        /* Sélection du zoom courant   */

    result = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0);
    gtk_widget_show(result);

    ref = G_OBJECT(result);

    g_signal_connect(result, "size-allocate", G_CALLBACK(on_size_allocate_for_asm_status), ref);

    /* Première partie : navigation */

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 16);
    gtk_widget_show(hbox);
    gtk_box_pack_start(GTK_BOX(result), hbox, TRUE, TRUE, 8);

    label = qck_create_label(ref, "segment", NULL);
    gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

    label = qck_create_label(ref, "phys", NULL);
    gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

    label = qck_create_label(ref, "virt", NULL);
    gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

    label = qck_create_label(ref, "offset", NULL);
    gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

    /* Seconde partie : architecture */

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    g_object_set_data(ref, "arch_box", hbox);
    gtk_widget_show(hbox);
    gtk_box_pack_start(GTK_BOX(result), hbox, FALSE, TRUE, 8);

    label = qck_create_label(ref, "arch", NULL);
    gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

    label = qck_create_label(ref, "size", NULL);
    gtk_box_pack_start(GTK_BOX(hbox), label, FALSE, FALSE, 0);

    /* Troisième partie : affichage */

    hbox = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 8);
    gtk_widget_show(hbox);
    gtk_box_pack_start(GTK_BOX(result), hbox, FALSE, FALSE, 8);

    zoom = qck_create_entry(ref, "zoom", "100%");
    gtk_entry_set_icon_from_icon_name(GTK_ENTRY(zoom), GTK_ENTRY_ICON_SECONDARY, "go-up-symbolic");

    g_signal_connect(zoom, "focus-in-event", G_CALLBACK(track_focus_change_in_text_area), NULL);
    g_signal_connect(zoom, "focus-out-event", G_CALLBACK(track_focus_change_in_text_area), NULL);
    g_signal_connect(zoom, "icon-press", G_CALLBACK(on_zoom_icon_press), stack);

    gtk_box_pack_start(GTK_BOX(hbox), zoom, FALSE, TRUE, 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : widget     = composant graphique qui vient d'évoluer.        *
*                allocation = espace réservé pour le composant visé.          *
*                ref        = espace de référencement global.                 *
*                                                                             *
*  Description : Réagit à un redimensionnement de la barre de désassemblage.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_size_allocate_for_asm_status(GtkWidget *widget, GdkRectangle *allocation, GObject *ref)
{
    GtkWidget *hbox;                        /* Sous-division horizontale   */

    hbox = GTK_WIDGET(g_object_get_data(ref, "arch_box"));

    gtk_widget_set_size_request(hbox, (allocation->width * 40) / 100, -1);

    /**
     * On intervient après que le containeur soit passé collecter les tailles
     * de ses enfants lors de son redimensionnement.
     *
     * Donc on force un prise en compte des changements.
     */
    gtk_container_check_resize(GTK_CONTAINER(widget));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : entry    = zone de texte visée par la procédure.             *
*                icon_pos = position de l'image associée à l'entrée.          *
*                event    = informations liées à l'événement.                 *
*                stack    = composant graphique de gestion des statuts.       *
*                                                                             *
*  Description : Réagit à un clic sur l'icône de zoom.                        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void on_zoom_icon_press(GtkEntry *entry, GtkEntryIconPosition icon_pos, GdkEventButton *event, GtkStatusStack *stack)
{
    GtkWidget *popup;                       /* Popup à faire surgir        */
    GdkRectangle rect;                      /* Zone précise à cibler       */

    if (event->button != GDK_BUTTON_PRIMARY)
        return;

    popup = gtk_popover_new(GTK_WIDGET(entry));

    gtk_entry_get_icon_area(entry, GTK_ENTRY_ICON_SECONDARY, &rect);
    gtk_popover_set_pointing_to(GTK_POPOVER(popup), &rect);

    gtk_widget_show(popup);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack    = barre de statut à actualiser.                     *
*                range    = emplacement à mettre en valeur.                   *
*                segment  = zone de binaire d'appartenance.                   *
*                symbol   = éventuelle position par rapport à un symbole.     *
*                encoding = encodage d'une éventuelle instruction ou NULL.    *
*                                                                             *
*  Description : Actualise les informations liées une position d'assemblage.  *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_status_stack_update_current_location(GtkStatusStack *stack, const mrange_t *range, const char *segment, const char *symbol, const char *encoding)
{
    assembly_info *info;                    /* Informations à constituer   */
    const vmpa2t *addr;                     /* Localisation de départ      */
    phys_t size;                            /* Taille de l'emplacement     */

    info = stack->asm_info;

    /* Bascule vers une zone courante nouvelle ? */

    addr = get_mrange_addr(range);
    size = get_mrange_length(range);

    if (cmp_mrange(&info->current, range) == 0
        && info->size == size
        && info->encoding == encoding)
        goto useless;

    /* Réinitialisation */

    reset_assembly_info(info);

    copy_mrange(&info->current, range);

    /* Zone d'appartenance */

    info->segment = strdup(segment);

    /* Adresses de base */

    vmpa2_phys_to_string(addr, MDS_UNDEFINED, info->phys, NULL);

    vmpa2_virt_to_string(addr, MDS_UNDEFINED, info->virt, NULL);

    info->encoding = encoding;
    info->size = size;

    /* Symbole concerné */

    if (symbol != NULL)
        info->symbol = strdup(symbol);

    /* Nettoyage et conclusion */

    info->reset = false;

    gtk_status_stack_show_current_location(stack);

 useless:

    ;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = barre de statut à actualiser.                        *
*                                                                             *
*  Description : Réinitialise les informations associées une position.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_status_stack_reset_current_location(GtkStatusStack *stack)
{
    assembly_info *info;                    /* Informations à constituer   */

    info = stack->asm_info;

    reset_assembly_info(info);

    gtk_status_stack_show_current_location(stack);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = pile de statuts à manipuler.                         *
*                                                                             *
*  Description : S'assure de l'affichage à jour de la partie "assemblage".    *
*                                                                             *
*  Retour      : G_SOURCE_REMOVE pour une exécution unique.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_status_stack_show_current_location(GtkStatusStack *stack)
{
    GObject *ref;                           /* Espace de référencements    */
    assembly_info *info;                    /* Informations à consulter    */
    GtkLabel *label;                        /* Etiquette à actualiser      */
    char raw_pos[6 + VMPA_MAX_LEN + 1];     /* Formatage final en direct   */
    char *content;                          /* Contenu dynamique           */

    stack->def_source = (GSourceFunc)gtk_status_stack_show_current_location;

    gtk_stack_set_visible_child_name(stack->main, "asm_info");

    ref = stack->asm_ref;
    info = stack->asm_info;

    /* Première partie : navigation */

    if (info->reset)
    {
        label = GTK_LABEL(g_object_get_data(ref, "segment"));
        gtk_label_set_text(label, NULL);

        label = GTK_LABEL(g_object_get_data(ref, "phys"));
        gtk_label_set_text(label, NULL);

        label = GTK_LABEL(g_object_get_data(ref, "virt"));
        gtk_label_set_text(label, NULL);

        label = GTK_LABEL(g_object_get_data(ref, "offset"));
        gtk_label_set_text(label, NULL);

    }
    else
    {
        label = GTK_LABEL(g_object_get_data(ref, "segment"));
        gtk_label_set_text(label, info->segment);

        snprintf(raw_pos, sizeof(raw_pos), "phys: %s", info->phys);

        label = GTK_LABEL(g_object_get_data(ref, "phys"));
        gtk_label_set_text(label, raw_pos);

        snprintf(raw_pos, sizeof(raw_pos), "virt: %s", info->virt);

        label = GTK_LABEL(g_object_get_data(ref, "virt"));
        gtk_label_set_text(label, raw_pos);

        label = GTK_LABEL(g_object_get_data(ref, "offset"));
        gtk_label_set_text(label, info->symbol != NULL ? info->symbol : "");

    }

    /* Seconde partie : architecture */

    if (info->reset || info->encoding == NULL || info->size == VMPA_NO_PHYSICAL)
    {
        label = GTK_LABEL(g_object_get_data(ref, "arch"));
        gtk_label_set_text(label, NULL);

        label = GTK_LABEL(g_object_get_data(ref, "size"));
        gtk_label_set_text(label, NULL);

    }
    else
    {
        label = GTK_LABEL(g_object_get_data(ref, "arch"));
        gtk_label_set_text(label, info->encoding);

        if (info->size > 1)
            asprintf(&content, "%" PRIu64 " %s", (uint64_t)info->size, _("bytes"));
        else
            asprintf(&content, "%" PRIu64 " %s", (uint64_t)info->size, _("byte"));

        label = GTK_LABEL(g_object_get_data(ref, "size"));
        gtk_label_set_text(label, content);

        free(content);

    }

    return G_SOURCE_REMOVE;

}



/* ---------------------------------------------------------------------------------- */
/*                            STATUT DES SUIVIS D'ACTIVITE                            */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : info = informations à réinitialiser.                         *
*                                                                             *
*  Description : Supprime l'empreinte mémoire d'informations d'activité.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void reset_progress_info(progress_info *info)
{
    size_t i;                               /* Boucle de parcours          */

    if (info->tag != 0)
        g_source_remove(info->tag);

    info->tag = 0;

    for (i = 0; i < info->count; i++)
    {
        if (info->statuses[i].message != NULL)
            free(info->statuses[i].message);
    }

    if (info->statuses != NULL)
    {
        free(info->statuses);
        info->statuses = NULL;
    }

    info->count = 0;

    g_mutex_init(&info->access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = composant global en cours de construction.           *
*                                                                             *
*  Description : Construit une barre d'état pour un suivi d'activité.         *
*                                                                             *
*  Retour      : Composant GTK mis en place.                                  *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static GtkWidget *build_progress_status_stack(GtkStatusStack *stack)
{
    GtkWidget *result;                      /* Support à retourner         */
    GObject *ref;                           /* Espace de référencements    */
    GtkWidget *progress;                    /* Barre de progression        */
    GtkWidget *label;                       /* Désignation de l'activité   */

    result = gtk_box_new(GTK_ORIENTATION_HORIZONTAL, 0);
    gtk_widget_show(result);

    ref = G_OBJECT(result);

    progress = gtk_progress_bar_new();
    g_object_set_data(ref, "progress", progress);
    gtk_widget_set_size_request(progress, PROGRESS_SIZE, -1);
    gtk_widget_set_valign(progress, GTK_ALIGN_CENTER);
    gtk_widget_show(progress);
    gtk_box_pack_start(GTK_BOX(result), progress, FALSE, TRUE, 8);

    label = qck_create_label(ref, "message", NULL);
    gtk_box_pack_start(GTK_BOX(result), label, TRUE, TRUE, 0);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = barre de statut à actualiser.                        *
*                msg   = nouveau message de statut à copier.                  *
*                max   = taille de la plage à parcourir.                      *
*                                                                             *
*  Description : Démarre le suivi d'une nouvelle activité.                    *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

activity_id_t gtk_status_stack_add_activity(GtkStatusStack *stack, const char *msg, unsigned long max)
{
    activity_id_t result;                   /* Numéro unique à renvoyer    */
    progress_info *info;                    /* Informations à consulter    */
    size_t new;                             /* Indice de l'activité créée  */

    if (stack == NULL) return NO_ACTIVITY_ID;

    info = stack->prog_info;

    g_mutex_lock(&info->access);

    result = ++info->generator;

    new = info->count++;

    info->statuses = (progress_status *)realloc(info->statuses,
                                                info->count * sizeof(progress_status));

    info->statuses[new].id = result;

    /* Intitulé */

    if (msg == NULL)
        info->statuses[new].message = NULL;
    else
        info->statuses[new].message = strdup(msg);

    /* Valeur */

    info->statuses[new].current = 0;
    info->statuses[new].max = max;
    info->statuses[new].last_updated = 0;

    /* Actualisation */

    if (info->tag != 0)
        g_source_remove(info->tag);

    info->tag = g_idle_add((GSourceFunc)gtk_status_stack_show_current_activity, stack);

    g_mutex_unlock(&info->access);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = barre de statut à actualiser.                        *
*                id    = identifiant de l'activité à cibler.                  *
*                extra = nouvelle échéance supplémentaire des traitements.    *
*                                                                             *
*  Description : Etend la portée des travaux d'une nouvelle activité.         *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_status_stack_extend_activity(GtkStatusStack *stack, activity_id_t id, unsigned long extra)
{
    progress_info *info;                    /* Informations à consulter    */
    size_t i;                               /* Boucle de parcours          */

    if (stack == NULL) return;

    info = stack->prog_info;

    g_mutex_lock(&info->access);

    for (i = 0; i < info->count; i++)
        if (info->statuses[i].id == id)
            break;

    assert(i < info->count);

    info->statuses[i].max += extra;

    g_mutex_unlock(&info->access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = barre de statut à actualiser.                        *
*                id    = identifiant de l'activité à cibler.                  *
*                msg   = nouveau message de statut à copier.                  *
*                                                                             *
*  Description : Actualise les informations concernant une activité.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_status_stack_update_activity(GtkStatusStack *stack, activity_id_t id, const char *msg)
{
    progress_info *info;                    /* Informations à consulter    */
    size_t i;                               /* Boucle de parcours          */
    bool msg_changed;                       /* Changement d'intitulé       */

    if (stack == NULL) return;

    info = stack->prog_info;

    g_mutex_lock(&info->access);

    for (i = 0; i < info->count; i++)
        if (info->statuses[i].id == id)
            break;

    assert(i < info->count);

    /* Intitulé */

    if (info->statuses[i].message != NULL)
    {
        if (msg == NULL)
            msg_changed = true;
        else
            msg_changed = (strcmp(info->statuses[i].message, msg) != 0);

        free(info->statuses[i].message);

    }
    else
        msg_changed = (msg != NULL);

    if (msg == NULL)
        info->statuses[i].message = NULL;
    else
        info->statuses[i].message = strdup(msg);

    /* On n'actualise que le sommet de la pile */

    if ((i + 1) == info->count && msg_changed)
    {
        if (info->tag != 0)
            g_source_remove(info->tag);

        info->tag = g_idle_add((GSourceFunc)gtk_status_stack_show_current_activity, stack);

    }

    g_mutex_unlock(&info->access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = barre de statut à actualiser.                        *
*                id    = identifiant de l'activité à cibler.                  *
*                inc   = nouvelle valeur pour une progression donnée.         *
*                                                                             *
*  Description : Actualise la progression d'une activité.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_status_stack_update_activity_value(GtkStatusStack *stack, activity_id_t id, unsigned long inc)
{
    progress_info *info;                    /* Informations à consulter    */
    size_t i;                               /* Boucle de parcours          */
    progress_status *status;                /* Raccourci de confort        */
    double new;                             /* Nouvelle progression        */

    if (stack == NULL) return;

    info = stack->prog_info;

    g_mutex_lock(&info->access);

    for (i = 0; i < info->count; i++)
        if (info->statuses[i].id == id)
            break;

    assert(i < info->count);

    status = &info->statuses[i];

    /* Valeur */

    status->current += inc;

    new = (status->current * 1.0) / status->max;

    /* On n'actualise que le sommet de la pile */

    if ((i + 1) == info->count && (new - status->last_updated) > (1.0 / PROGRESS_SIZE))
    {
        status->last_updated = new;

        if (info->tag != 0)
            g_source_remove(info->tag);

        info->tag = g_idle_add((GSourceFunc)gtk_status_stack_show_current_activity, stack);

    }

    g_mutex_unlock(&info->access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = barre de statut à actualiser.                        *
*                                                                             *
*  Description : Met fin au suivi d'une activité donnée.                      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void gtk_status_stack_remove_activity(GtkStatusStack *stack, activity_id_t id)
{
    progress_info *info;                    /* Informations à consulter    */
    size_t i;                               /* Boucle de parcours          */

    if (stack == NULL) return;

    info = stack->prog_info;

    g_mutex_lock(&info->access);

    for (i = 0; i < info->count; i++)
        if (info->statuses[i].id == id)
            break;

    assert(i < info->count);

    if (info->tag != 0)
        g_source_remove(info->tag);

    if (info->statuses[i].message != NULL)
        free(info->statuses[i].message);

    if (info->count == 1)
    {
        free(info->statuses);
        info->statuses = NULL;
    }
    else
    {
        memmove(&info->statuses[i], &info->statuses[i + 1],
                (info->count - i - 1) * sizeof(progress_status));

        info->statuses = (progress_status *)realloc(info->statuses,
                                                    (info->count - 1) * sizeof(progress_status));

    }

    info->count--;

    if (info->count == 0)
    {
        info->tag = 0;
        g_idle_add(stack->def_source, stack);
    }
    else
        info->tag = g_idle_add((GSourceFunc)gtk_status_stack_show_current_activity, stack);

    g_mutex_unlock(&info->access);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : stack = pile de statuts à manipuler.                         *
*                                                                             *
*  Description : S'assure de l'affichage à jour de la partie "activité".      *
*                                                                             *
*  Retour      : G_SOURCE_REMOVE pour une exécution unique.                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static gboolean gtk_status_stack_show_current_activity(GtkStatusStack *stack)
{
    GObject *ref;                           /* Espace de référencements    */
    progress_info *info;                    /* Informations à consulter    */
    progress_status *last;                  /* Dernier statut à traiter    */
    GtkProgressBar *progress;               /* Barre de progression        */
    GtkLabel *label;                        /* Désignation de l'activité   */

    if (!g_source_is_destroyed(g_main_current_source()))
    {
        gtk_stack_set_visible_child_name(stack->main, "prog_info");

        ref = stack->prog_ref;
        info = stack->prog_info;

        g_mutex_lock(&info->access);

        info->tag = 0;

        if (info->count > 0)
        {
            last = &info->statuses[info->count - 1];

            progress = GTK_PROGRESS_BAR(g_object_get_data(ref, "progress"));
            gtk_progress_bar_set_fraction(GTK_PROGRESS_BAR(progress), (last->current * 1.0) / last->max);

            label = GTK_LABEL(g_object_get_data(ref, "message"));
            gtk_label_set_text(label, last->message);

        }

        g_mutex_unlock(&info->access);

    }

    return G_SOURCE_REMOVE;

}
