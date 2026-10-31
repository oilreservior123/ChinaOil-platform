"""Reassemble approved public archives; verify bytes and SHA256 before use."""
from pathlib import Path
import argparse,hashlib,json,os,zipfile
p=argparse.ArgumentParser();p.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);args=p.parse_args();root=args.root
manifest=json.loads((root/'artifact-parts/manifest.json').read_text())
for item in manifest['archives']:
 target=root/item['target'];target.parent.mkdir(parents=True,exist_ok=True)
 if target.exists() and target.stat().st_size==item['size'] and hashlib.sha256(target.read_bytes()).hexdigest()==item['sha256']:
  print(f'Already verified: {item["target"]}');continue
 tmp=target.with_suffix(target.suffix+'.assembling');h=hashlib.sha256();size=0
 try:
  with tmp.open('wb') as out:
   for part in item['parts']:
    data=(root/part['path']).read_bytes()
    if len(data)!=part['size'] or hashlib.sha256(data).hexdigest()!=part['sha256']:raise ValueError('Invalid archive part: '+part['path'])
    out.write(data);h.update(data);size+=len(data)
  if size!=item['size'] or h.hexdigest()!=item['sha256']:raise ValueError('Archive checksum mismatch: '+item['target'])
  with zipfile.ZipFile(tmp) as z:
   bad=z.testzip()
   if bad:raise ValueError('Archive CRC mismatch: '+bad)
  os.replace(tmp,target);print(f'Assembled and verified: {item["target"]} ({size} bytes)')
 finally:
  if tmp.exists():tmp.unlink()
