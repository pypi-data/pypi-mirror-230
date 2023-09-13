
from iotellme import *
token='8eac160ca6a916e48eef5cc4b81e81bb0698e4d6c081862c3dbe8b877d398c8f'
users_id=1066
value=88
id1=1636
iotellme.Token(token,users_id)
iotellme.Read1(id1)
iotellme.Read()
print(iotellme.R["v1"])