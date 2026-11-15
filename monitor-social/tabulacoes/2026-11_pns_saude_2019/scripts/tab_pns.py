# PNS 2019, morador selecionado de 18 anos ou mais (posts 18/12 e 14/12)
import sys, pandas as pd, numpy as np
src,out=sys.argv[1],sys.argv[2]
spec={'V0024':(3,7),'UPA_PNS':(10,9),'V0025A':(33,1),'C006':(108,1),'C008':(117,3),'C009':(120,1),'J001':(370,1),'J01101':(386,1),'Q092':(986,1),'V00291':(1426,14)}
df=pd.read_fwf(src,colspecs=[(s-1,s-1+w) for s,w in spec.values()],names=list(spec),dtype=str,header=None)
df['V00291']=pd.to_numeric(df.V00291,errors='coerce'); df['C008']=pd.to_numeric(df.C008,errors='coerce')
a=df[(df.V0025A=='1')&(df.C008>=18)&df.V00291.notna()].copy()
w=a.V00291.to_numpy(); strat=a.V0024.to_numpy(); psu=a.UPA_PNS.to_numpy()
def ratio(y,m):
    m=np.asarray(m); y=np.asarray(y,float)
    num=(w*y*m).sum(); den=(w*m).sum(); r=num/den
    z=pd.Series(w*m*(y-r)/den); g=pd.DataFrame({'h':strat,'u':psu,'z':z}).groupby(['h','u']).z.sum().reset_index()
    v=0.0
    for h,gh in g.groupby('h'):
        n=len(gh)
        if n>1: v+=n/(n-1)*((gh.z-gh.z.mean())**2).sum()
    return 100*r, 100*np.sqrt(v)
def total(y,m): return (w*np.asarray(y,float)*np.asarray(m)).sum()
mul=(a.C006=='2').to_numpy(); hom=(a.C006=='1').to_numpy(); neg=a.C009.isin(['2','4']).to_numpy(); bra=(a.C009=='1').to_numpy()
G={'Mulheres':mul,'Homens':hom,'Mulheres negras':mul&neg,'Mulheres brancas':mul&bra,'Homens negros':hom&neg,'Homens brancos':hom&bra}
ind={'Consultou médico nos últimos 12 meses':(a.J01101=='1').to_numpy(),
     'Avalia a própria saúde como boa ou muito boa':a.J001.isin(['1','2']).to_numpy(),
     'Já recebeu diagnóstico de depressão':(a.Q092=='1').to_numpy()}
rows=[]
for nome,y in ind.items():
    for g,m in G.items():
        p,se=ratio(y,m); rows.append(dict(posts='18/12; 14/12',indicador=nome,grupo=g,valor=p,unidade='%',ep=se,cv=100*se/p,n_amostra=int(m.sum())))
idade=a.C008.to_numpy()
for lab,lo,hi in [('18 a 29',18,29),('30 a 59',30,59),('60 ou mais',60,200)]:
    for g in ['Mulheres','Homens']:
        m=G[g]&(idade>=lo)&(idade<=hi); p,se=ratio(ind['Já recebeu diagnóstico de depressão'],m)
        rows.append(dict(posts='14/12',indicador='Já recebeu diagnóstico de depressão',grupo=f'{g}, {lab} anos',valor=p,unidade='%',ep=se,cv=100*se/p,n_amostra=int(m.sum())))
dep=ind['Já recebeu diagnóstico de depressão']
for g,m in [('Total',np.ones(len(a),bool)),('Mulheres',mul),('Homens',hom)]:
    rows.append(dict(posts='validação',indicador='Pessoas com diagnóstico de depressão (total)',grupo=g,valor=total(dep,m)/1e3,unidade='mil pessoas',ep=np.nan,cv=np.nan,n_amostra=int((dep&m).sum())))
t=pd.DataFrame(rows); t.to_csv(out,index=False,float_format='%.2f')
pd.set_option('display.width',200); print(t.drop(columns=['posts']).round(1).to_string(index=False))
