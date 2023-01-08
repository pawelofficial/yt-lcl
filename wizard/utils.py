import logging 
import datetime 
import os 
import datetime
import re 
# sets up logger 
def setup_logger(name, log_file, level=logging.INFO):
    log_file=os.getcwd()+'/wizard/logs/'+log_file
    handler = logging.FileHandler(log_file)        
    BASIC_FORMAT = "%(levelname)s:%(name)s:%(message)s"  
    formatter=logging.Formatter(BASIC_FORMAT)
    handler.setFormatter(formatter)
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    return logger

# logs a variable so i can read it 
def log_variable(logger,var,msg='',wait=False,lvl='info'):
    ts=datetime.datetime.now().isoformat()
    if var is None:
        var='None'
    s= f' {msg} {ts} \n{var}'
    if lvl=='warning':
        logger.warning(s)
    else:
        logger.info(s)
    if wait:
        print(s)
        input('waiting in log ')
        

def path_join(l):        
    current_dir = os.path.dirname(os.path.abspath(__file__))
    path_join = lambda l : os.path.join(current_dir,*l).replace('\\','\\\\')
    return path_join(l)
        
        
def parse_url(url):
    #    url='https://www.youtube.com/watch?v=AjmpznRmAIQ&ab_channel=KitcoNEWS'
    #    url='https://www.youtube.com/watch?v=AjmpznRmAIQ'
    #    url='https://www.youtube.com/@kitco'
    id_reg=r'v=([^&]+)'
    channel_reg=r'ab_channel=(.*)|(\@.*)'
    url_reg=r'\&ab_channel.*'
    base_reg=r'(.*com/)'
    id=re.findall(id_reg,url)
    #print('id: ', id)
    channel=re.findall(channel_reg,url)
    #print('channel: ',channel)
    url=re.sub(url_reg,'',url)
    #print('url: ',url)
    base=re.findall(base_reg,url)[0]
    
    if id==[]:
        id=None 
    else:
        id=id[0]
        
    if channel==[]:
        channel=None
    else:
        channel=max(channel[0])
    return id,channel,url,base
    
def build_url(s,from_id=True):
    if from_id:
        return f'https://www.youtube.com/watch?v={s}'
    
        
from functools import wraps
def type_check(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        for i, (arg, hint) in enumerate(zip(args, func.__annotations__.values())):
            if not isinstance(arg, hint):
                raise TypeError(f"Argument {i+1} of {func.__name__} must be {hint.__name__}")
        return func(*args, **kwargs)
    return wrapper

#@type_check
#def f ( x : str ):
#    print(x)
#    
if __name__=='__main__':
    url='https://www.youtube.com/watch?v=AjmpznRmAIQ&ab_channel=KitcoNEWS'
    id,channel,url,base = parse_url(url=url)
    print(id,channel,url,base)
    
    url='https://www.youtube.com/watch?v=AjmpznRmAIQ'
    id,channel,url,base = parse_url(url=url)
    print(id,channel,url,base)

    url='https://www.youtube.com/@kitco' # should work also for https://www.youtube.com/kitco
    parse_url(url=url)
    id,channel,url,base = parse_url(url=url)
    print(id,channel,url,base)