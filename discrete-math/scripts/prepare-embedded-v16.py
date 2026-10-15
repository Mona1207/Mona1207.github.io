"""Prepare user-authorized public textbook parts; retain every page and its original geometry."""
from pathlib import Path
import argparse,json,subprocess,hashlib,tempfile,os
import fitz
parser=argparse.ArgumentParser();parser.add_argument('--dm',type=Path,required=True);parser.add_argument('--la',type=Path,required=True);parser.add_argument('--ps',type=Path,required=True);args=parser.parse_args()
root=Path(__file__).resolve().parents[1];target=root/'textbooks/v16';target.mkdir(parents=True,exist_ok=True)
old=json.loads((root/'data/textbook-catalog-v15.json').read_text());byid={b['id']:b for b in old['books']};manifest={'version':16,'books':[]}
for bid,path in [('DM2T',args.dm),('LA7',args.la),('PS3',args.ps)]:
 doc=fitz.open(path);starts=[1]
 if bid=='DM2T':
  seed=json.loads((root/'data/book-DM2T-v15.json').read_text());starts+=sorted(set(c['source']['pdf_page'] for c in seed['chapters'] if not c.get('parent_id')))
 else:starts+=[p['start'] for p in byid[bid]['parts'] if p['start']>1]
 starts=sorted(set(starts));book={'id':bid,'pdf_pages':len(doc),'parts':[]}
 for i,start in enumerate(starts):
  end=starts[i+1]-1 if i+1<len(starts) else len(doc);name=f'{bid}-{i:02}.pdf';out=target/name
  valid=False
  if out.exists():
   try:
    existing=fitz.open(out);valid=len(existing)==end-start+1;existing.close()
   except Exception:pass
  if not valid:
   with tempfile.TemporaryDirectory(prefix='textbook-v16-')as folder:
    temp=Path(folder)/'source.pdf';built=Path(folder)/'built.pdf';part=fitz.open();part.insert_pdf(doc,from_page=start-1,to_page=end-1,links=False);part.save(temp,garbage=4,deflate=True);part.close()
    subprocess.run(['gs','-q','-dNOPAUSE','-dBATCH','-sDEVICE=pdfwrite','-dCompatibilityLevel=1.5','-dAutoRotatePages=/None','-dDownsampleColorImages=true','-dColorImageResolution=155','-dDownsampleGrayImages=true','-dGrayImageResolution=155','-dDownsampleMonoImages=true','-dMonoImageResolution=300','-dJPEGQ=78','-sOutputFile='+str(built),str(temp)],check=True)
    complete=fitz.open(built);assert len(complete)==end-start+1;complete.close();os.replace(built,out)
  check=fitz.open(out);assert len(check)==end-start+1
  for n,p in enumerate(check):
   original=doc[start-1+n];assert abs(p.rect.width-original.rect.width)<2 and abs(p.rect.height-original.rect.height)<2
  data=out.read_bytes();book['parts'].append({'start':start,'end':end,'file':'/discrete-math/textbooks/v16/'+name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()});check.close()
 manifest['books'].append(book);print(bid,len(doc),len(book['parts']),sum(p['bytes']for p in book['parts']),flush=True);doc.close()
for stale in target.glob('*.source.pdf'):stale.unlink()
(root/'data/textbook-assets-v16.json').write_text(json.dumps(manifest,ensure_ascii=False,separators=(',',':'))+'\n')
