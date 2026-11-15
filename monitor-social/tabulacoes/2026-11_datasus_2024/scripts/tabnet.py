# Consulta ao TabNet/DataSUS: python3 tabnet.py <def> <arquivo.dbf> <Linha> <Coluna> [Campo=valor ...]
import sys, re, urllib.parse, subprocess, html
d,arq,lin,col=sys.argv[1:5]; filt=dict(a.split('=',1) for a in sys.argv[5:])
h=subprocess.run(['curl','-sS','--max-time','60',f'http://tabnet.datasus.gov.br/cgi/deftohtm.exe?{d}'],capture_output=True).stdout.decode('latin1')
act=re.search(r'ACTION="([^"]+)"',h).group(1)
inc=re.findall(r'NAME="Incremento".*?VALUE="([^"]+)"',h,re.S)[0]
fields=re.findall(r'NAME="(S[^"]+)"',h)
data=[('Linha',lin),('Coluna',col),('Incremento',inc),('Arquivos',arq)]
for f in fields:
    if f[1:] in filt:
        blk=h[h.find(f'NAME="{f}"'):]; blk=blk[:blk.find('</SELECT>')]
        opts=re.findall(r'VALUE="([^"]+)"[^>]*>\s*([^<\n]+)',blk)
        val=[v for v,t in opts if html.unescape(t).strip().lower()==filt[f[1:]].lower()]
        if not val: sys.exit(f'opção {filt[f[1:]]} não achada em {f}: {[html.unescape(t).strip() for v,t in opts][:30]}')
        data.append((f,val[0]))
    else: data.append((f,'TODAS_AS_CATEGORIAS__'))
data+=[('formato','prn'),('mostre','Mostra')]
t=subprocess.run(['curl','-sS','--max-time','90','-X','POST','--data',urllib.parse.urlencode(data,encoding='latin1'),'http://tabnet.datasus.gov.br'+act],capture_output=True).stdout.decode('latin1')
i=t.find('<PRE>'); j=t.find('</PRE>'); print(html.unescape(t[i+5:j]).strip() if i>0 else t[:800])
