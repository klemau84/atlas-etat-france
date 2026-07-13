
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Atlas de l'État français", page_icon="🏛️", layout="wide")
BASE = Path(__file__).parent

@st.cache_data
def load_data():
    return (
        pd.read_csv(BASE/"entites.csv"),
        pd.read_csv(BASE/"fiches_detaillees.csv"),
        pd.read_csv(BASE/"chronologie.csv", parse_dates=["date"]),
        pd.read_csv(BASE/"rapports.csv", parse_dates=["date_publication"]),
        pd.read_csv(BASE/"relations.csv"),
        pd.read_csv(BASE/"qualite_donnees.csv"),
        pd.read_csv(BASE/"documents.csv"),
        pd.read_csv(BASE/"backlog_enrichissement.csv"),
        pd.read_csv(BASE/"historique_financier.csv"),
        pd.read_csv(BASE/"dictionnaire_donnees.csv"),
        pd.read_csv(BASE/"journal_versions.csv"),
        pd.read_csv(BASE/"personnes.csv"),
        pd.read_csv(BASE/"mandats.csv"),
        pd.read_csv(BASE/"organes_gouvernance.csv"),
        pd.read_csv(BASE/"alertes.csv"),
        pd.read_csv(BASE/"indicateurs_synthese.csv"),
        pd.read_csv(BASE/"fraicheur_sources.csv"),
        pd.read_csv(BASE/"journal_audit.csv"),
        pd.read_csv(BASE/"index_recherche.csv"),
        pd.read_csv(BASE/"themes.csv"),
        pd.read_csv(BASE/"dossiers_thematiques.csv"),
        pd.read_csv(BASE/"sources.csv"),
    )

entites, fiches, chronologie, rapports, relations, qualite, documents, backlog, historique_financier, dictionnaire, journal_versions, personnes, mandats, organes, alertes, synthese, fraicheur, audit, index_recherche, themes, dossiers, sources = load_data()

st.title("Atlas de l'État français")
st.caption("V3.3 · Dossiers thématiques et exports consolidés")

with st.sidebar:
    categories = st.multiselect("Catégories", sorted(entites.categorie.unique()), default=sorted(entites.categorie.unique()))
    domaines = st.multiselect("Domaines", sorted(entites.domaine.unique()), default=sorted(entites.domaine.unique()))
    recherche = st.text_input("Recherche transversale")
    seulement_detaillees = st.checkbox("Fiches enrichies uniquement", False)

vue = entites[entites.categorie.isin(categories) & entites.domaine.isin(domaines)].copy()
if seulement_detaillees:
    vue = vue[vue.entity_id.isin(fiches.entity_id)]
if recherche:
    q = recherche.lower()
    ids_docs = documents[documents.titre.str.lower().str.contains(q, na=False)].entity_id.unique()
    ids_rap = rapports[rapports.titre.str.lower().str.contains(q, na=False)].entity_id.unique()
    ids_chr = chronologie[chronologie.evenement.str.lower().str.contains(q, na=False)].entity_id.unique()
    vue = vue[
        vue.nom.str.lower().str.contains(q, na=False)
        | vue.mission.str.lower().str.contains(q, na=False)
        | vue.domaine.str.lower().str.contains(q, na=False)
        | vue.tutelle.str.lower().str.contains(q, na=False)
        | vue.entity_id.isin(ids_docs)
        | vue.entity_id.isin(ids_rap)
        | vue.entity_id.isin(ids_chr)
    ]

a,b,c,d = st.columns(4)
a.metric("Organismes", len(entites))
b.metric("Fiches enrichies", len(fiches))
c.metric("Documents officiels", len(documents))
d.metric("Complétude moyenne", f"{qualite.completude_pct.mean():.1f} %")

st.subheader("Vue d'ensemble")
overview_cols = st.columns(3)
overview_cols[0].metric("Alertes ouvertes", len(alertes))
overview_cols[1].metric("Mandats recensés", len(mandats))
overview_cols[2].metric("Organes de gouvernance", len(organes))


tabs = st.tabs(["Annuaire","Fiche","Documents","Relations","Chronologie","Rapports","Complétude","Historique financier","Comparer","Personnes et mandats","Organes de gouvernance","Alertes","Fraîcheur","Recherche globale","Thématiques","Dossiers","Plan d'enrichissement","Dictionnaire","Sources"])

with tabs[0]:
    st.dataframe(vue[["nom","categorie","domaine","tutelle","dirigeant","niveau_fiche","statut_donnee"]], width="stretch", hide_index=True)

