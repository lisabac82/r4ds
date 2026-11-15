# PNAD Contínua anual 2022, visita 5 (último ano com o módulo completo para adultos): afazeres domésticos e cuidados (posts 01/12, 04/12, 05/12, 15/12, 22/12)
import sys, pandas as pd, numpy as np
src,out=sys.argv[1],sys.argv[2]
spec={'UPA':(12,9),'V1008':(28,2),'V1014':(30,2),'V1032':(58,15),'V2005':(92,2),'V2007':(94,1),'V2009':(103,3),'V2010':(106,1),
 'V4117A':(439,1),'V4119':(476,1),'V4120':(477,1),'V41201':(478,1),'V41202':(479,1),'V41203':(480,1),'V41204':(481,1),'V41205':(482,1),'V41206':(483,1),'V41207':(484,1),
 'V4121A':(486,1),'V4121B':(487,3),'VD4002':(673,1),'VD4031':(731,3),'VD5008':(819,8)}
for i in range(1,201): spec[f'R{i:03d}']=(859+15*(i-1),15)
cs=[(s-1,s-1+w) for s,w in spec.values()]
df=pd.read_fwf(src,colspecs=cs,names=list(spec),dtype=str,header=None)
num=['V1032','V2009','VD4031','VD5008','V4121B']+[f'R{i:03d}' for i in range(1,201)]
for c in num: df[c]=pd.to_numeric(df[c],errors='coerce')
df['dom']=df.UPA+df.V1008+df.V1014
fil=df.V2005.isin(['04','05','06'])
df['filho05']=(fil&(df.V2009<=5)).groupby(df.dom).transform('any')
a=df[df.V2009>=14].copy()
a['fez']=(a[['V4117A','V4119','V4120','V4121A']]=='1').any(axis=1)
a['horas']=a.V4121B.where(a.fez)
W=a[['V1032']+[f'R{i:03d}' for i in range(1,201)]].to_numpy()
def tot(m): return W[np.asarray(m)].sum(0)
def se(v): return np.sqrt(((v[1:]-v[0])**2).sum()/199)
def wmean(x,m):
    m=np.asarray(m)&np.isfinite(x); return (W[m]*x[m][:,None]).sum(0)/W[m].sum(0)
mul=(a.V2007=='2').to_numpy(); hom=(a.V2007=='1').to_numpy(); neg=a.V2010.isin(['2','4']).to_numpy(); bra=(a.V2010=='1').to_numpy()
fez=a.fez.to_numpy(); H=a.horas.to_numpy(float); oc=(a.VD4002=='1').to_numpy(); f05=a.filho05.to_numpy()
pago=a.VD4031.to_numpy(float)
# quintis de renda domiciliar per capita (peso principal)
r=a.VD5008.to_numpy(float); ok=np.isfinite(r)
o=np.argsort(r[ok]); cw=np.cumsum(a.V1032.to_numpy()[ok][o]); q=np.searchsorted(cw/cw[-1],[.2,.4,.6,.8]); cuts=r[ok][o][q]
quint=np.where(ok,np.searchsorted(cuts,r,side='right')+1,0)
rows=[]
def add(bloco,ind,g,v,unid,n,posts):
    e=v[0]; s=se(v); rows.append(dict(posts=posts,bloco=bloco,indicador=ind,grupo=g,valor=e,unidade=unid,ep=s,cv=100*s/abs(e) if e else np.nan,n_amostra=int(np.asarray(n).sum())))
G={'Mulheres':mul,'Homens':hom,'Mulheres negras':mul&neg,'Mulheres brancas':mul&bra,'Homens negros':hom&neg,'Homens brancos':hom&bra}
for g,m in G.items():
    add('Horas','Horas semanais em afazeres e/ou cuidados (média entre quem fez)',g,wmean(H,m&fez),'horas/semana',m&fez,'01/12; 04/12')
    add('Realização','Fez afazeres e/ou cuidados',g,100*tot(m&fez)/tot(m),'%',m,'04/12')
for g in ['Mulheres','Homens']:
    m=G[g]
    add('Horas','Horas semanais, ocupados(as)',g,wmean(H,m&fez&oc),'horas/semana',m&fez&oc,'01/12')
    add('Horas','Horas semanais, não ocupados(as)',g,wmean(H,m&fez&~oc),'horas/semana',m&fez&~oc,'01/12')
    add('Jornada total','Trabalho pago + afazeres/cuidados, ocupados(as)',g,wmean(np.where(fez,H,0)+pago,m&oc&np.isfinite(pago)),'horas/semana',m&oc,'01/12')
    add('Horas','Horas semanais, com filho(a) de 0 a 5 anos em casa',g,wmean(H,m&fez&f05),'horas/semana',m&fez&f05,'01/12')
    for k in range(1,6): add('Horas',f'Horas semanais, {k}º quinto de renda domiciliar per capita',g,wmean(H,m&fez&(quint==k)),'horas/semana',m&fez&(quint==k),'01/12')
    for c,lab in [('V41201','Preparar ou servir alimentos, lavar louça'),('V41204','Limpar ou arrumar a casa'),('V41202','Cuidar das roupas e sapatos'),
                  ('V41205','Organizar a casa: contas, compras, orientar empregados'),('V41206','Fazer compras ou pesquisar preços'),('V41203','Pequenos reparos e manutenção'),('V41207','Cuidar dos animais domésticos')]:
        add('Tarefas',f'Fez: {lab}',g,100*tot(m&(a[c]=='1').to_numpy())/tot(m),'%',m,'04/12; 05/12; 15/12')
    add('Cuidado','Cuidou de moradores (crianças, idosos, pessoas com deficiência ou doentes)',g,100*tot(m&(a.V4117A=='1').to_numpy())/tot(m),'%',m,'04/12')
    mm=m&f05; add('Cuidado','Cuidou de moradores, entre quem tem filho(a) de 0 a 5 anos em casa',g,100*tot(mm&(a.V4117A=='1').to_numpy())/tot(mm),'%',mm,'04/12')
d=wmean(H,mul&fez)-wmean(H,hom&fez); add('Diferença','Mulheres − homens (horas semanais)','—',d,'horas/semana',fez,'01/12; 04/12')
d=wmean(np.where(fez,H,0)+pago,mul&oc&np.isfinite(pago))-wmean(np.where(fez,H,0)+pago,hom&oc&np.isfinite(pago)); add('Diferença','Jornada total: mulheres − homens ocupados','—',d,'horas/semana',oc,'01/12')
d=wmean(H,mul&neg&fez)-wmean(H,mul&bra&fez); add('Diferença','Mulheres negras − brancas (horas)','—',d,'horas/semana',mul&fez,'01/12')
t=pd.DataFrame(rows); t.to_csv(out,index=False,float_format='%.2f')
pd.set_option('display.width',250); pd.set_option('display.max_rows',300)
print('limites dos quintos (R$ per capita):',cuts); print(t.drop(columns=['posts','ep']).round(1).to_string(index=False))
