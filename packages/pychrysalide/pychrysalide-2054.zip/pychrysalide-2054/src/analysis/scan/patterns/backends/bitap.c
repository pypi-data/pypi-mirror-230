
/* Chrysalide - Outil d'analyse de fichiers binaires
 * bitap.c - méthode de recherche basée sur l'algorithme Bitap
 *
 * Copyright (C) 2022 Cyrille Bagard
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
 *  along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
 */


#include "bitap.h"


#include <alloca.h>
#include <assert.h>
#include <sys/mman.h>
#include <sched.h>


#include "bitap-int.h"
#include "../../../../core/logs.h"
//#include "../../matches/bytes.h"



/* ---------------------- IMPLANTATION D'UNE NOUVELLE APPROCHE ---------------------- */


/* Initialise la classe des méthodes basée sur Bitmap. */
static void g_bitap_backend_class_init(GBitapBackendClass *);

/* Initialise une instance de méthodes basée sur Bitmap. */
static void g_bitap_backend_init(GBitapBackend *);

/* Supprime toutes les références externes. */
static void g_bitap_backend_dispose(GBitapBackend *);

/* Procède à la libération totale de la mémoire. */
static void g_bitap_backend_finalize(GBitapBackend *);



/* --------------------- IMPLEMENTATION DES FONCTIONS DE CLASSE --------------------- */


/* Indique la taille maximale des suites d'octets recherchées. */
size_t g_bitap_backend_get_atom_max_size(const GBitapBackend *);

/* Inscrit dans le moteur une chaîne de caractères à rechercher. */
static patid_t g_bitap_backend_enroll_plain_pattern(GBitapBackend *, GScanContext *, const uint8_t *, size_t);

/* Parcours un contenu binaire à la recherche de motifs. */
static void g_bitap_backend_run_scan(const GBitapBackend *, GScanContext *);

/* Imprime quelques faits quant aux éléments mis en place. */
static void g_bitap_backend_output_stats(const GBitapBackend *);



/* ---------------------- OPTIMISATIONS POUR ARCHITECTURE AVX2 ---------------------- */


#ifdef HAVE_AVX2

/* Indique la valeur portée par une expression rationnelle. */
static void extend_grouped_strings_avx2(grouped_strings_avx2_t ***, size_t *);

/* Inscrit dans le moteur une chaîne de caractères à rechercher. */
static patid_t enroll_plain_pattern_avx2(GBitapBackend *, GScanContext *, const bin_t *, size_t);

/* Parcours un contenu binaire à la recherche de motifs. */
static void run_scan_avx2(const GBitapBackend *, GScanContext *, const bin_t *, phys_t);

#endif



/* --------------------- OPTIMISATIONS POUR ARCHITECTURE AVX512 --------------------- */


#ifdef HAVE_AVX512_F

/* Indique la valeur portée par une expression rationnelle. */
static void extend_grouped_strings_avx512(grouped_strings_avx512_t ***, size_t *);

/* Inscrit dans le moteur une chaîne de caractères à rechercher. */
static patid_t enroll_plain_pattern_avx512(GBitapBackend *, GScanContext *, const bin_t *, size_t);

/* Parcours un contenu binaire à la recherche de motifs. */
static void run_scan_avx512(const GBitapBackend *, GScanContext *, const bin_t *, phys_t);

#endif



/* ---------------------------------------------------------------------------------- */
/*                        IMPLANTATION D'UNE NOUVELLE APPROCHE                        */
/* ---------------------------------------------------------------------------------- */


/* Indique le type défini pour un moteur de recherche pour données. */
G_DEFINE_TYPE(GBitapBackend, g_bitap_backend, G_TYPE_ENGINE_BACKEND);


/******************************************************************************
*                                                                             *
*  Paramètres  : klass = classe à initialiser.                                *
*                                                                             *
*  Description : Initialise la classe des méthodes basée sur Bitmap.          *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bitap_backend_class_init(GBitapBackendClass *klass)
{
    GObjectClass *object;                   /* Autre version de la classe  */
    GEngineBackendClass *backend;           /* Version de classe parente   */

    object = G_OBJECT_CLASS(klass);

    object->dispose = (GObjectFinalizeFunc/* ! */)g_bitap_backend_dispose;
    object->finalize = (GObjectFinalizeFunc)g_bitap_backend_finalize;

    backend = G_ENGINE_BACKEND_CLASS(klass);

    backend->get_max_size = (get_backend_atom_max_size_fc)g_bitap_backend_get_atom_max_size;
    backend->enroll_plain = (enroll_plain_into_backend_fc)g_bitap_backend_enroll_plain_pattern;
    backend->run_scan = (run_backend_scan_fc)g_bitap_backend_run_scan;
    backend->output = (output_backend_stats_fc)g_bitap_backend_output_stats;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance à initialiser.                            *
