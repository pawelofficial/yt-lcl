import torch 



def chunkify(t,n=3,ovr=0.1):
    n=n-1
    L=t.shape[1]        # len of tensor 
    q=L//n+1            # index multiplier 
    e=0                 # end index of tensor 
    i=-1                # index declaration 
    overlap=int(ovr*L)  # overlap in percentages 
    chunks=[]           # list to store subtensors 
    while e < L: 
        i+=1
        s=i* q - (overlap if i > 0 else 0)  
        e=(i+1) * q 
        t1=t[:,s:e]
        print(t1.shape,s,e,q)
        chunks.append(t1)
    return chunks
    
def chunkify2(t,n=3,ovr=0.1):
    n=n-1
    L=t.shape[1]        # len of tensor 
    q=L//n+1            # index multiplier 
    e=0                 # end index of tensor 
    i=-1                # index declaration 
    overlap=int(ovr*L)  # overlap in percentages 
    indices=[]           # list to store subtensors 
    while e < L: 
        i+=1
        s=i* q - (overlap if i > 0 else 0)  
        e=(i+1) * q 
        indices.append([s,e] )
    return indices
    
    
# 0 N, N+1 2N 

t = torch.rand(100).reshape(1,-1)

print(t.shape)

inds=chunkify2(t,10,ovr=0.1)
print(inds)



