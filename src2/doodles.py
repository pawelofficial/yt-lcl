def func(s):
    s=s.capitalize()
    if s[-1]=='.':
        return s 
    else:
        return s+'.'
     
    
s='foo bar.'


print(func(s))
