import requests
import json
import re
class iotellme():
    def clean_users_id(self,value):
        if(isinstance(value, int)==True): 
            regex = re.compile('^[0-9]{1,11}$', re.I)
            users_id_match = regex.match(str(value))
            if(bool(users_id_match)):
                return value
            else:
                print('error users_id')
        else:
            print('error int users_id')
    def clean_id(self,value):
        if(isinstance(value, int)==True): 
            regex = re.compile('^[0-9]{1,11}$', re.I)
            id_match = regex.match(str(value))
            if(bool(id_match)):
                return value
            else:
                print('error id')
        else:
            print('error int id')
    def clean_value(self,value):
        if(isinstance(value, int)==True or isinstance(value, float)==True): 
            regex = re.compile('[0-9]\.?[0-9]?', re.I)
            id_match = regex.match(str(value))
            if(bool(id_match)):
                return value
            else:
                print('error value')
        else:
            print('error int value')

    def clean_token(self,value):
        if(isinstance(value, str)==True): 
            regex = re.compile('^[a-z-0-9]{40,100}$', re.I)
            token_match = regex.match(str(value))
            if(bool(token_match)):
                return value
            else:
                print('error token')
        else:
            print('error str token')
    def Token(self,token,users_id):
            self.cloud='https://api.iotellme.net/'
            self.url = f'{self.cloud}send?users_id={self.clean_users_id(users_id)}&token={self.clean_token(token)}'
            self.write=self.url
            print(self.write)
            #read
            self.read_url=f'{self.cloud}read?users_id={self.clean_users_id(users_id)}&token={self.clean_token(token)}'
            self.read=self.read_url

    def Write1(self,id,v,s=0):
            self.write= self.write+f'&id1={self.clean_id(id)}&v1={self.clean_value(v)}&s1={self.clean_value(s)}'
            
    def Write2(self,id,v,s=0):
            self.write= self.write+f'&id2={self.clean_id(id)}&v2={self.clean_value(v)}&s2={self.clean_value(s)}'

    def Write3(self,id,v,s=0):
            self.write= self.write+f'&id3={self.clean_id(id)}&v3={self.clean_value(v)}&s3={self.clean_value(s)}'

    def Write4(self,id,v,s=0):
            self.write= self.write+f'&id4={self.clean_id(id)}&v4={self.clean_value(v)}&s4={self.clean_value(s)}'
            
    def Write5(self,id,v,s=0):
            self.write= self.write+f'&id5={self.clean_id(id)}&v5={self.clean_value(v)}&s5={self.clean_value(s)}'

    def Write6(self,id,v,s=0):
            self.write= self.write+f'&id6={self.clean_id(id)}&v6={self.clean_value(v)}&s6={self.clean_value(s)}'

    def Write7(self,id,v,s=0):
            self.write= self.write+f'&id7={self.clean_id(id)}&v7={self.clean_value(v)}&s7={self.clean_value(s)}'

    def Write8(self,id,v,s=0):
            self.write= self.write+f'&id8={self.clean_id(id)}&v8={self.clean_value(v)}&s8={self.clean_value(s)}'

    def Write9(self,id,v,s=0):
            self.write= self.write+f'&id9={self.clean_id(id)}&v9={self.clean_value(v)}&s9={self.clean_value(s)}'

    def Write10(self,id,v,s=0):
            self.write= self.write+f'&id10={self.clean_id(id)}&v10={self.clean_value(v)}&s10={self.clean_value(s)}'

    def Write11(self,id,v,s=0):
            self.write= self.write+f'&id11={self.clean_id(id)}&v11={self.clean_value(v)}&s11={self.clean_value(s)}'

    def Write12(self,id,v,s=0):
            self.write= self.write+f'&id12={self.clean_id(id)}&v12={self.clean_value(v)}&s12={self.clean_value(s)}'

    def Write13(self,id,v,s=0):
            self.write= self.write+f'&id13={self.clean_id(id)}&v13={self.clean_value(v)}&s13={self.clean_value(s)}'

    def Write14(self,id,v,s=0):
            self.write= self.write+f'&id14={self.clean_id(id)}&v14={self.clean_value(v)}&s14={self.clean_value(s)}'

    def Write15(self,id,v,s=0):
            self.write= self.write+f'&id15={self.clean_id(id)}&v15={self.clean_value(v)}&s15={self.clean_value(s)}'

    def Write16(self,id,v,s=0):
            self.write= self.write+f'&id16={self.clean_id(id)}&v16={self.clean_value(v)}&s16={self.clean_value(s)}'

    def Write17(self,id,v,s=0):
            self.write= self.write+f'&id17={self.clean_id(id)}&v17={self.clean_value(v)}&s17={self.clean_value(s)}'

    def Write18(self,id,v,s=0):
            self.write= self.write+f'&id18={self.clean_id(id)}&v18={self.clean_value(v)}&s18={self.clean_value(s)}'

    def Write19(self,id,v,s=0):
            self.write= self.write+f'&id19={self.clean_id(id)}&v19={self.clean_value(v)}&s19={self.clean_value(s)}'

    def Write20(self,id,v,s=0):
            self.write= self.write+f'&id20={self.clean_id(id)}&v20={self.clean_value(v)}&s20={self.clean_value(s)}'

    def Write21(self,id,v,s=0):
            self.write= self.write+f'&id21={self.clean_id(id)}&v21={self.clean_value(v)}&s21={self.clean_value(s)}'

    def Write22(self,id,v,s=0):
            self.write= self.write+f'&id22={self.clean_id(id)}&v22={self.clean_value(v)}&s22={self.clean_value(s)}'

    def Write23(self,id,v,s=0):
            self.write= self.write+f'&id23={self.clean_id(id)}&v23={self.clean_value(v)}&s23={self.clean_value(s)}'

    def Write24(self,id,v,s=0):
            self.write= self.write+f'&id24={self.clean_id(id)}&v24={self.clean_value(v)}&s24={self.clean_value(s)}'

    def Write25(self,id,v,s=0):
            self.write= self.write+f'&id25={self.clean_id(id)}&v25={self.clean_value(v)}&s25={self.clean_value(s)}'

    def Write26(self,id,v,s=0):
            self.write= self.write+f'&id26={self.clean_id(id)}&v26={self.clean_value(v)}&s26={self.clean_value(s)}'

    def Write27(self,id,v,s=0):
            self.write= self.write+f'&id27={self.clean_id(id)}&v27={self.clean_value(v)}&s27={self.clean_value(s)}'

    def Write28(self,id,v,s=0):
            self.write= self.write+f'&id28={self.clean_id(id)}&v28={self.clean_value(v)}&s28={self.clean_value(s)}'

    def Write29(self,id,v,s=0):
            self.write= self.write+f'&id29={self.clean_id(id)}&v29={self.clean_value(v)}&s29={self.clean_value(s)}'

    def Write30(self,id,v,s=0):
            self.write= self.write+f'&id30={self.clean_id(id)}&v30={self.clean_value(v)}&s30={self.clean_value(s)}'

    def Write31(self,id,v,s=0):
            self.write= self.write+f'&id31={self.clean_id(id)}&v31={self.clean_value(v)}&s31={self.clean_value(s)}'

    def Write32(self,id,v,s=0):
            self.write= self.write+f'&id32={self.clean_id(id)}&v32={self.clean_value(v)}&s32={self.clean_value(s)}'

    def Write33(self,id,v,s=0):
            self.write= self.write+f'&id33={self.clean_id(id)}&v33={self.clean_value(v)}&s33={self.clean_value(s)}'

    def Write34(self,id,v,s=0):
            self.write= self.write+f'&id34={self.clean_id(id)}&v34={self.clean_value(v)}&s34={self.clean_value(s)}'

    def Write35(self,id,v,s=0):
            self.write= self.write+f'&id35={self.clean_id(id)}&v35={self.clean_value(v)}&s35={self.clean_value(s)}'

    def Write36(self,id,v,s=0):
            self.write= self.write+f'&id36={self.clean_id(id)}&v36={self.clean_value(v)}&s36={self.clean_value(s)}'

    def Write37(self,id,v,s=0):
            self.write= self.write+f'&id37={self.clean_id(id)}&v37={self.clean_value(v)}&s37={self.clean_value(s)}'

    def Write38(self,id,v,s=0):
            self.write= self.write+f'&id38={self.clean_id(id)}&v38={self.clean_value(v)}&s38={self.clean_value(s)}'

    def Write39(self,id,v,s=0):
            self.write= self.write+f'&id39={self.clean_id(id)}&v39={self.clean_value(v)}&s39={self.clean_value(s)}'

    def Write40(self,id,v,s=0):
            self.write= self.write+f'&id40={self.clean_id(id)}&v40={self.clean_value(v)}&s40={self.clean_value(s)}'

    def Write41(self,id,v,s=0):
            self.write= self.write+f'&id41={self.clean_id(id)}&v41={self.clean_value(v)}&s41={self.clean_value(s)}'

    def Write42(self,id,v,s=0):
            self.write= self.write+f'&id42={self.clean_id(id)}&v42={self.clean_value(v)}&s42={self.clean_value(s)}'

    def Write43(self,id,v,s=0):
            self.write= self.write+f'&id43={self.clean_id(id)}&v43={self.clean_value(v)}&s43={self.clean_value(s)}'

    def Write44(self,id,v,s=0):
            self.write= self.write+f'&id44={self.clean_id(id)}&v44={self.clean_value(v)}&s44={self.clean_value(s)}'

    def Write45(self,id,v,s=0):
            self.write= self.write+f'&id45={self.clean_id(id)}&v45={self.clean_value(v)}&s45={self.clean_value(s)}'

    def Write46(self,id,v,s=0):
            self.write= self.write+f'&id46={self.clean_id(id)}&v46={self.clean_value(v)}&s46={self.clean_value(s)}'

    def Write47(self,id,v,s=0):
            self.write= self.write+f'&id47={self.clean_id(id)}&v47={self.clean_value(v)}&s47={self.clean_value(s)}'

    def Write48(self,id,v,s=0):
            self.write= self.write+f'&id48={self.clean_id(id)}&v48={self.clean_value(v)}&s48={self.clean_value(s)}'

    def Write49(self,id,v,s=0):
            self.write= self.write+f'&id49={self.clean_id(id)}&v49={self.clean_value(v)}&s49={self.clean_value(s)}'

    def Write50(self,id,v,s=0):
            self.write= self.write+f'&id40={self.clean_id(id)}&v40={self.clean_value(v)}&s40={self.clean_value(s)}'

