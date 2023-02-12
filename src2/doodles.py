    # moving a row up or down based on condition on that row 
    def _concat_on_condition(self,df,cond):
        # concatenates one word rows 
        no=0
        #cond = lambda x: len(x['txt'].split())<=3
        #cond = lambda x: x['pause_flt']<=0.1
        indexes_to_remove = []
        while no < len(df)-1:
            if no ==0:
                prev_row={}
                prev_row['en_flt'] = -999 # making sure dif1 does not happen 
            else:
                prev_row=df.iloc[no-1].to_dict()
            cur_row=df.iloc[no].to_dict()
            next_row=df.iloc[no+1].to_dict()
            txt=cur_row['txt']
            while cond(prev_row,cur_row,next_row):
                dif1=cur_row['st_flt']-prev_row['en_flt']
                dif2=next_row['st_flt'] - cur_row['en_flt']
                indexes_to_remove.append(no)
                if dif1<=dif2:
                    prev_row['txt']=prev_row['txt']+' ' + cur_row['txt']
                    prev_row['en_flt']=cur_row['en_flt']
                    df.iloc[no-1]=prev_row
                else:
                    next_row['txt']=cur_row['txt'] + ' ' + next_row['txt']
                    next_row['st_flt']=cur_row['st_flt']
                    df.iloc[no+1] = next_row
                no+=1
                if no==len(df)-1:
                    break
                prev_row=df.iloc[no-1].to_dict()
                cur_row=df.iloc[no].to_dict()
                next_row=df.iloc[no+1].to_dict()
                txt=cur_row['txt']
            no +=1 
            if no==len(df)-1:
                break