
/* Firebox Tools - Outils de configurations pour le WM Firebox
 * xml.c - lecture ou écriture de documents XML
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


#include "xml.h"


#include <inttypes.h>
#include <malloc.h>
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>


#include "cpp.h"
#include "extstr.h"
#include "pathname.h"


#ifdef DEBUG
#   define XML_LOG fprintf
#else
#   define XML_LOG if (FALSE) fprintf
#endif



/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc    = structure XML chargée. [OUT]                       *
*                context = contexte à utiliser pour les recherches. [OUT]     *
*                                                                             *
*  Description : Crée un nouveau fichier XML.                                 *
*                                                                             *
*  Retour      : true si l'opération a pu s'effectuer, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool create_new_xml_file(xmlDocPtr *xdoc, xmlXPathContextPtr *context)
{
    *xdoc = xmlNewDoc(BAD_CAST "1.0");

    if (*xdoc == NULL)
        return false;

    *context = xmlXPathNewContext(*xdoc);

    if (*context == NULL)
    {
        xmlFreeDoc(*xdoc);
        return false;
    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : content = données XML présentes en mémoire et à charge.      *
*                length  = quantité de ces données.                           *
*                xdoc    = structure XML chargée. [OUT]                       *
*                context = contexte à utiliser pour les recherches. [OUT]     *
*                                                                             *
*  Description : Charge un document XML entièrement en mémoire.               *
*                                                                             *
*  Retour      : true si l'opération a pu s'effectuer, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool load_xml_from_memory(const char *content, size_t length, xmlDocPtr *xdoc, xmlXPathContextPtr *context)
{
    *xdoc = xmlReadMemory(content, length, "noname.xml", NULL, 0);

    if (*xdoc == NULL)
        return false;

    *context = xmlXPathNewContext(*xdoc);

    if (*context == NULL)
    {
        xmlFreeDoc(*xdoc);
        return false;
    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc     = structure XML chargée.                            *
*                filename = nom du fichier à remplir.                         *
*                                                                             *
*  Description : Sauvegarde une structure XML dans un fichier.                *
*                                                                             *
*  Retour      : true si l'opération a pu s'effectuer, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool save_xml_file(xmlDocPtr xdoc, const char *filename)
{
    bool result;                            /* Bilan à retourner           */
    int ret;                                /* Bilan de l'appel            */

    /**
     * Le parti est pris de ne pas enregistrer de document vide !
     */

    if (xmlDocGetRootElement(xdoc) == NULL)
    {
        ret = unlink(filename);
        result = (ret == 0);
    }

    else
    {
        result = mkpath(filename);
        if (!result) goto exit;

        ret = xmlSaveFormatFileEnc(filename, xdoc, "UTF-8", 1);
        result = (ret != -1);

    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc     = structure XML chargée à supprimer.                *
*                context  = contexte utilisé pour les recherches.             *
*                                                                             *
*  Description : Ferme une structure XML.                                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void close_xml_file(xmlDocPtr xdoc, xmlXPathContextPtr context)
{
    xmlXPathFreeContext(context);
    xmlFreeDoc(xdoc);

    xmlCleanupParser();

}



/* ---------------------------------------------------------------------------------- */
/*                       OPERATIONS DE LECTURE D'UN FICHIER XML                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = nom du fichier à ouvrir.                          *
*                xdoc     = structure XML chargée. [OUT]                      *
*                xpathCtx = contexte à utiliser pour les recherches. [OUT]    *
*                                                                             *
*  Description : Ouvre un fichier XML de façon encadrée.                      *
*                                                                             *
*  Retour      : true si l'opération a pu s'effectuer, false sinon.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

gboolean open_xml_file(const char *filename, xmlDoc **xdoc, xmlXPathContextPtr *xpathCtx)
{
    /**
     * On s'autorise à récupérer des erreurs de fichier vide, ie ne contenant que :
     *
     *    <?xml version="1.0" encoding="UTF-8"?>
     *
     * On espère que la récupération d'autres situations d'erreurs est bien gérée.
     */

    *xdoc = xmlReadFile(filename, NULL, XML_PARSE_RECOVER);

    if (*xdoc == NULL)
    {
        XML_LOG(stderr, "Can not parse the XML file '%s'\n", filename);
        return FALSE;
    }

    *xpathCtx = xmlXPathNewContext(*xdoc);

    if (*xpathCtx == NULL)
    {
        XML_LOG(stderr, "Unable to create new XPath context\n");
        xmlFreeDoc(*xdoc);
        return FALSE;
    }

    return TRUE;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xpathCtx = contexte à utiliser pour les recherches.          *
*                path     = chemin d'accès au noeud visé.                     *
*                                                                             *
*  Description : Obtient de façon encadrée l'accès à un noeud défini.         *
*                                                                             *
*  Retour      : Adresse de l'accès trouvé.                                   *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

xmlXPathObjectPtr get_node_xpath_object(xmlXPathContextPtr xpathCtx, const char *path)
{
    xmlXPathObjectPtr result;               /* Noeud XML à renvoyer        */

    result = xmlXPathEvalExpression(BAD_CAST path, xpathCtx);

    if (result == NULL)
    {
        XML_LOG(stderr, "Unable to evaluate xpath expression '%s'\n", path);
        return NULL;
    }

    if (result->nodesetval == NULL)
    {
        XML_LOG(stderr, "Node '%s' not found\n", path);
        xmlXPathFreeObject(result);
        return NULL;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = noeud dont une propriété est à lire.                  *
*                                                                             *
*  Description : Obtient le nom de balise d'un noeud donné.                   *
*                                                                             *
*  Retour      : Valeur sous forme de chaîne de caractères ou NULL.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *qck_get_node_name(xmlNodePtr node)
{
    char *result;                           /* Valeur en question renvoyée */

    result = NULL;

    if (node != NULL)
        result = strdup((const char *)node->name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xpathCtx = contexte à utiliser pour les recherches.          *
*                path     = chemin d'accès au noeud visé.                     *
*                                                                             *
*  Description : Obtient le nom de balise d'un noeud donné.                   *
*                                                                             *
*  Retour      : Valeur sous forme de chaîne de caractères ou NULL.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_node_name(xmlXPathContextPtr xpathCtx, const char *path)
{
    char *result;                           /* Valeur en question renvoyée */
    xmlXPathObjectPtr xpathObj;             /* Point de départ XML         */

    result = NULL;

    xpathObj = get_node_xpath_object(xpathCtx, path);
    if (xpathObj == NULL) return NULL;

    if (xpathObj->nodesetval->nodeNr > 0)
        result = qck_get_node_name(xpathObj->nodesetval->nodeTab[0]);

    xmlXPathFreeObject(xpathObj);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = noeud dont une propriété est à lire.                  *
*                                                                             *
*  Description : Obtient une valeur placée entre <...> et </...>.             *
*                                                                             *
*  Retour      : Valeur sous forme de chaîne de caractères ou NULL.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *qck_get_node_text_value(xmlNodePtr node)
{
    char *result;                           /* Valeur en question renvoyée */

    result = NULL;

    if (node != NULL)
    {
        if (node->children != NULL)
            if (node->children->content != NULL)
                result = strdup((char *)node->children->content);

        /**
         * Si le noeud existe mais qu'il n'y pas de contenu,
         * il faut marquer la différence entre deux retours NULL.
         * 
         * On choisit donc :
         *   - NULL : pas de valeur trouvée car noeud non existant.
         *   - "" : pas de valeur trouvée, mais noeud bien présent.
         */

        if (result == NULL)
            result = strdup("");

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xpathCtx = contexte à utiliser pour les recherches.          *
*                path     = chemin d'accès au noeud visé.                     *
*                                                                             *
*  Description : Obtient une valeur placée entre <...> et </...>.             *
*                                                                             *
*  Retour      : Valeur sous forme de chaîne de caractères ou NULL.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_node_text_value(xmlXPathContextPtr xpathCtx, const char *path)
{
    char *result;                           /* Valeur en question renvoyée */
    xmlXPathObjectPtr xpathObj;             /* Point de départ XML         */

    result = NULL;

    xpathObj = get_node_xpath_object(xpathCtx, path);
    if (xpathObj == NULL) return NULL;

    if (xpathObj->nodesetval->nodeNr > 0)
        result = qck_get_node_text_value(xpathObj->nodesetval->nodeTab[0]);

    xmlXPathFreeObject(xpathObj);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xpathCtx = contexte à utiliser pour les recherches.          *
*                path     = chemin d'accès au noeud visé.                     *
*                out      = valeur booléenne associée à un noeud. [OUT]       *
*                                                                             *
*  Description : Obtient une valeur booléenne placée entre <...> et </...>.   *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_node_boolean_value(xmlXPathContextPtr xpathCtx, const char *path, bool *out)
{
    bool result;                            /* Bilan à retourner           */
    char *value;                            /* Valeur brute lue            */

    result = false;

    value = get_node_text_value(xpathCtx, path);

    if (value != NULL)
    {
        if (strlen(value) > 0)
        {
            result = true;
            *out = (strcasecmp(value, "true") == 0 || strcmp(value, "1") == 0);
        }

        free(value);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xpathCtx = contexte à utiliser pour les recherches.          *
*                path     = chemin d'accès au noeud visé.                     *
*                out      = valeur entière associée à un noeud. [OUT]         *
*                                                                             *
*  Description : Obtient une valeur entière placée entre <...> et </...>.     *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_node_long_value(xmlXPathContextPtr xpathCtx, const char *path, long *out)
{
    bool result;                            /* Bilan à retourner           */
    char *value;                            /* Valeur brute lue            */

    result = false;

    value = get_node_text_value(xpathCtx, path);

    if (value != NULL)
    {
        if (strlen(value) > 0)
        {
            result = true;
            *out = strtol(value, NULL, 10);
        }

        free(value);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = noeud dont une propriété est à lire.                  *
*                name = nom de la propriété à lire.                           *
*                                                                             *
*  Description : Obtient la valeur d'une propriété d'un élément.              *
*                                                                             *
*  Retour      : Valeur sous forme de chaîne de caractères ou NULL.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *qck_get_node_prop_value(xmlNodePtr node, const char *name)
{
    char *result;                           /* Valeur en question renvoyée */
    xmlAttrPtr attrib;                      /* Liste d'attributs présents  */

    result = NULL;

    if (node == NULL) return NULL;

    /* Lecture de la valeur */

    for (attrib = node->properties; attrib != NULL && result == NULL; attrib = attrib->next)
        if (xmlStrEqual(attrib->name, BAD_CAST name)) result = strdup((char *)attrib->children->content);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = noeud dont une propriété est à lire.                  *
*                name = nom de la propriété à lire.                           *
*                out  = valeur entière lue depuis le contenu textuel. [OUT]   *
*                                                                             *
*  Description : Obtient la valeur entière d'une propriété d'un élément.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool qck_get_node_prop_long_value(xmlNodePtr node, const char *name, long *out)
{
    bool result;                            /* Bilan à retourner           */
    char *value;                            /* Valeur brute lue            */

    value = qck_get_node_prop_value(node, name);

    if (value)
    {
        result = true;

        *out = strtol(value, NULL, 10);
        free(value);

    }
    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = noeud dont une propriété est à lire.                  *
*                name = nom de la propriété à lire.                           *
*                out  = valeur entière lue depuis le contenu textuel. [OUT]   *
*                                                                             *
*  Description : Obtient la valeur entière d'une propriété d'un élément.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool qck_get_node_prop_uint64_value(xmlNodePtr node, const char *name, uint64_t *out)
{
    bool result;                            /* Bilan à retourner           */
    char *value;                            /* Valeur brute lue            */

    value = qck_get_node_prop_value(node, name);

    if (value)
    {
        result = true;

        *out = strtoull(value, NULL, 10);
        free(value);

    }
    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xpathCtx = contexte à utiliser pour les recherches.          *
*                path     = chemin d'accès au noeud à traiter.                *
*                name     = nom de la propriété à lire.                       *
*                                                                             *
*  Description : Obtient la valeur d'une propriété d'un élément.              *
*                                                                             *
*  Retour      : Valeur sous forme de chaîne de caractères ou NULL.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *get_node_prop_value(xmlXPathContextPtr xpathCtx, const char *path, const char *name)
{
    char *result;                           /* Valeur en question renvoyée */
    xmlXPathObjectPtr xpathObj;             /* Point de départ XML         */

    result = NULL;

    xpathObj = get_node_xpath_object(xpathCtx, path);
    if (xpathObj == NULL) return NULL;

    if (xpathObj->nodesetval->nodeNr > 0)
        result = qck_get_node_prop_value(xpathObj->nodesetval->nodeTab[0], name);

    xmlXPathFreeObject(xpathObj);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xpathCtx = contexte à utiliser pour les recherches.          *
*                path     = chemin d'accès au noeud à traiter.                *
*                name     = nom de la propriété à lire.                       *
*                out      = valeur entière obtenue via contenu textuel. [OUT] *
*                                                                             *
*  Description : Obtient la valeur entière d'une propriété d'un élément.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_node_prop_long_value(xmlXPathContextPtr xpathCtx, const char *path, const char *name, long *out)
{
    bool result;                            /* Bilan à retourner           */
    xmlXPathObjectPtr xpathObj;             /* Point de départ XML         */

    result = NULL;

    xpathObj = get_node_xpath_object(xpathCtx, path);
    if (xpathObj == NULL) return NULL;

    if (xpathObj->nodesetval->nodeNr > 0)
        result = qck_get_node_prop_long_value(xpathObj->nodesetval->nodeTab[0], name, out);

    xmlXPathFreeObject(xpathObj);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xpathCtx = contexte à utiliser pour les recherches.          *
*                path     = chemin d'accès au noeud à traiter.                *
*                name     = nom de la propriété à lire.                       *
*                out      = valeur entière obtenue via contenu textuel. [OUT] *
*                                                                             *
*  Description : Obtient la valeur entière d'une propriété d'un élément.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool get_node_prop_uint64_value(xmlXPathContextPtr xpathCtx, const char *path, const char *name, uint64_t *out)
{
    bool result;                            /* Bilan à retourner           */
    xmlXPathObjectPtr xpathObj;             /* Point de départ XML         */

    result = NULL;

    xpathObj = get_node_xpath_object(xpathCtx, path);
    if (xpathObj == NULL) return NULL;

    if (xpathObj->nodesetval->nodeNr > 0)
        result = qck_get_node_prop_uint64_value(xpathObj->nodesetval->nodeTab[0], name, out);

    xmlXPathFreeObject(xpathObj);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node = noeud de texte avec un lien avec le document XML.     *
*                                                                             *
*  Description : Construit un chemin d'accès complet selon le fichier XML.    *
*                                                                             *
*  Retour      : Valeur à libérer de la mémoire après usage ou NULL.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *qck_build_filename_with_doc_url(xmlNodePtr node)
{
    char *result;                           /* Construction à retourner    */
    char *text;                             /* Valeur du texte lu          */
    char *last;                             /* Point de remplacement       */

    result = NULL;

    text = qck_get_node_text_value(node);

    if (text != NULL)
    {
        result = (char *)calloc(xmlStrlen(node->doc->URL) + strlen(text) + 1, sizeof(char));

        strcpy(result, (const char *)node->doc->URL);

        last = strrchr(result, '/');
        last++;

        strcpy(last, text);
        free(text);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xpathCtx = contexte à utiliser pour les recherches.          *
*                path     = chemin d'accès au noeud à traiter.                *
*                                                                             *
*  Description : Construit un chemin d'accès complet selon le fichier XML.    *
*                                                                             *
*  Retour      : Valeur sous forme de chaîne de caractères ou NULL.           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

char *build_filename_with_doc_url(xmlXPathContextPtr xpathCtx, const char *path)
{
    char *result;                           /* Valeur en question renvoyée */
    xmlXPathObjectPtr xpathObj;             /* Point de départ XML         */

    result = NULL;

    xpathObj = get_node_xpath_object(xpathCtx, path);
    if (xpathObj == NULL) return NULL;

    if (xpathObj->nodesetval->nodeNr > 0)
        result = qck_build_filename_with_doc_url(xpathObj->nodesetval->nodeTab[0]);

    xmlXPathFreeObject(xpathObj);

    return result;

}



/* ---------------------------------------------------------------------------------- */
/*                       OPERATIONS D'ECRITURE D'UN FICHIER XML                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : filename = nom du fichier à ouvrir.                          *
*                                                                             *
*  Description : Amorce l'écriture d'un nouveau fichier XML.                  *
*                                                                             *
*  Retour      : Rédacteur mis en place ou NULL en cas d'erreur.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

xmlTextWriterPtr start_writing_xml_file(const char *filename)
{
    xmlTextWriterPtr result;                /* Moyen à retourner           */
    int retval;                             /* Bilan d'une opération       */

    result = xmlNewTextWriterFilename(filename, 0);

    if (result == NULL)
    {
        XML_LOG(stderr, "Error creating the xml writer\n");
        return NULL;
    }

    retval = xmlTextWriterStartDocument(result, NULL, "UTF-8", "yes");
    if (retval < 0)
    {
        XML_LOG(stderr, "Error at xmlTextWriterStartDocument\n");
        xmlFreeTextWriter(result);
        return NULL;
    }

    retval = xmlTextWriterSetIndent(result, 1);
    if (retval < 0)
    {
        XML_LOG(stderr, "Error setting indentation\n");
        xmlFreeTextWriter(result);
        return NULL;
    }

    retval = xmlTextWriterSetIndentString(result, BAD_CAST "\t");
    if (retval < 0)
    {
        XML_LOG(stderr, "Error setting indentation string\n");
        xmlFreeTextWriter(result);
        return NULL;
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : writer = rédacteur dédié à l'écriture.                       *
*                                                                             *
*  Description : Met fin à l'écriture d'un nouveau fichier XML.               *
*                                                                             *
*  Retour      : Bilan de l'opération : true ou false.                        *
*                                                                             *
*  Remarques   : Ferme au besoin toutes les balises encore ouvertes.          *
*                                                                             *
******************************************************************************/

bool end_writing_xml_file(xmlTextWriterPtr writer)
{
    int retval;                             /* Bilan de l'opération        */

    retval = xmlTextWriterEndDocument(writer);
    if (retval < 0)
    {
        XML_LOG(stderr, "Error at xmlTextWriterEndDocument\n");
        return false;
    }

    xmlFreeTextWriter(writer);

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : writer = rédacteur dédié à l'écriture.                       *
*                name   = nom de la balise à écrire.                          *
*                                                                             *
*  Description : Ecrit une balise et ne la referme pas.                       *
*                                                                             *
*  Retour      : Bilan de l'opération : true ou false.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool open_xml_element(xmlTextWriterPtr writer, const char *name)
{
    int retval;                             /* Bilan de l'opération        */

    retval = xmlTextWriterStartElement(writer, BAD_CAST name);

    if (retval < 0)
        XML_LOG(stderr, "Error at xmlTextWriterWriteFormatElement\n");

    return (retval >= 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : writer = rédacteur dédié à l'écriture.                       *
*                                                                             *
*  Description : Ferme la dernière balise laissée ouverte.                    *
*                                                                             *
*  Retour      : Bilan de l'opération : true ou false.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool close_xml_element(xmlTextWriterPtr writer)
{
    int retval;                             /* Bilan de l'opération        */

    retval = xmlTextWriterEndElement(writer);

    if (retval < 0)
        XML_LOG(stderr, "Error at xmlTextWriterWriteFormatElement\n");

    return (retval >= 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : writer = rédacteur dédié à l'écriture.                       *
*                name   = nom de la balise à écrire.                          *
*                format = format de la chaîne à traiter.                      *
*                ...    = informations à inscrire.                            *
*                                                                             *
*  Description : Ecrit une balise avec un contenu textuel.                    *
*                                                                             *
*  Retour      : Bilan de l'opération : true ou false.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_xml_element_with_content(xmlTextWriterPtr writer, const char *name, const char *format, ...)
{
    va_list ap;                             /* Liste d'arguments variable  */
    int retval;                             /* Bilan de l'opération        */

    va_start(ap, format);

    retval = xmlTextWriterWriteVFormatElement(writer, BAD_CAST name, format, ap);

    if (retval < 0)
        XML_LOG(stderr, "Error at xmlTextWriterWriteFormatElement\n");

    va_end(ap);

    return (retval >= 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : writer = rédacteur dédié à l'écriture.                       *
*                name   = nom de l'attribut à écrire.                         *
*                format = format de la chaîne à traiter.                      *
*                ...    = informations à inscrire.                            *
*                                                                             *
*  Description : Ecrit un attribut avec un contenu textuel.                   *
*                                                                             *
*  Retour      : Bilan de l'opération : true ou false.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_xml_attribute(xmlTextWriterPtr writer, const char *name, const char *format, ...)
{
    va_list ap;                             /* Liste d'arguments variable  */
    int retval;                             /* Bilan de l'opération        */

    va_start(ap, format);

    retval = xmlTextWriterWriteVFormatAttribute(writer, BAD_CAST name, format, ap);

    if (retval < 0)
        XML_LOG(stderr, "Error at xmlTextWriterWriteFormatElement\n");

    va_end(ap);

    return (retval >= 0);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : writer = rédacteur dédié à l'écriture.                       *
*                format = format de la chaîne à traiter.                      *
*                ...    = informations à inscrire.                            *
*                                                                             *
*  Description : Ecrit un contenu textuel.                                    *
*                                                                             *
*  Retour      : Bilan de l'opération : true ou false.                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool write_xml_content(xmlTextWriterPtr writer, const char *format, ...)
{
    va_list ap;                             /* Liste d'arguments variable  */
    int retval;                             /* Bilan de l'opération        */

    va_start(ap, format);

    retval = xmlTextWriterWriteVFormatString(writer, format, ap);

    if (retval < 0)
        XML_LOG(stderr, "Error at xmlTextWriterWriteFormatElement\n");

    va_end(ap);

    return (retval >= 0);

}



/* ---------------------------------------------------------------------------------- */
/*                       OPERATIONS D'ECRITURE D'UN FICHIER XML                       */
/* ---------------------------------------------------------------------------------- */



/******************************************************************************
*                                                                             *
*  Paramètres  : context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès au noeud visé.                      *
*                                                                             *
*  Description : Fournit le premier noeud correspondant à un chemin XPath.    *
*                                                                             *
*  Retour      : Adresse du noeud trouvé ou NULL en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

xmlNodePtr get_node_from_xpath(xmlXPathContextPtr context, const char *path)
{
    xmlNodePtr result;                      /* Noeud trouvé à renvoyer     */
    xmlXPathObjectPtr xobject;              /* Point de départ XML         */

    result = NULL;

    xobject = get_node_xpath_object(context, path);
    if (xobject == NULL) return NULL;

    if (xobject->nodesetval->nodeNr > 0)
        result = xobject->nodesetval->nodeTab[0];

    xmlXPathFreeObject(xobject);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc    = structure XML chargée.                             *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès au noeud visé.                      *
*                name    = nom du nouveau noeud à créer.                      *
*                                                                             *
*  Description : Ajoute un noeud à un autre noeud.                            *
*                                                                             *
*  Retour      : Adresse du noeud mis en place ou NULL en cas d'échec.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

xmlNodePtr add_node_to_xpath(xmlDocPtr xdoc, xmlXPathContextPtr context, const char *path, const char *name)
{
    xmlNodePtr result;                      /* Noeud créé à retourner      */
    xmlNodePtr parent;                      /* Support du nouveau noeud    */

    parent = get_node_from_xpath(context, path);
    if (parent == NULL) return NULL;

    result = add_node_to_node(xdoc, parent, name);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc   = structure XML chargée.                              *
*                parent = noeud parent de rattachement.                       *
*                name   = nom du nouveau noeud à créer.                       *
*                                                                             *
*  Description : Ajoute un noeud à un autre noeud.                            *
*                                                                             *
*  Retour      : Adresse du noeud mis en place ou NULL en cas d'échec.        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

xmlNodePtr add_node_to_node(xmlDocPtr xdoc, xmlNodePtr parent, const char *name)
{
    xmlNodePtr result;                      /* Noeud créé à retourner      */

    result = xmlNewDocNode(xdoc, NULL, BAD_CAST name, NULL);
    result = xmlAddChild(parent, result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc = structure XML chargée.                                *
*                node = noeud à retirer de la structure.                      *
*                                                                             *
*  Description : Retire un noeud d'un document XML.                           *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void _remove_node_from_doc(xmlDocPtr xdoc, xmlNodePtr node)
{
    xmlUnlinkNode(node);
    xmlFreeNode(node);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc    = structure XML chargée.                             *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès au noeud visé.                      *
*                                                                             *
*  Description : Retire un noeud d'un document XML.                           *
*                                                                             *
*  Retour      : true si le noeud XML a bien été trouvé, false sinon.         *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool remove_node_from_doc(xmlDocPtr xdoc, xmlXPathContextPtr context, const char *path)
{
    bool result;                            /* Bilan à retourner           */
    xmlNodePtr node;                        /* Noeud à considérer          */

    node = get_node_from_xpath(context, path);

    if (node != NULL)
    {
        _remove_node_from_doc(xdoc, node);
        result = true;
    }
    else
        result = false;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc    = structure XML chargée.                             *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès au noeud visé.                      *
*                                                                             *
*  Description : S'assure qu'un noeud donné est bien présent dans le document.*
*                                                                             *
*  Retour      : Noeud en question ou NULL en cas d'échec à la création.      *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

xmlNodePtr ensure_node_exist(xmlDocPtr xdoc, xmlXPathContextPtr context, const char *path)
{
    xmlNodePtr result;                      /* Noeud à retourner           */
    char **levels;                          /* Niveaux dans le chemin      */
    size_t levels_count;                    /* Nombre de ces niveaux       */
    xmlNodePtr last;                        /* Dernier noeud valide        */
    size_t i;                               /* Boucle de parcours #1       */
    char *iter_path;                        /* Chamin d'accès pour le test */
    size_t j;                               /* Boucle de parcours #2       */
    xmlNodePtr iter;                        /* Test d'accès à un noeud     */
    char *cond;                             /* Marque de condition ('[')   */

    result = get_node_from_xpath(context, path);

    if (result == NULL)
    {
        levels = strtoka(path, "/", &levels_count);

        /* Recherche la racine valide la plus haute */

        last = xmlDocGetRootElement(xdoc);

        for (i = 0; i < levels_count && last != NULL; i++)
        {
            iter_path = strdup("");

            for (j = 0; j <= i; j++)
            {
                iter_path = stradd(iter_path, "/");
                iter_path = stradd(iter_path, levels[j]);
            }

            iter = get_node_from_xpath(context, iter_path);

            free(iter_path);

            if (iter == NULL) break;
            else last = iter;

        }

        /* Inscription des noeuds restants */

        if (last == NULL)
        {
            last = xmlNewDocNode(xdoc, NULL, BAD_CAST levels[i++], NULL);
            xmlDocSetRootElement(xdoc, last);

            if (i == levels_count)
                result = last;

        }

        for ( ; i < levels_count && last != NULL; i++)
        {
            cond = strchr(levels[i], '[');
            if (cond != NULL) *cond = '\0';

            result = xmlNewDocNode(xdoc, NULL, BAD_CAST levels[i], NULL);
            result = xmlAddChild(last, result);
            last = result;
        }

        /* Libération de la mémoire */

        for (i = 0; i < levels_count; i++)
            free(levels[i]);

        free(levels);

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc    = structure XML chargée.                             *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès au noeud visé.                      *
*                content = texte à inscrire en contenu.                       *
*                                                                             *
*  Description : S'assure qu'un noeud donné est bien présent dans le document.*
*                                                                             *
*  Retour      : true en cas de succès, false sinon.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_content_to_node(xmlDocPtr xdoc, xmlXPathContextPtr context, const char *path, const char *content)
{
    xmlNodePtr node;                        /* Noeud à modifier            */

    if (content == NULL) return true;

    node = ensure_node_exist(xdoc, context, path);
    if (node == NULL) return false;

    xmlNodeSetContent(node, BAD_CAST content);

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc    = structure XML chargée.                             *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès au noeud visé.                      *
*                value   = nombre à inscrire en contenu.                      *
*                                                                             *
*  Description : Ajoute un noeud avec contenu numérique au document.          *
*                                                                             *
*  Retour      : true en cas de succès, false sinon.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_uint_content_to_node(xmlDocPtr xdoc, xmlXPathContextPtr context, const char *path, unsigned int value)
{
    xmlNodePtr node;                        /* Noeud à modifier            */
    char content[sizeof(XSTR(UINT_MAX)) + 1];/* Valeur en chaîne            */

    if (content == NULL) return true;

    node = ensure_node_exist(xdoc, context, path);
    if (node == NULL) return false;

    sprintf(content, "%u", value);
    xmlNodeSetContent(node, BAD_CAST content);

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node  = noeud dont le contenu est à mettre à jour.           *
*                name  = nom de la propriété à créer.                         *
*                value = chaîne de caractère à placer.                        *
*                                                                             *
*  Description : Ajoute une propriété à un noeud existant donné.              *
*                                                                             *
*  Retour      : true en cas de succès, false sinon.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _add_string_attribute_to_node(xmlNodePtr node, const char *name, const char *value)
{
    xmlAttrPtr attrib;                      /* Attribut créé et en place   */

    attrib = xmlSetProp(node, BAD_CAST name, BAD_CAST value);

    return (attrib != NULL);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc    = structure XML chargée.                             *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès au noeud visé.                      *
*                name    = nom de la propriété à créer.                       *
*                value   = chaîne de caractère à placer.                      *
*                                                                             *
*  Description : Ajoute une propriété à un noeud existant donné.              *
*                                                                             *
*  Retour      : true en cas de succès, false sinon.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_string_attribute_to_node(xmlDocPtr xdoc, xmlXPathContextPtr context, const char *path, const char *name, const char *value)
{
    xmlNodePtr node;                        /* Noeud à modifier            */

    if (value == NULL) return true;

    node = ensure_node_exist(xdoc, context, path);
    if (node == NULL) return false;

    return _add_string_attribute_to_node(node, name, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node  = noeud dont le contenu est à mettre à jour.           *
*                name  = nom de la propriété à créer.                         *
*                value = valeur numérique à placer.                           *
*                                                                             *
*  Description : Ajoute une propriété à un noeud existant donné.              *
*                                                                             *
*  Retour      : true en cas de succès, false sinon.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _add_long_attribute_to_node(xmlNodePtr node, const char *name, long value)
{
    char tmp[11/*strlen("2147483647")*/];   /* Stockage temporaire         */

    snprintf(tmp, 11, "%ld", value);

    return _add_string_attribute_to_node(node, name, tmp);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc    = structure XML chargée.                             *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès au noeud visé.                      *
*                name    = nom de la propriété à créer.                       *
*                value   = valeur numérique à placer.                         *
*                                                                             *
*  Description : Ajoute une propriété à un noeud existant donné.              *
*                                                                             *
*  Retour      : true en cas de succès, false sinon.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_long_attribute_to_node(xmlDocPtr xdoc, xmlXPathContextPtr context, const char *path, const char *name, long value)
{
    xmlNodePtr node;                        /* Noeud à modifier            */

    node = ensure_node_exist(xdoc, context, path);
    if (node == NULL) return false;

    return _add_long_attribute_to_node(node, name, value);

}


/******************************************************************************
*                                                                             *
*  Paramètres  : node  = noeud dont le contenu est à mettre à jour.           *
*                name  = nom de la propriété à créer.                         *
*                value = valeur numérique à placer.                           *
*                                                                             *
*  Description : Ajoute une propriété à un noeud existant donné.              *
*                                                                             *
*  Retour      : true en cas de succès, false sinon.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool _add_uint64_attribute_to_node(xmlNodePtr node, const char *name, uint64_t value)
{
    bool result;                            /* Bilan à retourner           */
    char *tmp;                              /* Stockage temporaire         */
    int ret;                                /* Bilan de l'impression       */

    ret = asprintf(&tmp, "%" PRIu64, value);

    if (ret == -1)
        result = false;

    else
    {
        result = _add_string_attribute_to_node(node, name, tmp);
        free(tmp);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : xdoc    = structure XML chargée.                             *
*                context = contexte à utiliser pour les recherches.           *
*                path    = chemin d'accès au noeud visé.                      *
*                name    = nom de la propriété à créer.                       *
*                value   = valeur numérique à placer.                         *
*                                                                             *
*  Description : Ajoute une propriété à un noeud existant donné.              *
*                                                                             *
*  Retour      : true en cas de succès, false sinon.                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool add_uint64_attribute_to_node(xmlDocPtr xdoc, xmlXPathContextPtr context, const char *path, const char *name, uint64_t value)
{
    xmlNodePtr node;                        /* Noeud à modifier            */

    node = ensure_node_exist(xdoc, context, path);
    if (node == NULL) return false;

    return _add_uint64_attribute_to_node(node, name, value);

}
