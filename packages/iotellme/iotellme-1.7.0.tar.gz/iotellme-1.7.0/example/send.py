
from iotellme import *
token='8eac160ca6a916e48eef5cc4b81e81bb0698e4d6c081862c3dbe8b877d398c8f'
users_id=1
value=40
id1=3621
iotellme.Token(token,users_id)
iotellme.Write1(id1,value)
iotellme.Send()