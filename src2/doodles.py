

fp='C:\\Users\\zdune\\Documents\\moonboy\\speech-enhancer\\speech-enhancer\\src2\\przyslowki.txt'
f=open(fp,encoding='utf-8').read()


przyslowki=[]
for line in f.splitlines():
    if len(line)==1:
        continue
    if ' ' in line:
        continue
    przyslowki.append(line)


print(przyslowki)