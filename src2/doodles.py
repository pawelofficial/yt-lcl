
def extract_words(string): # function splitting text 

    chars=['. ',',','-']
    for char in chars:
        if char in string: 
            return string.split(char)[0].strip()+char.strip(),string.split(char)[1].strip()
        
        
s='my name is  pawel. and your name is gawel.'
x=extract_words(s)
print(x)