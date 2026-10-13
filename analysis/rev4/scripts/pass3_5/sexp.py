"""Minimal KiCad s-expression parser (shared by the pass3/5 scripts)."""
import re
_tok = re.compile(r'"(?:[^"\\]|\\.)*"|\(|\)|[^\s()"]+')
def parse(text):
    stack=[[]]
    for m in _tok.finditer(text):
        t=m.group(0)
        if t=='(': stack.append([])
        elif t==')':
            l=stack.pop(); stack[-1].append(l)
        elif t.startswith('"'): stack[-1].append(t[1:-1].replace('\\"','"'))
        else: stack[-1].append(t)
    return stack[0]
def find_all(node, name):
    """Yield direct children lists whose head == name."""
    for c in node:
        if isinstance(c,list) and c and c[0]==name: yield c
def find1(node,name,default=None):
    for c in find_all(node,name): return c
    return default
def walk(node):
    yield node
    for c in node:
        if isinstance(c,list): yield from walk(c)
