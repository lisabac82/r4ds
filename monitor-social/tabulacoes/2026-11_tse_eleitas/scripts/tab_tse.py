# TSE: candidaturas e eleitas, eleições gerais 2010-2026 (posts 07/12, 09/12, 11/12)
import sys, glob, os, pandas as pd
base,out=sys.argv[1],sys.argv[2]
cols=['ANO_ELEICAO','NR_TURNO','SG_UF','DS_CARGO','SQ_CANDIDATO','DS_SITUACAO_CANDIDATURA','DS_GENERO','DS_COR_RACA','DS_SIT_TOT_TURNO']
fr=[]
for y in ['2010','2014','2018','2022','2026']:
    for f in glob.glob(os.path.join(base,y,f'consulta_cand_{y}_*.csv')):
        if f.endswith('_BRASIL.csv'): continue
        d=pd.read_csv(f,sep=';',encoding='latin1',dtype=str,usecols=lambda c:c in cols); fr.append(d)
d=pd.concat(fr); d['ANO']=d.ANO_ELEICAO.astype(int)
st=d.DS_SIT_TOT_TURNO.str.upper().str.strip()
d['eleita']=st.str.startswith('ELEITO')|st.eq('MÉDIA')
d['urna']=d.eleita|st.isin(['SUPLENTE','NÃO ELEITO'])
d['mulher']=d.DS_GENERO.str.upper().eq('FEMININO')
d['negra']=d.DS_COR_RACA.str.upper().isin(['PRETA','PARDA'])
d['cargo']=d.DS_CARGO.str.upper().str.strip()
rows=[]
cargos=['DEPUTADO FEDERAL','DEPUTADO ESTADUAL','DEPUTADO DISTRITAL','SENADOR','GOVERNADOR','PRESIDENTE']
for ano in sorted(d.ANO.unique()):
    x=d[d.ANO==ano]
    for c in cargos:
        e=x[(x.cargo==c)&x.eleita].drop_duplicates('SQ_CANDIDATO')
        apt=x[(x.cargo==c)&(x.NR_TURNO=='1')&x.urna].drop_duplicates('SQ_CANDIDATO')
        if len(apt)==0 and len(e)==0: continue
        rows.append(dict(ano=ano,cargo=c,candidaturas_nas_urnas=len(apt),candidatas_mulheres=int(apt.mulher.sum()),pct_candidatas=100*apt.mulher.mean() if len(apt) else None,
            eleitos=len(e),eleitas_mulheres=int(e.mulher.sum()),pct_eleitas=100*e.mulher.mean() if len(e) else None,
            eleitas_negras=int((e.mulher&e.negra).sum()),eleitos_raca_informada=int(e.DS_COR_RACA.str.upper().isin(['BRANCA','PRETA','PARDA','AMARELA','INDÍGENA']).sum())))
t=pd.DataFrame(rows); t.to_csv(out,index=False,float_format='%.1f')
pd.set_option('display.width',250); print(t.round(1).to_string(index=False))
e=d[(d.ANO==2026)&d.eleita&d.cargo.isin(['DEPUTADO FEDERAL'])].drop_duplicates('SQ_CANDIDATO').reset_index(drop=True)
print('\nDep. federais eleitos 2026 por gênero x cor/raça:'); print(pd.crosstab(e.DS_COR_RACA,e.DS_GENERO,margins=True))
print('\nSituações 2026 (totalização):', d[d.ANO==2026].DS_SIT_TOT_TURNO.value_counts().head(12).to_dict())
print('Governador/Senador eleitas 2026 por UF:'); print(d[(d.ANO==2026)&d.eleita&d.mulher&d.cargo.isin(['GOVERNADOR','SENADOR'])].drop_duplicates('SQ_CANDIDATO')[['SG_UF','cargo','DS_COR_RACA']].to_string(index=False))
