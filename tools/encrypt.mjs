// Usage: node encrypt.mjs <content.html> <imgdir> <password> <out.json>
import fs from 'node:fs'; import path from 'node:path'; import { webcrypto as c } from 'node:crypto';
const [,, src, imgdir, pw, out] = process.argv;
let html = fs.readFileSync(src,'utf8').replace(/srcset="img-avif:([\w-]+)"/g,(m,n)=>`srcset="data:image/avif;base64,${fs.readFileSync(path.join(imgdir,n+'.avif')).toString('base64')}"`).replace(/src="img:([\w-]+)"/g,(m,n)=>`src="data:image/webp;base64,${fs.readFileSync(path.join(imgdir,n+'.webp')).toString('base64')}"`);
const salt=c.getRandomValues(new Uint8Array(16)), iv=c.getRandomValues(new Uint8Array(12)), iter=600000;
const base=await c.subtle.importKey('raw',new TextEncoder().encode(pw),'PBKDF2',false,['deriveKey']);
const key=await c.subtle.deriveKey({name:'PBKDF2',salt,iterations:iter,hash:'SHA-256'},base,{name:'AES-GCM',length:256},false,['encrypt']);
const ct=new Uint8Array(await c.subtle.encrypt({name:'AES-GCM',iv},key,new TextEncoder().encode(html)));
const b=u=>Buffer.from(u).toString('base64');
fs.writeFileSync(out,JSON.stringify({v:1,iter,salt:b(salt),iv:b(iv),ct:b(ct)}));
console.log('encrypted',html.length,'chars ->',out);
