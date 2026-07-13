
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Atlas de l'État français", page_icon="🏛️", layout="wide")
BASE = Path(__file__).parent

@st.cache_data
def load_data():
    return pd.read_csv(BASE/"entites.csv"), pd.read_csv(BASE/"sources.csv")

entites, sources = load_data()

st.title("Atlas de l'État français")
st.caption("V2.1 · Référentiel de 100 organismes majeurs")

with st.sidebar:
    st.header("Filtres")
    categories = st.multiselect("Catégories", sorted(entites.categorie.unique()), default=sorted(entites.categorie.unique()))
    domaines = st.multiselect("Domaines", sorted(entites.domaine.unique()), default=sorted(entites.domaine.unique()))
    niveaux = st.multiselect("Niveau de fiche", sorted(entites.niveau_fiche.unique()), default=sorted(entites.niveau_fiche.unique()))
    recherche = st.text_input("Recherche", placeholder="santé, énergie, CNRS...")

vue = entites[
    entites.categorie.isin(categories)
    & entites.domaine.isin(domaines)
    & entites.niveau_fiche.isin(niveaux)
].copy()

if recherche:
    q = recherche.lower()
    vue = vue[
        vue.nom.str.lower().str.contains(q, na=False)
        | vue.mission.str.lower().str.contains(q, na=False)
        | vue.domaine.str.lower().str.contains(q, na=False)
        | vue.tutelle.str.lower().str.contains(q, na=False)
    ]

a,b,c,d = st.columns(4)
a.metric("Organismes recensés", len(entites))
b.metric("Affichés", len(vue))
c.metric("Fiches prioritaires", int((entites.niveau_fiche=="Détaillée prioritaire").sum()))
d.metric("Domaines", entites.domaine.nunique())

st.info("V2.1 pose le référentiel de 100 organismes. Les budgets, effectifs et dirigeants seront intégrés dans la V2.2.")

tabs = st.tabs(["Annuaire","Fiche","Classements","Cartographie","Qualité des données","Sources"])

with tabs[0]:
    st.dataframe(vue[["nom","categorie","domaine","tutelle","mission","niveau_fiche"]], width="stretch", hide_index=True)
    st.download_button("Télécharger les 100 organismes", vue.to_csv(index=False).encode("utf-8-sig"), "atlas_etat_100_organismes.csv", "text/csv")

with tabs[1]:
    noms = vue.nom.sort_values().tolist()
    if noms:
        nom = st.selectbox("Organisme", noms)
        e = vue[vue.nom==nom].iloc[0]
        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Catégorie", e.categorie)
        c2.metric("Domaine", e.domaine)
        c3.metric("Tutelle", e.tutelle)
        c4.metric("Niveau", e.niveau_fiche)
        st.markdown(f"## {e.nom}")
        st.markdown(f"**Mission :** {e.mission}")
        st.markdown(f"**Dirigeant :** {e.dirigeant}")
        st.markdown(f"**Mode de nomination :** {e.mode_nomination}")
        st.markdown(f"**Budget :** {'À documenter' if pd.isna(e.budget_mde) else str(e.budget_mde)+' Md€'}")
        st.markdown(f"**Effectifs :** {'À documenter' if pd.isna(e.effectifs_etpt) else str(e.effectifs_etpt)}")
        st.markdown(f"[Site officiel]({e.site_officiel})")

with tabs[2]:
    cat = vue.groupby("categorie", as_index=False).size().sort_values("size", ascending=False)
    dom = vue.groupby("domaine", as_index=False).size().sort_values("size", ascending=False)
    left,right = st.columns(2)
    with left:
        st.plotly_chart(px.bar(cat,x="size",y="categorie",orientation="h",text="size",labels={"size":"Nombre","categorie":""}),width="stretch")
    with right:
        st.plotly_chart(px.bar(dom.head(20),x="domaine",y="size",text="size",labels={"domaine":"","size":"Nombre"}),width="stretch")

with tabs[3]:
    tree = vue.groupby(["tutelle","categorie"], as_index=False).size()
    st.plotly_chart(px.treemap(tree, path=["tutelle","categorie"], values="size"), width="stretch")

with tabs[4]:
    quality = vue.groupby(["niveau_fiche","statut_donnee"], as_index=False).size()
    st.dataframe(quality,width="stretch",hide_index=True)
    st.warning("Les champs financiers sont volontairement vides tant qu'ils ne sont pas associés à un millésime et une source officielle.")

with tabs[5]:
    st.dataframe(sources,width="stretch",hide_index=True)
