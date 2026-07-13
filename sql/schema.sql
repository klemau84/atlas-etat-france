
PRAGMA foreign_keys=ON;
CREATE TABLE entites(entity_id TEXT PRIMARY KEY,nom TEXT,categorie TEXT,domaine TEXT,tutelle TEXT,mission TEXT,site_officiel TEXT,niveau_fiche TEXT,budget_mde REAL,effectifs_etpt REAL,dirigeant TEXT,mode_nomination TEXT,date_mise_a_jour TEXT,statut_donnee TEXT);
CREATE TABLE fiches_detaillees(entity_id TEXT PRIMARY KEY,nom_complet TEXT,dirigeant TEXT,fonction_dirigeant TEXT,mode_nomination TEXT,debut_mandat TEXT,composition TEXT,budget_mde REAL,budget_annee INTEGER,effectifs_etpt REAL,effectifs_annee INTEGER,indicateur_activite TEXT,source_budget TEXT,source_gouvernance TEXT,qualite_detail TEXT);
CREATE TABLE relations(source_id TEXT,cible_id TEXT,relation TEXT,niveau TEXT);
CREATE TABLE chronologie(entity_id TEXT,date TEXT,type_evenement TEXT,evenement TEXT,source_url TEXT);
CREATE TABLE rapports(entity_id TEXT,titre TEXT,type_rapport TEXT,date_publication TEXT,url TEXT);
CREATE TABLE documents(entity_id TEXT,titre TEXT,type_document TEXT,url TEXT,periodicite TEXT);
CREATE TABLE historique_financier(entity_id TEXT,annee INTEGER,indicateur TEXT,valeur REAL,unite TEXT,source_url TEXT,qualite TEXT);
CREATE TABLE personnes(person_id TEXT PRIMARY KEY,nom TEXT,date_naissance TEXT,formation TEXT,parcours TEXT,source_principale TEXT);
CREATE TABLE mandats(person_id TEXT,entity_id TEXT,fonction TEXT,debut_mandat TEXT,fin_mandat TEXT,mode_nomination TEXT,statut_mandat TEXT,source_url TEXT);
CREATE TABLE organes_gouvernance(organe_id TEXT PRIMARY KEY,nom_organe TEXT,entity_id TEXT,type_organe TEXT,composition_resumee TEXT,role TEXT,statut TEXT,source_url TEXT);
CREATE TABLE qualite_donnees(entity_id TEXT PRIMARY KEY,nom TEXT,fiche_detaillee INTEGER,budget INTEGER,effectifs INTEGER,dirigeant INTEGER,rapport INTEGER,chronologie INTEGER,score_completude INTEGER,completude_pct REAL);
CREATE TABLE alertes(entity_id TEXT,type_alerte TEXT,detail TEXT,priorite TEXT);
CREATE TABLE sources(jeu_de_donnees TEXT,organisme TEXT,url TEXT);
