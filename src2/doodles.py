from fuzzywuzzy import fuzz
from fuzzywuzzy import process
s='''Cześć chłopaki i witajcie z powrotem w liftvault. czynnikiem, który jest często zaniedbywany w trójboju siłowym jest użycie sztangi do martwego ciągu zamiast sztangi.  sztanga sztanga do martwego ciągu ma dużą elastyczność, co powoduje, że moment, w którym ciężar odrywa się od podłogi, jest dobrze opóźniony ze sztangą, która jest prawie natychmiastowa, ale inni również twierdzą, że bicz sztangi martwego ciągu może mieć negatywny wpływ, więc dzisiaj pomyślałem interesujące byłoby przyjrzenie się dwóm przykładom, w których nieśmiertelni użytkownicy sztangi przeszli na sztangę, zaczynając od john hack, który niedawno startował w zawodach i podczas tych zawodów ustanowił rekord świata w martwym ciągu wynoszący 402,5 kg, a po tych zawodach wykonał blok  gdzie dodał sztywny drążek który opuścił, i osiągnął wagę 365 kilogramów lub nieco ponad 800 funtów, a wkrótce potem podciągnął 370 kilogramów na drążku w martwym ciągu, więc ten but  dałoby nam dobre porównanie co ciekawe, chociaż ciężar był większy na drążku martwego ciągu został on zablokowany jako pierwszy, ale różnica nie była dramatyczna, więc myślę, że w tym przypadku różnica około 10 kilogramów byłaby całkiem dokładna, ale ktoś inny, kto to zrobił  to samo co jamal browner jamal brał udział w tym samym spotkaniu co jon i podobnie jak john prowadził bloga o sztywnym drążku, który odszedł i na przestrzeni tygodni widać wyraźny postęp i jego technikę, z zauważalnym udoskonalaniem wylogowania, a to nawet oznaczało  że jego ostatni singiel wyglądał prawie na łatwiejszy niż ten z poprzedniego tygodnia, 
ale niestety jamal nie wykonał żadnego ciężkiego martwego ciągu, który ostatnio opuścił, więc musimy porównać z ostatnim singlem przed jego spotkaniem, co nie oddaje najdokładniejszego obrazu, ponieważ jest zdecydowanie  słabszy po jego spotkaniu i zgodnie z oczekiwaniami rzeczywiście widzimy znaczną różnicę, ale najbardziej wyróżnia się to, że wylogowanie wydaje się trwać znacznie dłużej, więc po doświadczeniu ciężarowiec z pewnością może zyskać przewagę dzięki używaniu sztangi do martwego ciągu dzięki za oglądanie wszystkim, którzy oglądali ten film, a dzisiejszą atrakcją dla subskrybentów jest george, a george był w stanie przykucnąć 215 kilogramów przy masie ciała wynoszącej zaledwie 68 kilogramów, jeśli lubisz oglądać ten kanał nie zapomnij polubić i zasubskrybować oraz obejrzeć jeden z sugerowanych filmów wyświetlanych teraz na ekranie.'''


l=s.split(' ')
N=3

fuzzy_string='dzieki za ogladanie'
new_s=''
new_s=[]

for i in range(0,len(l)-N):
    w=l[i:i+N]
    sentence=' '.join(w)
    
    ratio = fuzz.token_sort_ratio(sentence, fuzzy_string)
    print(sentence)
    if ratio>80:
        break
    
    w=sentence.split(' ')
    new_s.append(w[0])


# cuts off part of a string that's behind provided fuzzy_string
def fuzzy_cutoff(s,fuzzy_string='dzieki za ogladanie',include_fuzzy_string=False):
    new_s=[]
    N=len(fuzzy_string.split(' '))
    for i in range(0,len(l)-N):
        w=l[i:i+N]
        sentence=' '.join(w)
        ratio = fuzz.token_sort_ratio(sentence, fuzzy_string)
        print(sentence)
        if ratio>80:
            break
        w=[i.strip() for i in sentence.split(' ')]
        new_s.append(w[0])
    if include_fuzzy_string:
        new_s.append(fuzzy_string)
    return ' '.join(new_s)  


# returns part of a string that's behind a fuzzy string 
def fuzzy_startoff(s,fuzzy_string='liftvault',include_fuzzy_string=False):
    new_s=[]
    N=len(fuzzy_string.split(' '))
    bl=0
    for i in range(0,len(l)-N):
        w=l[i:i+N]
        sentence=' '.join(w)
        ratio = fuzz.token_sort_ratio(sentence, fuzzy_string)
        print(sentence)
        if ratio>80:
            bl=1
            if not include_fuzzy_string:
                continue
        w=[i.strip() for i in sentence.split(' ')]
        if bl:
            new_s.append(w[0])
    if include_fuzzy_string:
        new_s.append(fuzzy_string)
    return ' '.join(new_s)  


x=fuzzy_startoff(s=s)
print(x)