
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
        pd.read_csv(BASE/"sources.csv"),
    )

entites, fiches, chronologie, rapports, relations, qualite, sources = load_data()

st.title("Atlas de l'État français")
st.caption("V2.4 · Référentiel, relations institutionnelles et qualité des données")

with st.sidebar:
    categories = st.multiselect(
        "Catégories",
        sorted(entites.categorie.unique()),
        default=sorted(entites.categorie.unique()),
    )
    domaines = st.multiselect(
        "Domaines",
        sorted(entites.domaine.unique()),
        default=sorted(entites.domaine.unique()),
    )
    recherche = st.text_input("Recherche transversale")
    seulement_detaillees = st.checkbox("Fiches enrichies uniquement", False)

vue = entites[
    entites.categorie.isin(categories)
    & entites.domaine.isin(domaines)
].copy()

if seulement_detaillees:
    vue = vue[vue.entity_id.isin(fiches.entity_id)]

if recherche:
    q = recherche.lower()
    ids_rapports = rapports[
        rapports.titre.str.lower().str.contains(q, na=False)
        | rapports.type_rapport.str.lower().str.contains(q, na=False)
    ].entity_id.unique()
    ids_chrono = chronologie[
        chronologie.evenement.str.lower().str.contains(q, na=False)
        | chronologie.type_evenement.str.lower().str.contains(q, na=False)
    ].entity_id.unique()

    vue = vue[
        vue.nom.str.lower().str.contains(q, na=False)
        | vue.mission.str.lower().str.contains(q, na=False)
        | vue.domaine.str.lower().str.contains(q, na=False)
        | vue.tutelle.str.lower().str.contains(q, na=False)
        | vue.entity_id.isin(ids_rapports)
        | vue.entity_id.isin(ids_chrono)
    ]

a,b,c,d = st.columns(4)
a.metric("Organismes", len(entites))
b.metric("Fiches enrichies", len(fiches))
c.metric("Relations", len(relations))
d.metric("Complétude moyenne", f"{qualite.completude_pct.mean():.1f} %")

tabs = st.tabs([
    "Annuaire",
    "Fiche détaillée",
    "Relations",
    "Chronologie",
    "Rapports",
    "Qualité des données",
    "Budgets et effectifs",
    "Sources",
])

with tabs[0]:
    st.dataframe(
        vue[["nom","categorie","domaine","tutelle","dirigeant","niveau_fiche","statut_donnee"]],
        width="stretch",
        hide_index=True,
    )

with tabs[1]:
    options = vue.nom.sort_values().tolist()
    if options:
        nom = st.selectbox("Organisme", options)
        core = vue[vue.nom == nom].iloc[0]
        detail = fiches[fiches.entity_id == core.entity_id]
        quality_row = qualite[qualite.entity_id == core.entity_id].iloc[0]

        c1,c2,c3,c4 = st.columns(4)
        c1.metric("Catégorie", core.categorie)
        c2.metric("Domaine", core.domaine)
        c3.metric("Tutelle", core.tutelle)
        c4.metric("Complétude", f"{quality_row.completude_pct:.0f} %")

        st.markdown(f"## {core.nom}")
        st.markdown(f"**Mission :** {core.mission}")

        if detail.empty:
            st.info("Fiche succincte : enrichissement à venir.")
            st.markdown(f"[Site officiel]({core.site_officiel})")
        else:
            e = detail.iloc[0]
            st.markdown(f"**Dirigeant :** {e.dirigeant} — {e.fonction_dirigeant}")
            st.markdown(f"**Début de mandat :** {e.debut_mandat}")
            st.markdown(f"**Nomination :** {e.mode_nomination}")
            st.markdown(f"**Composition :** {e.composition}")
            st.markdown(f"**Indicateur d'activité :** {e.indicateur_activite}")

            x,y = st.columns(2)
            x.metric(
                "Budget",
                "N/D" if pd.isna(e.budget_mde) else f"{e.budget_mde*1000:.1f} M€"
            )
            y.metric(
                "Effectifs",
                "N/D" if pd.isna(e.effectifs_etpt) else int(e.effectifs_etpt)
            )
            st.markdown(
                f"[Gouvernance]({e.source_gouvernance}) · "
                f"[Finances / activité]({e.source_budget})"
            )
            st.caption(e.qualite_detail)

        rel_in = relations[relations.cible_id == core.entity_id].copy()
        rel_out = relations[relations.source_id == core.entity_id].copy()
        names = entites.set_index("entity_id")["nom"].to_dict()

        st.subheader("Relations directes")
        items = []
        for _, r in rel_in.iterrows():
            items.append([names.get(r.source_id, r.source_id), r.relation, core.nom, r.niveau])
        for _, r in rel_out.iterrows():
            items.append([core.nom, r.relation, names.get(r.cible_id, r.cible_id), r.niveau])

        if items:
            st.dataframe(
                pd.DataFrame(items, columns=["source","relation","cible","niveau"]),
                width="stretch",
                hide_index=True,
            )
        else:
            st.caption("Aucune relation directe encore documentée.")