with tabs[1]:
    options = vue.nom.sort_values().tolist()
    if options:
        nom = st.selectbox("Organisme", options)
        core = vue[vue.nom == nom].iloc[0]
        detail = fiches[fiches.entity_id == core.entity_id]
        qrow = qualite[qualite.entity_id == core.entity_id].iloc[0]
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Catégorie", core.categorie)
        c2.metric("Domaine", core.domaine)
        c3.metric("Tutelle", core.tutelle)
        c4.metric("Complétude", f"{qrow.completude_pct:.0f} %")
        st.markdown(f"## {core.nom}")
        st.markdown(f"**Mission :** {core.mission}")
        if detail.empty:
            st.info("Fiche succincte : enrichissement à venir.")
        else:
            e = detail.iloc[0]
            st.markdown(f"**Dirigeant :** {e.dirigeant} — {e.fonction_dirigeant}")
            st.markdown(f"**Début de mandat :** {e.debut_mandat}")
            st.markdown(f"**Nomination :** {e.mode_nomination}")
            st.markdown(f"**Composition :** {e.composition}")
            st.markdown(f"**Indicateur :** {e.indicateur_activite}")
        docs = documents[documents.entity_id == core.entity_id]
        if not docs.empty:
            st.subheader("Documents officiels")
            st.dataframe(docs[["titre","type_document","periodicite","url"]], width="stretch", hide_index=True)
        st.markdown(f"[Site officiel]({core.site_officiel})")

with tabs[2]:
    names = entites.set_index("entity_id")["nom"].to_dict()
    docs = documents.copy()
    docs["organisme"] = docs.entity_id.map(names)
    st.dataframe(docs[["organisme","titre","type_document","periodicite","url"]], width="stretch", hide_index=True)

with tabs[3]:
    names = entites.set_index("entity_id")["nom"].to_dict()
    rel = relations.copy()
    rel["source"] = rel.source_id.map(names)
    rel["cible"] = rel.cible_id.map(names)
    st.dataframe(rel[["source","relation","cible","niveau"]], width="stretch", hide_index=True)

with tabs[4]:
    names = entites.set_index("entity_id")["nom"].to_dict()
    ch = chronologie.copy()
    ch["organisme"] = ch.entity_id.map(names)
    st.dataframe(ch[["date","organisme","type_evenement","evenement","source_url"]].sort_values("date",ascending=False), width="stretch", hide_index=True)

with tabs[5]:
    names = entites.set_index("entity_id")["nom"].to_dict()
    rp = rapports.copy()
    rp["organisme"] = rp.entity_id.map(names)
    st.dataframe(rp[["organisme","titre","type_rapport","date_publication","url"]], width="stretch", hide_index=True)

with tabs[6]:
    st.dataframe(qualite.sort_values("completude_pct",ascending=False), width="stretch", hide_index=True)
    st.plotly_chart(px.histogram(qualite, x="completude_pct", nbins=7, labels={"completude_pct":"Complétude (%)"}), width="stretch")

with tabs[7]:
    names = entites.set_index("entity_id")["nom"].to_dict()
    hist = historique_financier.copy()
    if hist.empty:
        st.info("La structure historique est prête ; peu de séries homogènes sont encore intégrées.")
    else:
        hist["organisme"] = hist.entity_id.map(names)
        st.dataframe(hist[["organisme","annee","indicateur","valeur","unite","qualite","source_url"]], width="stretch", hide_index=True)
        for indicateur in hist.indicateur.unique():
            data = hist[hist.indicateur == indicateur]
            st.subheader(indicateur)
            st.plotly_chart(px.bar(data, x="organisme", y="valeur", color="annee", barmode="group",
                                   labels={"organisme":"","valeur":indicateur}), width="stretch")

with tabs[8]:
    choix = st.multiselect("Organismes à comparer", sorted(entites.nom.tolist()), default=sorted(entites.nom.tolist())[:3], max_selections=6)
    comp = entites[entites.nom.isin(choix)].copy()
    comp = comp.merge(qualite[["entity_id","completude_pct"]], on="entity_id", how="left")
    st.dataframe(comp[["nom","categorie","domaine","tutelle","dirigeant","budget_mde","effectifs_etpt","completude_pct"]], width="stretch", hide_index=True)
    if not comp.empty:
        scores = comp[["nom","completude_pct"]].sort_values("completude_pct")
        st.plotly_chart(px.bar(scores, x="completude_pct", y="nom", orientation="h", text="completude_pct",
                               labels={"completude_pct":"Complétude (%)","nom":""}), width="stretch")

with tabs[9]:
    names = entites.set_index("entity_id")["nom"].to_dict()
    persons = personnes.copy()
    md = mandats.copy()
    md["organisme"] = md.entity_id.map(names)
    st.subheader("Personnes")
    st.dataframe(persons, width="stretch", hide_index=True)
    st.subheader("Mandats")
    st.dataframe(md[["person_id","organisme","fonction","debut_mandat","fin_mandat","mode_nomination","statut_mandat","source_url"]], width="stretch", hide_index=True)

