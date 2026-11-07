def parse(s):
    """Minimal KiCad s-expression parser -> nested lists (strings kept as str)."""
    i=0; n=len(s); stack=[[]]
    while i<n:
        c=s[i]
        if c.isspace(): i+=1
        elif c=='(': stack.append([]); i+=1
        elif c==')':
            top=stack.pop(); stack[-1].append(top); i+=1
        elif c=='"':
            j=i+1; buf=[]
            while s[j]!='"':
                if s[j]=='\\': j+=1
                buf.append(s[j]); j+=1
            stack[-1].append("".join(buf)); i=j+1
        else:
            j=i
            while j<n and not s[j].isspace() and s[j] not in '()': j+=1
            stack[-1].append(s[i:j]); i=j
    return stack[0][0]
def find(node, tag):
    return [x for x in node if isinstance(x,list) and x and x[0]==tag]
def first(node, tag, default=None):
    r=find(node,tag); return r[0] if r else default
