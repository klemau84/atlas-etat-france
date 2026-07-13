from pathlib import Path
import sqlite3,pandas as pd
BASE=Path(__file__).resolve().parents[1]; DATA=BASE/'data'; DB=BASE/'database/atlas.sqlite'; SCHEMA=BASE/'sql/schema.sql'
TABLES=['entites', 'fiches_detaillees', 'relations', 'chronologie', 'rapports', 'documents', 'historique_financier', 'personnes', 'mandats', 'organes_gouvernance', 'qualite_donnees', 'alertes', 'sources']
def main():
    if DB.exists(): DB.unlink()
    con=sqlite3.connect(DB); con.executescript(SCHEMA.read_text(encoding='utf-8'))
    for t in TABLES:
        p=DATA/f'{t}.csv'
        if p.exists(): pd.read_csv(p).to_sql(t,con,if_exists='append',index=False)
    con.commit(); con.close(); print(DB)
if __name__=='__main__': main()
