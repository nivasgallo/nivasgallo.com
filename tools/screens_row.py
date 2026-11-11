import sys
from PIL import Image, ImageDraw
out=sys.argv[1]; files=sys.argv[2:]
w,gap,r=600,60,40
ims=[Image.open(f).convert('RGBA') for f in files]
h=round(ims[0].height*w/ims[0].width)
c=Image.new('RGBA',(len(ims)*w+(len(ims)-1)*gap,h),(0,0,0,0))
m=Image.new('L',(w,h),0); ImageDraw.Draw(m).rounded_rectangle((0,0,w-1,h-1),r,fill=255)
for i,im in enumerate(ims):
    im=im.resize((w,h),Image.LANCZOS); im.putalpha(m); c.alpha_composite(im,(i*(w+gap),0))
c.save(out,'WEBP',quality=86,method=6); print(out,c.size)
