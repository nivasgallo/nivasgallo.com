import sys
from PIL import Image
src,dst,maxw=sys.argv[1],sys.argv[2],int(sys.argv[3])
im=Image.open(src); im=im.convert('RGBA') if im.mode in('P','LA') else im
if im.width>maxw: im=im.resize((maxw,round(im.height*maxw/im.width)),Image.LANCZOS)
im.save(dst,'WEBP',quality=84,method=6); print(dst,im.size)
