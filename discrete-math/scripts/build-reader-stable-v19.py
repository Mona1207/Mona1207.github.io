from pathlib import Path
R=Path(__file__).resolve().parents[1]
app=(R/'assets/app-ui-v18.js').read_text()
for name in ['V15PageCrop','V16Reader']:
 marker='function '+name+'(';assert app.count(marker)==1;app=app.replace(marker,'function '+name+'BeforeStableV19(',1)
code='const R19_BUNDLED_MANIFEST='+(R/'data/textbook-assets-v16.json').read_text().strip()+';\n'+(R/'scripts/reader-stable-v19.js').read_text();app=app.replace('const Ys=',code+'\nconst Ys=',1)
(R/'assets/app-ui-reader-v19.js').write_text(app)
# The worker has its own JS global and needs the same compatibility shim.
worker="if(!Promise.withResolvers)Promise.withResolvers=function(){let resolve,reject;const promise=new Promise((ok,no)=>{resolve=ok;reject=no});return {promise,resolve,reject}};\n"+'const {WorkerMessageHandler}=await import("./pdf.worker.min.mjs");export {WorkerMessageHandler};\n'
(R/'assets/pdfjs-v15/pdf.reader-worker-v19.mjs').write_text(worker)
index=(R/'index.html').read_text().replace('app-ui-v18.js?v=18','app-ui-reader-v19.js?v=19.1');line='<link rel="stylesheet" href="/discrete-math/assets/reader-stable-v19.css?v=19.1">';index=index.replace(line+'\n','').replace('</head>',line+'\n</head>');(R/'index.html').write_text(index)
print('Built isolated reader hotfix; source study flow and stored records unchanged.')