########################################################################################################
    def Read1(self,id):
           self.read=self.read+f'&id1={self.clean_id(id)}'

    def Read2(self,id):
           self.read=self.read+f'&id2={self.clean_id(id)}'

    def Read3(self,id):
           self.read=self.read+f'&id3={self.clean_id(id)}'

    def Read4(self,id):
           self.read=self.read+f'&id4={self.clean_id(id)}'

    def Read5(self,id):
           self.read=self.read+f'&id5={self.clean_id(id)}'

    def Read6(self,id):
           self.read=self.read+f'&id6={self.clean_id(id)}'

    def Read7(self,id):
           self.read=self.read+f'&id7={self.clean_id(id)}'

    def Read8(self,id):
           self.read=self.read+f'&id8={self.clean_id(id)}'

    def Read9(self,id):
           self.read=self.read+f'&id9={self.clean_id(id)}'

    def Read10(self,id):
           self.read=self.read+f'&id10={self.clean_id(id)}'

    def Read11(self,id):
           self.read=self.read+f'&id11={self.clean_id(id)}'

    def Read12(self,id):
           self.read=self.read+f'&id12={self.clean_id(id)}'

    def Read13(self,id):
           self.read=self.read+f'&id13={self.clean_id(id)}'

    def Read14(self,id):
           self.read=self.read+f'&id14={self.clean_id(id)}'

    def Read15(self,id):
           self.read=self.read+f'&id15={self.clean_id(id)}'

    def Read16(self,id):
           self.read=self.read+f'&id16={self.clean_id(id)}'

    def Read17(self,id):
           self.read=self.read+f'&id17={self.clean_id(id)}'

    def Read18(self,id):
           self.read=self.read+f'&id18={self.clean_id(id)}'

    def Read19(self,id):
           self.read=self.read+f'&id19={self.clean_id(id)}'

    def Read20(self,id):
           self.read=self.read+f'&id20={self.clean_id(id)}'

    def Read21(self,id):
           self.read=self.read+f'&id21={self.clean_id(id)}'

    def Read22(self,id):
           self.read=self.read+f'&id22={self.clean_id(id)}'

    def Read23(self,id):
           self.read=self.read+f'&id23{self.clean_id(id)}'

    def Read24(self,id):
           self.read=self.read+f'&id24={self.clean_id(id)}'

    def Read25(self,id):
           self.read=self.read+f'&id25={self.clean_id(id)}'

    def Read26(self,id):
           self.read=self.read+f'&id26={self.clean_id(id)}'

    def Read27(self,id):
           self.read=self.read+f'&id27={self.clean_id(id)}'

    def Read28(self,id):
           self.read=self.read+f'&id28={self.clean_id(id)}'

    def Read29(self,id):
           self.read=self.read+f'&id29={self.clean_id(id)}'

    def Read30(self,id):
           self.read=self.read+f'&id30={self.clean_id(id)}'

    def Read31(self,id):
           self.read=self.read+f'&id31={self.clean_id(id)}'

    def Read32(self,id):
           self.read=self.read+f'&id32={self.clean_id(id)}'

    def Read33(self,id):
           self.read=self.read+f'&id33={self.clean_id(id)}'

    def Read34(self,id):
           self.read=self.read+f'&id34={self.clean_id(id)}'

    def Read35(self,id):
           self.read=self.read+f'&id35={self.clean_id(id)}'

    def Read36(self,id):
           self.read=self.read+f'&id36={self.clean_id(id)}'

    def Read37(self,id):
           self.read=self.read+f'&id37={self.clean_id(id)}'

    def Read38(self,id):
           self.read=self.read+f'&id38={self.clean_id(id)}'

    def Read39(self,id):
           self.read=self.read+f'&id39={self.clean_id(id)}'

    def Read40(self,id):
           self.read=self.read+f'&id40={self.clean_id(id)}'

    def Read41(self,id):
           self.read=self.read+f'&id41={self.clean_id(id)}'

    def Read42(self,id):
           self.read=self.read+f'&id42={self.clean_id(id)}'

    def Read43(self,id):
           self.read=self.read+f'&id43={self.clean_id(id)}'

    def Read44(self,id):
           self.read=self.read+f'&id404{self.clean_id(id)}'

    def Read45(self,id):
           self.read=self.read+f'&id45={self.clean_id(id)}'

    def Read46(self,id):
           self.read=self.read+f'&id46={self.clean_id(id)}'

    def Read47(self,id):
           self.read=self.read+f'&id47={self.clean_id(id)}'

    def Read48(self,id):
           self.read=self.read+f'&id48={self.clean_id(id)}'

    def Read49(self,id):
           self.read=self.read+f'&id49={self.clean_id(id)}'

    def Read50(self,id):
           self.read=self.read+f'&id50={self.clean_id(id)}'
    def Read(self):
        try:
            ressendbtn1 = requests.get(self.read)
            read= ressendbtn1.content
            self.R = json.loads(read)
        except Exception as e:
            print("No Internet Read")
            
    def Send(self):
        self.write= self.write 
        try:
            requests.get(self.write)
        except Exception as e:
            print("No Internet Send")

iotellme=iotellme()