
/* Chrysalide - Outil d'analyse de fichiers binaires
 * vmpa.c - équivalent Python du fichier "arch/vmpa.c"
 *
 * Copyright (C) 2018-2020 Cyrille Bagard
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


#include "vmpa.h"


#include <assert.h>
#include <malloc.h>
#include <stddef.h>
#include <string.h>


#include <i18n.h>
#include <common/macros.h>


#include "constants.h"
#include "../access.h"
#include "../helpers.h"



/* ---------------------- DEFINITION D'UNE POSITION EN MEMOIRE ---------------------- */


/* Encapsulation d'une localisation */
typedef struct _py_vmpa_t
{
    PyObject_HEAD                           /* Préambule Python            */

    vmpa2t addr;                            /* Elément natif               */
    bool tmp_arg;                           /* Nature de l'objet Python    */

} py_vmpa_t;


/* Initialise un objet Python de type 'vmpa2t'. */
static int py_vmpa_init(py_vmpa_t *, PyObject *, PyObject *);

/* Fournit une représentation d'une variable 'vmpa_t'. */
static PyObject *py_vmpa_to_str(PyObject *);

/* Effectue une comparaison avec un objet Python 'vmpa_t'. */
static PyObject *py_vmpa_richcompare(PyObject *, PyObject *, int);

/* Fournit une partie du contenu de la position représentée. */
static PyObject *py_vmpa_get_value(PyObject *, void *);

/* Définit une partie du contenu de la position représentée. */
static int py_vmpa_set_value(PyObject *, PyObject *, void *);

/* Effectue une conversion d'un objet Python en type 'vmpa_t'. */
static bool convert_pyobj_to_vmpa(PyObject *, vmpa2t *);

/* Effectue une opération de type 'add' avec le type 'vmpa'. */
static PyObject *py_vmpa_nb_add(PyObject *, PyObject *);



/* ------------------------ DEFINITION D'UNE ZONE EN MEMOIRE ------------------------ */


/* Encapsulation d'une couverture mémoire */
typedef struct _py_mrange_t
{
    PyObject_HEAD                           /* Préambule Python            */

    mrange_t range;                         /* Elément natif               */

} py_mrange_t;


/* Initialise un objet Python de type 'mrange_t'. */
static int py_mrange_init(py_mrange_t *, PyObject *, PyObject *);

/* Fournit une représentation d'une variable 'mrange_t'. */
static PyObject *py_mrange_to_str(PyObject *);



/* Effectue une comparaison avec un objet Python 'mrange_t'. */
static PyObject *py_mrange_richcompare(PyObject *, PyObject *, int);



/* Indique si une zone en contient une autre ou non. */
static PyObject *py_mrange_contains(PyObject *, PyObject *);




/* Fournit la position de départ de la zone mémoire représentée. */
static PyObject *py_mrange_get_addr(PyObject *, void *);

/* Définit la position de départ de la zone mémoire représentée. */
static int py_mrange_set_addr(PyObject *, PyObject *, void *);

/* Fournit la taille de la zone mémoire représentée. */
static PyObject *py_mrange_get_length(PyObject *, void *);

/* Définit la taille de la zone mémoire représentée. */
static int py_mrange_set_length(PyObject *, PyObject *, void *);

/* Calcule la position extérieure finale d'une couverture. */
static PyObject *py_mrange_get_end_addr(PyObject *, void *);



