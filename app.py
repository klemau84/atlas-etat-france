
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
        pd.read_csv(BASE/"sources.csv"),
    )

entites, fiches, sources = load_data()

st.title("Atlas de l'État français")
st.caption("V2.2 · 100 organismes, premières fiches enrichies")

with st.sidebar:
    categories = st.multiselect("Catégories", sorted(entites.categorie.unique()), default=sorted(entites.categorie.unique()))
    domaines = st.multiselect("Domaines", sorted(entites.domaine.unique()), default=sorted(entites.domaine.unique()))
    recherche = st.text_input("Recherche", placeholder="CNIL, recherche, énergie...")
    seulement_detaillees = st.checkbox("Afficher seulement les fiches enrichies", False)

vue = entites[entites.categorie.isin(categories) & entites.domaine.isin(domaines)].copy()
if seulement_detaillees:
    vue = vue[vue.entity_id.isin(fiches.entity_id)]
if recherche:
    q = recherche.lower()
    vue = vue[
        vue.nom.str.lower().str.contains(q, na=False)
        | vue.mission.str.lower().str.contains(q, na=False)
        | vue.domaine.str.lower().str.contains(q, na=False)
        | vue.tutelle.str.lower().str.contains(q, na=False)
    ]

a,b,c,d = st.columns(4)
a.metric("Organismes", len(entites))
b.metric("Fiches enrichies", len(fiches))
c.metric("Budgets renseignés", int(fiches.budget_mde.notna().sum()))
d.metric("Dirigeants renseignés", int(fiches.dirigeant.notna().sum()))

tabs = st.tabs(["Annuaire","Fiche détaillée","Budgets et effectifs","Gouvernance","Cartographie","Sources"])

with tabs[0]:
    st.dataframe(vue[["nom","categorie","domaine","tutelle","dirigeant","niveau_fiche","statut_donnee"]], width="stretch", hide_index=True)

with tabs[1]:
    options = vue.nom.sort_values().tolist()
    if options:
        nom = st.selectbox("Organisme", options)
        core = vue[vue.nom == nom].iloc[0]
        detail = fiches[fiches.entity_id == core.entity_id]
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Catégorie", core.categorie)
        c2.metric("Domaine", core.domaine)
        c3.metric("Tutelle", core.tutelle)
        c4.metric("Niveau", core.niveau_fiche)
        st.markdown(f"## {core.nom}")
        st.markdown(f"**Mission :** {core.mission}")
        if detail.empty:
            st.info("Cette fiche reste succincte. Elle sera enrichie dans un prochain lot.")
            st.markdown(f"**Dirigeant :** {core.dirigeant}")
            st.markdown(f"[Site officiel]({core.site_officiel})")
        else:
            e = detail.iloc[0]
            st.markdown(f"**Dirigeant :** {e.dirigeant} — {e.fonction_dirigeant}")
            st.markdown(f"**Début du mandat :** {e.debut_mandat}")
            st.markdown(f"**Nomination :** {e.mode_nomination}")
            st.markdown(f"**Composition :** {e.composition}")
            st.markdown(f"**Indicateur :** {e.indicateur_activite}")
            x,y = st.columns(2)
            x.metric("Budget", "N/D" if pd.isna(e.budget_mde) else f"{e.budget_mde*1000:.1f} M€ ({int(e.budget_annee)})")
            y.metric("Effectifs", "N/D" if pd.isna(e.effectifs_etpt) else f"{int(e.effectifs_etpt)} ({int(e.effectifs_annee)})")
            st.markdown(f"[Source gouvernance]({e.source_gouvernance}) · [Source finances]({e.source_budget})")
            st.caption(e.qualite_detail)

with tabs[2]:
    financial = fiches[["nom_complet","budget_mde","budget_annee","effectifs_etpt","effectifs_annee","qualite_detail"]].copy()
    financial["budget_millions"] = financial["budget_mde"] * 1000
    st.dataframe(financial, width="stretch", hide_index=True)
    chart = financial.dropna(subset=["budget_millions"])
    if not chart.empty:
        st.plotly_chart(
            px.bar(chart, x="nom_complet", y="budget_millions", text="budget_millions",
                   labels={"nom_complet":"","budget_millions":"Budget (M€)"}),
            width="stretch"
        )
    st.warning("Les montants ne sont comparables qu'à périmètre et millésime identiques.")

with tabs[3]:
    st.dataframe(
        fiches[["nom_complet","dirigeant","fonction_dirigeant","debut_mandat","mode_nomination","composition"]],
        width="stretch", hide_index=True
    )

with tabs[4]:
    tree = vue.groupby(["tutelle","categorie"], as_index=False).size()
    st.plotly_chart(px.treemap(tree, path=["tutelle","categorie"], values="size"), width="stretch")

with tabs[5]:
    st.dataframe(sources, width="stretch", hide_index=True)
    st.markdown("- Les valeurs financières sont associées à leur millésime.\n- Les fonctions dirigeantes sont datées et sourcées.\n- Une case vide signifie que la donnée n'a pas encore été intégrée, pas qu'elle est nulle.")
