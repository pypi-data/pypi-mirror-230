import numpy as np

input_shape = (5,5,3)
output_shape = (3,3,1)
result = np.zeros(output_shape)
result_s = np.zeros(output_shape)

a = np.zeros(input_shape)

all_sum = 0
for x in range(1,4):
    for y in range(1,4):
        for k in range(3):
            a[x,y,k]=x+y+k
            all_sum+=x+y+k

b = np.ones((1,3,3,3))

#b = np.random.rand(1,3,3,3)
print('All_sum',all_sum)
print('A:',a)

x = 1
y = 1

for x in range(result.shape[0]):
    for y in range(result.shape[1]):
        for p in range(b.shape[0]): 
            s=0


            #TODO: moltiplicare per lo stride
            delta_i = int((b.shape[1]-1)/2)
            delta_j = int((b.shape[2]-1)/2)
            
            range_i = range(x,x+b.shape[1])
            range_j = range(y,y+b.shape[2])

            #range_i = range(x-delta_i,x+delta_i+1)
            #range_j = range(y-delta_j,y+delta_j+1)

            #range_i = range(x-1,x+b.shape[1]-1)
            #range_j = range(y-1,y+b.shape[2]-1)

            #TODO: capire cosa si sbaglia nei bordi

            #todo: aggiungere lo step
            for i in range_i:
                for j in range_j:
                    for k in range(b.shape[3]):
                        #s+=1
                        #s += a[i+x,j+y,k]*b[i,j,k,p]
                        #s+=1
                    
                        #s+=1
                        #s += M[np.int8(a[i,j,k]+128),np.int8(b[p,i+1,j+1,k]+128)]

                        s += a[i,j,k]*b[p,i-x,j-y,k]

            result_s[x,y,p]=s

print('risultato conv:')
print(result_s)


result_s2 = np.zeros(output_shape)
#print('r',result[0][0])

input_shape = (3,3,3)
a = np.zeros(input_shape)

all_sum = 0
for x in range(3):
    for y in range(3):
        for k in range(3):
            a[x,y,k]=2+x+y+k
            all_sum+=2+x+y+k

for x in range(result.shape[0]):
    for y in range(result.shape[1]):
        for p in range(b.shape[0]): 
            s=0


            #TODO: moltiplicare per lo stride
            delta_i = (b.shape[1]-1)//2
            delta_j = (b.shape[2]-1)//2
            
            range_i = range(max(0,x-delta_i),min(x+delta_i+1,a.shape[1]))
            range_j = range(max(0,y-delta_j),min(y+delta_j+1,a.shape[2]))

            #range_i = range(x-delta_i,x+delta_i+1)
            #range_j = range(y-delta_j,y+delta_j+1)

            offset_i=x-delta_i
            offset_j=y-delta_j

            #TODO: capire cosa si sbaglia nei bordi

            #todo: aggiungere lo step
            for i in range_i:
                for j in range_j:
                    for k in range(b.shape[3]):
                        #s+=1
                        #s += a[i+x,j+y,k]*b[i,j,k,p]
                        #s+=1
                    
                        #s+=1
                        #s += M[np.int8(a[i,j,k]+128),np.int8(b[p,i+1,j+1,k]+128)]

                        s += a[i,j,k]*b[p,i-offset_i,j-offset_j,k]

            result_s2[x,y,p]=s

print('risultato conv 2:')
print(result_s2)

print("Test Pass:",(result_s==result_s2).all())