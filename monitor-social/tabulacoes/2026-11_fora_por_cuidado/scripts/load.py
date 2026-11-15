import sys, pandas as pd, numpy as np
src, out = sys.argv[1], sys.argv[2]
spec = {  # (start 1-based, width)
 'UF':(6,2),'UPA':(12,9),'Estrato':(21,7),'V1008':(28,2),'V1014':(30,2),'V1028':(50,15),
 'V2005':(93,2),'V2007':(95,1),'V2009':(104,3),'V2010':(107,1),
 'V4071':(376,1),'V4073':(380,1),'V4074A':(382,2),'V4077':(394,1),'V4078A':(396,1),
 'VD3004':(405,1),'VD4001':(409,1),'VD4002':(410,1),'VD4003':(411,1)}
for i in range(1,201): spec[f'R{i:03d}']=(479+15*(i-1),15)
names=list(spec); cs=[(a-1,a-1+w) for a,w in spec.values()]
df=pd.read_fwf(src,colspecs=cs,names=names,dtype=str,header=None)
for c in ['V1028','V2009']+[f'R{i:03d}' for i in range(1,201)]:
    df[c]=pd.to_numeric(df[c],errors='coerce')
df.to_parquet(out)
print(df.shape); print(df[['UF','V2007','V2009','VD4001','V4074A','V4078A','V1028','R001','R200']].head())
