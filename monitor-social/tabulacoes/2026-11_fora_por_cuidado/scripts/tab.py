import sys, json, pandas as pd, numpy as np
df=pd.read_parquet(sys.argv[1])
R=[f'R{i:03d}' for i in range(1,201)]
df['dom']=df.UPA+df.V1008+df.V1014
df['crianca05']=df.groupby('dom').V2009.transform(lambda s:(s<=5).any())
a=df[df.V2009>=14].copy()
W=a[['V1028']+R].to_numpy()
def reps(m): return W[np.asarray(m)].sum(0)
def stat(v):  # v: array len 201 (full, reps)
    est=v[0]; se=np.sqrt(((v[1:]-est)**2).sum()/199)
    return est, se
a['mulher']=a.V2007=='2'; a['homem']=a.V2007=='1'
a['fora']=a.VD4001=='2'
a['cuidado']=a.fora & ((a.V4074A=='07')|(a.V4078A=='1'))
a['quer']=a.cuidado & (a.V4073=='1')
a['raca']=a.V2010.map({'1':'Branca','2':'Preta','4':'Parda','3':'Amarela','5':'Indígena'}).fillna('Ignorada')
a['negra']=a.V2010.isin(['2','4'])
reg={'1':'Norte','2':'Nordeste','3':'Sudeste','4':'Sul','5':'Centro-Oeste'}
a['regiao']=a.UF.str[0].map(reg)
a['idade']=pd.cut(a.V2009,[13,24,39,59,200],labels=['14 a 24','25 a 39','40 a 59','60 ou mais'])
a['instr']=a.VD3004.map({'1':'Até fundamental incompleto','2':'Até fundamental incompleto','3':'Fundamental completo / médio incompleto','4':'Fundamental completo / médio incompleto','5':'Médio completo / superior incompleto','6':'Médio completo / superior incompleto','7':'Superior completo'})
a['cond']=a.V2005.map(lambda x:'Responsável' if x=='01' else ('Cônjuge' if x in('02','03') else ('Filha/enteada' if x in('04','05','06') else 'Outra')))
a['filho05']=a.crianca05.map({True:'Com criança de 0 a 5 anos em casa',False:'Sem criança de 0 a 5 anos em casa'})
n=a.to_numpy  # noqa
rows=[]
def add(grupo,cat,base):
    nr=reps(a.cuidado&base); dr=reps(base); fr=reps(a.fora&base); qr=reps(a.quer&base)
    tot,tse=stat(nr); rate,rse=stat(nr/dr); sf,sfse=stat(nr/fr); q,qse=stat(qr/nr)
    rows.append(dict(grupo=grupo,categoria=cat,n_amostra=int((a.cuidado&base).sum()),
      total_mil=tot/1e3,cv_total=100*tse/tot,
      taxa_pct=100*rate,cv_taxa=100*rse/rate,
      pct_dos_fora=100*sf,cv_pct_fora=100*sfse/sf,
      pct_queriam_trabalhar=100*q,cv_queriam=100*qse/q))
    return nr/dr
M=a.mulher; H=a.homem
rm=add('Sexo','Mulheres',M); rh=add('Sexo','Homens',H)
for g,col,cats in [('Cor ou raça (mulheres)','raca',['Branca','Preta','Parda','Indígena','Amarela']),
                   ('Região (mulheres)','regiao',list(reg.values())),
                   ('Idade (mulheres)','idade',['14 a 24','25 a 39','40 a 59','60 ou mais']),
                   ('Instrução (mulheres)','instr',['Até fundamental incompleto','Fundamental completo / médio incompleto','Médio completo / superior incompleto','Superior completo']),
                   ('Condição no domicílio (mulheres)','cond',['Responsável','Cônjuge','Filha/enteada','Outra']),
                   ('Criança pequena (mulheres)','filho05',['Com criança de 0 a 5 anos em casa','Sem criança de 0 a 5 anos em casa'])]:
    for c in cats: add(g,c,M&(a[col]==c))
rn=add('Cor ou raça (mulheres)','Negra (preta + parda)',M&a.negra)
rb=reps(a.cuidado&M&(a.raca=='Branca'))/reps(M&(a.raca=='Branca'))
# cruzamento raça x criança pequena
for c in ['Com criança de 0 a 5 anos em casa','Sem criança de 0 a 5 anos em casa']:
    add('Raça × criança pequena (mulheres)','Negras, '+c.lower(),M&a.negra&(a.filho05==c))
    add('Raça × criança pequena (mulheres)','Brancas, '+c.lower(),M&(a.raca=='Branca')&(a.filho05==c))
add('Sexo × criança pequena','Homens com criança de 0 a 5 anos em casa',H&a.crianca05)
t=pd.DataFrame(rows); t.to_csv(sys.argv[2],index=False,float_format='%.2f')
# testes
def test(name,x,y,ratio=False):
    d=x-y if not ratio else x/y
    e,se=stat(d); z=(e-(1 if ratio else 0))/se
    print(f'{name}: {"razão" if ratio else "dif (p.p.)"} = {e*(1 if ratio else 100):.2f}  EP={se*(1 if ratio else 100):.2f}  z={z:.1f}')
test('Mulheres - homens (taxa)',rm,rh)
test('Mulheres / homens (total)',reps(a.cuidado&M),reps(a.cuidado&H),ratio=True)
test('Negras - brancas (taxa)',rn,rb)
cm=reps(a.cuidado&M&a.crianca05)/reps(M&a.crianca05); sm=reps(a.cuidado&M&~a.crianca05)/reps(M&~a.crianca05)
test('Com criança - sem criança (taxa, mulheres)',cm,sm)
ch=reps(a.cuidado&H&a.crianca05)/reps(H&a.crianca05); test('Mulheres - homens com criança 0-5 (taxa)',cm,ch)
for g in ['Nordeste','Sul']:
    pass
# validação CV contra SIDRA 4093
e,se=stat(reps(M&a.fora)); print(f'Validação: mulheres fora da FT = {e/1e3:.0f} mil, CV={100*se/e:.2f}% (SIDRA 4093: 43016 mil, CV 0,3%)')
