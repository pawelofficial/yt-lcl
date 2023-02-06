

import re 
import pandas as pd 


s=' [Music] '

s='[Muzyka] foo '
s='foo bar Muzyka]'
r=r'\[.*\]'
r=r'^\[.*\ '
r=r"^\[\w+"
r=r"[aA-zZ]*\]"
x=re.sub(r,'',s)

print(x)


exit(1)

s='na <00:00:07.880><c>południowym </c><00:00:08.240><c>krańcu </c><00:00:08.600><c>kontynentu </c><00:00:08.960><c>australijskiego</c>' 
timestamps = re.findall(r'<(\d\d:\d\d:\d\d\.\d{3})>', s)
 

l=['foo','bar','kez']
fun=lambda ser: ser.aggregate(func = lambda x: x + ' ',axis=0)

ser=pd.Series(l)
#print(ser )
print(fun(ser))