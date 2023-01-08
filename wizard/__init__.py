


from .utils import * 
from .wizard import wizard




#if __package__=='wizard':                               # imports when run as package
#    from .utils import setup_logger,log_variable     
#else:                                                   # import when ran as script and from other scripts
#    from utils import log_variable,setup_logger
#class xxx:
#    def __init__(self) -> None:
#        self.vids_dir=os.getcwd().replace("\\","\\\\")+'\\\\vids\\\\'
#        self.logger=setup_logger(name='xxx_logger',log_file='xxx_logger.log')
#
#    # logs a variable 
#    def log_variable(self,var,msg='',wait=False,lvl='INFO'):
#        log_variable(logger=self.logger,var=var,msg='',wait=False,lvl=lvl)


#if __name__=='__main__':
#    myxxx=xxx()