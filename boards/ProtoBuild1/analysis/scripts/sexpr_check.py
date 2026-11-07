import sys
def check(path):
    s = open(path, encoding='utf-8', errors='replace').read()
    print(f"== {path.split('/')[-1]}: {len(s)} chars, CR count {s.count(chr(13))}, BOM {s.startswith(chr(0xfeff))}, tabs {s.count(chr(9))}, non-ascii {sum(1 for c in s if ord(c)>127)}")
    depth=0; i=0; n=len(s); line=1; instr=False; maxd=0; first_close_at_zero=None
    while i<n:
        c=s[i]
        if c=='\n': line+=1
        if instr:
            if c=='\\': i+=1
            elif c=='"': instr=False
        else:
            if c=='"': instr=True
            elif c=='(': depth+=1; maxd=max(maxd,depth)
            elif c==')':
                depth-=1
                if depth<0 and first_close_at_zero is None: first_close_at_zero=line
            elif c==';' or c=='#': pass
        i+=1
    print(f"   final depth {depth} (0 = balanced), max depth {maxd}, in-string at EOF {instr}, first underflow line {first_close_at_zero}")
    # top-level children
    import re
    toks = re.findall(r'^\s{0,2}\(([a-z_]+)', s, re.M)
    from collections import Counter
    print("   top-level-ish tokens:", Counter(toks).most_common(25))
for p in sys.argv[1:]: check(p)
