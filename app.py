
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="Atlas de l'État français", page_icon="🏛️", layout="wide")
BASE = Path(__file__).parent

@st.cache_data
def load_data():
    return pd.read_csv(BASE/"entites.csv"), pd.read_csv(BASE/"relations.csv"), pd.read_csv(BASE/"sources.csv")

entites, relations, sources = load_data()
st.title("Atlas de l'État français")
st.caption("V1 · Institutions, autorités indépendantes et grands opérateurs")

with st.sidebar:
    categories = st.multiselect("Catégories", sorted(entites.categorie.unique()), default=sorted(entites.categorie.unique()))
    domaines = st.multiselect("Domaines", sorted(entites.domaine.unique()), default=sorted(entites.domaine.unique()))
    statuts = st.multiselect("Statuts", sorted(entites.statut.unique()), default=sorted(entites.statut.unique()))
    recherche = st.text_input("Rechercher")

vue = entites[entites.categorie.isin(categories) & entites.domaine.isin(domaines) & entites.statut.isin(statuts)].copy()
if recherche:
    vue = vue[
        vue.nom.str.contains(recherche,case=False,na=False)
        | vue.mission.str.contains(recherche,case=False,na=False)
        | vue.domaine.str.contains(recherche,case=False,na=False)
        | vue.tutelle.str.contains(recherche,case=False,na=False)
    ]

a,b,c,d = st.columns(4)
a.metric("Entités recensées",len(entites))
b.metric("Entités affichées",len(vue))
c.metric("Autorités indépendantes",int(entites.categorie.str.contains("indépendante",case=False,na=False).sum()))
d.metric("Opérateurs",int(entites.categorie.str.contains("Opérateur",case=False,na=False).sum()))

st.info("Les cases budgétaires et de gouvernance restent vides lorsqu'aucune source homogène n'a encore été intégrée.")

t1,t2,t3,t4,t5,t6 = st.tabs(["Annuaire","Fiche organisme","Cartographie","Coûts et effectifs","Gouvernance","Sources"])

with t1:
    st.dataframe(vue[["nom","categorie","domaine","tutelle","mission","statut"]],width="stretch",hide_index=True)
    st.download_button("Télécharger l'annuaire",vue.to_csv(index=False).encode("utf-8-sig"),"atlas_etat.csv","text/csv")

with t2:
    noms = vue.nom.sort_values().tolist()
    if noms:
        nom = st.selectbox("Organisme",noms)
        e = vue[vue.nom==nom].iloc[0]
        x1,x2,x3,x4 = st.columns(4)
        x1.metric("Catégorie",e.categorie)
        x2.metric("Domaine",e.domaine)
        x3.metric("Statut",e.statut)
        x4.metric("Tutelle",e.tutelle)
        st.markdown(f"### {e.nom}")
        st.markdown(f"**Mission :** {e.mission}")
        st.markdown(f"**Cadre juridique :** {e.texte_fondateur}")
        st.markdown(f"**Dirigeant :** {e.dirigeant}")
        st.markdown(f"**Mode de nomination :** {e.mode_nomination}")
        st.markdown(f"[Site officiel]({e.site_officiel})")

with t3:
    counts = vue.groupby("categorie",as_index=False).size().sort_values("size")
    st.plotly_chart(px.bar(counts,x="size",y="categorie",orientation="h",text="size",labels={"size":"Nombre","categorie":""}),width="stretch")
    domains = vue.groupby("domaine",as_index=False).size().sort_values("size",ascending=False)
    st.plotly_chart(px.bar(domains,x="domaine",y="size",text="size",labels={"domaine":"","size":"Nombre"}),width="stretch")

with t4:
    st.dataframe(vue[["nom","categorie","budget_mde","effectifs_etpt","qualite_donnee"]],width="stretch",hide_index=True)
    st.warning("Les budgets et effectifs seront ajoutés avec leur millésime et leur source.")

with t5:
    st.dataframe(vue[["nom","categorie","dirigeant","mode_nomination","tutelle"]],width="stretch",hide_index=True)
    st.caption("Les dirigeants seront ajoutés avec une date de vérification officielle.")

with t6:
    st.dataframe(sources,width="stretch",hide_index=True)
    st.markdown("- Identifiant stable par organisme\n- Organismes fusionnés conservés dans l'historique\n- Budget et effectif toujours associés à un millésime\n- Absence de donnée publique ≠ absence d'activité")
