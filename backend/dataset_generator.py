import csv, random, math
from pathlib import Path
OUT_CSV = Path('backend/synthetic_dataset.csv')
N = 3000
extensions = ['txt','docx','pdf','jpg','png','exe','dll','xls','pptx','bin','enc']
def pseudo_entropy(fs, rf):
    base = math.log1p(fs); return round(min(8.0, base*(0.5+rf)),3)
rows=[]
for i in range(N):
    label = 1 if i<N//2 else 0
    fs = random.expovariate(1/200)+random.uniform(0,50)
    ext = random.choice(extensions)
    if label==1 and random.random()<0.4: ext = random.choice(['exe','dll','enc'])
    de = random.random() < (0.25 if label==1 else 0.05)
    rf = random.uniform(0.1,1.5) if label==1 else random.uniform(0.01,0.8)
    ep = pseudo_entropy(fs,rf)
    wc = int(max(0, random.gauss(5 if label==1 else 0.5,3)))
    rn = 1 if (label==1 and random.random()<0.4) else (1 if random.random()<0.02 else 0)
    npct = min(100, max(0,int(100*rf*random.random())))
    rows.append({'file_size_kb':round(fs,3),'ext':ext,'double_ext':1 if de else 0,
                 'entropy_proxy':ep,'write_count_last_min':wc,'rename_flag':rn,
                 'non_printable_pct':npct,'label':label})
with OUT_CSV.open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0].keys())); w.writeheader(); w.writerows(rows)
print('Wrote',len(rows),'rows to',OUT_CSV)
