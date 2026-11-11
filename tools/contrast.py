import sys,json
def L(h):
    h=h.lstrip('#'); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    c=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*c[0]+0.7152*c[1]+0.0722*c[2]
def cr(a,b):
    la,lb=sorted([L(a),L(b)],reverse=True); return (la+0.05)/(lb+0.05)
themes=json.loads(sys.argv[1])
pairs=[('ink','paper',7),('grey','paper',7),('accent','paper',7),('band-fg','band-bg',7),('band-muted','band-bg',7),('err','paper',7),('rule','paper',3)]
for name,t in themes.items():
    for f,b,need in pairs:
        if f in t and b in t:
            r=cr(t[f],t[b]); print(f"{name:6} {f:10} on {b:8} {r:5.2f}  {'OK' if r>=need else 'FAIL (need %s)'%need}")
