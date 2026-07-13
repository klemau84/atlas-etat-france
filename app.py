from pathlib import Path
import sqlite3,pandas as pd,plotly.express as px,streamlit as st
st.set_page_config(page_title="Atlas de l'État français",page_icon="🏛️",layout="wide")
DB=Path(__file__).parent/'database/atlas.sqlite'
@st.cache_resource
def con(): return sqlite3.connect(DB,check_same_thread=False)
@st.cache_data
def q(sql,params=None): return pd.read_sql_query(sql,con(),params=params or [])
st.title("Atlas de l'État français"); st.caption("V4.0 · Base SQLite relationnelle")
entites=q('select * from entites'); fiches=q('select * from fiches_detaillees'); relations=q('select * from relations'); rapports=q('select * from rapports'); chrono=q('select * from chronologie'); docs=q('select * from documents'); hist=q('select * from historique_financier'); qualite=q('select * from qualite_donnees'); personnes=q('select * from personnes'); mandats=q('select * from mandats'); organes=q('select * from organes_gouvernance'); alertes=q('select * from alertes'); sources=q('select * from sources')
with st.sidebar:
 cats=st.multiselect('Catégories',sorted(entites.categorie.dropna().unique()),default=sorted(entites.categorie.dropna().unique())); doms=st.multiselect('Domaines',sorted(entites.domaine.dropna().unique()),default=sorted(entites.domaine.dropna().unique())); recherche=st.text_input('Recherche')
vue=entites[entites.categorie.isin(cats)&entites.domaine.isin(doms)].copy()
if recherche:
 z=recherche.lower(); vue=vue[vue.nom.str.lower().str.contains(z,na=False)|vue.mission.str.lower().str.contains(z,na=False)|vue.domaine.str.lower().str.contains(z,na=False)|vue.tutelle.str.lower().str.contains(z,na=False)]
a,b,c,d=st.columns(4); a.metric('Organismes',len(entites)); b.metric('Fiches détaillées',len(fiches)); c.metric('Relations',len(relations)); d.metric('Complétude moyenne',f"{qualite.completude_pct.mean():.1f} %" if not qualite.empty else 'N/D')
tabs=st.tabs(['Annuaire','Fiche','Explorateur SQL','Relations','Chronologie','Rapports','Finances','Personnes','Gouvernance','Qualité','Sources'])
with tabs[0]: st.dataframe(vue[['nom','categorie','domaine','tutelle','mission','dirigeant','statut_donnee']],width='stretch',hide_index=True)
with tabs[1]:
 noms=vue.nom.sort_values().tolist()
 if noms:
  nom=st.selectbox('Organisme',noms); e=vue[vue.nom==nom].iloc[0]; det=fiches[fiches.entity_id==e.entity_id]; qr=qualite[qualite.entity_id==e.entity_id]
  x1,x2,x3,x4=st.columns(4); x1.metric('Catégorie',e.categorie); x2.metric('Domaine',e.domaine); x3.metric('Tutelle',e.tutelle); x4.metric('Complétude','N/D' if qr.empty else f"{qr.iloc[0].completude_pct:.0f} %")
  st.markdown(f"## {e.nom}"); st.markdown(f"**Mission :** {e.mission}")
  if not det.empty:
   r=det.iloc[0]; st.markdown(f"**Dirigeant :** {r.dirigeant} — {r.fonction_dirigeant}"); st.markdown(f"**Nomination :** {r.mode_nomination}"); st.markdown(f"**Composition :** {r.composition}")
  st.markdown(f"[Site officiel]({e.site_officiel})")
with tabs[2]:
 presets={'Organismes par catégorie':'select categorie,count(*) nombre from entites group by categorie order by nombre desc','Organismes par domaine':'select domaine,count(*) nombre from entites group by domaine order by nombre desc','Fiches les plus complètes':'select nom,completude_pct from qualite_donnees order by completude_pct desc','Rapports par organisme':'select e.nom,r.titre,r.type_rapport,r.date_publication,r.url from rapports r left join entites e on e.entity_id=r.entity_id order by r.date_publication desc'}
 p=st.selectbox('Requête',list(presets)); st.dataframe(q(presets[p]),width='stretch',hide_index=True)
with tabs[3]:
 names=entites.set_index('entity_id').nom.to_dict(); r=relations.copy(); r['source']=r.source_id.map(names); r['cible']=r.cible_id.map(names); st.dataframe(r[['source','relation','cible','niveau']],width='stretch',hide_index=True)
with tabs[4]:
 names=entites.set_index('entity_id').nom.to_dict(); x=chrono.copy(); x['organisme']=x.entity_id.map(names); st.dataframe(x[['date','organisme','type_evenement','evenement','source_url']],width='stretch',hide_index=True)
with tabs[5]:
 names=entites.set_index('entity_id').nom.to_dict(); rp=rapports.copy(); rp['organisme']=rp.entity_id.map(names); dc=docs.copy(); dc['organisme']=dc.entity_id.map(names); st.dataframe(rp[['organisme','titre','type_rapport','date_publication','url']],width='stretch',hide_index=True); st.dataframe(dc[['organisme','titre','type_document','periodicite','url']],width='stretch',hide_index=True)
with tabs[6]:
 names=entites.set_index('entity_id').nom.to_dict(); hf=hist.copy(); hf['organisme']=hf.entity_id.map(names); st.dataframe(hf[['organisme','annee','indicateur','valeur','unite','qualite','source_url']],width='stretch',hide_index=True)
with tabs[7]:
 names=entites.set_index('entity_id').nom.to_dict(); md=mandats.copy(); md['organisme']=md.entity_id.map(names); st.dataframe(personnes,width='stretch',hide_index=True); st.dataframe(md[['person_id','organisme','fonction','debut_mandat','fin_mandat','mode_nomination','statut_mandat','source_url']],width='stretch',hide_index=True)
with tabs[8]:
 names=entites.set_index('entity_id').nom.to_dict(); og=organes.copy(); og['organisme']=og.entity_id.map(names); st.dataframe(og[['organisme','nom_organe','type_organe','composition_resumee','role','statut','source_url']],width='stretch',hide_index=True)
with tabs[9]: st.dataframe(qualite.sort_values('completude_pct',ascending=False),width='stretch',hide_index=True); st.dataframe(alertes,width='stretch',hide_index=True)
with tabs[10]: st.dataframe(sources,width='stretch',hide_index=True); st.markdown('- SQLite est reconstruit depuis les CSV sources.\n- Les scripts d’import sont séparés de l’application.\n- Les CSV restent les formats d’échange et de contrôle.')
