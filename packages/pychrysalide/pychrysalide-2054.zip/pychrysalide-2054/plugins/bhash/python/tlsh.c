
/* Chrysalide - Outil d'analyse de fichiers binaires
 * tlsh.c - équivalent Python du fichier "plugins/bhash/tlsh.c"
 *
 * Copyright (C) 2021 Cyrille Bagard
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
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */


#include "tlsh.h"


#include <pygobject.h>


#include <plugins/pychrysalide/access.h>
#include <plugins/pychrysalide/helpers.h>
#include <plugins/pychrysalide/analysis/content.h>


#include "../tlsh.h"



/* Calcule l'empreinte TLSH d'un contenu binaire. */
static PyObject *py_bhash_compute_content_tlsh_hash(PyObject *, PyObject *);

/* Indique si une chaîne représente à priori une empreinte TLSH. */
static PyObject *py_bhash_is_valid_tlsh_hash(PyObject *, PyObject *);

/* Détermine la similarité entre deux empreintes TLSH. */
static PyObject *py_bhash_compare_tlsh_hash(PyObject *, PyObject *);



/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = paramètre à récupérer pour le traitement.             *
*                                                                             *
*  Description : Calcule l'empreinte TLSH d'un contenu binaire.               *
*                                                                             *
*  Retour      : Empreinte TLSH calculée ou None en cas d'échec.              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bhash_compute_content_tlsh_hash(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    int version;                            /* Affichage de la version ?   */
    GBinContent *content;                   /* Contenu binaire à traiter   */
    int ret;                                /* Bilan de lecture des args.  */
    char *digest;                           /* Empreinte calculée          */

#define BHASH_COMPUTE_CONTENT_TLSH_HASH_METHOD PYTHON_METHOD_DEF        \
(                                                                       \
    compute_content_tlsh_hash, "content, /, version=True",              \
    METH_VARARGS, py_bhash,                                             \
    "Compute the TLSH compact hash for a given binary content with a"   \
    " 1-byte checksum.\n"                                               \
    "\n"                                                                \
    "The *content* argument is a pychrysalide.analysis.BinContent"      \
    " instance providing the data to process. The optional *version*"   \
    " parameter add a 'T?' prefix to the result.\n"                     \
    "\n"                                                                \
    "The returned value is a MD5 digest string or *None* in case of"    \
    " error."                                                           \
)

    result = NULL;

    version = 1;

    ret = PyArg_ParseTuple(args, "O&|p", convert_to_binary_content, &content, &version);
    if (!ret) goto exit;

    digest = compute_content_tlsh_hash(content, version);

    if (digest != NULL)
    {
        result = PyUnicode_FromString(digest);
        free(digest);
    }
    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = paramètre à récupérer pour le traitement.             *
*                                                                             *
*  Description : Indique si une chaîne représente à priori une empreinte TLSH.*
*                                                                             *
*  Retour      : Bilan de l'analyse.                                          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bhash_is_valid_tlsh_hash(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    const char *h;                          /* Chaîne à considérer         */
    int ret;                                /* Bilan de lecture des args.  */
    bool status;                            /* Validité de la chaîne       */

#define BHASH_IS_VALID_TLSH_HASH_METHOD PYTHON_METHOD_DEF               \
(                                                                       \
    is_valid_tlsh_hash, "h",                                            \
    METH_VARARGS, py_bhash,                                             \
    "Check if a *h* string can be considered as a valid TLSH compact"   \
    " hash.\n"                                                          \
    "\n"                                                                \
    "The returned value is a boolean value."                            \
)

    result = NULL;

    ret = PyArg_ParseTuple(args, "s", &h);
    if (!ret) goto exit;

    status = is_valid_tlsh_hash(h);

    result = status ? Py_True : Py_False;
    Py_INCREF(result);

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self = objet Python concerné par l'appel.                    *
*                args = paramètres à récupérer pour le traitement.            *
*                                                                             *
*  Description : Détermine la similarité entre deux empreintes TLSH.          *
*                                                                             *
*  Retour      : Degré de différence relevé ou None en cas d'erreur.          *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_bhash_compare_tlsh_hash(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Valeur à retourner          */
    bool length;                            /* Indication de taille ?      */
    const char *ha;                         /* Première chaîne à considérer*/
    const char *hb;                         /* Seconde chaîne à considérer */
    int ret;                                /* Bilan de lecture des args.  */
    int32_t diff;                           /* Différence à calculer       */
    bool status;                            /* Validité de l'opération     */

#define BHASH_COMPARE_TLSH_HASH_METHOD PYTHON_METHOD_DEF                \
(                                                                       \
    compare_tlsh_hash, "ha, hb, /, length=True",                        \
    METH_VARARGS, py_bhash,                                             \
    "Compare two TLSH compact hashes.\n"                                \
    "\n"                                                                \
    "The *ha* and *hb* arguments are strings from which the hashes"     \
    " will be rebuilt. The"                                             \
    " pychrysalide.plugins.bhash.compute_content_tlsh_hash() method"    \
    " can be used to create such strings. The filtering of valid"       \
    " inputs rely internally on the"                                    \
    " pychrysalide.plugins.bhash.is_valid_tlsh_hash() function.\n"      \
    "\n"                                                                \
    "The *length* argument defines if the TLSH data size hint has to"   \
    " be considered by the comparison process.\n"                       \
    "\n"                                                                \
    "The returned value is a difference level provided as an integer"   \
    " value or *None* in case of error."                                \
)

    result = NULL;

    length = 1;

    ret = PyArg_ParseTuple(args, "ss|p", &ha, &hb, &length);
    if (!ret) goto exit;

    status = compare_tlsh_hash(ha, hb, length, &diff);

    if (status)
        result = PyLong_FromLong(diff);

    else
    {
        result = Py_None;
        Py_INCREF(result);
    }

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : super = module dont la définition est à compléter.           *
*                                                                             *
*  Description : Définit une extension du module 'bhash' à compléter.         *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool populate_bhash_module_with_tlsh(PyObject *super)
{
    bool result;                            /* Bilan à retourner           */

    static PyMethodDef py_tlsh_methods[] = {
        BHASH_COMPUTE_CONTENT_TLSH_HASH_METHOD,
        BHASH_IS_VALID_TLSH_HASH_METHOD,
        BHASH_COMPARE_TLSH_HASH_METHOD,
        { NULL }
    };

    result = register_python_module_methods(super, py_tlsh_methods);

    return result;

}
