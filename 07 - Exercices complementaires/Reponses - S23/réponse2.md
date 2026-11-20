# Class Activities 1.2 - Modèles de déploiement Cloud

*Créé par DRISS Amine*

---

## Question 1

**Le cloud public est caractérisé par :**

**Réponse : b) Un fournisseur qui possède et gère l'infrastructure accessible à plusieurs clients (multi-tenant)**

**Justification :** Le cloud public est un modèle où l'infrastructure est owned et opérée par un fournisseur tiers (Amazon, Microsoft, Google) et partagée entre plusieurs organisations et utilisateurs via Internet.

---

## Question 2

**Dans un cloud public, les ressources se trouvent :**

**Réponse : b) Chez le fournisseur de services cloud**

**Justification :** Dans le cloud public, toutes les ressources (serveurs, stockage, réseau) sont localisées dans les datacenters du fournisseur de cloud et accessibles à distance via Internet.

---

## Question 3

**Le modèle cloud privé est destiné :**

**Réponse : a) À une seule organisation**

**Justification :** Le cloud privé est une infrastructure dédiée exclusivement à une seule organisation, offrant un contrôle total et une personnalisation selon les besoins internes.

---

## Question 4

**Un cloud privé interne (on-premises) signifie que :**

**Réponse : b) L'organisation héberge et gère elle-même son cloud**

**Justification :** Le cloud privé on-premises signifie que l'organisation possède et opère sa propre infrastructure de cloud au sein de ses locaux, conservant un contrôle total sur les données.

---

## Question 5

**Un cloud privé externe (off-premises) correspond à :**

**Réponse : b) Un cloud privé géré par un tiers mais réservé à une organisation**

**Justification :** Le cloud privé externe est dédié à une seule organisation mais hébergé et géré par un fournisseur tiers dans ses datacenters (ex: Azure Dedicated Host).

---

## Question 6

**Le cloud communautaire est :**

**Réponse : b) Partagé par plusieurs organisations ayant des préoccupations communes**

**Justification :** Le cloud communautaire est une infrastructure partagée entre organisations qui ont des missions, intérêts ou exigences de conformité similaires (ex: secteur bancaire, santé).

---

## Question 7

**Exemple typique de cloud communautaire :**

**Réponse : b) Infrastructure partagée pour universités et centres de recherche**

**Justification :** Les universités et centres de recherche partagent souvent une infrastructure cloud pour collaborer sur des projets scientifiques, comme le réseau GENCI en France.

---

## Question 8

**Le cloud hybride combine :**

**Réponse : c) Différents modèles de cloud (public, privé, communautaire)**

**Justification :** Le cloud hybride permet de combiner plusieurs modèles de déploiement tout en maintenant une interconnectivité entre eux, offrant flexibilité et optimisation des coûts.

---

## Question 9

**Dans un modèle hybride, une organisation peut :**

**Réponse : b) Utiliser un cloud privé pour les données sensibles et un public pour les services généraux**

**Justification :** L'hybridation permet de garder les workloads critiques et sensibles en cloud privé tout en utilisant le cloud public pour les charges de travail élastiques et non-stratégiques.

---

## Question 10

**L'un des avantages du cloud privé par rapport au public est :**

**Réponse : b) Moins de restrictions réseau et plus de contrôle sur la sécurité**

**Justification :** Le cloud privé offre un contrôle total sur l'infrastructure, permettant de personnaliser les politiques de sécurité et d'éliminer les restrictions imposées par les environnements multi-tenant.

---

## Question 11

**L'architecture de référence du NIST est conçue pour être :**

**Réponse : b) Indépendante du fournisseur et générique**

**Justification :** Le NIST (National Institute of Standards and Technology) a conçu son architecture pour être neutre et applicable à tous les fournisseurs de cloud, quelle que soit leur technologie.

---

## Question 12

**Le rôle de l'architecture de référence est de :**

**Réponse : b) Fournir un modèle conceptuel pour discuter des besoins et responsabilités**

**Justification :** L'architecture de référence NIST définit les concepts et relations entre acteurs pour faciliter la compréhension des services cloud et des responsabilités de chaque partie.

---

## Question 13

**Combien d'acteurs principaux définit l'architecture de référence NIST ?**

**Réponse : c) 5**

**Justification :** L'architecture NIST identifie 5 acteurs principaux : le consommateur de cloud, le fournisseur de cloud, le courtier de cloud, le transporteur de cloud et l'auditeur.

---

## Question 14

**Parmi les acteurs NIST, le consommateur est :**

**Réponse : c) Celui qui utilise les services cloud**

**Justification :** Le consommateur de cloud est l'organisation ou l'individu qui souscrit et utilise les services cloud proposés par un fournisseur.

---

## Question 15

**Le fournisseur de cloud est responsable de :**

**Réponse : b) La mise à disposition et la gestion des services cloud**

**Justification :** Le fournisseur de cloud (Cloud Provider) est responsable de la création, de l'exploitation et de la gestion des services cloud mis à disposition des consommateurs.

---

## Question 16

**Le courtier en cloud (broker) a pour rôle :**

**Réponse : b) Intermédiaire entre le consommateur et le fournisseur de cloud**

**Justification :** Le courtier de cloud agit comme un intermédiaire qui aide les consommateurs à sélectionner, commander et gérer plusieurs services cloud auprès de différents fournisseurs.

---

## Question 17

**Le transporteur cloud (carrier) assure :**

**Réponse : b) La connectivité et le transport des services cloud**

**Justification :** Le carrier cloud assure le transport des données et services entre le fournisseur et le consommateur, généralement via des fournisseurs de services réseau ou télécoms.

---

## Question 18

**Le SLA (Service Level Agreement) est :**

**Réponse : a) Un contrat qui définit le niveau de service attendu**

**Justification :** Le SLA est un contrat formel entre le fournisseur et le consommateur qui définit les niveaux de service garantis (disponibilité, performance, support).

---

## Question 19

**L'auditeur cloud réalise :**

**Réponse : a) Des évaluations indépendantes de sécurité et de performance**

**Justification :** L'auditeur cloud réalise des évaluations indépendantes et objectives sur la sécurité, la conformité et les performances des services cloud.

---

## Question 20

**Un scénario d'utilisation type est :**

**Réponse : b) Un consommateur demande un service via un courtier cloud**

**Justification :** Un scénario typique implique qu'un consommateur contacte un courtier (broker) pour obtenir des conseils et accéder à des services cloud adaptés à ses besoins.

---

## Récapitulatif - Les 5 acteurs NIST

| Acteur | Rôle |
|--------|------|
| **Consommateur** | Utilise les services cloud |
| **Fournisseur** | Met à disposition et gère les services |
| **Courtier** | Intermédiaire entre consommateur et fournisseur |
| **Transporteur** | Assure la connectivité réseau |
| **Auditeur** | Réalise des évaluations indépendantes |

## Récapitulatif - Modèles de déploiement

| Modèle | Caractéristiques |
|--------|-----------------|
| **Cloud Public** | Multi-tenant, partagé, géré par un tiers |
| **Cloud Privé** | Dédié à une organisation, contrôle total |
| **Cloud Communauté** | Partagé par organisations aux intérêts communs |
| **Cloud Hybride** | Combination de plusieurs modèles |
