with open("scratch/pctheme.js", "r", encoding="utf-8") as f:
    content = f.read()

idx = 12217
print("Context around 12217:")
print(repr(content[idx-20:idx+100]))