with tabs[10]:
    names = entites.set_index("entity_id")["nom"].to_dict()
    og = organes.copy()
    og["organisme"] = og.entity_id.map(names)
    st.dataframe(og[["organisme","nom_organe","type_organe","composition_resumee","role","statut","source_url"]], width="stretch", hide_index=True)

with tabs[11]:
    names = entites.set_index("entity_id")["nom"].to_dict()
    al = alertes.copy()
    if not al.empty:
        al["organisme"] = al.entity_id.map(names)
        st.dataframe(al[["organisme","type_alerte","detail","priorite"]], width="stretch", hide_index=True)
        st.plotly_chart(px.bar(al.groupby("priorite",as_index=False).size(), x="priorite", y="size", text="size",
                               labels={"priorite":"","size":"Nombre d'alertes"}), width="stretch")
    else:
        st.success("Aucune alerte ouverte.")

with tabs[12]:
    st.subheader("Fraîcheur des sources")
    st.dataframe(fraicheur.sort_values(["statut_fraicheur","anciennete_jours"], na_position="last"), width="stretch", hide_index=True)
    dist = fraicheur.groupby("statut_fraicheur", as_index=False).size()
    st.plotly_chart(px.bar(dist, x="statut_fraicheur", y="size", text="size",
                           labels={"statut_fraicheur":"","size":"Nombre d'organismes"}), width="stretch")
    st.subheader("Journal d'audit")
    st.dataframe(audit, width="stretch", hide_index=True)

with tabs[13]:
    st.subheader("Recherche globale")
    q = st.text_input("Mot-clé global", key="global_search")
    if q:
        resultats = index_recherche[index_recherche.texte_indexe.str.contains(q.lower(), na=False)].copy()
        names = entites.set_index("entity_id")["nom"].to_dict()
        resultats["organisme"] = resultats.entity_id.map(names)
        st.dataframe(resultats[["organisme","type_resultat","titre","contenu","url"]], width="stretch", hide_index=True)
    else:
        st.caption("Saisir un mot-clé pour rechercher dans les organismes, rapports, documents et événements.")

with tabs[14]:
    st.subheader("Vues thématiques")
    theme = st.selectbox("Thème", sorted(themes.theme.unique()))
    subset = themes[themes.theme == theme]
    st.dataframe(subset[["nom","domaine","categorie"]], width="stretch", hide_index=True)
    counts = subset.groupby("categorie", as_index=False).size()
    st.plotly_chart(px.bar(counts, x="categorie", y="size", text="size",
                           labels={"categorie":"","size":"Nombre"}), width="stretch")

with tabs[15]:
    st.subheader("Dossiers thématiques")
    st.dataframe(dossiers.sort_values("nombre_organismes", ascending=False), width="stretch", hide_index=True)
    selected = st.selectbox("Dossier", sorted(dossiers.theme.unique()))
    d = dossiers[dossiers.theme == selected].iloc[0]
    c1,c2,c3,c4 = st.columns(4)
    c1.metric("Organismes", int(d.nombre_organismes))
    c2.metric("Relations", int(d.nombre_relations))
    c3.metric("Complétude", f"{d.completude_moyenne_pct:.1f} %")
    c4.metric("Sources récentes", int(d.sources_recentes))
    st.markdown(f"**Exemples :** {d.organismes_exemples}")

with tabs[16]:
    st.dataframe(backlog, width="stretch", hide_index=True)
    st.caption("Le score sert uniquement à ordonner les prochaines collectes de données.")

with tabs[17]:
    st.subheader("Dictionnaire des données")
    st.dataframe(dictionnaire, width="stretch", hide_index=True)
    st.subheader("Journal des versions")
    st.dataframe(journal_versions, width="stretch", hide_index=True)
    st.download_button("Exporter l'annuaire consolidé", entites.to_csv(index=False).encode("utf-8-sig"), "atlas_etat_entites_v2_7.csv", "text/csv")
    st.download_button("Exporter les fiches détaillées", fiches.to_csv(index=False).encode("utf-8-sig"), "atlas_etat_fiches_v3_3.csv", "text/csv")
    st.download_button("Exporter les relations", relations.to_csv(index=False).encode("utf-8-sig"), "atlas_etat_relations_v3_3.csv", "text/csv")
    st.download_button("Exporter les personnes", personnes.to_csv(index=False).encode("utf-8-sig"), "atlas_etat_personnes_v3_3.csv", "text/csv")
    st.download_button("Exporter les mandats", mandats.to_csv(index=False).encode("utf-8-sig"), "atlas_etat_mandats_v3_3.csv", "text/csv")

with tabs[18]:
    st.dataframe(sources, width="stretch", hide_index=True)