*                                                                             *
*  Description : Initialise une instance de méthodes basée sur Bitmap.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bitap_backend_init(GBitapBackend *backend)
{

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Supprime toutes les références externes.                     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bitap_backend_dispose(GBitapBackend *backend)
{
    G_OBJECT_CLASS(g_bitap_backend_parent_class)->dispose(G_OBJECT(backend));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = instance d'objet GLib à traiter.                   *
*                                                                             *
*  Description : Procède à la libération totale de la mémoire.                *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bitap_backend_finalize(GBitapBackend *backend)
{
    G_OBJECT_CLASS(g_bitap_backend_parent_class)->finalize(G_OBJECT(backend));

}


/******************************************************************************
*                                                                             *
*  Paramètres  : -                                                            *
*                                                                             *
*  Description : Crée une méthode de recherche basée sur l'algorithme Bitap.  *
*                                                                             *
*  Retour      : Méthode mise en place.                                       *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

GEngineBackend *g_bitap_backend_new(void)
{
    GBitapBackend *result;                  /* Structure à retourner       */

    result = g_object_new(G_TYPE_BITAP_BACKEND, NULL);

    return G_ENGINE_BACKEND(result);

}



/* ---------------------------------------------------------------------------------- */
/*                       IMPLEMENTATION DES FONCTIONS DE CLASSE                       */
/* ---------------------------------------------------------------------------------- */


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à consulter.                   *
*                                                                             *
*  Description : Indique la taille maximale des suites d'octets recherchées.  *
*                                                                             *
*  Retour      : Valeur strictement positive.                                 *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

size_t g_bitap_backend_get_atom_max_size(const GBitapBackend *backend)
{
    size_t result;                          /* Taille à faire connaître    */

    result = BITAP_ATOM_SIZE;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = contexte de l'analyse à mener.                     *
*                plain   = chaîne de caractères classique à intégrer.         *
*                len     = taille de cette chaîne.                            *
*                                                                             *
*  Description : Inscrit dans le moteur une chaîne de caractères à rechercher.*
*                                                                             *
*  Retour      : Bilan de l'opération.                                        *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static patid_t g_bitap_backend_enroll_plain_pattern(GBitapBackend *backend, GScanContext *context, const uint8_t *plain, size_t len)
{
    patid_t result;                         /* Identifiant à retourner     */

#ifdef HAVE_AVX512_F
    if (0)
        result = enroll_plain_pattern_avx512(backend, context, plain, len);
    else
#endif

#ifdef HAVE_AVX2
    if (0)
        result = enroll_plain_pattern_avx2(backend, context, plain, len);
    else
#endif

        result = INVALID_PATTERN_ID;

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = lieu d'enregistrement des résultats.               *
*                                                                             *
*  Description : Parcours un contenu binaire à la recherche de motifs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bitap_backend_run_scan(const GBitapBackend *backend, GScanContext *context)
{
    cpu_set_t old_mask;                     /* Cartographie des CPU #1     */
    int ret;                                /* Bilan d'un appel            */
    unsigned int cpu;                       /* Processeur courant          */
    cpu_set_t new_mask;                     /* Cartographie des CPU #2     */
    GBinContent *content;                   /* Contenu binaire manipulé    */
    phys_t dlen;                            /* Quantité de données         */
    vmpa2t pos;                             /* Point de départ ciblé       */
    const bin_t *data;                      /* Données à analyser          */

    ret = sched_getaffinity(0, sizeof(cpu_set_t), &old_mask);

    if (ret != 0)
    {
        LOG_ERROR_N("sched_getaffinity");
        goto exit;
    }

    ret = getcpu(&cpu, NULL);

    if (ret != 0)
    {
        LOG_ERROR_N("get_cpu");
        goto exit;
    }

    CPU_ZERO(&new_mask);
    CPU_SET(cpu, &new_mask);

    ret = sched_setaffinity(0, sizeof(cpu_set_t), &new_mask);

    if (ret != 0)
    {
        LOG_ERROR_N("sched_setaffinity");
        goto exit;
    }

    content = g_scan_context_get_content(context);

    dlen = g_binary_content_compute_size(content);

    g_binary_content_compute_start_pos(content, &pos);
    data = g_binary_content_get_raw_access(content, &pos, dlen);

    assert(data != NULL);




#ifdef HAVE_AVX512_F
    if (0)
        run_scan_avx512(backend, context, data, dlen);
    else
#endif

#ifdef HAVE_AVX2
    if (0)
        run_scan_avx2(backend, context, data, dlen);
    else
#endif

        ;

    g_object_unref(G_OBJECT(content));

 exit:

    ;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à consulter.                   *
*                                                                             *
*  Description : Imprime quelques faits quant aux éléments mis en place.      *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void g_bitap_backend_output_stats(const GBitapBackend *backend)
{
    printf("hello here!\n");

}



/* ---------------------------------------------------------------------------------- */
/*                        OPTIMISATIONS POUR ARCHITECTURE AVX2                        */
/* ---------------------------------------------------------------------------------- */


/**
 * Cf. https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html#techs=AVX,AVX2
 */

#ifdef HAVE_AVX2

/******************************************************************************
*                                                                             *
*  Paramètres  : strings = ensemble de groupes constitués. [OUT]              *
*                count   = nombre de groupes courant. [OUT]                   *
*                                                                             *
*  Description : Indique la valeur portée par une expression rationnelle.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void extend_grouped_strings_avx2(grouped_strings_avx2_t ***strings, size_t *count)
{
    grouped_strings_avx2_t *new;            /* Zone supplémentaire         */
    size_t i;                               /* Boucle de parcours          */

    /* Définition d'un nouvel élément vierge */

    new = aligned_alloc(256, sizeof(grouped_strings_avx2_t));

    for (i = 0; i < 256; i++)
        new->pattern_masks[i] = _mm256_set1_epi8(~0);

    new->found_masks = _mm256_set1_epi8(~0);

    new->R = _mm256_set1_epi8(~1);

    for (i = 0; i < 32; i++)
    {
        new->m[i] = 0;

        new->found_id[i] = INVALID_PATTERN_ID;

    }

    new->available = 32;
    new->used = 0;

    /* Inscription */

    *strings = realloc(*strings, ++(*count) * sizeof(grouped_strings_avx2_t *));

    (*strings)[*count - 1] = new;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend    = moteur de recherche à manipuler.                *
*                context    = contexte de l'analyse à mener.                  *
*                plain      = chaîne de caractères classique à intégrer.      *
*                plen       = taille de cette chaîne.                         *
*                                                                             *
*  Description : Inscrit dans le moteur une chaîne de caractères à rechercher.*
*                                                                             *
*  Retour      : Indice de résultats pour le motif.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static patid_t enroll_plain_pattern_avx2(GBitapBackend *backend, GScanContext *context, const bin_t *plain, size_t plen)
{
    patid_t result;                         /* Identifiant à retourner     */
    grouped_strings_avx2_t ***strings;      /* Groupe de chaînes visé      */
    size_t *count;                          /* Taille de ce groupe         */
    grouped_strings_avx2_t *last;           /* Dernier groupe à remplir    */
    size_t n;                               /* Indice dans le groupe       */
    size_t i;                               /* Boucle de parcours          */
    __m256i *letter;                        /* Lettre à marquer            */

    /* Sélection du groupe de travail adéquat */

    strings = &backend->manager_avx2.strings_8;
    count = &backend->manager_avx2.count_8;

    /* Préparation de la place nécessaire */

    if (*count == 0)
    {
        extend_grouped_strings_avx2(strings, count);

        last = (*strings)[0];

    }

    else
    {
        last = (*strings)[*count - 1];

        if (last->used == last->available)
        {
            extend_grouped_strings_avx2(strings, count);
            last = (*strings)[*count - 1];
        }

    }

    /* Intégration d'une nouvelle chaîne */

    n = last->used++;

    last->m[n] = plen;

    result = g_scan_context_get_new_pattern_id(context);

    last->found_id[n] = result;

    ((uint8_t *)&last->found_masks)[n] = (1 << plen);

    for (i = 0; i < plen; i++)
    {
        letter = last->pattern_masks + plain[i];
        ((uint8_t *)letter)[n] &= ~(1 << i);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = lieu d'enregistrement des résultats.               *
*                data    = données à analyser.                                *
*                dlen    = quantité de ces données.                           *
*                                                                             *
*  Description : Parcours un contenu binaire à la recherche de motifs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void run_scan_avx2(const GBitapBackend *backend, GScanContext *context, const bin_t *data, phys_t dlen)
{
    const group_manager_avx2_t *manager;    /* Accès simplifié             */

    register __m256i zero asm("ymm11");                           /* Constante 0 sur 256 bits    */
    size_t k;                               /* Boucle de parcours #1       */
    grouped_strings_avx2_t group;           /* Copie pour accès locaux     */

    register __m256i R asm("ymm12");                              /* Résultats courants          */
    register __m256i found_masks asm("ymm10"); /* Vérifications accélérées  */

    //__m256i pre_shift_mask;                 /* Préparation de décalage     */
    //phys_t i;                               /* Boucle de parcours #2       */




    const bin_t *iter;
    const bin_t *maxiter;
    //phys_t i;                               /* Boucle de parcours #2       */

    volatile register __m256i xxxx;                           /* Test de correspondances     */


    __m256i test;                           /* Test de correspondances     */
    __m256i test2;                           /* Test de correspondances     */
    __m256i status;                         /* Statut d'une comparaison    */

    int masks[10];

    int mask;                               /* Masque d'accès rapide       */
    size_t j;                               /* Boucle de parcours #3       */


    int ret;

    //return;

    /* Initialisations diverses */

    manager = &backend->manager_avx2;

    zero = _mm256_set1_epi16(0);

    asm volatile ("nop;nop;nop;nop;nop;nop;nop;nop;nop;");

    xxxx = _mm256_set1_epi8(~1);

    asm volatile ("nop;nop;nop;nop;nop;nop;nop;nop;nop;");

    /* Recherches des chaînes de moins de 8 caractères */

    printf(" --- manager->count_8: %zu\n", manager->count_8);

    ret = 0;

    for (k = 0; k < manager->count_8; k++)
    {
        memcpy(&group, manager->strings_8[k], sizeof(grouped_strings_avx2_t));

        //printf(" --- group.used: %zu\n", group.used);


        asm volatile
        (
            /*
             * R = _mm256_set1_epi8(~1);
             *
             */

            "movabs         $0xfefefefefefefefe, %%rax ; "
            "vpbroadcastq   %%rax, %[STATE] ; "

            /*
             *
             */

            "vmovdqa %[FOUND_SRC], %[FOUND_DST] ; "

            : [STATE] "=v"(R),
              [FOUND_DST] "=v"(found_masks)
            : [FOUND_SRC] "m"(group.found_masks)
            : "memory", "rax"

         );




        //pre_shift_mask = _mm256_set1_epi8(0xef);

        maxiter = data + dlen;



        for (iter = data; (iter + 10) < maxiter; iter += 10)
        {

            //printf("--- %llx <-> %c\n", (unsigned long long)(iter - data), *iter);


            asm volatile
            (
#if 0

                /*
                 * R = _mm256_or_si256(R, group.pattern_masks[data[i]]);
                 *
                 * Latency : 1-9
                 * Throughput : 0.5
                 * #Uops : 1-2
                 * Port Usage : 1*p015+1*p23
                 *
                 */

                "vpor   %[PATTERN], %[STATE], %[STATE] ; "

#else

                /*
                 * %ymm = group.pattern_masks[data[i]];
                 *
                 * Latency : 5-8
                 * Throughput : 0.5
                 * #Uops : 1
                 * Port Usage : 1*p23
                 *
                 */

                "vmovdqa    %[PATTERN0], %%ymm0 ; "
                "vmovdqa    %[PATTERN1], %%ymm1 ; "
                "vmovdqa    %[PATTERN2], %%ymm2 ; "
                "vmovdqa    %[PATTERN3], %%ymm3 ; "
                "vmovdqa    %[PATTERN4], %%ymm4 ; "
                "vmovdqa    %[PATTERN5], %%ymm5 ; "
                "vmovdqa    %[PATTERN6], %%ymm6 ; "
                "vmovdqa    %[PATTERN7], %%ymm7 ; "
                "vmovdqa    %[PATTERN7], %%ymm8 ; "
                "vmovdqa    %[PATTERN7], %%ymm9 ; "

                /*
                 * R = _mm256_or_si256(R, %ymm);
                 *
                 * Latency : 1
                 * Throughput : 0.33
                 * #Uops : 1
                 * Port Usage : 1*p015
                 *
                 */

                "vpor   %%ymm0, %[STATE], %[STATE] ; "

#endif

                /*
                 * R = _mm256_add_epi8(R, R);
                 *
                 * Latency : 1
                 * Throughput : 0.3
                 * #Uops : 1
                 * Port Usage : 1*p015
                 *
                 */

                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                /*
                 * test = _mm256_and_si256(R, group.found_masks);
                 *
                 * Latency : 1
                 * Throughput : 0.33
                 * #Uops : 1
                 * Port Usage : 1*p015
                 *
                 */

                "vpand  %[FOUND], %[STATE], %%ymm0 ; "

                /* Déroulemets... */

                "vpor   %%ymm1, %[STATE], %[STATE] ; "
                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                "vpor   %%ymm2, %[STATE], %[STATE] ; "
                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                "vpor   %%ymm3, %[STATE], %[STATE] ; "
                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                "vpor   %%ymm4, %[STATE], %[STATE] ; "
                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                "vpor   %%ymm5, %[STATE], %[STATE] ; "
                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                "vpor   %%ymm6, %[STATE], %[STATE] ; "
                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                "vpor   %%ymm7, %[STATE], %[STATE] ; "
                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                "vpor   %%ymm8, %[STATE], %[STATE] ; "
                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                "vpor   %%ymm9, %[STATE], %[STATE] ; "
                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                "vpand  %[FOUND], %[STATE], %%ymm1 ; "
                "vpand  %[FOUND], %[STATE], %%ymm2 ; "
                "vpand  %[FOUND], %[STATE], %%ymm3 ; "
                "vpand  %[FOUND], %[STATE], %%ymm4 ; "
                "vpand  %[FOUND], %[STATE], %%ymm5 ; "
                "vpand  %[FOUND], %[STATE], %%ymm6 ; "
                "vpand  %[FOUND], %[STATE], %%ymm7 ; "
                "vpand  %[FOUND], %[STATE], %%ymm8 ; "
                "vpand  %[FOUND], %[STATE], %%ymm9 ; "





                /*
                 * status = _mm256_cmpeq_epi8(test, zero);
                 *
                 * Latency : 1
                 * Throughput : 0.5
                 * #Uops : 1
                 * Port Usage : 1*p01
                 *
                 */

                "vpcmpeqb   %%ymm0, %[NUL], %%ymm0 ; "

                /*
                 * mask = _mm256_movemask_epi8(status);
                 *
                 * Latency : <5
                 * Throughput : 1
                 * #Uops : 1
                 * Port Usage : 1*p0
                 *
                 */

                "vpmovmskb  %%ymm0, %[MASK0] ; "





                "vpcmpeqb   %%ymm1, %[NUL], %%ymm1 ; "
                "vpcmpeqb   %%ymm2, %[NUL], %%ymm2 ; "
                "vpcmpeqb   %%ymm3, %[NUL], %%ymm3 ; "
                "vpcmpeqb   %%ymm4, %[NUL], %%ymm4 ; "
                "vpcmpeqb   %%ymm5, %[NUL], %%ymm5 ; "
                "vpcmpeqb   %%ymm6, %[NUL], %%ymm6 ; "
                "vpcmpeqb   %%ymm7, %[NUL], %%ymm7 ; "
                "vpcmpeqb   %%ymm8, %[NUL], %%ymm8 ; "
                "vpcmpeqb   %%ymm9, %[NUL], %%ymm9 ; "


                "vpmovmskb  %%ymm1, %[MASK1] ; "
                "vpmovmskb  %%ymm2, %[MASK2] ; "
                "vpmovmskb  %%ymm3, %[MASK3] ; "
                "vpmovmskb  %%ymm4, %[MASK4] ; "
                "vpmovmskb  %%ymm5, %[MASK5] ; "
                "vpmovmskb  %%ymm6, %[MASK6] ; "
                "vpmovmskb  %%ymm7, %[MASK7] ; "
                "vpmovmskb  %%ymm8, %[MASK8] ; "
                "vpmovmskb  %%ymm9, %[MASK9] ; "










                //"vmovdqa  %%ymm7, %[OUTPUT] ; "

                //"vmovdqa  %%ymm8, %[OUTPUT2] ; "

                : [STATE] "+v"(R),
                  [OUTPUT] "=v"(test),
                  [OUTPUT2] "=v"(test2),
                  [MASK0] "=r"(mask),
                  [MASK1] "=r"(mask),
                  [MASK2] "=r"(mask),
                  [MASK3] "=r"(mask),
                  [MASK4] "=r"(mask),
                  [MASK5] "=r"(mask),
                  [MASK6] "=r"(mask),
                  [MASK7] "=r"(mask),
                  [MASK8] "=r"(mask),
                  [MASK9] "=r"(mask),
                  [NUL] "+v"(zero)
                : [PATTERN0] "m"(group./*manager->strings_8[k]->*/pattern_masks[*iter]),
                  [PATTERN1] "m"(group./*manager->strings_8[k]->*/pattern_masks[*(iter + 1)]),
                  [PATTERN2] "m"(group./*manager->strings_8[k]->*/pattern_masks[*(iter + 2)]),
                  [PATTERN3] "m"(group./*manager->strings_8[k]->*/pattern_masks[*(iter + 3)]),
                  [PATTERN4] "m"(group./*manager->strings_8[k]->*/pattern_masks[*(iter + 4)]),
                  [PATTERN5] "m"(group./*manager->strings_8[k]->*/pattern_masks[*(iter + 5)]),
                  [PATTERN6] "m"(group./*manager->strings_8[k]->*/pattern_masks[*(iter + 6)]),
                  [PATTERN7] "m"(group./*manager->strings_8[k]->*/pattern_masks[*(iter + 7)]),
                  [PATTERN8] "m"(group./*manager->strings_8[k]->*/pattern_masks[*(iter + 8)]),
                  [PATTERN9] "m"(group./*manager->strings_8[k]->*/pattern_masks[*(iter + 9)]),
                  [FOUND] "v"(found_masks)
                : "memory", "ymm0", "ymm1", "ymm2", "ymm3", "ymm4", "ymm5", "ymm6", "ymm7", "ymm8", "ymm9"

             );


            /*
            printf("        test: %02hhx %02hhx %02hhx %02hhx   %02hhx %02hhx %02hhx %02hhx   ...   %02hhx %02hhx %02hhx %02hhx\n",
                   ((uint8_t *)&test)[0],
                   ((uint8_t *)&test)[1],
                   ((uint8_t *)&test)[2],
                   ((uint8_t *)&test)[3],
                   ((uint8_t *)&test)[4],
                   ((uint8_t *)&test)[5],
                   ((uint8_t *)&test)[6],
                   ((uint8_t *)&test)[7],
                   ((uint8_t *)&test)[16],
                   ((uint8_t *)&test)[17],
                   ((uint8_t *)&test)[18],
                   ((uint8_t *)&test)[19]);

            printf("       test2: %02hhx %02hhx %02hhx %02hhx   %02hhx %02hhx %02hhx %02hhx   ...   %02hhx %02hhx %02hhx %02hhx\n",
                   ((uint8_t *)&test2)[0],
                   ((uint8_t *)&test2)[1],
                   ((uint8_t *)&test2)[2],
                   ((uint8_t *)&test2)[3],
                   ((uint8_t *)&test2)[4],
                   ((uint8_t *)&test2)[5],
                   ((uint8_t *)&test2)[6],
                   ((uint8_t *)&test2)[7],
                   ((uint8_t *)&test2)[16],
                   ((uint8_t *)&test2)[17],
                   ((uint8_t *)&test2)[18],
                   ((uint8_t *)&test2)[19]);
            */

#if 0
            //printf(" > %c\n", data[i]);

            R = _mm256_or_si256(R, group.pattern_masks[*iter]);

            //printf("group pattern: %hhx\n", *((uint8_t *)&group.pattern_masks[data[i]]));

            //printf("R:             %hhx\n", *((uint8_t *)&R));

            //R = _mm256_and_si256(R, pre_shift_mask);

            //printf("R after and:   %hhx\n", *((uint8_t *)&R));

            R = _mm256_add_epi8(R, R);
            //R = _mm256_slli_si256(R, 1);

            //printf("R after shift: %hhx\n", *((uint8_t *)&R));

            test = _mm256_and_si256(R, group.found_masks);

#if 1
            status = _mm256_cmpeq_epi8(test, zero);

            mask = _mm256_movemask_epi8(status);
#else
            //mask = _mm256_movemask_epi8(test) ^ 0xffffffff;
            mask = _mm256_movemask_epi8(test);
#endif


#endif


            //printf("   mask : %x\n", mask);

            if (mask != 0)
                for (j = 0; j < group.used; j++)
                {
                    if ((mask & 0x1) == 1)
                    {
                        //assert((i + 1) >= group.m[j]);

                        g_scan_context_register_atom_match(context,
                                                           group.found_id[j],
                                                           (iter - data) + 1 - group.m[j]);

                    }

                    mask >>= 1;

                }

        }





#if 0
        for (; iter < maxiter; iter++)
        {

            //printf("--- %llx <-> %c\n", (unsigned long long)(iter - data), *iter);


            asm volatile
            (
                /*
                 * R = _mm256_or_si256(R, group.pattern_masks[data[i]]);
                 *
                 * Latency : 1
                 * Throughput : 0.33
                 * #Uops : 1
                 * Port Usage : 1*p015
                 *
                 */

                "vpor   %[PATTERN], %[STATE], %[STATE] ; "

                /*
                 * R = _mm256_add_epi8(R, R);
                 *
                 * Latency : 1
                 * Throughput : 0.3
                 * #Uops : 1
                 * Port Usage : 1*p015
                 *
                 */

                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                /*
                 * test = _mm256_and_si256(R, group.found_masks);
                 *
                 * Latency : 1
                 * Throughput : 0.33
                 * #Uops : 1
                 * Port Usage : 1*p015
                 *
                 */

                "vpand  %[FOUND], %[STATE], %%ymm7 ; "

                /*
                 * status = _mm256_cmpeq_epi8(test, zero);
                 *
                 * Latency : 1
                 * Throughput : 0.5
                 * #Uops : 1
                 * Port Usage : 1*p01
                 *
                 */

                "vpcmpeqb   %%ymm7, %[NUL], %%ymm8 ; "

                /*
                 * mask = _mm256_movemask_epi8(status);
                 *
                 * Latency : <5
                 * Throughput : 1
                 * #Uops : 1
                 * Port Usage : 1*p0
                 *
                 */

                "vpmovmskb  %%ymm8, %[MASK0] ; "


                //"vmovdqa  %%ymm7, %[OUTPUT] ; "

                //"vmovdqa  %%ymm8, %[OUTPUT2] ; "

                : [STATE] "+v"(R),
                  [OUTPUT] "=v"(test),
                  [OUTPUT2] "=v"(test2),
                  [MASK0] "=r"(mask),
                  [NUL] "+v"(zero)
                : [PATTERN] "m"(group./*manager->strings_8[k]->*/pattern_masks[*iter]),
                  [FOUND] "v"(found_masks)
                : "memory", "ymm7", "ymm8"

             );


            /*
            printf("        test: %02hhx %02hhx %02hhx %02hhx   %02hhx %02hhx %02hhx %02hhx   ...   %02hhx %02hhx %02hhx %02hhx\n",
                   ((uint8_t *)&test)[0],
                   ((uint8_t *)&test)[1],
                   ((uint8_t *)&test)[2],
                   ((uint8_t *)&test)[3],
                   ((uint8_t *)&test)[4],
                   ((uint8_t *)&test)[5],
                   ((uint8_t *)&test)[6],
                   ((uint8_t *)&test)[7],
                   ((uint8_t *)&test)[16],
                   ((uint8_t *)&test)[17],
                   ((uint8_t *)&test)[18],
                   ((uint8_t *)&test)[19]);

            printf("       test2: %02hhx %02hhx %02hhx %02hhx   %02hhx %02hhx %02hhx %02hhx   ...   %02hhx %02hhx %02hhx %02hhx\n",
                   ((uint8_t *)&test2)[0],
                   ((uint8_t *)&test2)[1],
                   ((uint8_t *)&test2)[2],
                   ((uint8_t *)&test2)[3],
                   ((uint8_t *)&test2)[4],
                   ((uint8_t *)&test2)[5],
                   ((uint8_t *)&test2)[6],
                   ((uint8_t *)&test2)[7],
                   ((uint8_t *)&test2)[16],
                   ((uint8_t *)&test2)[17],
                   ((uint8_t *)&test2)[18],
                   ((uint8_t *)&test2)[19]);
            */

#if 0
            //printf(" > %c\n", data[i]);

            R = _mm256_or_si256(R, group.pattern_masks[*iter]);

            //printf("group pattern: %hhx\n", *((uint8_t *)&group.pattern_masks[data[i]]));

            //printf("R:             %hhx\n", *((uint8_t *)&R));

            //R = _mm256_and_si256(R, pre_shift_mask);

            //printf("R after and:   %hhx\n", *((uint8_t *)&R));

            R = _mm256_add_epi8(R, R);
            //R = _mm256_slli_si256(R, 1);

            //printf("R after shift: %hhx\n", *((uint8_t *)&R));

            test = _mm256_and_si256(R, group.found_masks);

#if 1
            status = _mm256_cmpeq_epi8(test, zero);

            mask = _mm256_movemask_epi8(status);
#else
            //mask = _mm256_movemask_epi8(test) ^ 0xffffffff;
            mask = _mm256_movemask_epi8(test);
#endif


#endif


            //printf("   mask : %x\n", mask);

            if (mask != 0)
                for (j = 0; j < group.used; j++)
                {
                    if ((mask & 0x1) == 1)
                    {
                        //assert((i + 1) >= group.m[j]);

                        g_scan_context_register_atom_match(context,
                                                           group.found_id[j],
                                                           (iter - data) + 1 - group.m[j]);

                    }

                    mask >>= 1;

                }

        }

#endif


    }


}














#if 0


#if 0

/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = lieu d'enregistrement des résultats.               *
*                content = données binaires à analyser.                       *
*                                                                             *
*  Description : Parcours un contenu binaire à la recherche de motifs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void run_scan_avx2(const GBitapBackend *backend, GScanContext *context, GBinContent *content)
{
    const group_manager_avx2_t *manager;    /* Accès simplifié             */

    grouped_strings_avx2_t groups[10];           /* Copie pour accès locaux     */


    phys_t dlen;                            /* Quantité de données         */
    vmpa2t pos;                             /* Point de départ ciblé       */
    const bin_t *data;                      /* Données à analyser          */
    __m256i zero;                           /* Constante 0 sur 256 bits    */
    size_t k;                               /* Boucle de parcours #1       */

    grouped_strings_avx2_t group;          /* Copie pour accès locaux     */
    __m256i R;                              /* Résultats courants          */
    __m256i pre_shift_mask;                 /* Préparation de décalage     */
    phys_t i;                               /* Boucle de parcours #2       */
    __m256i test;                           /* Test de correspondances     */
    __m256i status;                         /* Statut d'une comparaison    */
    int mask;                               /* Masque d'accès rapide       */
    size_t j;                               /* Boucle de parcours #3       */

    uint32_t leaves;
    int ret;


    phys_t old_i;
    phys_t p;

    //return;

    /* Initialisations diverses */

    manager = &backend->manager_avx2;

    dlen = g_binary_content_compute_size(content);

    g_binary_content_compute_start_pos(content, &pos);
    data = g_binary_content_get_raw_access(content, &pos, dlen);

    zero = _mm256_set1_epi16(0);

    /* Recherches des chaînes de moins de 8 caractères */

    printf(" --- manager->count_8: %zu\n", manager->count_8);

    ret = 0;

    //for (k = 0; k < manager->count_8; k++)
    //    memcpy(&groups[k], manager->strings_8[k], sizeof(grouped_strings_avx2_t));


    for (i = 0; i < dlen; )
    {

        //printf(" --- %llx\n", (unsigned long long)i);

        p = i + 4096;

        if (p > dlen)
            p = dlen;

        old_i = i;

        printf("old_i: %llx\n", (unsigned long long)old_i);

        for (k = 0; k < manager->count_8; k++)
        {

            group = *manager->strings_8[k];

            R = group.R;

            for (i = old_i ; i < p; i++)
            {

                //group = &groups[k];

                //printf(" k: %zu  i: %llx\n", k, (unsigned long long)i);

                //R = group.R;//_mm256_set1_epi8(~1);

                R = _mm256_or_si256(R, group.pattern_masks[data[i]]);

                R = _mm256_add_epi8(R, R);

                test = _mm256_and_si256(R, group.found_masks);

#if 0
                status = _mm256_cmpeq_epi8(test, zero);

                mask = _mm256_movemask_epi8(status);
#else
                //mask = _mm256_movemask_epi8(test) ^ 0xffffffff;
                mask = _mm256_movemask_epi8(test);
#endif

                if (mask != 0xffffffff)
                {
                    leaves = group.leaves;

                    for (j = 0; j < group.used; j++)
                    {
                        if ((mask & 0x1) == 0)
                        {
                            if (leaves & 0x1) //group.leaves & (1u << j))
                                ;//define_full_match_avx2(backend, context, content, &group, j, i + 1);

                        }

                        mask >>= 1;

                        leaves >>= 1;

                    }

                }

                group.R = R;//_mm256_set1_epi8(~1);

                memcpy(manager->strings_8[k], &group, sizeof(grouped_strings_avx2_t));

            }


        }

    }

    printf("oh: %d\n", ret);


}


#else



/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = lieu d'enregistrement des résultats.               *
*                content = données binaires à analyser.                       *
*                                                                             *
*  Description : Parcours un contenu binaire à la recherche de motifs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void run_scan_avx2(const GBitapBackend *backend, GScanContext *context, GBinContent *content)
{
    const group_manager_avx2_t *manager;    /* Accès simplifié             */
    phys_t dlen;                            /* Quantité de données         */
    vmpa2t pos;                             /* Point de départ ciblé       */
    const bin_t *data;                      /* Données à analyser          */
    __m256i zero;                           /* Constante 0 sur 256 bits    */
    size_t k;                               /* Boucle de parcours #1       */
    grouped_strings_avx2_t group;           /* Copie pour accès locaux     */
    __m256i R;                              /* Résultats courants          */
    __m256i pre_shift_mask;                 /* Préparation de décalage     */
    phys_t i;                               /* Boucle de parcours #2       */
    __m256i test;                           /* Test de correspondances     */
    __m256i status;                         /* Statut d'une comparaison    */
    int mask;                               /* Masque d'accès rapide       */
    size_t j;                               /* Boucle de parcours #3       */

    uint32_t leaves;
    int ret;

    //return;

    /* Initialisations diverses */

    manager = &backend->manager_avx2;

    dlen = g_binary_content_compute_size(content);

    g_binary_content_compute_start_pos(content, &pos);
    data = g_binary_content_get_raw_access(content, &pos, dlen);

    zero = _mm256_set1_epi16(0);

    /* Recherches des chaînes de moins de 8 caractères */

    printf(" --- manager->count_8: %zu\n", manager->count_8);

    ret = 0;

    for (k = 0; k < manager->count_8; k++)
    {
        memcpy(&group, manager->strings_8[k], sizeof(grouped_strings_avx2_t));

        //printf(" --- group.used: %zu\n", group.used);

        R = _mm256_set1_epi8(~1);

        //pre_shift_mask = _mm256_set1_epi8(0xef);

        for (i = 0; i < dlen; ++i)
        {
            //printf(" > %c\n", data[i]);

            R = _mm256_or_si256(R, group.pattern_masks[data[i]]);

            //printf("group pattern: %hhx\n", *((uint8_t *)&group.pattern_masks[data[i]]));

            //printf("R:             %hhx\n", *((uint8_t *)&R));

            //R = _mm256_and_si256(R, pre_shift_mask);

            //printf("R after and:   %hhx\n", *((uint8_t *)&R));

            R = _mm256_add_epi8(R, R);
            //R = _mm256_slli_si256(R, 1);

            //printf("R after shift: %hhx\n", *((uint8_t *)&R));

            test = _mm256_and_si256(R, group.found_masks);

#if 0
            status = _mm256_cmpeq_epi8(test, zero);

            mask = _mm256_movemask_epi8(status);
#else
            //mask = _mm256_movemask_epi8(test) ^ 0xffffffff;
            mask = _mm256_movemask_epi8(test);
#endif

            if (mask != 0xffffffff)
            {
                leaves = group.leaves;

                for (j = 0; j < group.used; j++)
                {
                    if ((mask & 0x1) == 0)
                    {
                        //assert((i + 1) >= group.m[j]);

                        if (leaves & 0x1) //group.leaves & (1u << j))
                            define_full_match_avx2(backend, context, content, &group, j, i + 1);
                        //else
                        //{
                        //    ret++;
                            //printf("%x\n", (unsigned int)i + 1);
                        //}
                        //else
                            //  g_scan_context_register_sub_match(context, group.found_id[j], i + 1 - group.m[j]);

                    }

                    mask >>= 1;

                    leaves >>= 1;

                }

            }

        }

    }

    printf("oh: %d\n", ret);

    /* Recherches des chaînes de moins de 16 caractères */

    for (k = 0; k < manager->count_16; k++)
    {
        memcpy(&group, manager->strings_16[k], sizeof(grouped_strings_avx2_t));

        R = _mm256_set1_epi16(~1);

        for (i = 0; i < dlen; ++i)
        {
            R = _mm256_or_si256(R, group.pattern_masks[data[i]]);
            R = _mm256_slli_epi16(R, 1);

            test = _mm256_and_si256(R, group.found_masks);

            status = _mm256_cmpeq_epi16(test, zero);

            mask = _mm256_movemask_epi8(status);

            if (mask != 0)
                for (j = 0; j < group.used; j++)
                {
                    if (mask & 0x3)
                    {
                        assert((i + 1) >= group.m[j]);

                        if (group.leaves & (1llu << j))
                            define_full_match_avx2(backend, context, content, &group, j, i + 1);
                        else
                            ;//g_scan_context_register_sub_match(context, group.found_id[j], i + 1 - group.m[j]);

                    }

                    mask >>= 2;

                }

        }

    }

}

#endif



#endif

















#endif



/* ---------------------------------------------------------------------------------- */
/*                       OPTIMISATIONS POUR ARCHITECTURE AVX512                       */
/* ---------------------------------------------------------------------------------- */


/**
 * Cf. https://www.intel.com/content/www/us/en/docs/intrinsics-guide/index.html#techs=AVX_512
 *   - https://agner.org/optimize/
 *   - https://uops.info/table.html
 */

#ifdef HAVE_AVX512_F

/******************************************************************************
*                                                                             *
*  Paramètres  : strings = ensemble de groupes constitués. [OUT]              *
*                count   = nombre de groupes courant. [OUT]                   *
*                                                                             *
*  Description : Indique la valeur portée par une expression rationnelle.     *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void extend_grouped_strings_avx512(grouped_strings_avx512_t ***strings, size_t *count)
{
    grouped_strings_avx512_t *new;          /* Zone supplémentaire         */
    size_t i;                               /* Boucle de parcours          */

    /* Définition d'un nouvel élément vierge */

    new = aligned_alloc(0x1000, sizeof(grouped_strings_avx512_t));

    for (i = 0; i < 256; i++)
        new->pattern_masks[i] = _mm512_set1_epi8(~0);

    new->found_masks = _mm512_set1_epi8(~0);

    new->R = _mm512_set1_epi8(~1);

    for (i = 0; i < 64; i++)
    {
        new->m[i] = 0;

        new->found_id[i] = INVALID_PATTERN_ID;

    }

    new->available = 64;
    new->used = 0;

    /* Inscription */

    *strings = realloc(*strings, ++(*count) * sizeof(grouped_strings_avx512_t *));

    (*strings)[*count - 1] = new;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = contexte de l'analyse à mener.                     *
*                plain   = chaîne de caractères classique à intégrer.         *
*                plen    = taille de cette chaîne.                            *
*                                                                             *
*  Description : Inscrit dans le moteur une chaîne de caractères à rechercher.*
*                                                                             *
*  Retour      : Indice de résultats pour le motif.                           *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static patid_t enroll_plain_pattern_avx512(GBitapBackend *backend, GScanContext *context, const bin_t *plain, size_t plen)
{
    patid_t result;                         /* Identifiant à retourner     */
    grouped_strings_avx512_t ***strings;    /* Groupe de chaînes visé      */
    size_t *count;                          /* Taille de ce groupe         */
    grouped_strings_avx512_t *last;         /* Dernier groupe à remplir    */
    size_t n;                               /* Indice dans le groupe       */
    size_t i;                               /* Boucle de parcours          */
    __m512i *letter;                        /* Lettre à marquer            */

    /* Sélection du groupe de travail adéquat */

    strings = &backend->manager_avx512.strings_8;
    count = &backend->manager_avx512.count_8;

    /* Préparation de la place nécessaire */

    if (*count == 0)
    {
        extend_grouped_strings_avx512(strings, count);

        last = (*strings)[0];

    }

    else
    {
        last = (*strings)[*count - 1];

        if (last->used == last->available)
        {
            extend_grouped_strings_avx512(strings, count);
            last = (*strings)[*count - 1];
        }

    }

    /* Intégration d'une nouvelle chaîne */

    n = last->used++;

    last->m[n] = plen;

    result = g_scan_context_get_new_pattern_id(context);

    last->found_id[n] = result;

    ((uint8_t *)&last->found_masks)[n] = (1 << plen);

    for (i = 0; i < plen; i++)
    {
        letter = last->pattern_masks + plain[i];
        ((uint8_t *)letter)[n] &= ~(1 << i);
    }

    return result;

}


/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = lieu d'enregistrement des résultats.               *
*                data    = données à analyser.                                *
*                dlen    = quantité de ces données.                           *
*                                                                             *
*  Description : Parcours un contenu binaire à la recherche de motifs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void run_scan_avx512(const GBitapBackend *backend, GScanContext *context, const bin_t *data, phys_t dlen)
{
    const group_manager_avx512_t *manager;  /* Accès simplifié             */

    //register __m512i zero asm("zmm19");                           /* Constante 0 sur 512 bits    */

    //__m512i shift8_mask;                    /* Masque pour décalage manuel */


    size_t k;                               /* Boucle de parcours #1       */
    /*__attribute__((aligned(0x1000)))*/ grouped_strings_avx512_t group;         /* Copie pour accès locaux     */
    //void *grpptr;
    //grouped_strings_avx512_t *_group;       /* Copie pour accès locaux     */

    int ret;


    register __m512i R asm("zmm28");                              /* Résultats courants          */
    register __m512i found_masks asm("zmm21"); /* Vérifications accélérées  */


    register __mmask64 test_mask asm("k6");


    register const bin_t *iter asm("rsi");
    register const bin_t *maxiter/* asm("rdi")*/;
    //phys_t i;                               /* Boucle de parcours #2       */


    //__m512i test;

    __mmask64 mask;                         /* Masque d'accès rapide       */
    size_t j;                               /* Boucle de parcours #3       */


    /* Initialisations diverses */

    manager = &backend->manager_avx512;




    /* Recherches des chaînes de moins de 8 caractères */

    //asm volatile ("nop; nop; nop; nop; nop; nop; nop; ");

    //zero = _mm512_set1_epi8(0);

    //asm volatile ("nop; nop; nop; nop; nop; nop; nop; ");

    //shift8_mask = _mm512_set1_epi8(0x7f);



#define WORK_ON_COPY

    for (k = 0; k < manager->count_8; k++)
    {
#ifdef WORK_ON_COPY
        memcpy(&group, manager->strings_8[k], sizeof(grouped_strings_avx512_t));

#else

        grpptr = alloca(sizeof(grouped_strings_avx512_t) + 0x1000);

        _group = grpptr + 0x1000 - (((unsigned long)grpptr) % 0x1000);

        //_group = manager->strings_8[k];

        memcpy(_group, manager->strings_8[k], sizeof(grouped_strings_avx512_t));

        ret = mlock(_group, sizeof(grouped_strings_avx512_t));

        printf("ret = %d\n", ret);
#endif



        //printf(" --- group %p  --  used: %zu (sz: %zu)\n", &group, group.used, sizeof(grouped_strings_avx512_t));
        //printf(" --- group.used: %zu (sz: %zu)\n", group.used, sizeof(grouped_strings_avx512_t));


        asm volatile
        (
            /*
             * R = _mm512_set1_epi8(~1);
             *
             */

            "movabs         $0xfefefefefefefefe, %%rax ; "
            "vpbroadcastq   %%rax, %[STATE] ; "

            "movabs         $0xffffffffffffffff, %%rax ; "
            "kmovq          %%rax, %[KMASK] ; "

            /*
             *
             */

            "vmovdqa64 %[FOUND_SRC], %[FOUND_DST] ; "

            : [STATE] "=v"(R),
              [KMASK] "=Yk"(test_mask),
              [FOUND_DST] "=v"(found_masks)
#ifdef WORK_ON_COPY
            : [FOUND_SRC] "m"(group.found_masks)
#else
            : [FOUND_SRC] "m"(_group->found_masks)
#endif
            : "memory", "rax"

         );







        //for (i = 0; i < dlen; i++)

        maxiter = data + dlen;

        for (iter = data; iter < maxiter; iter++)
        {

            //printf("--- %llx <-> %c\n", (unsigned long long)(iter - data), *iter);


            asm volatile goto
            (
                /*
                 * R = _mm512_or_si512(R, group.pattern_masks[*iter]);
                 *
                 * Latency : 1-9
                 * Throughput : 0.5
                 * #Uops : 1-2
                 * Port Usage : 1*p05+1*p23
                 *
                 */

                "vpord  %[PATTERN], %[STATE], %[STATE] ; "

                /*
                 * R = _mm512_add_epi8(R, R);
                 *
                 * Latency : 1
                 * Throughput : 0.5
                 * #Uops : 1
                 * Port Usage : 1*p05
                 *
                 */

                "vpaddb %[STATE], %[STATE], %[STATE] ; "

                /*
                 * mask = _mm512_test_epi8_mask(R, group.found_masks);
                 *
                 * Latency : 3
                 * Throughput : 1
                 * #Uops : 2
                 * Port Usage : 1*p23+1*p5
                 *
                 */

                /******************************
                 * Version 0

                ******************/

                //"vptestmb   %[FOUND], %[STATE], %%k7 ; "

                /******************************
                 * Version 1

                "vmovdqa64  %[STATE], %%zmm12 ; "

                "vptestmb   %[FOUND], %%zmm12, %%k7 ; "

                ******************/

                /******************************
                 * Version 2

                "vpandd     %[STATE], %[FOUND], %%zmm12 ; "

                "vpcmpneqb  %[NUL], %%zmm12, %%k7 ; "

                ******************/


                "vmovdqa64  %[STATE], %%zmm12 ; "

                "vptestmb   %[FOUND], %%zmm12, %%k7 ; "


                "ktestq %[KMASK], %%k7 ; "

                "jc %l[next_iter] ; "





                /*
                 * (suite)
                 *
                 * Latency : 3
                 * Throughput : 1
                 * #Uops : 1
                 * Port Usage : 1*p5
                 *
                 */

                "kmovq  %%k7, %[MASK0] ; "

                //"vmovdqa64  %%zmm12, %[OUTPUT] ; "

                //"nop; nop; nop; nop; nop; nop; nop; nop; "
                //"nop; nop; nop; nop; nop; nop; nop; nop; "

                : [STATE] "+v"(R),
                  //[OUTPUT] "=v"(test),
                  [MASK0] "=r"(mask)
                  //[NUL] "=v"(zero)
#ifdef WORK_ON_COPY
                : [PATTERN] "m"(group.pattern_masks[*iter]),
#else
                : [PATTERN] "m"(_group->pattern_masks[*iter]),
#endif
                  [FOUND] "v"(found_masks),
                  [KMASK] "Yk"(test_mask)
                : "memory", "k7", "zmm12"
                : next_iter

             );




            /*
            printf("  found mask: %hhx %hhx %hhx %hhx   %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&group.found_masks)[0],
                   ((uint8_t *)&group.found_masks)[1],
                   ((uint8_t *)&group.found_masks)[2],
                   ((uint8_t *)&group.found_masks)[3],
                   ((uint8_t *)&group.found_masks)[4],
                   ((uint8_t *)&group.found_masks)[5],
                   ((uint8_t *)&group.found_masks)[6],
                   ((uint8_t *)&group.found_masks)[7]);


            printf("        test: %hhx %hhx %hhx %hhx   %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&test)[0],
                   ((uint8_t *)&test)[1],
                   ((uint8_t *)&test)[2],
                   ((uint8_t *)&test)[3],
                   ((uint8_t *)&test)[4],
                   ((uint8_t *)&test)[5],
                   ((uint8_t *)&test)[6],
                   ((uint8_t *)&test)[7]);


            printf("  -> mask: 0x%llx\n", (unsigned long long)mask);
            */


#ifdef WORK_ON_COPY

            //if (mask != 0xffffffffffffffffllu)
                for (j = 0; j < group.used; j++)
                {
                    if ((mask & 0x1) == 0)
                    {
                        //assert((i + 1) >= group.m[j]);

                        g_scan_context_register_atom_match(context,
                                                           group.found_id[j],
                                                           (iter - data) + 1 - group.m[j]);

                    }

                    mask >>= 1;

                }

#else

#   error "WEFEF"

            if (mask != 0xffffffffffffffffllu)
                for (j = 0; j < _group->used; j++)
                {
                    if ((mask & 0x1) == 0)
                    {
                        //assert((i + 1) >= group.m[j]);

                        g_scan_context_register_atom_match(context,
                                                           _group->found_id[j],
                                                           (iter - data) + 1 - _group->m[j]);

                    }

                    mask >>= 1;

                }

#endif


            next_iter:

            //;

            //iter++;

        }

    }

}











#if 0











/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = lieu d'enregistrement des résultats.               *
*                content = données binaires à analyser.                       *
*                                                                             *
*  Description : Parcours un contenu binaire à la recherche de motifs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void run_scan_avx512____good_asm_perfs(const GBitapBackend *backend, GScanContext *context, GBinContent *content)
{
    const group_manager_avx512_t *manager;  /* Accès simplifié             */
    phys_t dlen;                            /* Quantité de données         */
    vmpa2t pos;                             /* Point de départ ciblé       */
    const bin_t *data;                      /* Données à analyser          */


    //__m512i shift8_mask;                    /* Masque pour décalage manuel */


    size_t k;                               /* Boucle de parcours #1       */
    grouped_strings_avx512_t group;         /* Copie pour accès locaux     */

    register __m512i found_masks asm("zmm21"); /* Vérifications accélérées  */


    //register volatile __m512i zero/* asm("zmm19")*/;                           /* Constante 0 sur 512 bits    */
    register __m512i R asm("zmm28");                              /* Résultats courants          */

    //int counter;

    const bin_t *iter;
    const bin_t *maxiter;
    //phys_t i;                               /* Boucle de parcours #2       */


    __m512i test;

    __mmask64 mask;                         /* Masque d'accès rapide       */
    size_t j;                               /* Boucle de parcours #3       */


    //register __m512i z30 asm("zmm30");


    //return;


    //counter = 0;

    //return;

    /* Initialisations diverses */

    manager = &backend->manager_avx512;

    dlen = g_binary_content_compute_size(content);

    g_binary_content_compute_start_pos(content, &pos);
    data = g_binary_content_get_raw_access(content, &pos, dlen);

    /* Recherches des chaînes de moins de 8 caractères */

    printf(" --- manager512->count_8: %zu\n", manager->count_8);

    asm volatile ("nop; nop; nop; nop; nop; nop; nop; ");

    //zero = _mm512_set1_epi8(0);

    asm volatile ("nop; nop; nop; nop; nop; nop; nop; ");

    //shift8_mask = _mm512_set1_epi8(0x7f);


    for (k = 0; k < manager->count_8; k++)
    {
        memcpy(&group, manager->strings_8[k], sizeof(grouped_strings_avx512_t));




        //printf(" --- group %p  --  used: %zu (sz: %zu)\n", &group, group.used, sizeof(grouped_strings_avx512_t));
        //printf(" --- group.used: %zu (sz: %zu)\n", group.used, sizeof(grouped_strings_avx512_t));


        asm volatile
        (
            /*
             * R = _mm512_set1_epi8(~1);
             *
             */

            "movabs         $0xfefefefefefefefe, %%rax ; "
            "vpbroadcastq   %%rax, %[STATE] ; "

            /*
             *
             */

            "vmovdqa64 %[FOUND_SRC], %[FOUND_DST] ; "

            : [STATE] "=v"(R),
              [FOUND_DST] "=v"(found_masks)
            : [FOUND_SRC] "m"(group.found_masks)
            : "memory", "rax"

         );







        //for (i = 0; i < dlen; i++)

        maxiter = data + dlen;

        for (iter = data; iter < maxiter; iter++)
        {

            //printf("--- %llx <-> %c\n", (unsigned long long)(iter - data), *iter);


            asm volatile
            (

                /*
                 * R = _mm512_or_si512(R, group.pattern_masks[*iter]);
                 *
                 * Latency : 1-9
                 * Throughput : 0.5
                 * #Uops : 1-2
                 * Port Usage : 1*p05+1*p23
                 *
                 */

                "vpord  %[PATTERN], %[STATE], %[STATE] ; "

                /*
                 * R = _mm512_add_epi8(R, R);
                 *
                 * Latency : 1
                 * Throughput : 0.5
                 * #Uops : 1
                 * Port Usage : 1*p05
                 *
                 */

                "vpaddb   %[STATE], %[STATE], %[STATE] ; "

                /*
                 * mask = _mm512_test_epi8_mask(R, group.found_masks);
                 *
                 * Latency : 3
                 * Throughput : 1
                 * #Uops : 2
                 * Port Usage : 1*p23+1*p5
                 *
                 */

                /******************************
                 * Version 0

                ******************/

                "vptestmb   %[FOUND], %[STATE], %%k7 ; "

                /******************************
                 * Version 1

                "vmovdqa64  %[STATE], %%zmm12 ; "

                "vptestmb   %[FOUND], %%zmm12, %%k0 ; "

                ******************/

                /******************************
                 * Version 2

                "vpandd     %[STATE], %[FOUND], %%zmm12 ; "

                "vpcmpneqb  %[NUL], %%zmm12, %%k7 ; "

                ******************/

                /*
                 * (suite)
                 *
                 * Latency : 3
                 * Throughput : 1
                 * #Uops : 1
                 * Port Usage : 1*p5
                 *
                 */

                "kmovq  %%k7, %[MASK0] ; "

                //"vmovdqa64  %%zmm12, %[OUTPUT] ; "

                //"nop; nop; nop; nop; nop; nop; nop; nop; "
                //"nop; nop; nop; nop; nop; nop; nop; nop; "

                : [STATE] "+v"(R),
                  [OUTPUT] "=v"(test),
                  [MASK0] "=r"(mask)/*,
                  [NUL] "+v"(zero)*/
                : [PATTERN] "v"(group.pattern_masks[*iter]),
                  [FOUND] "v"(found_masks)
                : "memory", "k0", "zmm12"

             );




            /*
            printf("  found mask: %hhx %hhx %hhx %hhx   %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&group.found_masks)[0],
                   ((uint8_t *)&group.found_masks)[1],
                   ((uint8_t *)&group.found_masks)[2],
                   ((uint8_t *)&group.found_masks)[3],
                   ((uint8_t *)&group.found_masks)[4],
                   ((uint8_t *)&group.found_masks)[5],
                   ((uint8_t *)&group.found_masks)[6],
                   ((uint8_t *)&group.found_masks)[7]);


            printf("        test: %hhx %hhx %hhx %hhx   %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&test)[0],
                   ((uint8_t *)&test)[1],
                   ((uint8_t *)&test)[2],
                   ((uint8_t *)&test)[3],
                   ((uint8_t *)&test)[4],
                   ((uint8_t *)&test)[5],
                   ((uint8_t *)&test)[6],
                   ((uint8_t *)&test)[7]);


            printf("  -> mask: 0x%llx\n", (unsigned long long)mask);
            */

#if 0

            /*
            printf("           R: %hhx %hhx %hhx %hhx   %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&R)[0],
                   ((uint8_t *)&R)[1],
                   ((uint8_t *)&R)[2],
                   ((uint8_t *)&R)[3],
                   ((uint8_t *)&R)[4],
                   ((uint8_t *)&R)[5],
                   ((uint8_t *)&R)[6],
                   ((uint8_t *)&R)[7]);

            printf("  found mask: %hhx %hhx %hhx %hhx   %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&group.found_masks)[0],
                   ((uint8_t *)&group.found_masks)[1],
                   ((uint8_t *)&group.found_masks)[2],
                   ((uint8_t *)&group.found_masks)[3],
                   ((uint8_t *)&group.found_masks)[4],
                   ((uint8_t *)&group.found_masks)[5],
                   ((uint8_t *)&group.found_masks)[6],
                   ((uint8_t *)&group.found_masks)[7]);
            */

            /*

            printf("        test: %hhx %hhx %hhx %hhx   %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&test)[0],
                   ((uint8_t *)&test)[1],
                   ((uint8_t *)&test)[2],
                   ((uint8_t *)&test)[3],
                   ((uint8_t *)&test)[4],
                   ((uint8_t *)&test)[5],
                   ((uint8_t *)&test)[6],
                   ((uint8_t *)&test)[7]);

            */

#endif





#   define TEST_MASK 0xffffffffffffffffllu
#   define TEST_BIT 0


            //printf("mask: %llx\n", (unsigned long long)mask);


            if (mask != TEST_MASK)
            {
                //printf("mask: %llx\n", (unsigned long long)mask);

                //counter++;
                //printf("Ouhc: %p - %x\n", &group, *((uint8_t *)&mask));
                //printf("Ouhc: %x\n", 1);
                //asm("vzeroupper;");
                //printf("Ouhc: %hhx\n", R[0]);
                for (j = 0; j < group.used; j++)
                {
                    if ((mask & 0x1) == TEST_BIT)
                    {
                        //assert((i + 1) >= group.m[j]);

                        //printf(">> FOUND %zu @ %x !!!!!!!!!!!!!!\n", j, (unsigned int)i + 1);
                        printf(">> FOUND %zu @ %x !!!!!!!!!!!!!!\n", j, (unsigned int)(iter - data) + 1);


                    }

                    mask >>= 1;
                    //printf("> mask: %llx\n", (unsigned long long)mask);

                }



            }



        }

        //printf("%hhx\n", ((uint8_t *)&R)[0], ((uint8_t *)&mask)[0]);

    }

    //printf("counter=%d\n", counter);


}




/******************************************************************************
*                                                                             *
*  Paramètres  : backend = moteur de recherche à manipuler.                   *
*                context = lieu d'enregistrement des résultats.               *
*                content = données binaires à analyser.                       *
*                                                                             *
*  Description : Parcours un contenu binaire à la recherche de motifs.        *
*                                                                             *
*  Retour      : -                                                            *
*                                                                             *
*  Remarques   : -                                                            *
*                                                                             *
******************************************************************************/

static void run_scan_avx512_best_test(const GBitapBackend *backend, GScanContext *context, GBinContent *content)
{
    const group_manager_avx512_t *manager;  /* Accès simplifié             */
    phys_t dlen;                            /* Quantité de données         */
    vmpa2t pos;                             /* Point de départ ciblé       */
    const bin_t *data;                      /* Données à analyser          */


    //__m512i shift8_mask;                    /* Masque pour décalage manuel */


    size_t k;                               /* Boucle de parcours #1       */
    grouped_strings_avx512_t group;         /* Copie pour accès locaux     */

    //register __m512i zero;                           /* Constante 0 sur 512 bits    */
    register __m512i R;                              /* Résultats courants          */

    //int counter;

    const bin_t *iter;
    const bin_t *maxiter;
    //phys_t i;                               /* Boucle de parcours #2       */


    //__m512i test;

    __mmask64 mask;                         /* Masque d'accès rapide       */
    size_t j;                               /* Boucle de parcours #3       */

    //return;


    //counter = 0;

    //return;

    /* Initialisations diverses */

    manager = &backend->manager_avx512;

    dlen = g_binary_content_compute_size(content);

    g_binary_content_compute_start_pos(content, &pos);
    data = g_binary_content_get_raw_access(content, &pos, dlen);

    /* Recherches des chaînes de moins de 8 caractères */

    printf(" --- manager512->count_8: %zu\n", manager->count_8);

    //zero = _mm512_set1_epi8(0);

    //shift8_mask = _mm512_set1_epi8(0x7f);



    for (k = 0; k < manager->count_8; k++)
    {
        memcpy(&group, manager->strings_8[k], sizeof(grouped_strings_avx512_t));

        //printf(" --- group %p  --  used: %zu (sz: %zu)\n", &group, group.used, sizeof(grouped_strings_avx512_t));
        //printf(" --- group.used: %zu (sz: %zu)\n", group.used, sizeof(grouped_strings_avx512_t));

        R = _mm512_set1_epi8(~1);



        /* vpord zmm, zmm, zmm : latence 1, 1*p05 */
        //R = _mm512_or_si512(R, group.pattern_masks[data[0]]);

        //for (i = 0; i < dlen; i++)

        maxiter = data + dlen;

        for (iter = data; iter < maxiter; iter++)
        {

            //printf("--- %llx <-> %c\n", (unsigned long long)(iter - data), *iter);


            //R = _mm512_or_si512(R, group.pattern_masks[data[i]]);
            R = _mm512_or_si512(R, group.pattern_masks[*iter]);


#if 1
            /* vpaddb zmm, zmm, zmm : latence 1, 1*p05 */
            R = _mm512_add_epi8(R, R);
#else
            /* vpandd zmm, zmm, zmm : latence 1, 1*p5 */
            R = _mm512_and_si512(R, shift8_mask);
            /* vpslldq zmm, zmm, imm8 : latence 1, 1*p5 */
            R = _mm512_bslli_epi128(R, 1);

#endif

            /*
            printf("           R: %hhx %hhx %hhx %hhx   %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&R)[0],
                   ((uint8_t *)&R)[1],
                   ((uint8_t *)&R)[2],
                   ((uint8_t *)&R)[3],
                   ((uint8_t *)&R)[4],
                   ((uint8_t *)&R)[5],
                   ((uint8_t *)&R)[6],
                   ((uint8_t *)&R)[7]);

            printf("  found mask: %hhx %hhx %hhx %hhx   %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&group.found_masks)[0],
                   ((uint8_t *)&group.found_masks)[1],
                   ((uint8_t *)&group.found_masks)[2],
                   ((uint8_t *)&group.found_masks)[3],
                   ((uint8_t *)&group.found_masks)[4],
                   ((uint8_t *)&group.found_masks)[5],
                   ((uint8_t *)&group.found_masks)[6],
                   ((uint8_t *)&group.found_masks)[7]);
            */

#if 1
            /* vptestmb k, zmm, zmm : latence 3, 1*p5 */
            mask = _mm512_test_epi8_mask(R, group.found_masks);


            //test = _mm512_add_epi64(R, zero);

            //mask = _mm512_test_epi8_mask(test, group.found_masks);





#   define TEST_MASK 0xffffffffffffffffllu
#   define TEST_BIT 0

            /* comparaison : != */


#else
            /* vpandd zmm, zmm, zmm : latence 1, 1*p05 */
            test = _mm512_and_si512(R, group.found_masks);


            printf("        test: %hhx %hhx %hhx %hhx   %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&test)[0],
                   ((uint8_t *)&test)[1],
                   ((uint8_t *)&test)[2],
                   ((uint8_t *)&test)[3],
                   ((uint8_t *)&test)[4],
                   ((uint8_t *)&test)[5],
                   ((uint8_t *)&test)[6],
                   ((uint8_t *)&test)[7]);

            /* vpmovb2m k, zmm : latence 3 (au lieu de 1 !?), 1*p0 */
            //mask = _mm512_movepi8_mask(test);

#   define TEST_MASK 0
#   define TEST_BIT 0


            //test = _mm512_popcnt_epi8(test);

#endif


            //printf("  final mask: %16llx\n", (unsigned long long)mask);



            //R = _mm512_or_si512(R, group.pattern_masks[data[i + 1]]);

#if 1


            if (mask != TEST_MASK)
            {
                //counter++;
                //printf("Ouhc: %p - %x\n", &group, *((uint8_t *)&mask));
                printf("Ouhc: %p\n", &group);
                //printf("Ouhc: %hhx\n", R[0]);
                for (j = 0; j < group.used; j++)
                {
                    if ((mask & 0x1) == TEST_BIT)
                    {
                        //assert((i + 1) >= group.m[j]);

                        //printf(">> FOUND %zu @ %x !!!!!!!!!!!!!!\n", j, (unsigned int)i + 1);
                        printf(">> FOUND %zu @ %x !!!!!!!!!!!!!!\n", j, (unsigned int)(iter - data) + 1);


                    }

                    mask >>= 1;

                }



            }


#else

            if (_mm512_reduce_or_epi64(test) != 0)
            {
                for (j = 0; j < group.used; j++)
                {
                    if (((uint8_t *)&test)[j] == 0)
                    {
                        //assert((i + 1) >= group.m[j]);

                        printf(">> FOUND %zu @ %x !!!!!!!!!!!!!!\n", j, (unsigned int)i + 1);

                    }


                }

            }

#endif


        }

        //printf("%hhx\n", ((uint8_t *)&R)[0], ((uint8_t *)&mask)[0]);

    }

    //printf("counter=%d\n", counter);


}





static void run_scan_avx512__saved(const GBitapBackend *backend, GScanContext *context, GBinContent *content)
{
    const group_manager_avx512_t *manager;  /* Accès simplifié             */
    phys_t dlen;                            /* Quantité de données         */
    vmpa2t pos;                             /* Point de départ ciblé       */
    const bin_t *data;                      /* Données à analyser          */


    __m512i shift8_mask;                    /* Masque pour décalage manuel */


    size_t k;                               /* Boucle de parcours #1       */
    grouped_strings_avx512_t group;         /* Copie pour accès locaux     */


    __m512i R;                              /* Résultats courants          */

    //int counter;

    phys_t i;                               /* Boucle de parcours #2       */


    __m512i test;

    __mmask64 mask;                         /* Masque d'accès rapide       */
    size_t j;                               /* Boucle de parcours #3       */



    //counter = 0;

    //return;

    /* Initialisations diverses */

    manager = &backend->manager_avx512;

    dlen = g_binary_content_compute_size(content);

    g_binary_content_compute_start_pos(content, &pos);
    data = g_binary_content_get_raw_access(content, &pos, dlen);

    /* Recherches des chaînes de moins de 8 caractères */

    printf(" --- manager512->count_8: %zu\n", manager->count_8);



    shift8_mask = _mm512_set1_epi8(0x7f);


    for (k = 0; k < manager->count_8; k++)
    {
        memcpy(&group, manager->strings_8[k], sizeof(grouped_strings_avx512_t));

        //printf(" --- group %p  --  used: %zu (sz: %zu)\n", &group, group.used, sizeof(grouped_strings_avx512_t));
        //printf(" --- group.used: %zu (sz: %zu)\n", group.used, sizeof(grouped_strings_avx512_t));

        R = _mm512_set1_epi8(~1);

        /* vpord zmm, zmm, zmm : latence 1, 1*p05 */
        R = _mm512_or_si512(R, group.pattern_masks[data[0]]);

        for (i = 0; i < dlen; i++)
        {

            /*
            printf("--- %llx <-> %c\n", (unsigned long long)i, data[i]);

            printf("  R: %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&R)[0],
                   ((uint8_t *)&R)[1],
                   ((uint8_t *)&R)[2],
                   ((uint8_t *)&R)[3]);

            printf("  mask: %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&group.pattern_masks[data[i]])[0],
                   ((uint8_t *)&group.pattern_masks[data[i]])[1],
                   ((uint8_t *)&group.pattern_masks[data[i]])[2],
                   ((uint8_t *)&group.pattern_masks[data[i]])[3]);
            */

            //R = _mm512_or_si512(R, group.pattern_masks[data[i]]);

            /*
            printf("  R: %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&R)[0],
                   ((uint8_t *)&R)[1],
                   ((uint8_t *)&R)[2],
                   ((uint8_t *)&R)[3]);
            */

#if 1
            /* vpaddb zmm, zmm, zmm : latence 1, 1*p05 */
            R = _mm512_add_epi8(R, R);
#else
            /* vpandd zmm, zmm, zmm : latence 1, 1*p5 */
            R = _mm512_and_si512(R, shift8_mask);
            /* vpslldq zmm, zmm, imm8 : latence 1, 1*p5 */
            R = _mm512_bslli_epi128(R, 1);

#endif

#if 1
            /* vptestmb k, zmm, zmm : latence 3, 1*p5 */
            mask = _mm512_test_epi8_mask(R, group.found_masks);
#else
            test = _mm512_and_si512(R, group.found_masks);
            test = _mm512_popcnt_epi8(test);

#endif

            /*
            printf("  found mask: %hhx %hhx %hhx %hhx\n",
                   ((uint8_t *)&group.found_masks)[0],
                   ((uint8_t *)&group.found_masks)[1],
                   ((uint8_t *)&group.found_masks)[2],
                   ((uint8_t *)&group.found_masks)[3]);

            printf("  final mask: %16llx\n", (unsigned long long)mask);
            */


            R = _mm512_or_si512(R, group.pattern_masks[data[i + 1]]);

#if 1

            if (mask != 0xffffffffffffffffllu)
            {
                //counter++;
                //printf("Ouhc: %p - %x\n", &group, *((uint8_t *)&mask));
                //printf("Ouhc: %p\n", &group);
                for (j = 0; j < group.used; j++)
                {
                    if ((mask & 0x1) == 0)
                    {
                        //assert((i + 1) >= group.m[j]);

                        printf(">> FOUND %zu @ %x !!!!!!!!!!!!!!\n", j, (unsigned int)i + 1);


                    }

                    mask >>= 1;

                }



            }


#else

            if (_mm512_reduce_or_epi64(test) != 0)
            {
                for (j = 0; j < group.used; j++)
                {
                    if (((uint8_t *)&test)[j] == 0)
                    {
                        //assert((i + 1) >= group.m[j]);

                        printf(">> FOUND %zu @ %x !!!!!!!!!!!!!!\n", j, (unsigned int)i + 1);

                    }


                }

            }

#endif


        }

        //printf("%hhx\n", ((uint8_t *)&R)[0], ((uint8_t *)&mask)[0]);

    }

    //printf("counter=%d\n", counter);


}
#endif



#endif
