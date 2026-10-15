from pathlib import Path
import hashlib,json
import fitz
root=Path(__file__).resolve().parents[1];manifest=json.loads((root/'data/textbook-assets-v16.json').read_text());total=0
for book in manifest['books']:
 expected=1
 for part in book['parts']:
  assert part['start']==expected;path=root/part['file'].split('/discrete-math/')[1];data=path.read_bytes();assert len(data)==part['bytes'];assert hashlib.sha256(data).hexdigest()==part['sha256'];pdf=fitz.open(path);assert len(pdf)==part['end']-part['start']+1
  # Decode both boundary pages of every part, where global/local index errors occur.
  for n in {0,len(pdf)-1}:
   pix=pdf[n].get_pixmap(matrix=fitz.Matrix(.15,.15));assert pix.width>10 and pix.height>10
  pdf.close();expected=part['end']+1
 assert expected==book['pdf_pages']+1;total+=book['pdf_pages'];print('PASS',book['id'],book['pdf_pages'],'pages; contiguous parts, checksums, PDF count and first/last page decoding.')
assert total==858
