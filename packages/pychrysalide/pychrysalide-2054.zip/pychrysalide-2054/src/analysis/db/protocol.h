
/* Chrysalide - Outil d'analyse de fichiers binaires
 * protocol.h - prototypes pour la description du protocole impactant les BD Chrysalide
 *
 * Copyright (C) 2014-2019 Cyrille Bagard
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


#ifndef _ANALYSIS_DB_PROTOCOL_H
#define _ANALYSIS_DB_PROTOCOL_H



/**
 * Version de la définition courante du protocole.
 */
#define CDB_PROTOCOL_VERSION 0xc0de0005

/**
 * 0xc0de0005 :
 *   - création des rôles d'aministrateur et d'analyste
 */



/**
 * Délai maximal de réaction pour les coupures de flux (en ms).
 */
#define CDB_CONN_TIMEOUT 1000











/* Rôle à envoyer lors des présentations */
typedef enum _ClientRole
{
    CRL_UNDEFINED = 0,                      /* Rôle non défini             */
    CRL_ADMIN     = 1,                      /* Rôle d'administrateur       */
    CRL_ANALYST   = 2,                      /* Rôle d'analyste             */

} ClientRole;

/* Niveaux de privilèges */
typedef enum _ServerPrivLevels
{
    SPV_UNDEFINED     = 0,                  /* Rôle non défini             */
    SPV_ADMINISTRATOR = 1,                  /* Pleins pouvoirs             */
    SPV_MANAGER       = 2,                  /* Gestionnaire de comptes     */
    SPV_CREATOR       = 3,                  /* Gestionnaire d'analyses     */
    SPV_ANALYST       = 4,                  /* Analyste de binaires        */

} ServerPrivLevels;




/**
 * Précisions pour la commande DBC_LOADING_STATUS.
 */


/* Eléments de base nécessaires */
typedef enum _LoadingStatusHint
{
    LSH_READY        = 0,                   /* (Plus) rien n'est requis    */
    LSH_ON_WAIT_LIST = 1,                   /* Concurrence des connexions  */
    LSH_NEED_CONTENT = 2,                   /* Suppléments nécessaires     */
    LSH_NEED_FORMAT  = 3,                   /* Suppléments nécessaires     */
    LSH_NEED_ARCH    = 4,                   /* Suppléments nécessaires     */

} LoadingStatusHint;






/**
 * Une fois la connexion établie, les paquets ont tous la forme suivante :
 *
 *    [ type de collection visée ; cf. DBFeatures ]
 *    [ action à mener ; cf. DBAction             ]
 *    [ élément de type GDbItem sérialisé...      ]
 *
 */

/* Fonctionnalités offertes nativement */
typedef enum _DBFeatures
{
    DBF_BOOKMARKS,                          /* Signets dans le code        */
    DBF_COMMENTS,                           /* Commentaires ajoutés        */
    DBF_MOVES,                              /* Déplacements dans du code   */
    DBF_DISPLAY_SWITCHERS,                  /* Choix d'affichage           */

    DBF_COUNT

} DBFeatures;

/* Interactions disponibles vis à vis d'une collection. */
typedef enum _DBAction
{
    DBA_ADD_ITEM,                           /* Ajout d'un élément          */
    DBA_REM_ITEM,                           /* Suppression d'un élément    */
    DBA_CHANGE_STATE,                       /* Changement d'activité       */

    DBA_COUNT

} DBAction;



/* Marqueur de fin pour une transmission d'identifiants */
#define SNAPSHOT_END_MARK "eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee"




/**
 * Commandes envoyées d'un côté à un autre.
 */
