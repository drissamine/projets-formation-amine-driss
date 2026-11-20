# Class Activities 1.1 - Identification des modèles Cloud (IaaS, PaaS, SaaS)

## Objectif

Les étudiants apprennent à différencier concrètement IaaS, PaaS et SaaS.

## Consigne

Pour chaque situation, choisissez si le service correspond à IaaS, PaaS ou SaaS, puis justifiez votre réponse.

---

## Question 1

**Vous créez une machine virtuelle Windows sur AWS et installez vous-même SQL Server.**

**Réponse : IaaS**

**Justification :** Vous gérez la machine virtuelle et SQL Server vous-même. AWS fournit uniquement l'infrastructure (serveur physique, stockage, réseau). Vous êtes responsable du système d'exploitation, des mises à jour et des données.

---

## Question 2

**Vous utilisez Azure SQL Database pour stocker vos données sans gérer le serveur.**

**Réponse : PaaS**

**Justification :** Azure SQL Database est une base de données en tant que service. Microsoft gère le serveur, les mises à jour, les correctifs de sécurité et la haute disponibilité. Vous gérez uniquement vos données.

---

## Question 3

**Vous stockez vos documents en ligne avec Dropbox.**

**Réponse : SaaS**

**Justification :** Dropbox est un service de stockage de fichiers complet, prêt à l'emploi. Aucune gestion d'infrastructure, d'application ou de serveur n'est nécessaire. Vous utilisez simplement le service.

---

## Question 4

**Vous déployez une application Python sur Google App Engine.**

**Réponse : PaaS**

**Justification :** Google App Engine est une plateforme qui gère l'infrastructure serveur, l'équilibreur de charge et le scaling automatique. Vous déployez uniquement votre code source (application Python).

---

## Question 5

**Vous utilisez Microsoft Office 365 (Word, Excel, Teams) via le navigateur.**

**Réponse : SaaS**

**Justification :** Office 365 est un ensemble d'applications professionnelles complètes hébergées dans le cloud. Aucune installation, gestion de serveur ou maintenance n'est requise. Tout est géré par Microsoft.

---

## Question 6

**Vous créez un bucket S3 sur AWS pour stocker des fichiers et configurer les permissions.**

**Réponse : IaaS**

**Justification :** Amazon S3 est un stockage objetbas niveau (infrastructure). Vous gérez l'organisation des fichiers, les permissions d'accès et le cycle de vie des données. AWS fournit uniquement l'espace de stockage.

---

## Question 7

**Vous utilisez un ERP en ligne (SAP S/4HANA Cloud) pour gérer votre entreprise.**

**Réponse : SaaS**

**Justification :** SAP S/4HANA Cloud est un ERP complet en tant que service. L'ensemble des processus métier (comptabilité, RH, supply chain) est hébergé et géré par SAP. L'entreprise utilise simplement l'application.

---

## Question 8

**Vous créez une VM Ubuntu sur Google Cloud Compute Engine et configurez manuellement Apache et MySQL.**

**Réponse : IaaS**

**Justification :** Vous créez une machine virtuelle brute et installez/configurez vous-même le serveur web (Apache) et la base de données (MySQL). Google Cloud gère uniquement le matériel physique. Vous êtes responsable de tout le reste (OS, logiciels, configurations).

---

## Question 9

**Vous utilisez AWS RDS (Relational Database Service) pour déployer PostgreSQL avec sauvegardes automatiques.**

**Réponse : PaaS**

**Justification :** AWS RDS est un service de base de données managé. Amazon gère l'installation, les mises à jour, les sauvegardes automatiques, la réplication et la haute disponibilité. Vous configurez et utilisez uniquement la base de données.

---

## Question 10

**Vous collaborez avec votre équipe via Google Docs pour écrire un rapport.**

**Réponse : SaaS**

**Justification :** Google Docs est un traitement de texte collaboratif en ligne. Aucune installation, gestion de serveur ou maintenance n'est nécessaire. L'application est entièrement hébergée et gérée par Google.

---

## Récapitulatif

| Modèle | Définition | Exemples |
|--------|-----------|----------|
| **IaaS** | Infrastructure as a Service - Vous gérez : OS, données, applications | VM AWS, S3, Compute Engine |
| **PaaS** | Platform as a Service - Vous gérez : données, applications | Azure SQL, Google App Engine, AWS RDS |
| **SaaS** | Software as a Service - Vous utilisez simplement le service | Dropbox, Office 365, SAP Cloud, Google Docs |
