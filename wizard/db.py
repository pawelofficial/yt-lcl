import sqlite3 

if __package__=='wizard':                               # imports when run as package
    from .utils import setup_logger,log_variable,path_join     
else:                                                   # import when ran as script and from other scripts
    from utils import log_variable,setup_logger,path_join




class db:
    def __init__(self) -> None:
        self.db_dir = path_join(l=['db'])
        self.db_fp = path_join(l=['db','temp.db'])
        self.con=self.con(db='sqlite')
        
        self.cur=self.con.cursor()  
        self.sqls={                                                 # USEFUL SQLS 
            "CREATE_CHANNEL_TABLE": lambda channel_name:            # CREATE CHANNEL TABLE 
                f"""       
                CREATE TABLE  {channel_name} (
                    ID varchar(20) PRIMARY KEY, 
                    TITLE varchar(500), 
                    URL varchar(500),
                    UPLOAD_DT date,
                    PARSED_TRANSCRIPT text,
                    RAW_TRANSCRIPT text
                    );"""
        }
        
        
    def con(self,db='slqite'):
        if db=='sqlite':
            return self.sqlite_con()
        
    def sqlite_con(self):
        return sqlite3.connect(self.db_fp)
        
    def drop_table(self,table_name):
        self.cur.execute(f"DROP TABLE {table_name};")
    
    def truncate_table(self,table_name):
        s=f'TRUNCATE TABLE {table_name};'
    
    # inserts wrapper 
    def insert_into(self,table_name,**kwargs):
        for k,v in kwargs.items():
            if k=='column':
                self.insert_into_l(table_name=table_name,**kwargs)
                return 
            if k=='d':
                self.insert_into_d(table_name=table_name,**kwargs)
                return 
            
    # inserts list into a table 
    def insert_into_l(self,table_name,column,values ):
        for i in values:
            i=i.replace('\'','\'\'')
            s=f"""INSERT INTO {table_name}({column}) values( \'{i  }\' ) ;"""
            self.cur.execute(s)    
            self.con.commit()
            
    # inserts dictionary into a table 
    def insert_into_d(self,table_name,d):
        f=  lambda s: s.replace('\'','\'\'') # removes backslashes 
        columns=', '.join(list(d.keys()))
        values = ', '.join([ f' \'{f(v)}\' ' for v in list(d.values())  ] ) 
        
        
        s=f"""INSERT INTO {table_name}({columns}) values( {values} ) ;"""
#        print(s)
        self.cur.execute(s)
        self.con.commit()
            
    def select_star(self,table_name):
        s=f'SELECT * FROM {table_name};'
        o=self.cur.execute(s)
        return o.fetchall()

    
    def select_antijoin(self,table_name,column_name,l) -> list : # SELECT C1 FROM TABLE WHERE C1 NOT IN ( ... ); 
        values = ', '.join([ f' \'{v}\' ' for v in  l ] ) 
        s=f'SELECT {column_name} FROM {table_name} WHERE {column_name} IN ({values} );'
        o=self.cur.execute(s).fetchall()
        
        output=[t[0] for t in o]
        
        return [i for i in l if i not in output]
        
    
if __name__=='__main__':
    db=db()
#    o=db.select_star(table_name='TEST')
#    print(o)
    db.drop_table('TEST')
    db.cur.execute(db.sqls['CREATE_CHANNEL_TABLE']('TEST'))
    exit(1)
    
