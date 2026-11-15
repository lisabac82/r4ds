import sys, pandas as pd, numpy as np
df=pd.read_parquet(sys.argv[1]); out=sys.argv[2]
R=['V1028']+[f'R{i:03d}' for i in range(1,201)]
a=df[(df.V2009>=14)&(df.VD4002=='1')].copy()   # ocupados
W=a[R].to_numpy()
def tot(m): return W[np.asarray(m)].sum(0)
def se(v): return np.sqrt(((v[1:]-v[0])**2).sum()/199)
def wmed(x,m):
    m=np.asarray(m)&np.isfinite(x); xs=x[m]; ws=W[m]; o=np.argsort(xs); xs=xs[o]; ws=ws[o]
    c=ws.cumsum(0); half=c[-1]/2; idx=(c>=half).argmax(0); return xs[idx]
def wmean(x,m):
    m=np.asarray(m)&np.isfinite(x); return (W[m]*x[m][:,None]).sum(0)/W[m].sum(0)
M=(a.V2007=='2').to_numpy(); H=(a.V2007=='1').to_numpy()
neg=a.V2010.isin(['2','4']).to_numpy(); bra=(a.V2010=='1').to_numpy()
dom=a.VD4009.isin(['03','04']).to_numpy(); semc=(a.VD4009=='04').to_numpy()
contr=(a.VD4012=='1').to_numpy()
y=a.VD4019.to_numpy(float).copy(); y[~(y>0)]=np.nan
yp=a.VD4016.to_numpy(float).copy(); yp[~(yp>0)]=np.nan
h=a.VD4031.to_numpy(float).copy(); yh=np.where(h>0,y/h,np.nan)
rows=[]
def r(bloco,nome,v,unid,n):
    e=v[0]; s=se(v); rows.append(dict(bloco=bloco,indicador=nome,valor=e,unidade=unid,ep=s,cv=100*s/abs(e) if e else np.nan,n_amostra=int(n)))
# ---- Domésticas
r('Domésticas','Trabalhadoras domésticas',tot(M&dom)/1e3,'mil pessoas',(M&dom).sum())
r('Domésticas','Trabalhadores domésticos (homens)',tot(H&dom)/1e3,'mil pessoas',(H&dom).sum())
r('Domésticas','Mulheres entre os trabalhadores domésticos',100*tot(M&dom)/tot(dom),'%',dom.sum())
r('Domésticas','Domésticas entre as mulheres ocupadas',100*tot(M&dom)/tot(M),'%',M.sum())
r('Domésticas','Negras entre as domésticas',100*tot(M&dom&neg)/tot(M&dom),'%',(M&dom).sum())
r('Domésticas','Negras entre as demais ocupadas',100*tot(M&~dom&neg)/tot(M&~dom),'%',(M&~dom).sum())
r('Domésticas','Sem carteira entre as domésticas',100*tot(M&semc)/tot(M&dom),'%',(M&dom).sum())
r('Domésticas','Sem carteira entre as domésticas negras',100*tot(M&semc&neg)/tot(M&dom&neg),'%',(M&dom&neg).sum())
r('Domésticas','Sem carteira entre as domésticas brancas',100*tot(M&semc&bra)/tot(M&dom&bra),'%',(M&dom&bra).sum())
r('Domésticas','Não contribuem para a previdência (domésticas)',100*tot(M&dom&~contr)/tot(M&dom),'%',(M&dom).sum())
r('Domésticas','Com 50 anos ou mais (domésticas)',100*tot(M&dom&(a.V2009>=50).to_numpy())/tot(M&dom),'%',(M&dom).sum())
r('Domésticas','Rendimento mediano, trabalho principal: domésticas',wmed(yp,M&dom),'R$/mês',(M&dom).sum())
r('Domésticas','Rendimento mediano, trabalho principal: domésticas com carteira',wmed(yp,M&dom&~semc),'R$/mês',(M&dom&~semc).sum())
r('Domésticas','Rendimento mediano, trabalho principal: domésticas sem carteira',wmed(yp,M&semc),'R$/mês',(M&semc).sum())
r('Domésticas','Rendimento mediano, trabalho principal: todas as ocupadas',wmed(yp,M),'R$/mês',M.sum())
r('Domésticas','Rendimento médio, trabalho principal: domésticas',wmean(yp,M&dom),'R$/mês',(M&dom).sum())
r('Domésticas','Horas habituais médias por semana (domésticas)',wmean(h,M&dom),'horas',(M&dom).sum())
# ---- Rendimento por sexo e raça (todos os trabalhos)
grp={'Homens':H,'Mulheres':M,'Homens brancos':H&bra,'Homens negros':H&neg,'Mulheres brancas':M&bra,'Mulheres negras':M&neg}
med={k:wmed(y,g) for k,g in grp.items()}; mea={k:wmean(y,g) for k,g in grp.items()}; hor={k:wmed(yh,g) for k,g in grp.items()}
for k,g in grp.items():
    r('Rendimento','Médio, todos os trabalhos: '+k,mea[k],'R$/mês',g.sum())
    r('Rendimento','Mediano, todos os trabalhos: '+k,med[k],'R$/mês',g.sum())
    r('Rendimento','Mediano por hora: '+k,hor[k],'índice por hora (usar só na razão)',g.sum())
for lab,num,den in [('Mulheres / homens','Mulheres','Homens'),('Mulheres negras / homens brancos','Mulheres negras','Homens brancos'),
                    ('Mulheres brancas / homens brancos','Mulheres brancas','Homens brancos'),('Mulheres negras / homens negros','Mulheres negras','Homens negros'),
                    ('Mulheres negras / mulheres brancas','Mulheres negras','Mulheres brancas')]:
    r('Razão (R$ a cada R$ 100)','Média: '+lab,100*mea[num]/mea[den],'R$ por R$ 100',0)
    r('Razão (R$ a cada R$ 100)','Mediana: '+lab,100*med[num]/med[den],'R$ por R$ 100',0)
    r('Razão (R$ a cada R$ 100)','Mediana por hora: '+lab,100*hor[num]/hor[den],'R$ por R$ 100',0)
r('Validação','Rendimento médio habitual todos os trabalhos (total)',wmean(y,np.ones(len(a),bool)),'R$/mês',len(a))
r('Validação','Trabalhadores domésticos (total)',tot(dom)/1e3,'mil pessoas',dom.sum())
t=pd.DataFrame(rows); t.to_csv(out,index=False,float_format='%.2f')
pd.set_option('display.width',250); pd.set_option('display.max_rows',200)
print(t.round(2).to_string(index=False))