with tabs[2]:
    names = entites.set_index("entity_id")["nom"].to_dict()
    rel = relations.copy()
    rel["source"] = rel.source_id.map(names)
    rel["cible"] = rel.cible_id.map(names)

    selected_level = st.multiselect(
        "Type de relation",
        sorted(rel.niveau.unique()),
        default=sorted(rel.niveau.unique()),
    )
    rel_view = rel[rel.niveau.isin(selected_level)]

    st.dataframe(
        rel_view[["source","relation","cible","niveau"]],
        width="stretch",
        hide_index=True,
    )

    st.subheader("Organismes les plus reliés")
    counts = pd.concat([
        rel_view[["source"]].rename(columns={"source":"organisme"}),
        rel_view[["cible"]].rename(columns={"cible":"organisme"}),
    ]).value_counts().reset_index(name="nombre_relations")

    st.plotly_chart(
        px.bar(
            counts.head(20).sort_values("nombre_relations"),
            x="nombre_relations",
            y="organisme",
            orientation="h",
            text="nombre_relations",
            labels={"nombre_relations":"Relations","organisme":""},
        ),
        width="stretch",
    )

with tabs[3]:
    names = entites.set_index("entity_id")["nom"].to_dict()
    chrono = chronologie.copy()
    chrono["organisme"] = chrono.entity_id.map(names)
    selected = st.multiselect(
        "Organismes",
        sorted(chrono.organisme.dropna().unique()),
        default=sorted(chrono.organisme.dropna().unique()),
    )
    chrono = chrono[chrono.organisme.isin(selected)].sort_values("date", ascending=False)
    st.dataframe(
        chrono[["date","organisme","type_evenement","evenement","source_url"]],
        width="stretch",
        hide_index=True,
    )

with tabs[4]:
    names = entites.set_index("entity_id")["nom"].to_dict()
    reps = rapports.copy()
    reps["organisme"] = reps.entity_id.map(names)
    st.dataframe(
        reps[["organisme","titre","type_rapport","date_publication","url"]]
        .sort_values("date_publication", ascending=False),
        width="stretch",
        hide_index=True,
    )

with tabs[5]:
    st.subheader("Complétude par organisme")
    st.dataframe(
        qualite.sort_values("completude_pct", ascending=False),
        width="stretch",
        hide_index=True,
    )

    dist = qualite.groupby("completude_pct", as_index=False).size()
    st.plotly_chart(
        px.bar(
            dist,
            x="completude_pct",
            y="size",
            text="size",
            labels={"completude_pct":"Complétude (%)","size":"Nombre d'organismes"},
        ),
        width="stretch",
    )

    st.warning(
        "La complétude mesure uniquement la présence de champs documentés. "
        "Elle ne mesure pas la qualité intrinsèque de l'organisme."
    )

with tabs[6]:
    financial = fiches[
        ["nom_complet","budget_mde","budget_annee","effectifs_etpt","effectifs_annee","qualite_detail"]
    ].copy()
    financial["budget_millions"] = financial["budget_mde"] * 1000
    st.dataframe(financial, width="stretch", hide_index=True)

    chart = financial.dropna(subset=["budget_millions"])
    if not chart.empty:
        st.plotly_chart(
            px.bar(
                chart,
                x="nom_complet",
                y="budget_millions",
                text="budget_millions",
                labels={"nom_complet":"","budget_millions":"Budget (M€)"},
            ),
            width="stretch",
        )

with tabs[7]:
    st.dataframe(sources, width="stretch", hide_index=True)
    st.markdown(
        "- Les relations sont documentaires, pas hiérarchiques par défaut.\n"
        "- La complétude est calculée sur six dimensions : fiche, budget, effectifs, dirigeant, rapport et chronologie.\n"
        "- Une case vide n'est jamais interprétée comme zéro."
    )
