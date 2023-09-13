
import time
from iotellme import *
import random
token='8eac160ca6a916e48eef5cc4b81e81bb0698e4d6c081862c3dbe8b877d398c8f'
users_id=1066
id1=1642
id2=1641
id3=1640
id4=1639
id5=1638
while True:
    value=random.randint(1,100)
    iotellme.Token(token,users_id)
    iotellme.Write1(id1,value)
    iotellme.Write2(id2,value)
    iotellme.Write3(id3,value)
    iotellme.Write4(id4,value)
    iotellme.Write5(id5,value)
    iotellme.Send()
    iotellme.Read1(id1)
    iotellme.Read2(id2)
    iotellme.Read3(id3)
    iotellme.Read4(id3)
    iotellme.Read5(id3)
    iotellme.Read()
    print('v1=',iotellme.R["v1"],'v2=',iotellme.R["v2"],'v3=',iotellme.R["v3"],'v4=',iotellme.R["v4"],'v5=',iotellme.R["v5"])
    time.sleep(1)