####
#    l=[ 'CAQCwY8Ci34', '__KpRarNkWE', 'f5PzRYoMUUU', 'zHO8nvovAmo', '_5sQe_mGqFk', 'XpQ7YCXx9Zg', 'vlxs2PSz78s', '2jG63mYbf2E', '6IeEIRkzkj8', 'g2sR-5nnUvo', 'LUDfMCmtzSs', '2w0m_LmtP4k', 'u8qcRy9jg9M', '_vKjUCZJ8Jw', 'UTjVuiaNDOI', 'kkC3Mn9zDOA', 'YaNXa4yLv-w', 'hs0QqDicAPk', 'kHqlUHxaSGE', 'Umcn3jHf_xk']
#    db.insert_into(table_name='TEST',column='ID',values=l)
    
    
    l2=['ENwb4vWeHc0', 'CAQCwY8Ci34', '__KpRarNkWE', 'f5PzRYoMUUU', 'zHO8nvovAmo', '_5sQe_mGqFk', 'XpQ7YCXx9Zg', 'vlxs2PSz78s', '2jG63mYbf2E', '6IeEIRkzkj8', 'g2sR-5nnUvo', 'LUDfMCmtzSs', '2w0m_LmtP4k', 'u8qcRy9jg9M', '_vKjUCZJ8Jw', 'UTjVuiaNDOI', 'kkC3Mn9zDOA', 'YaNXa4yLv-w', 'hs0QqDicAPk', 'kHqlUHxaSGE', 'Umcn3jHf_xk']
    o=db.select_antijoin(table_name='TEST',column_name='ID',l=l2)
    print(o)
    exit(1)

    
    db.drop_table('TEST')
    db.cur.execute(db.sqls['CREATE_CHANNEL_TABLE']('TEST'))
    
    # insert a list to a table 
    # 'ENwb4vWeHc0': '20230106', 'CAQCwY8Ci34': '20230105', '__KpRarNkWE': '20230104',  - wywalone 
    d={'f5PzRYoMUUU': '20230104', 'zHO8nvovAmo': '20230103', '_5sQe_mGqFk': '20230101', 'XpQ7YCXx9Zg': '20221230'}
    l=list(d.keys())    
    l=[ 'CAQCwY8Ci34', '__KpRarNkWE', 'f5PzRYoMUUU', 'zHO8nvovAmo', '_5sQe_mGqFk', 'XpQ7YCXx9Zg', 'vlxs2PSz78s', '2jG63mYbf2E', '6IeEIRkzkj8', 'g2sR-5nnUvo', 'LUDfMCmtzSs', '2w0m_LmtP4k', 'u8qcRy9jg9M', '_vKjUCZJ8Jw', 'UTjVuiaNDOI', 'kkC3Mn9zDOA', 'YaNXa4yLv-w', 'hs0QqDicAPk', 'kHqlUHxaSGE', 'Umcn3jHf_xk']
    l=[ 'CAQCwY8Ci34', '__KpRarNkWE', 'f5PzRYoMUUU', 'zHO8nvovAmo', '_5sQe_mGqFk', 'XpQ7YCXx9Zg', 'vlxs2PSz78s', '2jG63mYbf2E', '6IeEIRkzkj8', 'g2sR-5nnUvo', 'LUDfMCmtzSs', '2w0m_LmtP4k', 'u8qcRy9jg9M', '_vKjUCZJ8Jw', 'UTjVuiaNDOI', 'kkC3Mn9zDOA', 'YaNXa4yLv-w', 'hs0QqDicAPk', 'kHqlUHxaSGE', 'Umcn3jHf_xk']
    
    db.insert_into('TEST',column='ID',values = l)

    l2=['ENwb4vWeHc0', 'CAQCwY8Ci34', '__KpRarNkWE', 'f5PzRYoMUUU', 'zHO8nvovAmo', '_5sQe_mGqFk', 'XpQ7YCXx9Zg', 'vlxs2PSz78s', '2jG63mYbf2E', '6IeEIRkzkj8', 'g2sR-5nnUvo', 'LUDfMCmtzSs', '2w0m_LmtP4k', 'u8qcRy9jg9M', '_vKjUCZJ8Jw', 'UTjVuiaNDOI', 'kkC3Mn9zDOA', 'YaNXa4yLv-w', 'hs0QqDicAPk', 'kHqlUHxaSGE', 'Umcn3jHf_xk']    
#    l2=['f5PzRYoMUUU', 'zHO8nvovAmo', '_5sQe_mGqFk', 'XpQ7YCXx9Zg','FOO']
    o=db.select_antijoin(table_name='TEST',column_name='ID',l=l2)
    print(o)
#    l2=[l[0],l[1]]
#    o=db.select_antijoin(table_name='TEST',column_name='ID',l=l2)
    # insert a d to a table 
#    d={'ID':'1','TITLE':'FOO','URL':'FOO','PARSED_TRANSCRIPT':'FOO'}
#    db.insert_into_d('TEST',d)
#    d={'ID':'2','TITLE':'FOO','URL':'FOO','PARSED_TRANSCRIPT':'FOO'}
#    db.insert_into_d('TEST',d)
#    d={'ID':'3','TITLE':'FOO','URL':'FOO','PARSED_TRANSCRIPT':'FOO'}
#    db.insert_into_d('TEST',d)
    
#    o=db.select_star(table_name='TEST')
#    print(o.fetchall())
    