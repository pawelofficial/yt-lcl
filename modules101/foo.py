
#import enhancer 
#import enhancer.effects.effect1 as ef1
#from enhancer.filters import filter1
#from enhancer.formats.format1 import main
#
#ef1.main()
#filter1.main()
#main()

# one way to do import 


#from enhancer.effects import * 
#effect1.help()

print(dir())


import enhancer as e 

e.effect1.dupa()
e.effect1.d()


import wizard
w=wizard.wizard()
w.download_vid()




#w.download_vid(url : str )
#w.convert_to_wav(filename: str)
#w.speech_to_text(filename : str)
#w.diarizize(filename : str)
#w.find_words(filename: str, words : list)
#w.make_shorts(filename : str, words : list, left:int,right:int,diarize : Bool)
#    w.make_shorts(from_transcript = True,transcript=t, **kwargs)
#    w.make_shorts(from_timestamps=True, timestamps=t,**kwargs)
#w.enhance_sound(config=config.json)


