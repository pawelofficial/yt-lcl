this is a yt-news-wizard project i am making 







classes:
    wizard - wrapper class for workflows of all other classes 
    ytd - youtube downloader for downloading subs from youtube 
    transcript - class for analyzing youtube transcripts 
    spark - class for all things spark 
    *utils - file with utility functions and wrappers shared everywhere 


ytd.methods:
    .download_subs 
        -> downloads subtitles from youtube 
            - in  -> subs_d : dic | url : string 
            - out -> subs_d : dic | * dumps .txt to /tmp/ 
        
transcript.methods:
    .parse_subs:
        -> parses raw subtitles from youtube 
            - in -> subs_d : dic 
            - out -> subs_d : dic | *dumps .txt to /tmp
    .scan:
        -> scans parsed subtitles for a keyword 
            - in  -> subs_d : dic , keyword : str 
            - out -> subs_d : dic 
utils.functions:
    .path_join:
        -> relative to absolute path translation
            - in  -> path_l: list 
            - out -> path_s : str 
    .parse_url:




subs_d : { 
    "ytd" : { 
        "channel":None 
        ,"url":None
        ,"id":None
        ,"base_url":None
    }
    "trs" : {
        "raw_subs":""
        ,"parsed_subs": dataframe {line_no, text, keyword1, keyword2}
    }
    
    }
