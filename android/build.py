#!/usr/bin/env python3
"""Build using Android SDK + JDK, with a separately preserved release keystore."""
import os,subprocess,shutil,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent
sdk=Path(os.environ['ANDROID_HOME'])
tools=sdk/'build-tools'/'35.0.0'
jar=next((sdk/'platforms'/'android-35').rglob('android.jar'))
keystore=Path(os.environ['MONA_KEYSTORE'])
assert keystore.is_file(),'Missing release keystore'
assert os.environ.get('MONA_STORE_PASSWORD'),'Missing keystore password'
build=R/'build';build.mkdir(exist_ok=True)
classes=build/'classes';classes.mkdir(exist_ok=True)
dex=build/'dex';dex.mkdir(exist_ok=True)
def run(args): subprocess.run([str(a) for a in args],check=True)
run([tools/'aapt','package','-f','-M',R/'AndroidManifest.xml','-S',R/'res','-I',jar,'-F',build/'resources.apk'])
compiler=['javac'] if shutil.which('javac') else ['java','-jar',os.environ['MONA_ECJ_JAR']]
boot=os.pathsep.join([str(jar),str(tools/'core-lambda-stubs.jar')])
run([*compiler,'-encoding','UTF-8','-source','8','-target','8','-bootclasspath',boot,'-d',classes,*sorted((R/'src').rglob('*.java'))])
run([tools/'d8','--lib',jar,'--min-api','26','--output',dex,*sorted(classes.rglob('*.class'))])
shutil.copy2(build/'resources.apk',build/'unsigned.apk')
with zipfile.ZipFile(build/'unsigned.apk','a',compression=zipfile.ZIP_DEFLATED) as z:
 for p in dex.glob('*.dex'):z.write(p,p.name)
run([tools/'zipalign','-f','4',build/'unsigned.apk',build/'aligned.apk'])
import xml.etree.ElementTree as ET
version=ET.parse(R/'AndroidManifest.xml').getroot().attrib['{http://schemas.android.com/apk/res/android}versionName']
output=build/('mona-study-'+version+'.apk')
run([tools/'apksigner','sign','--ks',keystore,'--ks-key-alias','mona-release','--ks-pass','env:MONA_STORE_PASSWORD','--key-pass','env:MONA_STORE_PASSWORD','--out',output,build/'aligned.apk'])
run([tools/'apksigner','verify','--verbose','--print-certs',output])
print(output)
