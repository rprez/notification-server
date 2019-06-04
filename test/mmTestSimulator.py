import sys
import socket
from encodings.idna import dots

if len(sys.argv)>=4:
    print( "book file: "+ sys.argv[1])
else:
    print( "Missing param\nParam1: <bookPath>\nParam2: <IP>\nParam3: <par|impar>\n Param4: <chunk size> Optional")
    exit()

chunkSize=None
if len(sys.argv)==5:
    chunkSize=int(sys.argv[4])
    

def waitForChunk(soc,index):
    
    dataStream=""
    
    lineLen=len(dotSeparatedBook[index])  
    
    charCount=lineLen
    data=""
    while charCount>0:# falta timeout
        try:
            data=soc.recv(lineLen)
            if len(data)==0:
                return [None,None]
            
            data=data.decode('utf-8')
            print("rx "+str(len(data))+"bytes: "+data);

            dataStream+=data
            
            if dataStream == dotSeparatedBook[index]:
                return [True,data]
            
            charCount=lineLen-len(dataStream)
        except Exception as e:
            print(e)
            print("Last data stream:\n"+dataStream)
            break
    
    return [False,data]


def chunkstring(string, length):
    return (string[0+i:length+i] for i in range(0, len(string), length))

def getAction(index,modo):
    
    if (index%2==0 and modo=="par") or (index%2==1 and modo=="impar"):
        return "SEND"
    return "RECV"

bookPath=sys.argv[1]
ip=sys.argv[2]
modo=sys.argv[3]

lineasPares=[]
lineasImpares=[]
book=open(bookPath).read()

dotSeparatedBook=book.split(".\r")
if chunkSize!=None:
    dotSeparatedBook=list(chunkstring(book, chunkSize))

count=0

for x in dotSeparatedBook:
    if count%2==0:
        lineasPares.append(x)
    else:
        lineasImpares.append(x)
    count+=1
  
    
#imparBook=open("par.txt","w+")
#imparBook.write("".join(lineasImpares));
#imparBook.close()  
    
#parBook=open("impar.txt","w+")
#parBook.write("".join(lineasPares));
#parBook.close()


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((ip, 52200))


print("Total chunck:"+str(len(dotSeparatedBook)))
s.settimeout(60.0)  
#s.setblocking(False)
testResult=True
for x in range(0,len(dotSeparatedBook)):
    
    action=getAction(x, modo)
    if action=="SEND":
        state=s.send(dotSeparatedBook[x].encode())
        if state!=None:
            print("Sended "+str(state)+" / "+str(len(dotSeparatedBook[x]))+" bytes")
    else:
        result,data=waitForChunk(s, x)
        if result==None:
            print("Error at waiting chunk "+str(x))
            break
        elif result:
            print("Success receiving chunk "+str(x))
        else:
            print("Fail at receiving chunk "+str(x))
            print("Expected:\n"+dotSeparatedBook[x]+"\nReceived:\n"+data)
            testResult=False
            break
            
print("Test Finished\nSucess:"+str(testResult))
s.close()
