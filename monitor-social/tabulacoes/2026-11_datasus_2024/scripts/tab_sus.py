# DataSUS: SIM e Sinasc 2024 (posts 16/12, 17/12 e semana de 23/11)
import sys, pandas as pd, numpy as np
sim_f,sin_f,out=sys.argv[1],sys.argv[2],sys.argv[3]
sim=pd.read_csv(sim_f,sep=';',dtype=str,usecols=['SEXO','RACACOR','IDADE','CAUSABAS','LOCOCOR','OBITOPUERP','OBITOGRAV','DTOBITO'],encoding='latin1')
sin=pd.read_csv(sin_f,sep=';',dtype=str,usecols=['RACACORMAE','IDADEMAE','CONSULTAS','MESPRENAT','KOTELCHUCK','CONSPRENAT','ESCMAE2010'],encoding='latin1')
cb=sim.CAUSABAS.fillna('').str.upper()
mul=sim.SEXO=='2'
c3=cb.str[:3]
mat=mul&( (c3.between('O00','O95')) | c3.isin(['O98','O99','A34']) | ((cb.str[:4].isin(['F530','F531','F539','M830']) | (c3=='F53')) & sim.OBITOPUERP.isin(['1','2'])) )
rac={'1':'Branca','2':'Preta','3':'Amarela','4':'Parda','5':'Indígena'}
nv=len(sin); rows=[]
def add(post,ind,g,v,unid,n): rows.append(dict(posts=post,indicador=ind,grupo=g,valor=v,unidade=unid,n=n))
add('16/12','Nascidos vivos','Total',nv,'nascimentos',nv)
add('16/12','Óbitos maternos (declarados, sem fator de correção)','Total',int(mat.sum()),'óbitos',int(mat.sum()))
add('16/12','Razão de mortalidade materna (sem correção)','Total',1e5*mat.sum()/nv,'por 100 mil nascidos vivos',int(mat.sum()))
neg_sim=sim.RACACOR.isin(['2','4']); neg_sin=sin.RACACORMAE.isin(['2','4'])
for lab,ms,mn in [('Negras (pretas e pardas)',neg_sim,neg_sin),('Brancas',sim.RACACOR=='1',sin.RACACORMAE=='1'),('Pretas',sim.RACACOR=='2',sin.RACACORMAE=='2'),('Pardas',sim.RACACOR=='4',sin.RACACORMAE=='4'),('Indígenas',sim.RACACOR=='5',sin.RACACORMAE=='5')]:
    d=int((mat&ms).sum()); b=int(mn.sum()); add('16/12','Razão de mortalidade materna (sem correção)',lab,1e5*d/b,'por 100 mil nascidos vivos',d)
add('16/12','Óbitos maternos sem raça informada','Total',int((mat&~sim.RACACOR.isin(list(rac))).sum()),'óbitos',0)
add('16/12','Nascidos vivos sem raça da mãe informada','Total',int((~sin.RACACORMAE.isin(list(rac))).sum()),'nascimentos',0)
# pré-natal
ok7=sin.CONSULTAS=='4'; cedo=pd.to_numeric(sin.MESPRENAT,errors='coerce')<=3
kot=sin.KOTELCHUCK.isin(['4','5'])
for lab,m in [('Total',pd.Series(True,index=sin.index)),('Negras (pretas e pardas)',neg_sin),('Brancas',sin.RACACORMAE=='1'),('Pretas',sin.RACACORMAE=='2'),('Pardas',sin.RACACORMAE=='4'),('Indígenas',sin.RACACORMAE=='5'),
              ('Mães de 10 a 19 anos',pd.to_numeric(sin.IDADEMAE,errors='coerce')<20),('Mães sem instrução ou fundamental I',sin.ESCMAE2010.isin(['0','1'])),('Mães com superior completo',sin.ESCMAE2010=='5')]:
    n=int(m.sum())
    add('17/12','7 ou mais consultas de pré-natal',lab,100*(ok7&m).sum()/n,'% dos nascidos vivos',n)
    add('17/12','Pré-natal iniciado no 1º trimestre',lab,100*(cedo&m).sum()/n,'% dos nascidos vivos',n)
    add('17/12','Pré-natal adequado ou mais que adequado (índice de Kotelchuck)',lab,100*(kot&m).sum()/n,'% dos nascidos vivos',n)
# homicídios de mulheres (agressões X85-Y09)
hom=mul&c3.between('X85','Y09')
add('23/11','Mulheres mortas por agressão (homicídio), 2024','Total',int(hom.sum()),'óbitos',int(hom.sum()))
add('23/11','Uma mulher morta por agressão a cada','Total',366*24/hom.sum(),'horas',int(hom.sum()))
add('23/11','Mulheres negras entre as vítimas','Total',100*(hom&neg_sim).sum()/hom.sum(),'%',int(hom.sum()))
add('23/11','Mortas dentro de casa (local do óbito: domicílio)','Total',100*(hom&(sim.LOCOCOR=='3')).sum()/hom.sum(),'%',int(hom.sum()))
homh=(sim.SEXO=='1')&c3.between('X85','Y09')
add('23/11','Homens mortos dentro de casa, entre os homens vítimas','Total',100*(homh&(sim.LOCOCOR=='3')).sum()/homh.sum(),'%',int(homh.sum()))
add('validação','Total de óbitos no SIM 2024','Total',len(sim),'óbitos',len(sim))
t=pd.DataFrame(rows); t.to_csv(out,index=False,float_format='%.2f')
pd.set_option('display.width',200); print(t.round(1).to_string(index=False))
