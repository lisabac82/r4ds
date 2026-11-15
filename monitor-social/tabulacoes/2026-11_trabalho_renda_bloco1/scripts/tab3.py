# Bloco 1: indicadores de trabalho da PNAD Contínua trimestral (posts 16/11 a 08/12)
import sys, pandas as pd, numpy as np
df=pd.read_parquet(sys.argv[1]); out=sys.argv[2]
SM=1621.0  # salário mínimo de 2026
R=['V1028']+[f'R{i:03d}' for i in range(1,201)]
df['dom']=df.UPA+df.V1008+df.V1014
fil=df.V2005.isin(['04','05','06'])
df['filho05']=(fil&(df.V2009<=5)).groupby(df.dom).transform('any')
df['filho014']=(fil&(df.V2009<=14)).groupby(df.dom).transform('any')
df['tem_conj']=df.V2005.isin(['02','03']).groupby(df.dom).transform('any')
a=df[df.V2009>=14].copy()
W=a[R].to_numpy()
def tot(m): return W[np.asarray(m)].sum(0)
def se(v): return np.sqrt(((v[1:]-v[0])**2).sum()/199)
def wmean(x,m):
    m=np.asarray(m)&np.isfinite(x); return (W[m]*x[m][:,None]).sum(0)/W[m].sum(0)
mulher=(a.V2007=='2').to_numpy(); homem=(a.V2007=='1').to_numpy()
negra=a.V2010.isin(['2','4']).to_numpy(); branca=(a.V2010=='1').to_numpy()
ocup=(a.VD4002=='1').to_numpy(); deso=(a.VD4002=='2').to_numpy(); ft=(a.VD4001=='1').to_numpy()
pos=a.VD4009.to_numpy(); cnpj=(a.V4019=='1').to_numpy()
informal=np.isin(pos,['02','04','10'])|(np.isin(pos,['08','09'])&~cnpj)
sem13=ocup&~np.isin(pos,['01','03','05','07'])
y=a.VD4019.to_numpy(float).copy(); y[~(y>0)]=np.nan
h=a.VD4031.to_numpy(float)
idade=a.V2009.to_numpy()
pais=a.V2005.isin(['01','02','03']).to_numpy()
f05=a.filho05.to_numpy(); f014=a.filho014.to_numpy()
diretor=(a.V4010.fillna('').str[0]=='1').to_numpy()&ocup
comercio=(a.VD4010.fillna('').str.lstrip('0')=='4').to_numpy()
rows=[]
def add(bloco,ind,grupo,v,unid,n,posts):
    e=v[0]; s=se(v); rows.append(dict(posts=posts,bloco=bloco,indicador=ind,grupo=grupo,valor=e,unidade=unid,ep=s,cv=100*s/abs(e) if e else np.nan,n_amostra=int(np.asarray(n).sum())))
G={'Mulheres':mulher,'Homens':homem,'Mulheres negras':mulher&negra,'Mulheres brancas':mulher&branca,'Homens negros':homem&negra,'Homens brancos':homem&branca}
def pct(num,den): return 100*tot(num)/tot(den)
# 1. Desocupação e informalidade (17/11 noite, 20/11)
for g,m in G.items():
    add('Desocupação','Taxa de desocupação',g,pct(m&deso,m&ft),'%',m&ft,'17/11 noite; 20/11')
    add('Informalidade','Taxa de informalidade (ocupados)',g,pct(m&informal,m&ocup),'%',m&ocup,'20/11; 30/11')
    add('13º salário','Ocupados sem direito a 13º (sem carteira, conta própria, empregador, familiar)',g,pct(m&sem13,m&ocup),'%',m&ocup,'30/11')
    add('Salário mínimo','Ocupados com rendimento de até 1 salário mínimo (R$ 1.621)',g,pct(m&ocup&(y<=SM),m&ocup&np.isfinite(y)),'%',m&ocup&np.isfinite(y),'02/12 noite')
for lab,lo,hi in [('14 a 24 anos',14,24),('25 a 39 anos',25,39),('40 a 59 anos',40,59)]:
    for g in ['Mulheres','Homens','Mulheres negras']:
        m=G[g]&(idade>=lo)&(idade<=hi); add('Desocupação','Taxa de desocupação',f'{g}, {lab}',pct(m&deso,m&ft),'%',m&ft,'17/11 noite')
# 2. Penalidade materna (17/11): responsáveis/cônjuges de 25 a 44 anos
base=pais&(idade>=25)&(idade<=44)
for sx,ms in [('Mulheres',mulher),('Homens',homem)]:
    for lab,mm in [('com filho(a) de 0 a 5 anos',f05),('sem filho(a) de até 14 anos',~f014)]:
        m=base&ms&mm
        add('Penalidade materna','Nível de ocupação (% ocupados)',f'{sx} {lab}',pct(m&ocup,m),'%',m,'17/11')
        add('Penalidade materna','Rendimento médio, todos os trabalhos',f'{sx} {lab}',wmean(y,m&ocup),'R$/mês',m&ocup,'17/11')
        add('Penalidade materna','Jornada parcial (menos de 30 horas)',f'{sx} {lab}',pct(m&ocup&(h<30),m&ocup),'%',m&ocup,'17/11')