/* ---------------------------------------------------------------------------------- */
/*                        DEFINITION D'UNE POSITION EN MEMOIRE                        */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance d'objet à initialiser.                       *
*                args = arguments passés pour l'appel.                        *
*                kwds = mots clefs éventuellement fournis en complément.      *
*                                                                             *
*  Description : Initialise un objet Python de type 'vmpa2t'.                 *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_vmpa_init(py_vmpa_t *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */
    unsigned long long phy;                 /* Position physique           */
    unsigned long long virt;                /* Adresse en mémoire virtuelle*/
    int ret;                                /* Bilan de lecture des args.  */

#define VMPA_DOC                                                            \
    "VMPA stands for Virtual Memory or Physical Address.\n"                 \
    "\n"                                                                    \
    "Thus vmpa objects are locations inside a binary content. Their"        \
    " coordinates are composed of a physical offset and a virtual address." \
    " Both of them can be undefined thanks to special values"               \
    " pychrysalide.arch.vmpa.VmpaSpecialValue."                             \
    "\n"                                                                    \
    "Instances can be created using the following constructor:\n"           \
    "\n"                                                                    \
    "    vmpa(phys=NO_PHYSICAL, virt=NO_VIRTUAL)"                           \
    "\n"                                                                    \
    "Where phys and virt are the values of the physical and virtual"        \
    " positions for the location."

    result = -1;

    phy = VMPA_NO_PHYSICAL;
    virt = VMPA_NO_VIRTUAL;

    ret = PyArg_ParseTuple(args, "|KK", &phy, &virt);
    if (!ret) goto exit;

    init_vmpa(&self->addr, phy, virt);

    self->tmp_arg = false;

    result = 0;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : obj = objet Python à traiter.                                *
*                                                                             *
*  Description : Fournit une représentation d'une variable 'vmpa_t'.          *
*                                                                             *
*  Retour      : Chaîne de caractère pour Python.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_vmpa_to_str(PyObject *obj)
{
    PyObject *result;                       /* Chaîne à retourner          */
    vmpa2t *addr;                           /* Véritable adresse manipulée */
    phys_t physical;                        /* Position physique           */
    VMPA_BUFFER(phys_str);                  /* Version humaine de position */
    virt_t virtual;                         /* Adresse virtuelle           */
    VMPA_BUFFER(virt_str);                  /* Version humaine d'adresse   */

    addr = &((py_vmpa_t *)obj)->addr;

    physical = get_phy_addr(addr);

    if (physical == VMPA_NO_PHYSICAL)
        strncpy(phys_str, _("None"), sizeof(phys_str) - 1);
    else
        vmpa2_phys_to_string(addr, MDS_UNDEFINED, phys_str, NULL);

    virtual = get_virt_addr(addr);

    if (virtual == VMPA_NO_VIRTUAL)
        strncpy(virt_str, _("None"), sizeof(virt_str) - 1);
    else
        vmpa2_virt_to_string(addr, MDS_UNDEFINED, virt_str, NULL);

    result = PyUnicode_FromFormat("<phy=%s, virt=%s>", phys_str, virt_str);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : a  = premier object Python à consulter.                      *
*                b  = second object Python à consulter.                       *
*                op = type de comparaison menée.                              *
*                                                                             *
*  Description : Effectue une comparaison avec un objet Python 'vmpa_t'.      *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_vmpa_richcompare(PyObject *a, PyObject *b, int op)
{
    PyObject *result;                       /* Bilan à retourner           */
    vmpa2t *addr_a;                         /* Première adresse à traiter  */
    vmpa2t addr_b;                          /* Seconde adresse à traiter   */
    int comp;                               /* Résultat d'une comparaison  */

    addr_a = &((py_vmpa_t *)a)->addr;

    if (!convert_pyobj_to_vmpa(b, &addr_b))
        return NULL;

    comp = cmp_vmpa(addr_a, &addr_b);

    switch (op)
    {
        case Py_LT:
            result = comp < 0 ? Py_True : Py_False;
            break;

        case Py_LE:
            result = comp <= 0 ? Py_True : Py_False;
            break;

        case Py_EQ:
            result = comp == 0 ? Py_True : Py_False;
            break;

        case Py_NE:
            result = comp != 0 ? Py_True : Py_False;
            break;

        case Py_GT:
            result = comp > 0 ? Py_True : Py_False;
            break;

        case Py_GE:
            result = comp >= 0 ? Py_True : Py_False;
            break;

        default:
            assert(false);
            result = Py_NotImplemented;
            break;

    }

    Py_INCREF(result);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = définition d'adresse visée par la procédure.       *
*                closure = sélection de la valeur à traiter.                  *
*                                                                             *
*  Description : Fournit une partie du contenu de la position représentée.    *
*                                                                             *
*  Retour      : Nombre positif ou nul ou None.                               *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_vmpa_get_value(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    py_vmpa_t *vmpa;                        /* Véritable objet Python      */
    char *key;                              /* Contenu à cibler précisément*/

    vmpa = (py_vmpa_t *)self;

    key = (char *)closure;

    if (strcmp(key, "phys") == 0)
    {
        if (get_phy_addr(&vmpa->addr) == VMPA_NO_PHYSICAL)
        {
            result = Py_None;
            Py_INCREF(result);
        }
        else result = Py_BuildValue("K", get_phy_addr(&vmpa->addr));
    }
    else
    {
        if (get_virt_addr(&vmpa->addr) == VMPA_NO_VIRTUAL)
        {
            result = Py_None;
            Py_INCREF(result);
        }
        else result = Py_BuildValue("K", get_virt_addr(&vmpa->addr));
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = définition d'adresse visée par la procédure.       *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = sélection de la valeur à traiter.                  *
*                                                                             *
*  Description : Définit une partie du contenu de la position représentée.    *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_vmpa_set_value(PyObject *self, PyObject *value, void *closure)
{
    int result;                             /* Bilan à faire remonter      */
    py_vmpa_t *vmpa;                        /* Véritable objet Python      */
    char *key;                              /* Contenu à cibler précisément*/
    PY_LONG_LONG val;                       /* Valeur traduite génériquemt */
    int overflow;                           /* Détection d'une grosse val. */

    result = 0;

    vmpa = (py_vmpa_t *)self;

    key = (char *)closure;

    if (strcmp(key, "phys") == 0)
    {
        if (value == Py_None)
            init_vmpa(&vmpa->addr, VMPA_NO_PHYSICAL, get_virt_addr(&vmpa->addr));

        else
        {
            val = PyLong_AsLongLongAndOverflow(value, &overflow);

            if (val == -1 && (overflow == 1 || PyErr_Occurred()))
            {
                result = -1;
                PyErr_Clear();
            }
            else init_vmpa(&vmpa->addr, val, get_virt_addr(&vmpa->addr));

        }

    }
    else
    {
        if (value == Py_None)
            init_vmpa(&vmpa->addr, get_phy_addr(&vmpa->addr), VMPA_NO_VIRTUAL);

        else
        {
            val = PyLong_AsLongLongAndOverflow(value, &overflow);

            if (val == -1 && (overflow == 1 || PyErr_Occurred()))
            {
                result = -1;
                PyErr_Clear();
            }
            else init_vmpa(&vmpa->addr, get_phy_addr(&vmpa->addr), val);

        }

    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : obj  = objet Python à tenter de convertir.                   *
*                addr = structure équivalente pour Chrysalide.                *
*                                                                             *
*  Description : Effectue une conversion d'un objet Python en type 'vmpa_t'.  *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static bool convert_pyobj_to_vmpa(PyObject *obj, vmpa2t *addr)
{
    bool result;                            /* Résulats à retourner        */
    PyTypeObject *py_vmpa_type;             /* Type Python pour 'vmpa'     */
    int ret;                                /* Bilan d'un appel            */
    PY_LONG_LONG value;                     /* Valeur de type générique    */
    int overflow;                           /* Détection d'une grosse val. */

    result = false;

    py_vmpa_type = get_python_vmpa_type();

    ret = PyObject_IsInstance(obj, (PyObject *)py_vmpa_type);

    /* S'il n'y a rien à faire... */
    if (ret == 1)
    {
        *addr = ((py_vmpa_t *)obj)->addr;
        result = true;
    }

    /* Sinon on demande à Python... */
    else
    {
        value = PyLong_AsLongLongAndOverflow(obj, &overflow);

        if (value == -1 && (overflow == 1 || PyErr_Occurred()))
        {
            PyErr_Clear();
            PyErr_SetString(PyExc_TypeError, _("Unable to cast object as VMPA."));
        }

        else
        {
            init_vmpa(addr, value, value);
            result = true;
        }

    }

    return result;

}




/******************************************************************************
*                                                                             *
*  Paramètres  : o1 = premier élément concerné par l'opération.               *
*                o2 = second élément concerné par l'opération.                *
*                                                                             *
*  Description : Effectue une opération de type 'add' avec le type 'vmpa'.    *
*                                                                             *
*  Retour      : Résultat de l'opération.                                     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_vmpa_nb_add(PyObject *o1, PyObject *o2)
{
    PyObject *result;                       /* Résultat à retourner        */
    vmpa2t addr1;                           /* Première adresse à traiter  */
    vmpa2t addr2;                           /* Seconde adresse à traiter   */
    PyTypeObject *py_vmpa_type;             /* Type Python pour 'vmpa'     */

    if (!convert_pyobj_to_vmpa(o1, &addr1))
        return NULL;

    if (!convert_pyobj_to_vmpa(o2, &addr2))
        return NULL;

    py_vmpa_type = get_python_vmpa_type();

    result = PyObject_CallObject((PyObject *)py_vmpa_type, NULL);

    init_vmpa(&((py_vmpa_t *)result)->addr,
              addr1.physical + addr2.physical,
              addr1.virtual + addr2.virtual);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_vmpa_type(void)
{
    static PyNumberMethods py_vmpa_nb_proto = {

        .nb_add = py_vmpa_nb_add,

        /*
     binaryfunc nb_add;
     binaryfunc nb_subtract;
     binaryfunc nb_multiply;
     binaryfunc nb_remainder;
     binaryfunc nb_divmod;
     ternaryfunc nb_power;
     unaryfunc nb_negative;
     unaryfunc nb_positive;
     unaryfunc nb_absolute;
     inquiry nb_bool;
     unaryfunc nb_invert;
     binaryfunc nb_lshift;
     binaryfunc nb_rshift;
     binaryfunc nb_and;
     binaryfunc nb_xor;
     binaryfunc nb_or;
     unaryfunc nb_int;
     void *nb_reserved;
     unaryfunc nb_float;

     binaryfunc nb_inplace_add;
     binaryfunc nb_inplace_subtract;
     binaryfunc nb_inplace_multiply;
     binaryfunc nb_inplace_remainder;
     ternaryfunc nb_inplace_power;
     binaryfunc nb_inplace_lshift;
     binaryfunc nb_inplace_rshift;
     binaryfunc nb_inplace_and;
     binaryfunc nb_inplace_xor;
     binaryfunc nb_inplace_or;

     binaryfunc nb_floor_divide;
     binaryfunc nb_true_divide;
     binaryfunc nb_inplace_floor_divide;
     binaryfunc nb_inplace_true_divide;
     
     unaryfunc nb_index;

        */

    };

    static PyGetSetDef py_vmpa_getseters[] = {

        {
            "phys", py_vmpa_get_value, py_vmpa_set_value,
            "Give access to the physical offset of the location.", "phys"
        },

        {
            "virt", py_vmpa_get_value, py_vmpa_set_value,
            "Give access to the virtual address of the location.", "virt"
        },
        { NULL }

    };

    static PyTypeObject py_vmpa_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.vmpa",
        .tp_basicsize   = sizeof(py_vmpa_t),

        .tp_as_number   = &py_vmpa_nb_proto,

        .tp_str         = py_vmpa_to_str,

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = VMPA_DOC,

        .tp_richcompare = py_vmpa_richcompare,

        .tp_getset      = py_vmpa_getseters,

        .tp_init        = (initproc)py_vmpa_init,
        .tp_new         = PyType_GenericNew,

    };

    return &py_vmpa_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.vmpa'.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_vmpa_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python pour 'vmpa'     */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_vmpa_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        if (PyType_Ready(type) != 0)
            return false;

        module = get_access_to_python_module("pychrysalide.arch");

        if (!register_python_module_object(module, type))
            return false;

        if (!define_arch_vmpa_constants(type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : obj = objet Python à traiter.                                *
*                                                                             *
*  Description : Donne accès au coeur d'un objet 'pychrysalide.arch.vmpa'.    *
*                                                                             *
*  Retour      : Localistion réelle ou NULL en cas de mauvaise conversion.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

vmpa2t *get_internal_vmpa(PyObject *obj)
{
    int ret;                                /* Bilan d'analyse             */

    ret = PyObject_IsInstance(obj, (PyObject *)get_python_vmpa_type());
    if (!ret) return NULL;

    return &((py_vmpa_t *)obj)->addr;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr = structure interne à copier en objet Python.           *
*                                                                             *
*  Description : Convertit une structure de type 'vmpa2t' en objet Python.    *
*                                                                             *
*  Retour      : Object Python résultant de la conversion opérée.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *build_from_internal_vmpa(const vmpa2t *addr)
{
    PyObject *result;                       /* Instance à retourner        */
    PyTypeObject *type;                     /* Type à instancier           */
    PyObject *args;                         /* Liste des arguments d'appel */

    type = get_python_vmpa_type();

    args = Py_BuildValue("KK", get_phy_addr(addr), get_virt_addr(addr));

    result = PyObject_CallObject((PyObject *)type, args);

    Py_DECREF(args);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en adresse n'importe quoi.                *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_any_to_vmpa(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
#ifndef NDEBUG
    py_vmpa_t *self;                        /* Objet Python alloué         */
#endif
    int ret;                                /* Test intermédiaire          */
    PY_LONG_LONG value;                     /* Valeur de type générique    */
    int overflow;                           /* Détection d'une grosse val. */
    py_vmpa_t *tmp;                         /* Objet creux temporaire      */

    result = 0;

    /* Nettoyage en cours ? */

    if (arg == NULL)
    {
#ifndef NDEBUG
        self = container_of(*(vmpa2t **)dst, py_vmpa_t, addr);
        assert(self->tmp_arg);
#endif

        clean_vmpa_arg(*(vmpa2t **)dst);

        result = 1;
        goto done;

    }

    /* Si l'objet est au bon format, rien à faire ! */

    ret = PyObject_IsInstance(arg, (PyObject *)get_python_vmpa_type());

    if (ret == 1)
    {
        *((vmpa2t **)dst) = get_internal_vmpa(arg);

        result = 1;
        goto done;

    }

    /* Sinon on demande à Python... */

    value = PyLong_AsLongLongAndOverflow(arg, &overflow);

    if (value == -1 && (overflow == 1 || PyErr_Occurred()))
        PyErr_Clear();

    else
    {
        tmp = malloc(sizeof(py_vmpa_t));

        init_vmpa(&tmp->addr, VMPA_NO_PHYSICAL, value);

        tmp->tmp_arg = true;

        *((vmpa2t **)dst) = &tmp->addr;

        result = Py_CLEANUP_SUPPORTED;
        goto done;

    }

    PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to vmpa");

 done:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : addr = localisation obtenue par lecture d'argument.          *
*                                                                             *
*  Description : Libère la mémoire allouée pour un passage d'argument.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

void clean_vmpa_arg(vmpa2t *addr)
{
    py_vmpa_t *self;                        /* Objet Python alloué         */

    self = container_of(addr, py_vmpa_t, addr);

    if (self->tmp_arg)
        free(self);

}



/* ---------------------------------------------------------------------------------- */
/*                          DEFINITION D'UNE ZONE EN MEMOIRE                          */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : self = instance d'objet à initialiser.                       *
*                args = arguments passés pour l'appel.                        *
*                kwds = mots clefs éventuellement fournis en complément.      *
*                                                                             *
*  Description : Initialise un objet Python de type 'mrange_t'.               *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_mrange_init(py_mrange_t *self, PyObject *args, PyObject *kwds)
{
    int result;                             /* Bilan à retourner           */
    PyObject *py_vmpa;                      /* Localisation version Python */
    unsigned long long length;              /* Taille physique             */
    int ret;                                /* Bilan de lecture des args.  */
    vmpa2t *addr;                           /* Localisation version C      */

    result = -1;

    ret = PyArg_ParseTuple(args, "OK", &py_vmpa, &length);
    if (!ret) goto exit;

    ret = PyObject_IsInstance(py_vmpa, (PyObject *)get_python_vmpa_type());
    if (!ret) goto exit;

    addr = get_internal_vmpa(py_vmpa);
    if (addr == NULL) goto exit;

    init_mrange(&self->range, addr, length);

    result = 0;

 exit:

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : obj = objet Python à traiter.                                *
*                                                                             *
*  Description : Fournit une représentation d'une variable 'mrange_t'.        *
*                                                                             *
*  Retour      : Chaîne de caractère pour Python.                             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_mrange_to_str(PyObject *obj)
{
    PyObject *result;                       /* Chaîne à retourner          */
    mrange_t *range;                        /* Espace mémoire à traiter    */
    vmpa2t *addr;                           /* Véritable adresse manipulée */
    phys_t physical;                        /* Position physique           */
    VMPA_BUFFER(phys_str);                  /* Version humaine de position */
    virt_t virtual;                         /* Adresse virtuelle           */
    VMPA_BUFFER(virt_str);                  /* Version humaine d'adresse   */
    vmpa2t length;                          /* Fausse taille physique      */
    VMPA_BUFFER(len_str);                   /* Version humaine de longueur */

    range = get_internal_mrange(obj);
    assert(range != NULL);

    addr = get_mrange_addr(range);

    physical = get_phy_addr(addr);

    if (physical == VMPA_NO_PHYSICAL)
        strncpy(phys_str, _("None"), sizeof(phys_str) - 1);
    else
        vmpa2_phys_to_string(addr, MDS_UNDEFINED, phys_str, NULL);

    virtual = get_virt_addr(addr);

    if (virtual == VMPA_NO_VIRTUAL)
        strncpy(virt_str, _("None"), sizeof(virt_str) - 1);
    else
        vmpa2_virt_to_string(addr, MDS_UNDEFINED, virt_str, NULL);

    init_vmpa(&length, get_mrange_length(range), VMPA_NO_VIRTUAL);

    vmpa2_phys_to_string(&length, MDS_UNDEFINED, len_str, NULL);

    result = PyUnicode_FromFormat("(<phy=%s, virt=%s>, +%s)", phys_str, virt_str, len_str);

    return result;

}




/******************************************************************************
*                                                                             *
*  Paramètres  : a  = premier object Python à consulter.                      *
*                b  = second object Python à consulter.                       *
*                op = type de comparaison menée.                              *
*                                                                             *
*  Description : Effectue une comparaison avec un objet Python 'mrange_t'.    *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_mrange_richcompare(PyObject *a, PyObject *b, int op)
{
    PyObject *result;                       /* Bilan à retourner           */
    mrange_t *range_a;                      /* Premier espace à traiter    */
    mrange_t *range_b;                      /* Second espace à traiter     */
    int status;                             /* Résultat d'une comparaison  */

    range_a = get_internal_mrange(a);

    range_b = get_internal_mrange(b);
    if (range_b == NULL) return NULL;

    status = cmp_mrange(range_a, range_b);

    result = status_to_rich_cmp_state(status, op);

    Py_INCREF(result);

    return result;

}









/******************************************************************************
*                                                                             *
*  Paramètres  : self = contenu binaire à manipuler.                          *
*                args = non utilisé ici.                                      *
*                                                                             *
*  Description : Indique si une zone en contient une autre ou non.            *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_mrange_contains(PyObject *self, PyObject *args)
{
    PyObject *result;                       /* Bilan à faire remonter      */
    int ret;                                /* Bilan de lecture des args.  */
    PyObject *range_obj;                    /* Objet pour un intervale     */
    mrange_t *range;                        /* Région mémoire de contenance*/
    mrange_t *sub;                          /* Région mémoire contenue ?   */

    ret = PyArg_ParseTuple(args, "O", &range_obj);
    if (!ret) return NULL;

    ret = PyObject_IsInstance(range_obj, (PyObject *)get_python_mrange_type());
    if (!ret) return NULL;

    range = get_internal_mrange(self);
    sub = get_internal_mrange(range_obj);

    result = (mrange_contains_mrange(range, sub) ? Py_True : Py_False);

    Py_INCREF(result);

    return result;

}





/******************************************************************************
*                                                                             *
*  Paramètres  : self    = définition de l'espace visé par la procédure.      *
*                closure = élément non utilisé ici.                           *
*                                                                             *
*  Description : Fournit la position de départ de la zone mémoire représentée.*
*                                                                             *
*  Retour      : Nouvelle objet mis en place.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_mrange_get_addr(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    mrange_t *range;                        /* Espace mémoire à manipuler  */

    range = get_internal_mrange(self);

    result = build_from_internal_vmpa(get_mrange_addr(range));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = définition de l'espace visé par la procédure.      *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = élément non utilisé ici.                           *
*                                                                             *
*  Description : Définit la position de départ de la zone mémoire représentée.*
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_mrange_set_addr(PyObject *self, PyObject *value, void *closure)
{
    int result;                             /* Bilan à faire remonter      */
    vmpa2t *addr;                           /* Localisation version C      */
    mrange_t *range;                        /* Espace mémoire à manipuler  */

    result = 0;

    addr = get_internal_vmpa(value);
    if (addr == NULL) return -1;

    range = get_internal_mrange(self);

    init_mrange(range, addr, get_mrange_length(range));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = définition de l'espace visé par la procédure.      *
*                closure = élément non utilisé ici.                           *
*                                                                             *
*  Description : Fournit la taille de la zone mémoire représentée.            *
*                                                                             *
*  Retour      : Nouvelle objet mis en place.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_mrange_get_length(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    mrange_t *range;                        /* Espace mémoire à manipuler  */

    range = get_internal_mrange(self);

    result = Py_BuildValue("K", get_mrange_length(range));

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = définition de l'espace visé par la procédure.      *
*                value   = valeur fournie à intégrer ou prendre en compte.    *
*                closure = élément non utilisé ici.                           *
*                                                                             *
*  Description : Définit la taille de la zone mémoire représentée.            *
*                                                                             *
*  Retour      : Bilan de l'opération pour Python.                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static int py_mrange_set_length(PyObject *self, PyObject *value, void *closure)
{
    int result;                             /* Bilan à faire remonter      */
    mrange_t *range;                        /* Espace mémoire à manipuler  */
    PY_LONG_LONG val;                       /* Valeur traduite génériquemt */
    int overflow;                           /* Détection d'une grosse val. */
    vmpa2t tmp;                             /* Copie pour recopie          */

    result = 0;

    range = get_internal_mrange(self);

    val = PyLong_AsLongLongAndOverflow(value, &overflow);

    if (val == -1 && (overflow == 1 || PyErr_Occurred()))
    {
        result = -1;
        PyErr_Clear();
    }
    else
    {
        copy_vmpa(&tmp, get_mrange_addr(range));
        init_mrange(range, &tmp, val);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : self    = définition de l'espace visé par la procédure.      *
*                closure = élément non utilisé ici.                           *
*                                                                             *
*  Description : Calcule la position extérieure finale d'une couverture.      *
*                                                                             *
*  Retour      : Nouvelle objet mis en place.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static PyObject *py_mrange_get_end_addr(PyObject *self, void *closure)
{
    PyObject *result;                       /* Valeur à retourner          */
    mrange_t *range;                        /* Espace mémoire à manipuler  */
    vmpa2t end;                             /* Adresse à reproduire        */

    range = get_internal_mrange(self);
    compute_mrange_end_addr(range, &end);

    result = build_from_internal_vmpa(&end);

    return result;

}














/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Fournit un accès à une définition de type à diffuser.        *
*                                                                             *
*  Retour      : Définition d'objet pour Python.                              *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyTypeObject *get_python_mrange_type(void)
{
    static PyMethodDef py_mrange_methods[] = {
        {
            "contains", py_mrange_contains,
            METH_VARARGS,
            "contains($self, other, /)\n--\n\nTell if the current range contains another given range or address."
        },
#if 0
        { "read_u8", py_arch_instruction_read_u8,
          METH_VARARGS,
          "read_u8($self, addr, /)\n--\n\nRead an unsigned byte from a given position."
        },
#endif
        { NULL }
    };

    static PyGetSetDef py_mrange_getseters[] = {
        {
            "addr", py_mrange_get_addr, py_mrange_set_addr,
            "Give access to the start location of the memory range.", NULL
        },
        {
            "length", py_mrange_get_length, py_mrange_set_length,
            "Give access to the length of the memory range.", NULL
        },
        {
            "end", py_mrange_get_end_addr, NULL,
            "Provide the final external point of the memory range.", NULL
        },
        { NULL }
    };

    static PyTypeObject py_mrange_type = {

        PyVarObject_HEAD_INIT(NULL, 0)

        .tp_name        = "pychrysalide.arch.mrange",
        .tp_basicsize   = sizeof(py_mrange_t),

        .tp_str         = py_mrange_to_str,

        .tp_flags       = Py_TPFLAGS_DEFAULT,

        .tp_doc         = "Python object for mrange_t.",

        .tp_richcompare = py_mrange_richcompare,

        .tp_methods     = py_mrange_methods,
        .tp_getset      = py_mrange_getseters,

        .tp_init        = (initproc)py_mrange_init,
        .tp_new         = PyType_GenericNew,

    };

    return &py_mrange_type;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : module = module dont la définition est à compléter.          *
*                                                                             *
*  Description : Prend en charge l'objet 'pychrysalide.arch.mrange'.          *
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

bool ensure_python_mrange_is_registered(void)
{
    PyTypeObject *type;                     /* Type Python pour 'mrange'   */
    PyObject *module;                       /* Module à recompléter        */

    type = get_python_mrange_type();

    if (!PyType_HasFeature(type, Py_TPFLAGS_READY))
    {
        if (PyType_Ready(type) != 0)
            return false;

        module = get_access_to_python_module("pychrysalide.arch");

        if (!register_python_module_object(module, type))
            return false;

    }

    return true;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : obj = objet Python à traiter.                                *
*                                                                             *
*  Description : Donne accès au coeur d'un objet 'pychrysalide.arch.mrange'.  *
*                                                                             *
*  Retour      : Localistion réelle ou NULL en cas de mauvaise conversion.    *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

mrange_t *get_internal_mrange(PyObject *obj)
{
    int ret;                                /* Bilan d'analyse             */

    ret = PyObject_IsInstance(obj, (PyObject *)get_python_mrange_type());
    if (!ret) return NULL;

    return &((py_mrange_t *)obj)->range;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : range = structure interne à copier en objet Python.          *
*                                                                             *
*  Description : Convertit une structure de type 'mrange_t' en objet Python.  *
*                                                                             *
*  Retour      : Object Python résultant de la conversion opérée.             *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

PyObject *build_from_internal_mrange(const mrange_t *range)
{
    PyObject *result;                       /* Instance à retourner        */
    PyTypeObject *type;                     /* Type à instancier           */
    PyObject *addr_obj;                     /* Objet pour l'adresse de base*/
    PyObject *args;                         /* Liste des arguments d'appel */

    type = get_python_mrange_type();

    addr_obj = build_from_internal_vmpa(get_mrange_addr(range));

    args = Py_BuildValue("OK", addr_obj, get_mrange_length(range));

    result = PyObject_CallObject((PyObject *)type, args);

    Py_DECREF(args);
    Py_DECREF(addr_obj);

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : arg = argument quelconque à tenter de convertir.             *
*                dst = destination des valeurs récupérées en cas de succès.   *
*                                                                             *
*  Description : Tente de convertir en espace mémoire n'importe quoi.         *
*                                                                             *
*  Retour      : Bilan de l'opération, voire indications supplémentaires.     *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

int convert_any_to_mrange(PyObject *arg, void *dst)
{
    int result;                             /* Bilan à retourner           */
    int ret;                                /* Test intermédiaire          */
    mrange_t *src;                          /* Modèle de données à copier  */

    result = 0;

    /* Si l'objet est au bon format, rien à faire ! */

    ret = PyObject_IsInstance(arg, (PyObject *)get_python_mrange_type());

    if (ret == 1)
    {
        src = get_internal_mrange(arg);
        copy_mrange((mrange_t *)dst, src);

        result = 1;
        goto done;

    }

    PyErr_SetString(PyExc_TypeError, "unable to convert the provided argument to mrange");

 done:

    return result;

}
