
/* Chrysalide - Outil d'analyse de fichiers binaires
 * translate.c - conversion de structures liées aux greffons en objets Python
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


#include "translate.h"


#include <assert.h>


#include "plugin.h"
#include "../helpers.h"
#include "../struct.h"



/******************************************************************************
*                                                                             *
*  Paramètres  : iface = ensemble d'informations à transcrire en Python.      *
*                                                                             *
*  Description : Traduit une description d'interface de greffon.              *
*                                                                             *
*  Retour      : Structure mise en place ou NULL en cas d'erreur.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *translate_plugin_interface_to_python(const plugin_interface *iface)
{
    PyObject *result;                       /* Construction à retourner    */
    PyTypeObject *base;                     /* Modèle d'objet à créer      */
    bool status;                            /* Bilan d'une traduction      */
    PyObject *array;                        /* Tableau à insérer           */
    size_t i;                               /* Boucle de parcours          */
    PyTypeObject *itype;                    /* Type d'élément à créer      */
    PyObject *item;                         /* Elément mis en place        */

    base = get_python_py_struct_type();

    result = PyObject_CallFunction((PyObject *)base, NULL);
    assert(result != NULL);

    status = true;

    if (status) status = TRANSLATE_STRING_FIELD(result, iface, gtp_name);
    if (status) status = TRANSLATE_STRING_FIELD(result, iface, name);
    if (status) status = TRANSLATE_STRING_FIELD(result, iface, desc);
    if (status) status = TRANSLATE_STRING_FIELD(result, iface, version);
    if (status) status = TRANSLATE_STRING_FIELD(result, iface, url);

    if (status) status = TRANSLATE_BOOLEAN_FIELD(result, iface, container);

    if (status) status = TRANSLATE_ARRAY_FIELD(result, iface, required, &array);

    if (status)
    {
        itype = get_python_plugin_module_type();

        for (i = 0; i < iface->required_count; i++)
        {
            item = PyUnicode_FromString(iface->required[i]);
            PyTuple_SetItem(array, i, item);
        }

    }

    if (status) status = TRANSLATE_ARRAY_FIELD(result, iface, actions, &array);

    if (status)
    {
        itype = get_python_plugin_module_type();

        for (i = 0; i < iface->actions_count; i++)
        {
            item = cast_with_constants_group_from_type(itype, "PluginAction", iface->actions[i]);
            PyTuple_SetItem(array, i, item);
        }

    }

    if (!status)
    {
        Py_DECREF(result);
        result = NULL;
    }

    return result;

}
