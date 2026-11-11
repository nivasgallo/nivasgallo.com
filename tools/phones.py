import sys, os
from PIL import Image
src_dir, out = sys.argv[1], sys.argv[2]
names = {'home':'fb9b9212-image.png','betslip':'dd93948d-image.png','settled':'95ef0730-image.png','markets':'1d0cc305-image.png'}
ims = {k: Image.open(os.path.join(src_dir,v)).convert('RGBA') for k,v in names.items()}
def save(im, base):
    im.save(base+'.avif','AVIF',quality=70)
    im.save(base+'.webp','WEBP',quality=84,method=6)
    print(base, im.size, os.path.getsize(base+'.avif')//1024,'KB avif', os.path.getsize(base+'.webp')//1024,'KB webp')
for k,im in ims.items():
    w=680; save(im.resize((w,round(im.height*w/im.width)),Image.LANCZOS), os.path.join(out,k))
# hero: journey order home, markets, betslip, settled
pw,gap=540,80; ph=round(2556*pw/1296)
canvas=Image.new('RGBA',(4*pw+3*gap,ph),(0,0,0,0))
for i,k in enumerate(['home','markets','betslip','settled']):
    canvas.alpha_composite(ims[k].resize((pw,ph),Image.LANCZOS),(i*(pw+gap),0))
save(canvas, os.path.join(out,'screens'))