typedef enum _DBCommand
{
    /* ------------------------- Commandes à portée générale ------------------------- */

    /**
     * Le client envoie un tout premier paquet de la forme suivante :
     *
     *    [ Ordre de sauvegarde : DBC_HELO            ]
     *    [ Protocole supporté : CDB_PROTOCOL_VERSION ]
     *    [ Rôle visé ; cf ClientRole                 ]
     *    [ Compléments selon le rôle visé            ]
     *
     * Le serveur effectue les validations et renvoie un bilan :
     *
     *    [ Ordre de sauvegarde : DBC_WELCOME         ]
     *    [ Statut d'exécution ; cf. DBError          ]
     *
     */

    DBC_HELO,                               /* Connexion initiale C -> S   */
    DBC_WELCOME,                            /* Réponse initiale S -> C     */


    /* ------------------------ Commandes pour administrateur ------------------------ */

    /**
     * Le client envoie une requête pour lister les binaires de la forme suivante :
     *
     *    [ Demande de liste : DBC_LIST_BINARIES      ]
     *
     * Le serveur liste tous les répertoires présents et renvoie cette liste :
     *
     *    [ Marqueur de liste : DBC_EXISTING_BINARIES ]
     *    [ Quantité d'éléments en ULEB128            ]
     *    [ Noms en chaîne RLE...                     ]
     *
     */

    DBC_LIST_BINARIES,                      /* Fourniture des identifiants */
    DBC_EXISTING_BINARIES,                  /* Eléments présents           */


    /* ------------------------ Commandes pour analyste ------------------------ */

    /**
     * Gestion de la commande 'DBC_LOADING_STATUS'.
     *
     * Le serveur envoie un statut de prise en charge au début d'une connexion :
     *
     *    [ Indication du serveur : DBC_LOADING_STATUS]
     *    [ Statut courant ; cf. LoadingStatusHint    ]
     *
     */

    DBC_LOADING_STATUS,                     /* Indications initiales       */

    /**
     * Gestion de la commande 'DBC_SET_CONTENT'.
     *
     * Le client connecté envoie un paquet de la forme suivante :
     *
     *    [ Ordre de sauvegarde : DBC_SET_CONTENT     ]
     *    [ Quantité des données suivantes            ]
     *    [ Position du contenu + données de stockage ]
     *
     * Le serveur s'exécute et renvoie un bilan :
     *
     *    [ Ordre de sauvegarde : DBC_SET_CONTENT     ]
     *    [ Statut d'exécution ; cf. DBError          ]
     *
     */

    DBC_SET_CONTENT,














    /**
     * Gestion de la commande 'DBC_SAVE'.
     *
     * Le client connecté envoie un paquet de la forme suivante :
     *
     *    [ Ordre de sauvegarde : DBC_SAVE            ]
     *
     * Le serveur s'exécute et renvoie un bilan :
     *
     *    [ Ordre de sauvegarde : DBC_SAVE            ]
     *    [ Statut d'exécution ; cf. DBError          ]
     *
     */

    DBC_SAVE,                               /* Enregistrement de l'archive */

    DBC_COLLECTION,                         /* Implication d'une collection*/

    /**
     * Gestion de la commande 'DBC_[GS]ET_ALL_ITEMS'.
     *
     * Un client qui se connecte à un serveur doit en premier lieu envoyer :
     *
     *    [ Demande de mise à jour : DBC_GET_ALL_ITEMS  ]
     *
     * Tant qu'il ne reçoit pas la commande DBC_SET_ALL_ITEMS depuis le
     * serveur, toutes les actions sur une collection sont à rejeter car elles
     * lui seront retransmises plus tard.
     *
     * De son côté, le serveur répond par une requête :
     *
     *    [ Notification de maj : DBC_SET_ALL_ITEMS     ]
     *    [ marqueur de démarrage : octet 0x1           ]
     *
     * Dans la foulée, il enverra ensuite les éléments avec des paquets classiques :
     *
     *    [ Traitement de collection : DBC_COLLECTION   ]
     *    [ Action : DBA_ADD_ITEM                       ]
     *    ...
     *
     * La séquence se termine par une requête finale :
     *
     *    [ Notification de maj : DBC_SET_ALL_ITEMS     ]
     *    [ marqueur de fin : octet 0x0                 ]
     *
     */

    DBC_GET_ALL_ITEMS,                      /* Mise à jour à la connexion  */
    DBC_SET_ALL_ITEMS,                      /* Mise à jour à la connexion  */

    /**
     * Gestion de la commande 'DBC_SET_LAST_ACTIVE'.
     *
     * Le client connecté envoie un paquet de la forme suivante :
     *
     *    [ Statut d'historique : DBC_SET_LAST_ACTIVE   ]
     *    [ <horodatage du dernier élément actif>       ]
     *
     * Le serveur s'exécute et notifie le client d'éventuels changements,
     * avec une série de paquets de la forme :
     *
     *    [ Traitement de collection : DBC_COLLECTION   ]
     *    [ Action : DBA_CHANGE_STATE                   ]
     *    [ <élément dont le statut a évolué>           ]
     *
     */

    DBC_SET_LAST_ACTIVE,                    /* Définition du dernier actif */   // REMME

    /* ------- Gestion des instantanés ------- */

    /**
     * Gestion de la commande 'DBC_GET_SNAPSHOTS'.
     *
     * Le client connecté envoie un paquet de la forme suivante :
     *
     *    [ Gestion d'instantané : DBC_GET_SNAPSHOTS            ]
     *
     */

    DBC_GET_SNAPSHOTS,

    /**
     * Gestion de la commande 'DBC_SNAPSHOTS_UPDATED'.
     *
     * Le serveur envoie au client un paquet de la forme suivante :
     *
     *    [ Gestion d'instantané : DBC_SNAPSHOTS_UPDATED        ]
     *    [ <liste de descriptions d'instantanés>               ]
     *    [ Marqueur de fin : SNAPSHOT_END_MARK                 ]
     *
     */

    DBC_SNAPSHOTS_UPDATED,                  /* Identification d'instantanés*/

    /**
     * Gestion de la commande 'DBC_GET_CUR_SNAPSHOT'.
     *
     * Le client connecté envoie un paquet de la forme suivante :
     *
     *    [ Gestion d'instantané : DBC_GET_CUR_SNAPSHOT         ]
     *
     */

    DBC_GET_CUR_SNAPSHOT,                   /* Demande d'identification    */

    /**
     * Gestion de la commande 'DBC_CUR_SNAPSHOT_UPDATED'.
     *
     * Le serveur envoie au client un paquet de la forme suivante :
     *
     *    [ Gestion d'instantané : DBC_CUR_SNAPSHOT_UPDATED     ]
     *    [ <identifiant d'instantané>                          ]
     *
     */

    DBC_CUR_SNAPSHOT_UPDATED,               /* Mise à jour de l'instantané */

    /**
     * Gestion de la commande 'DBC_SET_CUR_SNAPSHOT'.
     *
     * Le client connecté envoie un paquet de la forme suivante :
     *
     *    [ Gestion d'instantané : DBC_SET_CUR_SNAPSHOT         ]
     *    [ <identifiant d'instantané>                          ]
     *
     */

    DBC_SET_CUR_SNAPSHOT,                   /* Définition de l'instantané  */

    /**
     * Gestion de la commande 'DBC_SET_SNAPSHOT_NAME'.
     *
     * Le client connecté envoie un paquet de la forme suivante :
     *
     *    [ Gestion d'instantané : DBC_SET_SNAPSHOT_NAME        ]
     *    [ <identifiant d'instantané>                          ]
     *    [ <chaîne de caractères>                              ]
     *
     * Le serveur renvoie ensuite automatiquement un paquet
     * de type 'DBC_SNAPSHOTS_UPDATED'.
     */

    DBC_SET_SNAPSHOT_NAME,                  /* Désignation de l'instantané */

    /**
     * Gestion de la commande 'DBC_SET_SNAPSHOT_DESC'.
     *
     * Le client connecté envoie un paquet de la forme suivante :
     *
     *    [ Gestion d'instantané : DBC_SET_SNAPSHOT_DESC        ]
     *    [ <identifiant d'instantané>                          ]
     *    [ <chaîne de caractères>                              ]
     *
     * Le serveur renvoie ensuite automatiquement un paquet
     * de type 'DBC_SNAPSHOTS_UPDATED'.
     */

    DBC_SET_SNAPSHOT_DESC,                  /* Description de l'instantané */

    /**
     * Gestion de la commande 'DBC_CREATE_SNAPSHOT'.
     *
     * Le client connecté envoie un paquet de la forme suivante :
     *
     *    [ Gestion d'instantané : DBC_CREATE_SNAPSHOT          ]
     *
     * Le serveur renvoie ensuite automatiquement un paquet
     * de type 'DBC_SNAPSHOTS_UPDATED'.
     */

    DBC_CREATE_SNAPSHOT,                    /* Création d'instantané       */

    /**
     * Gestion de la commande 'DBC_REMOVE_SNAPSHOT'.
     *
     * Le client connecté envoie un paquet de la forme suivante :
     *
     *    [ Gestion d'instantané : DBC_REMOVE_SNAPSHOT          ]
     *    [ <identifiant d'instantané>                          ]
     *    [ indicateur de récursivité : octet 0x1 ou 0x0        ]
     *
     * Le serveur renvoie ensuite automatiquement un paquet
     * de type 'DBC_SNAPSHOTS_UPDATED'.
     */

    DBC_REMOVE_SNAPSHOT,                    /* Suppression d'instantané    */

    DBC_COUNT

} DBCommand;







/**
 * Erreurs pouvant survenir...
 */
typedef enum _DBError
{
    DBE_NONE,                               /* Succès d'une opération      */
    DBE_BAD_EXCHANGE,                       /* Incohérence des échanges    */

    DBE_WRONG_VERSION,                      /* Proto Client != Serveur     */
    DBE_SYS_ERROR,                          /* Erreur suite à un appel sys.*/
    DBE_ARCHIVE_ERROR,                      /* Soucis du côté libarchive   */
    DBE_XML_VERSION_ERROR,                  /* Vieille archive présente    */
    DBE_DB_LOADING_ERROR,                   /* Erreur pendant le chargement*/

    DBE_WRONG_HASH,                         /* Empreinte inattendue        */
    DBE_XML_ERROR,                          /* Erreur lors d'une définition*/
    DBE_SNAPSHOT_NOT_FOUND,                 /* Instantané non trouvé       */
    DBE_SNAPSHOT_RESTORE_FAILURE,           /* Echec d'une restauration    */
    DBE_SNAPSHOT_ROOT_REMOVAL,              /* Tentative de suppression    */

    DBE_COUNT

} DBError;











#endif  /* _ANALYSIS_DB_PROTOCOL_H */
