# Decode the packed javascript from line 220 of pctheme.js:
# eval(function(p,a,c,k,e,r){...})
import re

def decode_packed(p, a, c, k, e, r):
    def get_char(c):
        if c < 62:
            return ''
        else:
            return get_char(int(c/62)) + (chr(c%62 + 29) if c%62 > 35 else c.toString(36)) # JS logic
            
    # Python equivalent of the JS unpacker:
    # e = function(c){return(c<62?'':e(parseInt(c/62)))+((c=c%62)>35?String.fromCharCode(c+29):c.toString(36))}
    def e_func(c):
        c_mod = c % 62
        char_val = chr(c_mod + 29) if c_mod > 35 else base36encode(c_mod)
        prefix = e_func(int(c/62)) if c >= 62 else ''
        return prefix + char_val

    def base36encode(number):
        # 0-9a-z
        if number < 10:
            return str(number)
        return chr(ord('a') + number - 10)

    # If the unpacker function runs:
    # while(c--)if(k[c])p=p.replace(new RegExp('\\b'+e(c)+'\\b','g'),k[c])
    # Let's do the replacement:
    words = k
    for i in range(len(words)-1, -1, -1):
        if words[i]:
            packed_word = e_func(i)
            # Use regex word boundaries
            p = re.sub(r'\b' + re.escape(packed_word) + r'\b', words[i], p)
    return p

# Packed arguments from pctheme.js line 220:
p = "9.addEventListener('DOMContentLoaded',3(){1 n=9.querySelector('#o');1 6=q.r(n.querySelectorAll('p'));1 d=s Set();1 e=s Date();1 f=e.getHours();1 g=e.getMinutes();3 h(){a String.fromCharCode(97+4.t(4.7()*26))}6.u(3(b,c){1 v=h();1 w=4.7().x(y).z(2,5);1 A=v+f+g+c+w;b.classList.B(A)});1 i=6.C(3(b,c){1 8=b.cloneNode(true);1 D=h();1 E=4.7().x(y).z(2,5);1 j=D+f+g+c+E;8.k=j;d.B(j);a 8});i.sort(3(){a 4.7()-0.5});i.u(3(8){1 F=4.t(4.7()*6.length);1 l=6[F];l.parentNode.insertBefore(8,l)});1 m=9.createElement('style');9.head.appendChild(m);1 G=q.r(d).C(3(k){a"#o ."+k}).join(", ")+" { display: none; }";m.sheet.insertRule(G,0)});"
k = '||var||function|Math||originalParagraphs|random|clone|document|return|paragraph|index|hiddenClassNames|date|hour|minute|getRandomLetter|clonedParagraphs|cloneClassName|className|referenceParagraph|styleElement|container|TextContent||Array|from|new|floor|forEach|originalLetter|originalRandomPart|toString|36|substr|originalClassName|add|map|cloneLetter|cloneRandomPart|randomIndex|cssRule'.split('|')

unpacked = decode_packed(p, 43, 43, k, None, {})
print("Unpacked JS:")
print(unpacked)
