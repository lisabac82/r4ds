# Post 18/11: quanto ela recebe a cada R$ 100 dele, por escolaridade, região e idade (PNAD Contínua 2T2026)
import sys, pandas as pd, numpy as np
df=pd.read_parquet(sys.argv[1]); out=sys.argv[2]
a=df[(df.V2009>=14)&(df.VD4002=='1')].copy()
R=['V1028']+[f'R{i:03d}' for i in range(1,201)]
W=a[R].to_numpy()
y=a.VD4019.to_numpy(float).copy(); y[~(y>0)]=np.nan
h=a.VD4031.to_numpy(float); yh=np.where(h>0,y/h,np.nan)
mul=(a.V2007=='2').to_numpy(); hom=(a.V2007=='1').to_numpy()
def wmean(x,m):
    m=m&np.isfinite(x); return (W[m]*x[m][:,None]).sum(0)/W[m].sum(0)
def wmed(x,m):
    m=m&np.isfinite(x); xs=x[m]; ws=W[m]; o=np.argsort(xs); xs=xs[o]; c=ws[o].cumsum(0); return xs[(c>=c[-1]/2).argmax(0)]
def se(v): return np.sqrt(((v[1:]-v[0])**2).sum()/199)
instr=a.VD3004.map({'1':'Até fundamental incompleto','2':'Até fundamental incompleto','3':'Fundamental completo e médio incompleto','4':'Fundamental completo e médio incompleto','5':'Médio completo e superior incompleto','6':'Médio completo e superior incompleto','7':'Superior completo'}).to_numpy()
reg=a.UF.str[0].map({'1':'Norte','2':'Nordeste','3':'Sudeste','4':'Sul','5':'Centro-Oeste'}).to_numpy()
idade=pd.cut(a.V2009,[13,24,39,59,200],labels=['14 a 24','25 a 39','40 a 59','60 ou mais']).astype(str).to_numpy()
rows=[]
def razao(grupo,cat,m):
    rm=wmean(y,m&mul)/wmean(y,m&hom)*100; rd=wmed(y,m&mul)/wmed(y,m&hom)*100; rh=wmed(yh,m&mul)/wmed(yh,m&hom)*100
    s=se(rm); rows.append(dict(grupo=grupo,categoria=cat,razao_media=rm[0],ep=s,cv=100*s/rm[0],z_contra_100=(rm[0]-100)/s,razao_mediana=rd[0],razao_mediana_hora=rh[0],
        media_mulheres=wmean(y,m&mul)[0],media_homens=wmean(y,m&hom)[0],n_mulheres=int((m&mul).sum()),n_homens=int((m&hom).sum())))
razao('Total','Todas as pessoas ocupadas',np.ones(len(a),bool))
for g,arr,cats in [('Escolaridade',instr,['Até fundamental incompleto','Fundamental completo e médio incompleto','Médio completo e superior incompleto','Superior completo']),
                   ('Região',reg,['Norte','Nordeste','Sudeste','Sul','Centro-Oeste']),('Idade',idade,['14 a 24','25 a 39','40 a 59','60 ou mais'])]:
    for c in cats: razao(g,c,arr==c)
t=pd.DataFrame(rows); t.to_csv(out,index=False,float_format='%.2f')
pd.set_option('display.width',250); print(t.round(1).to_string(index=False))
# diferença entre superior completo e fundamental incompleto
m1=(instr=='Superior completo'); m0=(instr=='Até fundamental incompleto')
d=wmean(y,m1&mul)/wmean(y,m1&hom)-wmean(y,m0&mul)/wmean(y,m0&hom); print('Razão superior − razão fundamental (p.p.): %.1f  EP %.1f'%(100*d[0],100*se(d)))
