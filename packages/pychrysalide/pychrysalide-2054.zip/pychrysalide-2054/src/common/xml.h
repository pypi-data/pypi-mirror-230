
/* Firebox Tools - Outils de configurations pour le WM Firebox
 * xml.h - prototypes pour la lecture ou l'écriture de documents XML
 *
 * Copyright (C) 2009-2019 Cyrille Bagard
 *
 *  This file is part of Firebox Tools.
 *
 *  Firebox Tools is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  Firebox Tools is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#ifndef _XML_H
#define _XML_H


#include <glib.h>
#include <stdbool.h>
#include <stdint.h>
#include <libxml/tree.h>
#include <libxml/xmlwriter.h>
#include <libxml/xpath.h>



/* Crée un nouveau fichier XML. */
bool create_new_xml_file(xmlDocPtr *, xmlXPathContextPtr *);

/*  Charge un document XML entièrement en mémoire. */
bool load_xml_from_memory(const char *, size_t, xmlDocPtr *, xmlXPathContextPtr *);

/* Sauvegarde une structure XML dans un fichier. */
bool save_xml_file(xmlDocPtr, const char *);

/* Ferme une structure XML. */
void close_xml_file(xmlDocPtr, xmlXPathContextPtr);



/* --------------------- OPERATIONS DE LECTURE D'UN FICHIER XML --------------------- */


#define XPATH_OBJ_NODES_COUNT(obj) (obj != NULL ? obj->nodesetval->nodeNr : 0)
#define NODE_FROM_PATH_OBJ(obj, i) obj->nodesetval->nodeTab[i]


/* Ouvre un fichier XML de façon encadrée. */
gboolean open_xml_file(const char *, xmlDoc **, xmlXPathContextPtr *);

/* Obtient de façon encadrée l'accès à un noeud défini. */
xmlXPathObjectPtr get_node_xpath_object(xmlXPathContextPtr, const char *);

/* Obtient le nom de balise d'un noeud donné. */
char *qck_get_node_name(xmlNodePtr);

/* Obtient le nom de balise d'un noeud donné. */
char *get_node_name(xmlXPathContextPtr, const char *);

/* Obtient une valeur placée entre <...> et </...>. */
char *qck_get_node_text_value(xmlNodePtr);

/* Obtient une valeur placée entre <...> et </...>. */
char *get_node_text_value(xmlXPathContextPtr, const char *);

/* Obtient une valeur booléenne placée entre <...> et </...>. */
bool get_node_boolean_value(xmlXPathContextPtr, const char *, bool *);

/* Obtient une valeur entière placée entre <...> et </...>. */
bool get_node_long_value(xmlXPathContextPtr, const char *, long *);

/* Obtient la valeur d'une propriété d'un élément. */
char *qck_get_node_prop_value(xmlNodePtr, const char *);

/* Obtient la valeur entière d'une propriété d'un élément. */
bool qck_get_node_prop_long_value(xmlNodePtr, const char *, long *);

/* Obtient la valeur entière d'une propriété d'un élément. */
bool qck_get_node_prop_uint64_value(xmlNodePtr, const char *, uint64_t *);

/* Obtient la valeur d'une propriété d'un élément. */
char *get_node_prop_value(xmlXPathContextPtr, const char *, const char *);

/* Obtient la valeur entière d'une propriété d'un élément. */
bool get_node_prop_long_value(xmlXPathContextPtr, const char *, const char *, long *);

/* Obtient la valeur entière d'une propriété d'un élément. */
bool get_node_prop_uint64_value(xmlXPathContextPtr, const char *, const char *, uint64_t *);

/* Construit un chemin d'accès complet selon le fichier XML. */
char *qck_build_filename_with_doc_url(xmlNodePtr);

/* Construit un chemin d'accès complet selon le fichier XML. */
char *build_filename_with_doc_url(xmlXPathContextPtr xpathCtx, const char *path);



/* --------------------- OPERATIONS D'ECRITURE D'UN FICHIER XML --------------------- */


/* Amorce l'écriture d'un nouveau fichier XML. */
xmlTextWriterPtr start_writing_xml_file(const char *);

/* Met fin à l'écriture d'un nouveau fichier XML. */
bool end_writing_xml_file(xmlTextWriterPtr);

/* Ecrit une balise et ne la referme pas. */
bool open_xml_element(xmlTextWriterPtr, const char *);

/* Ferme la dernière balise laissée ouverte. */
bool close_xml_element(xmlTextWriterPtr);

/* Ecrit une balise avec un contenu textuel. */
bool write_xml_element_with_content(xmlTextWriterPtr, const char *, const char *, ...);

/* Ecrit un attribut avec un contenu textuel. */
bool write_xml_attribute(xmlTextWriterPtr, const char *, const char *, ...);

/* Ecrit un contenu textuel. */
bool write_xml_content(xmlTextWriterPtr, const char *, ...);



/* --------------------- OPERATIONS D'ECRITURE D'UN FICHIER XML --------------------- */


/* Fournit le premier noeud correspondant à un chemin XPath. */
xmlNodePtr get_node_from_xpath(xmlXPathContextPtr, const char *);

/* Ajoute un noeud à un autre noeud. */
xmlNodePtr add_node_to_xpath(xmlDocPtr, xmlXPathContextPtr, const char *, const char *);

/* Ajoute un noeud à un autre noeud. */
xmlNodePtr add_node_to_node(xmlDocPtr, xmlNodePtr, const char *);

/* Retire un noeud d'un document XML. */
void _remove_node_from_doc(xmlDocPtr, xmlNodePtr);

/* Retire un noeud d'un document XML. */
bool remove_node_from_doc(xmlDocPtr, xmlXPathContextPtr, const char *);

/* S'assure qu'un noeud donné est bien présent dans le document. */
xmlNodePtr ensure_node_exist(xmlDocPtr, xmlXPathContextPtr, const char *);

/* S'assure qu'un noeud donné est bien présent dans le document. */
bool add_content_to_node(xmlDocPtr, xmlXPathContextPtr, const char *, const char *);

/* Ajoute un noeud avec contenu numérique au document. */
bool add_uint_content_to_node(xmlDocPtr, xmlXPathContextPtr, const char *, unsigned int);

/* Ajoute une propriété à un noeud existant donné. */
bool _add_string_attribute_to_node(xmlNodePtr, const char *, const char *);

/* Ajoute une propriété à un noeud existant donné. */
bool add_string_attribute_to_node(xmlDocPtr, xmlXPathContextPtr, const char *, const char *, const char *);

/* Ajoute une propriété à un noeud existant donné. */
bool _add_long_attribute_to_node(xmlNodePtr, const char *, long);

/* Ajoute une propriété à un noeud existant donné. */
bool add_long_attribute_to_node(xmlDocPtr, xmlXPathContextPtr, const char *, const char *, long);

/* Ajoute une propriété à un noeud existant donné. */
bool _add_uint64_attribute_to_node(xmlNodePtr, const char *, uint64_t);

/* Ajoute une propriété à un noeud existant donné. */
bool add_uint64_attribute_to_node(xmlDocPtr, xmlXPathContextPtr, const char *, const char *, uint64_t);



#endif  /* _XML_H */