for rc,mr in [('negras',negra),('brancas',branca)]:
    for lab,mm in [('com filho(a) de 0 a 5 anos',f05),('sem filho(a) de até 14 anos',~f014)]:
        m=base&mulher&mr&mm; add('Penalidade materna','Nível de ocupação (% ocupados)',f'Mulheres {rc} {lab}',pct(m&ocup,m),'%',m,'17/11')
# 3. Empreendedoras e MEI (19/11)
for g in ['Mulheres','Homens','Mulheres negras','Mulheres brancas']:
    m=G[g]&ocup; cp=m&(pos=='09'); emp=m&(pos=='08')
    add('Negócio próprio','Conta própria (% dos ocupados)',g,pct(cp,m),'%',m,'19/11')
    add('Negócio próprio','Empregadoras/es (% dos ocupados)',g,pct(emp,m),'%',m,'19/11')
    add('Negócio próprio','Conta própria: total',g,tot(cp)/1e3,'mil pessoas',cp,'19/11')
    add('Negócio próprio','Conta própria com CNPJ (aprox. MEI e afins)',g,pct(cp&cnpj,cp),'% dos conta própria',cp,'19/11 noite')
    add('Negócio próprio','Conta própria com CNPJ: total',g,tot(cp&cnpj)/1e3,'mil pessoas',cp&cnpj,'19/11 noite')
    add('Negócio próprio','Rendimento médio, conta própria',g,wmean(y,cp),'R$/mês',cp,'19/11')
    add('Negócio próprio','Rendimento médio, conta própria sem CNPJ',g,wmean(y,cp&~cnpj),'R$/mês',cp&~cnpj,'19/11')
# 4. Jornada longa (16/11 noite, 14/12 noite)
emp_priv=np.isin(pos,['01'])&ocup
for g in ['Mulheres','Homens']:
    m=G[g]&emp_priv
    add('Jornada','Empregados com carteira: jornada habitual de 44 horas ou mais',g,pct(m&(h>=44),m),'%',m,'16/11 noite; 14/12 noite')
    m2=m&comercio; add('Jornada','Comércio, com carteira: jornada de 44 horas ou mais',g,pct(m2&(h>=44),m2),'%',m2,'16/11 noite')
    add('Jornada','Comércio, com carteira: total',g,tot(m2)/1e3,'mil pessoas',m2,'16/11 noite')
# 5. Teto de vidro (08/12)
add('Direção','Mulheres entre diretores e gerentes','Total',pct(diretor&mulher,diretor),'%',diretor,'08/12')
add('Direção','Mulheres entre os ocupados','Total',pct(ocup&mulher,ocup),'%',ocup,'08/12')
for g in ['Mulheres negras','Mulheres brancas','Homens negros','Homens brancos']:
    add('Direção','Participação entre diretores e gerentes',g,pct(diretor&G[g],diretor),'%',diretor,'08/12')
    add('Direção','Participação entre os ocupados',g,pct(ocup&G[g],ocup),'%',ocup,'08/12')
for g in ['Mulheres','Homens']:
    add('Direção','Rendimento médio de diretores e gerentes',g,wmean(y,diretor&G[g]),'R$/mês',diretor&G[g],'08/12')
# 6. Chefia (30/11 noite, 02/12): responsáveis pelo domicílio
resp=(a.V2005=='01').to_numpy()
add('Chefia','Domicílios com mulher como responsável','Total',pct(resp&mulher,resp),'%',resp,'02/12; 30/11 noite')
for rc,mr in [('negra',negra),('branca',branca)]:
    add('Chefia','Domicílios com mulher como responsável, por raça da responsável',f'Responsável {rc}',pct(resp&mulher&mr,resp&mr),'%',resp&mr,'02/12')
mono=resp&mulher&~a.tem_conj.to_numpy()&f014
add('Chefia','Responsáveis mulheres sem cônjuge e com filho(a) de até 14 anos','Total',tot(mono)/1e3,'mil domicílios',mono,'02/12; 30/11 noite')
add('Chefia','Mulheres responsáveis sem cônjuge e com filho(a) de até 14 anos, entre as responsáveis','Mulheres',pct(mono,resp&mulher),'%',resp&mulher,'02/12')
monoh=resp&homem&~a.tem_conj.to_numpy()&f014
add('Chefia','Homens responsáveis sem cônjuge e com filho(a) de até 14 anos','Total',tot(monoh)/1e3,'mil domicílios',monoh,'02/12')
add('Chefia','Rendimento médio, mães sozinhas com filho(a) até 14 anos (ocupadas)','Mulheres',wmean(y,mono&ocup),'R$/mês',mono&ocup,'30/11 noite')
add('Chefia','Mães sozinhas com filho(a) até 14 anos: % ocupadas','Mulheres',pct(mono&ocup,mono),'%',mono,'30/11 noite')
t=pd.DataFrame(rows); t.to_csv(out,index=False,float_format='%.2f')
pd.set_option('display.width',250); pd.set_option('display.max_rows',300); pd.set_option('display.max_colwidth',60)
print(t.drop(columns=['posts','ep']).round(1).to_string(index=False))
