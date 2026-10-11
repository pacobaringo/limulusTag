import re
def parse(s):
    tok=re.findall(r'\(|\)|"(?:\\.|[^"\\])*"|[^\s()]+',s)
    st=[[]]
    for t in tok:
        if t=='(': st.append([])
        elif t==')': x=st.pop(); st[-1].append(x)
        else: st[-1].append(t[1:-1] if t.startswith('"') else t)
    return st[0][0]
def find(n,key): return [c for c in n if isinstance(c,list) and c and c[0]==key]
def one(n,key):
    r=find(n,key); return r[0] if r else None
