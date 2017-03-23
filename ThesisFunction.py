#!/usr/bin/python
# coding: utf-8

# In[1]:
import suds
from suds.client import Client
from suds.plugin import MessagePlugin
from suds.sax.date import UTC
class BugfixMessagePlugin(MessagePlugin):  
    def marshalled(self, context):
        tp = context.envelope.childAtPath('Body/queryRQ/transport')
        tp.setPrefix(tp.findPrefix('http://gutp.jp/fiap/2009/11/'))

myplugins = (
    BugfixMessagePlugin(),)
WSDL_URL = 'http://161.200.90.122/axis2/services/FIAPStorage?wsdl' 
client = Client(WSDL_URL, cache=None, plugins=myplugins) 

def MainLibary():
    global np,pd,logging,datetime,timedelta,calendar,client,uuid,mean_squared_error
    import logging
    import uuid 
    import numpy as np
    import pandas as pd 
    import random 
    from datetime import datetime
    from datetime import timedelta
    import calendar

    
# In[14]:
#MainLibary()
#-------------------------------------------------------------------------------------------------------
#For Check Point ID
#-------------------------------------------------------------------------------------------------------
def Create_AllPoint():
    global All_Point_ID,coll
    All_Point_ID = pd.read_csv("Data/Point_ID.csv") #import Point ID from CSV file
    All_Point_ID = All_Point_ID['0'].values
    All_Point_ID = pd.Series(All_Point_ID)
    All_Point_ID = All_Point_ID.str.rsplit('/', expand=True,n=8)
    coll = ['http', 'place','fl','direction','room','zone','kind','duty','value']
    All_Point_ID.columns = coll

def Find_PointID (place="",fl="",direction="",room="",zone="",kind="",value=""):
    result = All_Point_ID
    if place == "": pass
    else:result = result.loc[(result.place==place)]
    if fl == "":pass
    else:result = result.loc[(result.fl==fl)]
    if direction == "":pass
    else:result = result.loc[(result.direction==direction)]
    if room == "":pass
    else:result = result.loc[(result.room==room)]
    if zone =="":pass
    else:result = result.loc[(result.zone==zone)]
    if kind == "":pass
    elif kind=='Air':result = result.loc[(result.kind=="aircon1")|(result.kind=="aircon2")|(result.kind=="aircon3")|(result.kind=="aircon_3ph1")|(result.kind=="aircon_3ph2")]
    elif kind=='Light':result = result.loc[(result.kind=="light1")|(result.kind=="light2")|(result.kind=="light3")]
    elif kind=='Outlet':result = result.loc[(result.kind=="outlet1")|(result.kind=="outlet2")|(result.kind=="outlet3")]
    else:result = result.loc[(result.kind==kind)]    
    if value == "":pass
    elif value == 'energy':result = result.loc[(result.value=="energy_r")|(result.value=="energy_s")|(result.value=="energy_t")|(result.value=="energy")]
    elif value == 'pir':result = result.loc[(result.value=="PIR")|(result.value=="pir")]
    else:result = result.loc[(result.value==value)]
    Pointname = result[coll].apply(lambda x: '/'.join(x), axis=1)
    Point = []
    [Point.append(Pointname[result.index[x]]) for x in range(len(result.index))]
    ind = Pointname.index.tolist()
    Pointid = {}
    Pointid["Point_Name"] = Point
    Pointid["IND"] = ind
    return Pointid    

#-------------------------------------------------------------------------------------------------------
#For Check Data
#-------------------------------------------------------------------------------------------------------
def Check_time_in_range(start, end, x):
    if start <= end: return start <= x <= end
    else: return start <= x or x <= end    
def Check_File(qt,lt,idx):
    try:
        df = pd.read_csv('Data/%s.csv'%idx)
        df = df.set_index('TIME')
        df.index = pd.to_datetime(df.index)
        df.index.names = ['TIME']
        qt1,lt1,qt2,lt2,case,how = Check_case(df,qt,lt)
        if case == 'Case1': return 'Have Data',qt1,lt1,qt2,lt2,df,case,how
        else: return 'NO data',qt1,lt1,qt2,lt2,df,case,how
    except :return 'No file',qt,lt,"","","",'Case0','Nofile'    
def Check_case (df,qt,lt):
    result1 = Check_time_in_range(df.index[0],df.index[-1],qt)
    result2 = Check_time_in_range(df.index[0],df.index[-1],lt)
    if result1 == True and result2 == True:return qt,lt,"","",'Case1','Case อยู่ในช่วง'
    elif result1 == False and result2 == True :
        lt = df.index[0] - timedelta(minutes = 1)
        return qt,lt,"","",'Case2','Case เฟิ้ดบน'
    elif result1 == True and result2 == False :
        qt = df.index[-1] + timedelta(minutes = 1)
        return qt,lt,"","",'Case3','Case เฟิ้ดล่าง'
    elif result1 == False and result2 == False and lt  > df.index[-1] and qt  > df.index[-1] :
        qt = df.index[-1] + timedelta(minutes = 1)
        return qt,lt,"","",'Case4','Case เฟิ้ดล่างทั้งหมด'
    elif result1 == False and result2 == False and lt <df.index[0] and qt <df.index[0]:
        lt = df.index[0] - timedelta(minutes = 1)
        return qt,lt,"","",'Case5','Case เฟิ้ดบนทั้งหมด'
    elif result1 == False and result2 == False :
        qt1 = qt
        lt1 = df.index[0] - timedelta(minutes = 1)
        qt2 = df.index[-1] + timedelta(minutes = 1)
        lt2 = lt
        return qt1,lt1,qt2,lt2,'Case6','Case เฟิ้ดครอบ 2 ครั้ง'

#-------------------------------------------------------------------------------------------------------
#For Prepare Data in Dataframe format
#-------------------------------------------------------------------------------------------------------    
def Call_Dataframe (Point_ID,idx,qt,lt,ttt):
    Start_Time = datetime.now()
    qt = datetime.strptime(qt,"%Y-%m-%d %H:%M:%S") 
    lt = datetime.strptime(lt,"%Y-%m-%d %H:%M:%S")
    Count_Fetch = 0
    Count_Storage = 0
    result,qt1,lt1,qt2,lt2,df,case,how = Check_File(qt,lt,idx) 
    print result
    if result == 'Have Data':
        Table = df.loc[qt:lt]
        Count_Storage = len(Table)
    elif result == 'No file':
        Table = Fetch_His(Point_ID,lt1,qt1,ttt)
        Table = Set_Table(Table)
        Table.to_csv("Data/%s.csv"%idx) 
        Count_Fetch = len(Table)
    elif qt2 != "" and lt2 != "": 
        Table = Fetch_His(Point_ID,lt1,qt1,ttt)
        Table2 = Fetch_His(Point_ID,lt2,qt2,ttt)
        Table = Table.append(Table2)
        Table = Set_Table(Table)
        Count_Fetch = len(Table)
        df = df.append(Table)
        df = df.sort_index(axis=0)
        df.to_csv("Data/%s.csv"%idx)
        Table = df.loc[qt:lt]
        Count_Storage = len(Table)- Count_Fetch
    else :
        Table = Fetch_His(Point_ID,lt1,qt1,ttt)
        Table = Set_Table(Table)
        Count_Fetch = len(Table)
        df = df.append(Table)
        df = df.sort_index(axis=0)
        df.to_csv("Data/%s.csv"%idx)
        Table = df.loc[qt:lt]
        Count_Storage = len(Table)- Count_Fetch
    try:Table = Table.apply(pd.to_numeric)  
    except: pass
    End_Time = datetime.now() - Start_Time
    return Table,Count_Fetch,Count_Storage,End_Time.total_seconds()
def Prepare_Data(Type,Point_ID,Idx,qt,lt):
    #Table = []
    if Type =='AIR':
        #print Point_ID
        if len(Point_ID) == 1 : 
            print '---------------------------FETCH_EN_AIR1pg---------------------------'
            Point_ID = Point_ID[0]
            Idx = Idx[0]
            Table,Count_Fetch,Count_Storage,End_Time = Call_Dataframe(Point_ID,Idx,qt,lt,'AIR')
            Table = Table.apply(pd.to_numeric)
        elif len(Point_ID) != 1 : 
            Table3_ = {}      
            print '---------------------------FETCH_EN_AIR3ph---------------------------'
            Table3_[0],Count_FetchR,Count_StorageR,End_TimeR = Call_Dataframe(Point_ID[0],Idx[0],qt,lt,'AIR') #dsdsd
            Table3_[0].columns = ['R']
            Table3_[1],Count_FetchS,Count_StorageS,End_TimeS = Call_Dataframe(Point_ID[1],Idx[1],qt,lt,'AIR')
            Table3_[1].columns = ['S']
            Table3_[2],Count_FetchT,Count_StorageT,End_TimeT = Call_Dataframe(Point_ID[2],Idx[2],qt,lt,'AIR')
            Table3_[2].columns = ['T']
            Count_Fetch = Count_FetchR+Count_FetchS+Count_FetchT
            Count_Storage = Count_StorageR+Count_StorageS+Count_StorageT
            End_Time = End_TimeR+End_TimeS+End_TimeT
            for i in range(1,3):
                Table3_[0] = pd.merge(Table3_[0],Table3_[i],left_index=True, right_index=True, how='outer')
            Table3_[0] = Table3_[0].apply(pd.to_numeric)
            Table = pd.DataFrame(Table3_[0].sum(1))
            Table.columns = ['VALUE']
            #print Table
        #Table.index = Table.index.time
        #Table = Table_AIR_En.fillna(method='ffill')
    elif Type == 'LIGHT':
        print '---------------------------FETCH_LIGHT---------------------------'
        if len(Point_ID) == 1 : 
            Point_ID = Point_ID[0]
            Idx = Idx[0]
            Table,Count_Fetch,Count_Storage,End_Time = Call_Dataframe(Point_ID,Idx,qt,lt,'LIGHT')
            try:
                Table = Table.apply(pd.to_numeric)
                Table = Table.resample('1T', label='right', closed='right').mean()
                Table = Table.fillna(0)
            except:
                pass
        elif len(Point_ID) != 1 :
            Tablek_ = {}
            Count_Fetch,Count_Storage,End_Time = [],[],[]
            for k in range(len(Point_ID)):
                Tablek_[k],Count_FetchS,Count_StorageS,End_TimeS = Call_Dataframe(Point_ID[k],Idx[k],qt,lt,'LIGHT')
                try:
                    Tablek_[k] = Tablek_[k].apply(pd.to_numeric)
                    Tablek_[k].columns = ['ValueLIGHTNO%i'%(k+1)]
                    Tablek_[k] =  Tablek_[k].resample('1T', label='right', closed='right').sum()
                    Tablek_[k] = Tablek_[k].fillna(0)
                except:
                    pass
                Count_Fetch.append(Count_FetchS)
                Count_Storage.append(Count_StorageS)
                End_Time.append(End_TimeS)
            for i in range(1,len(Point_ID)):
                Tablek_[0] = pd.merge(Tablek_[0],Tablek_[i],left_index=True, right_index=True, how='outer')
            Table = pd.DataFrame(Tablek_[0].sum(1))
            Table.columns = ['VALUE']
            Count_Fetch = sum(Count_Fetch)
            Count_Storage = sum(Count_Storage)
            End_Time = sum(End_Time)
    
    elif Type == 'Outlet':
        print '---------------------------FETCH_Outlet---------------------------'
        if len(Point_ID) == 1 : 
            Point_ID = Point_ID[0]
            Idx = Idx[0]
            Table,Count_Fetch,Count_Storage,End_Time = Call_Dataframe(Point_ID,Idx,qt,lt,'Outlet')
            try:
                Table = Table.apply(pd.to_numeric)
                Table = Table.resample('1T', label='right', closed='right').mean()
                Table = Table.fillna(0)
            except:
                pass
        elif len(Point_ID) != 1 :
            Tablek_ = {}
            Count_Fetch,Count_Storage,End_Time = [],[],[]
            for k in range(len(Point_ID)):
                Tablek_[k],Count_FetchS,Count_StorageS,End_TimeS = Call_Dataframe(Point_ID[k],Idx[k],qt,lt,'Outlet')
                try:
                    Tablek_[k] = Tablek_[k].apply(pd.to_numeric)
                    Tablek_[k].columns = ['ValueOutletNO%i'%(k+1)]
                    Tablek_[k] =  Tablek_[k].resample('1T', label='right', closed='right').sum()
                    Tablek_[k] = Tablek_[k].fillna(0)
                except:
                    pass
                Count_Fetch.append(Count_FetchS)
                Count_Storage.append(Count_StorageS)
                End_Time.append(End_TimeS)
            for i in range(1,len(Point_ID)):
                Tablek_[0] = pd.merge(Tablek_[0],Tablek_[i],left_index=True, right_index=True, how='outer')
            Table = pd.DataFrame(Tablek_[0].sum(1))
            Table.columns = ['VALUE']
            Count_Fetch = sum(Count_Fetch)
            Count_Storage = sum(Count_Storage)
            End_Time = sum(End_Time)
    
    
    
    
    elif Type == 'PIR':
        print '---------------------------FETCH_PIR---------------------------'
        if len(Point_ID) == 1 : #มี PIR ตัวเดียว
            Point_ID = Point_ID[0]
            Idx = Idx[0]
            Table,Count_Fetch,Count_Storage,End_Time = Call_Dataframe(Point_ID,Idx,qt,lt,'PIR')
            Table['VALUE'] = Table['VALUE'].map({'ON': 1, 'OFF': 0})
            Table.apply(pd.to_numeric)
            Table = Table.resample('1T', label='right', closed='right').sum()
            Table = Table.fillna(0)
            Table.loc[Table['VALUE'] != 0, 'VALUE'] = 1
            Table.loc[Table['VALUE'] == 0, 'VALUE'] = -1
            #Table.index = Table.index.time
        elif len(Point_ID) != 1 :#มีPIR มากกว่า 1
            Tablek_ = {}
            Count_Fetch,Count_Storage,End_Time = [],[],[]
            for k in range(len(Point_ID)): 
                Tablek_[k],Count_FetchS,Count_StorageS,End_TimeS = Call_Dataframe(Point_ID[k],Idx[k],qt,lt,'PIR')
                Count_Fetch.append(Count_FetchS)
                Count_Storage.append(Count_StorageS)
                #print len(Tablek_[k])
                End_Time.append(End_TimeS)
                Tablek_[k].columns = ['ValuePIRNO%i'%(k+1)]
                Tablek_[k]['ValuePIRNO%i'%(k+1)] = Tablek_[k]['ValuePIRNO%i'%(k+1)].map({'ON': 1, 'OFF': 0})
                Tablek_[k].apply(pd.to_numeric)
                Tablek_[k] = Tablek_[k].resample('1T', label='right', closed='right').sum()
                Tablek_[k] = Tablek_[k].fillna(0)
                Tablek_[k].loc[Tablek_[k]['ValuePIRNO%i'%(k+1)] != 0, 'ValuePIRNO%i'%(k+1)] = 1
            for i in range(1,len(Point_ID)):
                Tablek_[0] = pd.merge(Tablek_[0],Tablek_[i],left_index=True, right_index=True, how='outer')
            Table = pd.DataFrame(Tablek_[0].sum(1))
            #print Table
            Table.columns = ['VALUE']
            Table.loc[Table['VALUE'] != 0, 'VALUE'] = 1
            Table.loc[Table['VALUE'] == 0, 'VALUE'] = -1
            Count_Fetch = sum(Count_Fetch)
            Count_Storage = sum(Count_Storage)
            End_Time = sum(End_Time)
            
    elif Type == 'TEMP':
        print '---------------------------FETCH_TEMP---------------------------'
        if len(Point_ID) == 1 : 
            Point_ID = Point_ID[0]
            Idx = Idx[0]
            Table,Count_Fetch,Count_Storage,End_Time = Call_Dataframe(Point_ID,Idx,qt,lt,'TEMP')
            try:
                Table = Table.apply(pd.to_numeric)
                Table = Table.resample('1T', label='right', closed='right').mean()
                Table = Table.fillna(0)
            except:
                pass
        elif len(Point_ID) != 1 :
            Tablek_ = {}
            Count_Fetch,Count_Storage,End_Time = [],[],[]
            for k in range(len(Point_ID)):
                Tablek_[k],Count_FetchS,Count_StorageS,End_TimeS = Call_Dataframe(Point_ID[k],Idx[k],qt,lt,'TEMP')
                try:
                    Tablek_[k] = Tablek_[k].apply(pd.to_numeric)
                    Tablek_[k].columns = ['ValueTEMPNO%i'%(k+1)]
                    Tablek_[k] =  Tablek_[k].resample('1T', label='right', closed='right').mean()
                    Tablek_[k] = Tablek_[k].fillna(0)
                except:
                    pass
                Count_Fetch.append(Count_FetchS)
                Count_Storage.append(Count_StorageS)
                End_Time.append(End_TimeS)
            for i in range(1,len(Point_ID)):
                Tablek_[0] = pd.merge(Tablek_[0],Tablek_[i],left_index=True, right_index=True, how='outer')
            Table = pd.DataFrame(Tablek_[0].mean(1))
            Table.columns = ['VALUE']
            Count_Fetch = sum(Count_Fetch)
            Count_Storage = sum(Count_Storage)
            End_Time = sum(End_Time)
    elif Type == 'HUMIDITY':
        print '---------------------------FETCH_HUMIDITY---------------------------'
        if len(Point_ID) == 1 :
            Point_ID = Point_ID[0]
            Idx = Idx[0]
            Table,Count_Fetch,Count_Storage,End_Time = Call_Dataframe(Point_ID,Idx,qt,lt,'HUMIDITY')
            Table = Table.resample('1T', label='right', closed='right').mean()
            Table = Table.fillna(0)
        elif len(Point_ID) != 1 :
            Tablek_ = {}
            Count_Fetch,Count_Storage,End_Time = [],[],[]
            for k in range(len(Point_ID)): 
                Tablek_[k],Count_FetchS,Count_StorageS,End_TimeS = Call_Dataframe(Point_ID[k],Idx[k],qt,lt,'HUMIDITY')
                Count_Fetch.append(Count_FetchS)
                Count_Storage.append(Count_StorageS)
                End_Time.append(End_TimeS)
                Tablek_[k].columns = ['ValueTEMPNO%i'%(k+1)]
                Tablek_[k] =  Tablek_[k].resample('1T', label='right', closed='right').mean()
                Tablek_[k] = Tablek_[k].fillna(0)
            for i in range(1,len(Point_ID)):
                Tablek_[0] = pd.merge(Tablek_[0],Tablek_[i],left_index=True, right_index=True, how='outer')
            Table = pd.DataFrame(Tablek_[0].mean(1))
            Table.columns = ['VALUE']
            Count_Fetch = sum(Count_Fetch)
            Count_Storage = sum(Count_Storage)
            End_Time = sum(End_Time)
    elif Type == 'ILLUMINANCE':
        print '---------------------------FETCH_ILLUMINANCE---------------------------'
        if len(Point_ID) == 1 :
            Point_ID = Point_ID[0]
            Idx = Idx[0]
            Table,Count_Fetch,Count_Storage,End_Time = Call_Dataframe(Point_ID,Idx,qt,lt,'ILLUMINANCE')
            Table = Table.resample('1T', label='right', closed='right').mean()
            Table = Table.fillna(0)
        elif len(Point_ID) != 1 :
            Tablek_ = {}
            Count_Fetch,Count_Storage,End_Time = [],[],[]
            for k in range(len(Point_ID)): 
                Tablek_[k],Count_FetchS,Count_StorageS,End_TimeS = Call_Dataframe(Point_ID[k],Idx[k],qt,lt,'ILLUMINANCE')
                Count_Fetch.append(Count_FetchS)
                Count_Storage.append(Count_StorageS)
                End_Time.append(End_TimeS)
                Tablek_[k].columns = ['ValueTEMPNO%i'%(k+1)]
                Tablek_[k] =  Tablek_[k].resample('1T', label='right', closed='right').mean()
                Tablek_[k] = Tablek_[k].fillna(0)
            for i in range(1,len(Point_ID)):
                Tablek_[0] = pd.merge(Tablek_[0],Tablek_[i],left_index=True, right_index=True, how='outer')
            Table = pd.DataFrame(Tablek_[0].mean(1))
            Table.columns = ['VALUE']
            Count_Fetch = sum(Count_Fetch)
            Count_Storage = sum(Count_Storage)
            End_Time = sum(End_Time)
    #print Count_Fetch
    #print Count_Storage
    #print End_Time
    return Table,Count_Fetch,Count_Storage,End_Time


#-------------------------------------------------------------------------------------------------------
#For follow IEEE1888 protocol Fetch, Write
#-------------------------------------------------------------------------------------------------------
def Create_TP_FETCH(Point,qt,lt):
    key = client.factory.create('{http://gutp.jp/fiap/2009/11/}key')
    key._id = Point
    key._attrName = "time"
    key._lteq = lt
    key._gteq = qt
    query = client.factory.create('{http://gutp.jp/fiap/2009/11/}query')
    query._id = uuid.uuid4()
    query._type = "storage"
    query._acceptableSize = "5000"
    query.key = key
    header = client.factory.create('{http://gutp.jp/fiap/2009/11/}header')
    header.error = None
    header.query = query
    tp = client.factory.create('{http://gutp.jp/fiap/2009/11/}transport')
    tp.header = header
    return tp

def Create_TP_FETCH_Check_Max_Min_time(Point,ttype):
    key = client.factory.create('{http://gutp.jp/fiap/2009/11/}key')
    key._id = Point
    key._attrName = "time"
    key._select = ttype
    query = client.factory.create('{http://gutp.jp/fiap/2009/11/}query')
    query._id = uuid.uuid4()
    query._type = "storage"
    query._acceptableSize = "5000"
    query.key = key
    header = client.factory.create('{http://gutp.jp/fiap/2009/11/}header')
    header.error = None
    header.query = query
    tp = client.factory.create('{http://gutp.jp/fiap/2009/11/}transport')
    tp.header = header
    return tp

def Create_TP_WRITE(Point,value,time):
    val = client.factory.create('{http://gutp.jp/fiap/2009/11/}value')
    val.value = value
    val._time = time
    point = client.factory.create('{http://gutp.jp/fiap/2009/11/}point')
    point._id = Point
    point.value.append(val)
    body = client.factory.create('{http://gutp.jp/fiap/2009/11/}body')
    body.point.append(point)
    tp = client.factory.create('{http://gutp.jp/fiap/2009/11/}transport')
    tp.body = body
    return tp


def Fetch_His(POINT_ID,lt,qt,ttt):
    Point_Value,Point_Time,data = Set_Value()
    tp = Create_TP_FETCH(POINT_ID,qt,lt)
    print '******-----FETCH Data from IEEE1888 Stirage-----******'
    try:
        result = client.service.query(tp)
    except Exception as e:
        print e.message
    try:
        for j in range(len(result.body.point[0].value)):  
            try:
                if '_time' and 'value' in result.body.point[0].value[j]:
                    try :
                        if ttt !='PIR':
                            float(result.body.point[0].value[j].value)
                        Point_Time.append(result.body.point[0].value[j]._time.strftime("%Y-%m-%d %H:%M:%S"))           
                        Point_Value.append(result.body.point[0].value[j].value)
                    except:
                        pass
            except:
            #else:
                pass
    except:
        pass
    try: #เช็คก่อนว่าข้อมูลที่ส่งมาครบแล้วหรือยัง แล้วเก็บเข้าตารางทีละรอบไปเรื่อยๆ จนเสร็จ
        while result.header.query._cursor != "" : #check cursor
            tp.header.query._cursor = "%s"%result.header.query._cursor
            try:
                result = client.service.query(tp)
            except Exception as e:
                print e.message
            for j in range(len(result.body.point[0].value)): 
                try:
                    if '_time' and 'value' in result.body.point[0].value[j]:
                        try :
                            if ttt !='PIR':
                                 float(result.body.point[0].value[j].value)
                            Point_Time.append(result.body.point[0].value[j]._time.strftime("%Y-%m-%d %H:%M:%S"))
                            Point_Value.append(result.body.point[0].value[j].value)
                        except:
                            pass
                except:
                    pass
    except:
        pass
    data["VALUE"] = Point_Value
    data["TIME"] = Point_Time
    Table = pd.DataFrame(data)
    return Table

def Write_IEEE1888(POINT_ID,value,time): 
    class BugfixMessagePlugin(MessagePlugin):  
        def marshalled(self, context):
            tp = context.envelope.childAtPath('Body/dataRQ/transport')
            tp.setPrefix(tp.findPrefix('http://gutp.jp/fiap/2009/11/'))
    myplugins = (
        BugfixMessagePlugin(),)
    client = Client(WSDL_URL, cache=None, plugins=myplugins) 
    tp = Create_TP_WRITE(POINT_ID,value,time)
    try:
        result = client.service.data(tp)
        print 'Success'
    except Exception as e:
        print e.message

def Check_Max_Min_time(POINT_ID,ttype):
    if ttype in ['Max','Min']:
        tp = Create_TP_FETCH_Check_Max_Min_time(POINT_ID,ttype)
        print '******-----FETCH Data from IEEE1888 Stirage-----******'
        try:
            result = client.service.query(tp)
        except Exception as e:
            print e.message
        Time = result.body.point[0].value[0]._time.strftime("%Y-%m-%d %H:%M:%S")
        Value = result.body.point[0].value[0].value
        return Time,Value
    else:
        print 'Wrong input please defind Max or Min ....'
        
#-------------------------------------------------------------------------------------------------------
#For Data analytic part
#-------------------------------------------------------------------------------------------------------
def Addtime (tm, mins):
    fulldate = tm + timedelta(minutes = mins)
    return fulldate

def Filter_PIR_Movepass (df,thres=1):
    df1 = df[df['%s'%df.columns[0]]==1] 
    Table = df.copy()
    for x in df1.index:
        if (Table.loc[x- timedelta(minutes = thres):x+ timedelta(minutes = thres)].drop(x)==-1).all().VALUE == True :
            Table.set_value(x, 'VALUE', -1)
    return Table

def Filter_PIR_Minimun_Movement(df,thres): 
    Table = df.copy()
    df1 = df[df['%s'%df.columns[0]]==1] 
    for x in df1.index:
        for y in range(1,thres):
            try:
                if Table.loc[x+ timedelta(minutes = y)].VALUE==-1:
                    Table.set_value(x+ timedelta(minutes = y), 'VALUE', 1)
            except: pass
    return Table

def Filter_PIR_Minimum_time_User_disapper (df,thres):
    print len(df.loc[df.VALUE==1])
    Table = df.copy()
    df1 = df[df['%s'%df.columns[0]]==-1] 
    Time_fix = df1.index[0]
    for x in df1.index[1:]:
        if Table.loc[x- timedelta(minutes = 1)].VALUE == 1:
            if (Table.loc[x:x+ timedelta(minutes = thres-1)]==-1).all().VALUE == True  :
                pass
            else :
                Table.set_value(x, 'VALUE', 1)
            Time_fix = x
        elif Table.loc[x- timedelta(minutes = 1)].VALUE == -1:  
            if (Table.loc[Time_fix:Time_fix + timedelta(minutes = thres)]==-1).all().VALUE == True :
                pass
            else:
                Table.set_value(x, 'VALUE', 1)
    return Table


def Filter_PIR_Minimun_Movement_V1(df,thres): 
    collumns = df.columns.values[0]
    df1 = df[df['%s'%df.columns[0]]==1]
    df2 = df[df['%s'%df.columns[0]]==-1]
    df3 = pd.DataFrame()
    if df1.empty != True:
        while (df1.empty !=  True):
            df4 = pd.DataFrame(pd.Series(1., index=pd.date_range(df1.index[0], periods=thres, freq='min')))
            df3 = df3.append(df4)
            df1 = df1.drop(df4.index,errors = 'ignore')
        df3.index.name = 'TIME'
        df3.columns = [collumns]
        df3 = df3.append(df2)
        df3 = df3.reset_index()
        df3 = df3.drop_duplicates(subset='TIME', keep='first')
        df3 = df3.set_index('TIME')
        df3.sort_index(inplace=True)
        return df3
    else:
        df.index.name = 'TIME'
        return df  

def Filter_Temperature_Data(Df,condi=5,Alpha=0.9,Beta=0.01,Thes=10,CompareBF = 'No'):
    df = Df.copy()
    Compare = {}
    Compare['Before_Filter'] = Df.copy()
    Intial_V = df.iloc[0:condi][df.columns[0]].tolist()
    Value_index = df.iloc[0:condi][df.columns[0]].index.tolist() 
    print df.index[condi]
    for x in range(condi,len(df)):
        Value_index.append(df.index[x])
        Table = df.iloc[x-condi:x][df.columns[0]].tolist() 
        Value_forecast = double_exponential_smoothing(Table,Alpha,Beta)[-1]
        if abs((Value_forecast - df.iloc[x][0])*100/df.iloc[x][0]) <= Thes :
            Intial_V.append(Value_forecast)
        else:
            print df.index[x]
            Intial_V.append(Intial_V[x-1])
            df.loc[str(df.index[x])] = Intial_V[x-1]
    Table1 = pd.DataFrame(Intial_V,index=Value_index)
    Table1.columns = [df.columns]
    if CompareBF =='No':
        return Table1
    elif CompareBF == 'Yes':
        Compare['After_Filter'] = Table1
        return Compare
    
def Split_time(df):    
    Table = pd.DataFrame()
    for group in df.groupby(df.index.date):
        group[1].columns = [str(group[1].index[0].date())]
        group[1].index = group[1].index.strftime("%H:%M:%S")
        Table = pd.concat([Table,group[1]], axis=1)
    Table.index = pd.to_datetime(Table.index).time
    return Table.sort_index(axis=1)

#-------------------------------------------------------------------------------------------------------
#For Statistic
#-------------------------------------------------------------------------------------------------------   

def average(series, n=None):
    if n is None:
        return average(series, len(series))
    return float(sum(series[-n:]))/n
def weighted_average(series, weights):
    result = 0.0
    weights.reverse()
    for n in range(len(weights)):
        result += series[-n-1] * weights[n]
    return result
def exponential_smoothing(series, alpha):
    result = [series[0]] # first value is same as series
    print 'result = ', result 
    for n in range(1, len(series)):
        result.append(alpha * series[n] + (1 - alpha) * result[n-1])
    return result
def double_exponential_smoothing(series, alpha, beta):
    result = [series[0]]
    for n in range(1, len(series)+1):
        if n == 1:
            level, trend = series[0], series[1] - series[0]
        if n >= len(series): # we are forecasting
            value = result[-1]
        else:
            value = series[n]
        last_level, level = level, alpha*value + (1-alpha)*(level+trend)
        trend = beta*(level-last_level) + (1-beta)*trend
        result.append(level+trend)
    return result
def initial_trend(series, slen):
    sum = 0.0
    for i in range(slen):
        sum += float(series[i+slen] - series[i]) / slen
    return sum / slen
def initial_seasonal_components(series, slen):
    seasonals = {}
    season_averages = []
    n_seasons = int(len(series)/slen)
    # compute season averages
    for j in range(n_seasons):
        season_averages.append(sum(series[slen*j:slen*j+slen])/float(slen))
    # compute initial values
    for i in range(slen):
        sum_of_vals_over_avg = 0.0
        for j in range(n_seasons):
            sum_of_vals_over_avg += series[slen*j+i]-season_averages[j]
        seasonals[i] = sum_of_vals_over_avg/n_seasons
    return seasonals
def triple_exponential_smoothing(series, slen, alpha, beta, gamma, n_preds):
    result = []
    seasonals = initial_seasonal_components(series, slen)
    for i in range(len(series)+n_preds):
        if i == 0: # initial values
            smooth = series[0]
            trend = initial_trend(series, slen)
            result.append(series[0])
            continue
        if i >= len(series): # we are forecasting
            m = i - len(series) + 1
            result.append((smooth + m*trend) + seasonals[i%slen])
        else:
            val = series[i]
            last_smooth, smooth = smooth, alpha*(val-seasonals[i%slen]) + (1-alpha)*(smooth+trend)
            trend = beta * (smooth-last_smooth) + (1-beta)*trend
            seasonals[i%slen] = gamma*(val-smooth) + (1-gamma)*seasonals[i%slen]
            result.append(smooth+trend+seasonals[i%slen])
    return result

def Cal_Min_SSE(x,Table):
    Pred = triple_exponential_smoothing(Table,96, x[0], x[1], x[2], 96)
    Pred1 = Pred[0:len(Table)]
    return mean_squared_error(Table,Pred1)
def Forecast(df):
    Table = []
    for u in range(len(df.columns)): 
        Table += df.ix[:,u].values.tolist() 
    result_min =  minimize(Cal_Min_SSE, [0.5, 0.5, 0.5],args=(Table,), method='SLSQP', bounds=[(0,1), (0,1), (0,1)]).x.tolist()
    alpha, beta, gamma = result_min[0],result_min[1],result_min[2]
    print 'Alpha = ',alpha
    print 'Beta = ',beta
    print 'Gamma = ',gamma
    Forecast_value = pd.DataFrame(triple_exponential_smoothing(Table,96, alpha, beta, beta, 96))
    Forecast_value = Forecast_value[len(Table):len(Forecast_value)]
    col = ['Forecast']
    Result = df.merge(pd.DataFrame(data = Forecast_value[0].values,index =df.index,columns=col ),left_index=True,right_index=True)
    Re = {}
    for y in Result.columns:
        Re[y] =  pd.DataFrame(Result[y])
    #Result = {}
    #Result = {'Old' : pd.DataFrame(Khet), 'Forecast': Forecast_value}
    #Result['Forecast'] = Forecast_value#Forecast_value[len(Khet):len(Forecast_value)]
    Graph_Full(Re,'Forecast and Input','Time','Energy (Wh)')
    Result = pd.DataFrame(data = Forecast_value[0].values,index =df.index,columns=col )
    Graph_Full(Result,Name= 'Forecast')
    return Result

#-------------------------------------------------------------------------------------------------------
#For Utility
#-------------------------------------------------------------------------------------------------------   
def Set_Value():
    Point_Value = []
    Point_Time = []
    data = {}
    return Point_Value,Point_Time,data
def Check_time():
    time_now = datetime.now()
    return time_now#,time_10days
def Set_Table(Table):
    Table = Table.set_index("TIME")
    Table.index = pd.to_datetime(Table.index)
    Table.index.names = ['TIME']
    return Table
def Re_Table (Table,typee,x): 
    if typee=='minutes':
        return Table.resample('%iT'%x, label='right', closed='right').sum() 
    elif typee == 'days':
        return Table.resample('%iT'%x, label='right', closed='right').sum()
    
def Graph_Full(Table,Name='Khetnon',Name_XAxis='Time',Name_YAxis='Energy'):
    print type(Table)
    Data = []
    if type(Table) == list:
        Data.append(go.Scatter(
        x = Table.index,
        y = Table[Table.columns[0]],
        name = '%s'%Table.columns[0],
        line = dict(
        color = ('random.choice(tableau20)'),
        width = 2),
        mode = 'lines'))
    elif type(Table) == type(pd.DataFrame()):
        for x in Table.columns:
            Data.append(go.Scatter(
            x = Table[x].index,
            y = Table[x],
            name = '%s'%x,
            line = dict(
                color = ('random.choice(tableau20)'),
                width = 2),
            mode = 'lines'))
    else : #dict
        for col in Table.keys() :
            Data.append(go.Scatter(
            x = Table[col].index,
            y = Table[col][Table[col].columns[0]],
            name = '%s'%col,
            line = dict(
                color = ('random.choice(tableau20)'),
                width = 2),
            mode = 'lines'))
    layout = Layout(title = '%s'%Name,
    xaxis=XAxis(title = '%s'%Name_XAxis),
    yaxis=YAxis(title = '%s'%Name_YAxis),
        )
    fig = dict(data=Data, layout=layout)
    plotly.offline.iplot(fig)
    #py.sign_in('DemoAccount', '2qdyfjyr7o')
    
def Graph_Full_se(Table,Name='Pong',Name_XAxis='Time',Name_YAxis='En'):
    print type(Table)
    Data = []
    if type(Table) != dict:
        Data.append(go.Scatter(
        x = Table.index,
        y = Table[Table.columns[0]],
        name =  '%s'%Table.columns[0],
         mode = 'markers',
            marker = dict(
            size = 5,
            color = 'random.choice(tableau20)' ,       
            line = dict(
                #color = ('random.choice(tableau20)'),
                width = 2)
            )))
    else :
        for col in Table.keys() :
            Data.append(go.Scatter(
            x = Table[col].index,
            y = Table[col][Table[col].columns[0]],
            name = '%s'%col,
            mode = 'markers',
            marker = dict(
            size = 5,
            color = 'random.choice(tableau20)' ,       
            line = dict(
                #color = ('random.choice(tableau20)'),
                width = 2)
            )))
             
    layout = Layout(title = '%s'%Name,
    xaxis=XAxis(title = '%s'%Name_XAxis),
    yaxis=YAxis(title = '%s'%Name_YAxis),
        )
    fig = dict(data=Data, layout=layout)
    #print Wa
    plotly.offline.iplot(fig)
    #py.sign_in('DemoAccount', '2qdyfjyr7o')


# In[10]:

def Prepare_Data_Show_Characteristic(Scale,period=1,Seperate='No',Season='No',Room=''): #'lab_tsrl_dsprl_emrl' resemple Table 15 min
    time_now = Check_time()
    if Season == 'Yes':
        qt = '2016-01-01 00:00:00'
    elif Season == 'No':
        qt = (time_now - timedelta(weeks = period*4)- timedelta(days = 1)).strftime('%Y-%m-%d 00:00:00')
    lt = (time_now - timedelta(days = 1)).strftime('%Y-%m-%d 23:59:00')
    print 'Start Time  : ', qt
    print 'Stop Time  : ', lt
    if Scale=='All':
        pass
    elif Scale == 'Floor12':
        count_floor = 0
        col_floor = []
        Room = All_Point_ID.loc[(All_Point_ID['fl']=='fl12') & ((All_Point_ID['kind']=='aircon1') | (All_Point_ID['kind']=='aircon2')|(All_Point_ID['kind']=='aircon_3ph1')
                | (All_Point_ID['kind']=='aircon_3ph2') )]['room'].unique().tolist()
        Table_floor = {}
        for y in Room:
            print 'Room : ',y
            count_floor += 1
            col_floor.append(y)
            Table_floor[y] = Prepare_Data_Show_Characteristic("Room",period,Seperate='No',Room=y)
            if count_floor == 1 :
                Table = Table_floor[y]
            else :
                Table = pd.merge(Table,pd.DataFrame(Table_floor[y]),left_index=True, right_index=True, how='outer')
        Table.columns = col_floor
        return Table
    elif Scale == 'Floor13':
        count_floor = 0
        col_floor = []
        Room = All_Point_ID.loc[(All_Point_ID['fl']=='fl13') & ((All_Point_ID['kind']=='aircon1') | (All_Point_ID['kind']=='aircon2')|(All_Point_ID['kind']=='aircon_3ph1')
                | (All_Point_ID['kind']=='aircon_3ph2') )]['room'].unique().tolist()
        Table_floor = {}
        for y in Room:
            print 'Room : ',y
            count_floor += 1
            col_floor.append(y)  
            Table_floor[y] = Prepare_Data_Show_Characteristic ('Room',period,Seperate,Season,Room=y)
            if count_floor == 1 :
                Table = Table_floor[y]
            else :
                Table = pd.merge(Table,pd.DataFrame(Table_floor[y]),left_index=True, right_index=True, how='outer')
        Table.columns = col_floor
        return pd.DataFrame(Table.sum(1))
    elif Scale =='Room':
        Table_AIR_En,Table_LIGHT_EN,Table_Outlet_EN= {},{},{}
        Zone = All_Point_ID.loc[(All_Point_ID['room']=='%s'%Room)]['zone'].unique().tolist()
        print '******************************************',Room,'******************************************'
        print '*******************',Room,' have ',len(Zone),'*******************'
        count = 0
        col = []
        Table_all = {}
        for x in Zone:
            count += 1
            floors =  All_Point_ID['fl'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            building = All_Point_ID['place'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            direction =  All_Point_ID['direction'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            print '----',Room,'  ',x,'---'
            print '---------------------------AIR--------------------------------'
            Command_AIR_EN = Find_PointID(room=Room,zone=x,kind='Air')
            if len(Command_AIR_EN['Point_Name']) != 1 :
                Point_ID_AIR = Command_AIR_EN['Point_Name']
                idx_AIR = Command_AIR_EN['IND']
            else:
                Point_ID_AIR = [Command_AIR_EN['Point_Name'][0]]
                idx_AIR = [Command_AIR_EN['IND'][0]]
            print Point_ID_AIR,idx_AIR

            print '---------------------------LIGHT--------------------------------'
            Command_Light_EN = Find_PointID(room=Room,zone=x,kind='Light')
            if len(Command_Light_EN['Point_Name']) != 1 :
                Point_ID_LIGHT = Command_Light_EN['Point_Name']
                idx_LIGHT = Command_Light_EN['IND']
            else:
                Point_ID_LIGHT = [Command_Light_EN['Point_Name'][0]]
                idx_LIGHT = [Command_Light_EN['IND'][0]]
            print Point_ID_LIGHT,idx_LIGHT

            print '---------------------------Outlet--------------------------------'
            Command_Outlet_EN = Find_PointID(room=Room,zone=x,kind='Outlet')
            if len(Command_Outlet_EN['Point_Name']) != 1 :
                Point_ID_Outlet = Command_Outlet_EN['Point_Name']
                idx_Outlet = Command_Outlet_EN['IND']
            else:
                Point_ID_Outlet = [Command_Outlet_EN['Point_Name'][0]]
                idx_Outlet = [Command_Outlet_EN['IND'][0]]
            print Point_ID_Outlet,idx_Outlet
            #####################################
            Air,Light,Outlet = 'No','No','No'
            if Point_ID_AIR != [] and idx_AIR != []:
                Air = 'Yes'
                Table_AIR_En[x],Count_FetchS_AIR,Count_StorageS_AIR,End_TimeS_AIR = Prepare_Data('AIR',Point_ID_AIR,idx_AIR,qt,lt)
                print 'Filter Energy data'
                Table_AIR_En[x] = Table_AIR_En[x][Table_AIR_En[x]<2000] #Filter Data
            if Point_ID_LIGHT != [] and idx_LIGHT != []:
                Light = 'Yes'
                Table_LIGHT_EN[x],Count_FetchS_LIGHT,Count_StorageS_LIGHT,End_TimeS_LIGHT = Prepare_Data('LIGHT',Point_ID_LIGHT,idx_LIGHT,qt,lt)
            if Point_ID_Outlet != [] and idx_Outlet != []:
                Outlet = 'Yes'
                Table_Outlet_EN[x],Count_FetchS_Outlet,Count_StorageS_Outlet,End_TimeS_Outlet = Prepare_Data('Outlet',Point_ID_Outlet,idx_Outlet,qt,lt)
                Table_Outlet_EN[x] = Table_Outlet_EN[x][Table_Outlet_EN[x]<5000]
            #####################################
            
            if count == 1 :
                if Air == 'Yes':
                    Table_all['Air'] = Table_AIR_En[x]
                if Light == 'Yes':
                    Table_all['Light'] = Table_LIGHT_EN[x]
                if Outlet == 'Yes':
                    Table_all['Outlet'] = Table_Outlet_EN[x]
            else :
                if Air == 'Yes':
                    Table_all['Air'] = pd.merge(Table_all['Air'],Table_AIR_En[x],left_index=True, right_index=True, how='outer')
                if Light == 'Yes':
                    Table_all['Light'] = pd.merge(Table_all['Light'],Table_LIGHT_EN[x],left_index=True, right_index=True, how='outer')
                if Outlet == 'Yes':
                    Table_all['Outlet'] = pd.merge(Table_all['Outlet'],Table_Outlet_EN[x],left_index=True, right_index=True, how='outer')
            #col.append(x)
        #print len(Table_all['Air']),'sdfsdf',len(Table_all['Light']),'sdfsdf',len(Table_all['Outlet'])
        if Seperate =='No':
            Table = pd.DataFrame()
            for x in Table_all.keys():
                #Table = pd.merge(Table,Table_all[x],left_index=True, right_index=True, how='outer').fillna(0).sum(axis=1)
                print x , len(Table),'fgfg',len(Table_all[x])
                Table = pd.concat([Table,Table_all[x]], axis=1).fillna(0).sum(axis=1)
            return pd.DataFrame(Table).resample('15T', label='right', closed='right').sum()
        elif Seperate =='Yes':
            Table = {}
            for x in Table_all.keys():
                Table[x] = pd.DataFrame(Table_all[x].sum(1)).resample('15T', label='right', closed='right').sum()
            return Table
def Show_Characteristic(Mode,Scale,Display,period=1,Plot='No',avg='No',Season='No',seperate='No',room=''):
    Data = Prepare_Data_Show_Characteristic(Scale,period,seperate,Season,Room=room)
    Result = {}
    #Result1 = {}
    for group in Data.groupby(Data.index.weekday_name):
        col = []
        Table = pd.DataFrame()
        Table_Data = group[1]
        day = group[0]
        if Display == 'Show All':
            #Result['%s'%day] = {}
            Result['%s'%day] = pd.DataFrame(Table_Data)
            #for group in Table.groupby(Table.index.strftime("%B")):
                #Result['%s'%day][group[0]] =  pd.DataFrame(group[1])
        elif Display == 'Show Mean':
            for group in Table_Data.groupby(Table_Data.index.date):
                col.append(str(group[1].index[0].date()))
                group[1].index = group[1].index.strftime("%H:%M:%S")
                Table = pd.concat([Table,group[1]], axis=1)
            Table.columns = col
            Table.index = pd.to_datetime(Table.index).time
            Result['%s'%day] = Table.fillna(method='pad')
    if Plot == 'Yes':
        if Mode == 'Weekly Energy':
            print 'Plot Graph ......'
            if avg =='No':
                for x in Result.keys():
                    Graph_Full(Result[x],x,'TIME','ENERGY(Wh)')
            elif avg == 'Yes':
                for x in Result.keys():
                    Graph_Full(pd.DataFrame(Result[x].mean(1)),x,'TIME','ENERGY(Wh)')
        if Mode == 'Weekly Energy avg Compare':
            print 'Plot Graph ......'
            Table = {}
            for x in Result.keys():
                Table[x] = pd.DataFrame(Result[x].mean(1))
            Graph_Full(Table,'All','TIME','ENERGY(Wh)')
    elif Plot == 'No':
        pass
    return Result
        
def Main_Wasted_Energy_Calculation_ALL (Scale,time,thres,Temp_thres,fix=15,Check_Value='Yes',Write_Storage = 'Yes',Room=""):
    time_now = Check_time()
    qt = (time_now - timedelta(days = time)).strftime('%Y-%m-%d 00:00:00')
    lt = (time_now - timedelta(days = time)).strftime('%Y-%m-%d 23:59:00')
    Write_Time =  qt.split()[0]+' 01:00:00'
    Write_Time = datetime.strptime(Write_Time, '%Y-%m-%d %H:%M:%S')
    #print 'Start time =' ,qt
    #print 'End time =' ,lt
    count_PIR = 0
    count_AIR = 0
    Count_Fetch,Count_Storage,End_Time = [],[],[]
    Count_Fetch_Room,Count_Storage_Room,End_Time_Room  = [],[],[]
    Count_Fetch_Floor,Count_Storage_Floor,End_Time_Floor  = [],[],[]
    if Scale == 'All':
        pass
    elif Scale == 'Build4':
        Floor = All_Point_ID.loc[(All_Point_ID['place']=='eng4')]['fl'].unique().tolist()
        Table_AIR_En_Floor,Table_PIR_Floor,Table_TEMP_Floor= {},{},{}
        Total_wasted_energy_floor,Total_Energy_floor,Ratio_Waste_floor= {},{},{}
        for z in Floor:
            Table_AIR_En_Floor[z],Table_PIR_Floor[z],Table_TEMP_Floor[z],Count_Fetch,Count_Storage,End_Time,Total_wasted_energy_floor[z],Total_Energy_floor[z],Ratio_Waste_floor[z] = Main_Wasted_Energy_Calculation_ALL (z,time,thres,fix,Temp_thres,Write_Storage,Check_Value)
            Count_Fetch_Floor.append(Count_Fetch)
            Count_Storage_Floor.append(Count_Storage)
            End_Time_Floor.append(End_Time)
        return Table_AIR_En_Floor,Table_PIR_Floor,Table_TEMP_Floor,sum(Count_Fetch_Floor),sum(Count_Storage_Floor),sum(End_Time_Floor),Total_wasted_energy_floor,Total_Energy_floor,Ratio_Waste_floor
    elif Scale == 'fl13':
        Have_sensor = set(All_Point_ID.loc[(All_Point_ID['fl']=='fl13') & ((All_Point_ID['kind']=='sensor1')|(All_Point_ID['kind']=='sensor2') )]['room'].unique().tolist())
        Have_Air = set(All_Point_ID.loc[(All_Point_ID['fl']=='fl13') & ((All_Point_ID['kind']=='aircon1') | (All_Point_ID['kind']=='aircon2')|(All_Point_ID['kind']=='aircon_3ph1')
        | (All_Point_ID['kind']=='aircon_3ph2') )]['room'].unique().tolist())
        Room = list(Have_sensor.intersection(Have_Air))
        Table_AIR_En_Room,Table_PIR_Room,Table_TEMP_Room= {},{},{}
        Total_wasted_energy_Room,Total_Energy_Room,Ratio_Waste_Room= {},{},{}
        for y in Room:
            #print y
            Table_AIR_En_Room[y],Table_PIR_Room[y],Table_TEMP_Room[y],Count_Fetch,Count_Storage,End_Time,Total_wasted_energy_Room[y],Total_Energy_Room[y],Ratio_Waste_Room[y] = Main_Wasted_Energy_Calculation_ALL ('room',time,thres,fix,Temp_thres,Write_Storage,Check_Value,Room=y)
            Count_Fetch_Room.append(Count_Fetch)
            Count_Storage_Room.append(Count_Storage)
            End_Time_Room.append(End_Time)
        return Table_AIR_En_Room,Table_PIR_Room,Table_TEMP_Room,sum(Count_Fetch_Room),sum(Count_Storage_Room),sum(End_Time_Room),Total_wasted_energy_Room,Total_Energy_Room,Ratio_Waste_Room
    elif Scale == 'fl12':
        Have_sensor = set(All_Point_ID.loc[(All_Point_ID['fl']=='fl12') & ((All_Point_ID['kind']=='sensor1')|(All_Point_ID['kind']=='sensor2') )]['room'].unique().tolist())
        Have_Air = set(All_Point_ID.loc[(All_Point_ID['fl']=='fl12') & ((All_Point_ID['kind']=='aircon1') | (All_Point_ID['kind']=='aircon2')|(All_Point_ID['kind']=='aircon_3ph1')
        | (All_Point_ID['kind']=='aircon_3ph2') )]['room'].unique().tolist())
        Room = list(Have_sensor.intersection(Have_Air))
        Table_AIR_En_Room,Table_PIR_Room,Table_TEMP_Room= {},{},{}
        Total_wasted_energy_Room,Total_Energy_Room,Ratio_Waste_Room= {},{},{}
        for y in Room:
            #print y
            Table_AIR_En_Room[y],Table_PIR_Room[y],Table_TEMP_Room[y],Count_Fetch,Count_Storage,End_Time,Total_wasted_energy_Room[y],Total_Energy_Room[y],Ratio_Waste_Room[y] = Main_Wasted_Energy_Calculation_ALL ('room',time,thres,fix,Temp_thres,Write_Storage,Check_Value,Room=y)
            Count_Fetch_Room.append(Count_Fetch)
            Count_Storage_Room.append(Count_Storage)
            End_Time_Room.append(End_Time)
        return Table_AIR_En_Room,Table_PIR_Room,Table_TEMP_Room,sum(Count_Fetch_Room),sum(Count_Storage_Room),sum(End_Time_Room),Total_wasted_energy_Room,Total_Energy_Room,Ratio_Waste_Room
    elif Scale == 'room':
        Table_AIR_En,Table_PIR,Table_TEMP= {},{},{}
        Total_wasted_energy,Total_Energy,Ratio_Waste = {},{},{}
        Zone = All_Point_ID.loc[(All_Point_ID['room']=='%s'%Room)]['zone'].unique().tolist()
        print '******************************************',Room,'******************************************'
        print '*******************',Room,' have ',len(Zone),'*******************'
        print 'Start time =' ,qt
        print 'End time =' ,lt
        for x in Zone:
            floors =  All_Point_ID['fl'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            building = All_Point_ID['place'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            direction =  All_Point_ID['direction'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            
            Point_ID_Wasted_Ratio = 'http://khetnon/%s/%s/%s/%s/%s/analytic/wasted_energy/per_day'%(building,floors,direction,Room,x)
            Point_ID_Wasted = 'http://khetnon/%s/%s/%s/%s/%s/analytic/wasted_energy/per_day_value'%(building,floors,direction,Room,x)
            print ''
            print ''
            print 'Point_ID_Wasted_Ratio   :',Point_ID_Wasted_Ratio
            print 'Point_ID_Wasted   :',Point_ID_Wasted
            print '----',Room,'  ',x,'---'
            if Check_Value == 'Yes':
                Wasted_Value_Ratio = Fetch_His(Point_ID_Wasted_Ratio,lt,qt,'Waste') #เช็คว่ามี ข้อมูลหรือไม่่
                Wasted_Value = Fetch_His(Point_ID_Wasted,lt,qt,'Waste') #เช็คว่ามี ข้อมูลหรือไม่่
            elif Check_Value == 'No':
                Wasted_Value_Ratio = pd.DataFrame()
                Wasted_Value = pd.DataFrame()
            if Wasted_Value_Ratio.empty == True or Wasted_Value.empty == True: ### อาจจะเอา if ออกเพื่อสั่งคำนวณใหม่ทั้งหมดก็ได้
            #try:
                Command_AIR_EN = Find_PointID(room=Room,zone=x,kind='Air')
                print '---------------------------AIR--------------------------------'
                if len(Command_AIR_EN['Point_Name']) != 1 :
                    Point_ID_AIR = Command_AIR_EN['Point_Name']
                    idx_AIR = Command_AIR_EN['IND']
                else:
                    Point_ID_AIR = [Command_AIR_EN['Point_Name'][0]]
                    idx_AIR = [Command_AIR_EN['IND'][0]]
                print Point_ID_AIR,idx_AIR
                print '---------------------------PIR--------------------------------'
                Command_PIR = Find_PointID(room=Room,zone=x,value='pir')
                if len(Command_PIR['Point_Name']) != 1 :
                    Point_ID_PIR = Command_PIR['Point_Name']
                    idx_PIR = Command_PIR['IND']
                else:
                    Point_ID_PIR = [Command_PIR['Point_Name'][0]]
                    idx_PIR = [Command_PIR['IND'][0]]
                print Point_ID_PIR,idx_PIR
                print '---------------------------TEMP--------------------------------'
                Command_AIR_TEMP = Find_PointID(room=Room,zone=x,value='temperature')
                if len(Command_AIR_TEMP['Point_Name']) != 1 :
                    Point_ID_TEMP = Command_AIR_TEMP['Point_Name']
                    idx_TEMP = Command_AIR_TEMP['IND']
                else:
                    Point_ID_TEMP = [Command_AIR_TEMP['Point_Name'][0]]
                    idx_TEMP = [Command_AIR_TEMP['IND'][0]]
                print Point_ID_TEMP,idx_TEMP

                print 'Aircon = 1','  PIR = ',len(Command_AIR_TEMP['Point_Name']),'  Temp = ',len(Command_AIR_TEMP['Point_Name'])
                count_PIR = count_PIR + len(Command_AIR_TEMP['Point_Name'])
                count_AIR = count_AIR + 1
                Count_FetchS_AIR,Count_StorageS_AIR,End_TimeS_AIR = 0,0,0
                Count_FetchS_PIR,Count_StorageS_PIR,End_TimeS_PIR = 0,0,0
                Count_FetchS_TEMP,Count_StorageS_TEMP,End_TimeS_TEMP = 0,0,0
                if Point_ID_AIR != [] and idx_AIR != []:
                    Table_AIR_En[x],Count_FetchS_AIR,Count_StorageS_AIR,End_TimeS_AIR = Prepare_Data('AIR',Point_ID_AIR,idx_AIR,qt,lt)
                    print 'Count_FetchS',Count_FetchS_AIR,'  Count_StorageS',Count_StorageS_AIR,'  End_TimeS',End_TimeS_AIR
                if Point_ID_PIR != [] and idx_PIR != []:
                    Table_PIR[x],Count_FetchS_PIR,Count_StorageS_PIR,End_TimeS_PIR = Prepare_Data('PIR',Point_ID_PIR,idx_PIR,qt,lt)
                    print 'Count_FetchS',Count_FetchS_PIR,'  Count_StorageS',Count_StorageS_PIR,'  End_TimeS',End_TimeS_PIR
                if Point_ID_TEMP != [] and idx_TEMP != []:
                    Table_TEMP[x],Count_FetchS_TEMP,Count_StorageS_TEMP,End_TimeS_TEMP = Prepare_Data('TEMP',Point_ID_TEMP,idx_TEMP,qt,lt)
                    print 'Filter Temperature data'
                    try :
                        Table_TEMP[x] = Filter_Temperature_Data(Table_TEMP[x].dropna())
                    except: pass
                    print 'Count_FetchS',Count_FetchS_TEMP,'  Count_StorageS',Count_StorageS_TEMP,'  End_TimeS',End_TimeS_TEMP
                Count_Fetch.append(Count_FetchS_AIR+Count_FetchS_PIR+Count_FetchS_TEMP)
                Count_Storage.append(Count_StorageS_AIR+Count_StorageS_PIR+Count_StorageS_TEMP)
                End_Time.append(End_TimeS_AIR+End_TimeS_PIR+End_TimeS_TEMP)
                ###### Process prepare data end
                #####################################
                if Table_AIR_En[x].empty != True and Table_PIR[x].empty != True and Table_TEMP[x].empty != True:
                    print '>>Filter PIR Data>>'
                    Table_PIR[x] = Filter_PIR_Movepass(Table_PIR[x],1)
                    Table_PIR[x] = Filter_PIR_Minimun_Movement(Table_PIR[x],3)
                    Table_PIR[x] = Filter_PIR_Minimum_time_User_disapper(Table_PIR[x],thres)
                    print '>>>>>>Cal>>>>>>>>>'
                    Table = pd.merge(Table_AIR_En[x],Table_PIR[x],left_index=True, right_index=True, how='outer') 
                    Table = pd.merge(Table,Table_TEMP[x],left_index=True, right_index=True, how='outer')
                    Table.columns = ['EN_AIR','PIR','TEMP']
                    Table = Table.dropna()
                    Total_wasted_energy[x] = Table['EN_AIR'].loc[((Table['PIR']==-1))|((Table['PIR']==1)&(Table['TEMP']<Temp_thres))].sum()
                    Total_Energy[x] = Table['EN_AIR'].sum()
                    #print Total_Energy[x]
                    if Total_Energy[x]!=0:
                        Ratio_Waste[x] = Total_wasted_energy[x]*100/Total_Energy[x]
                    else:
                        Ratio_Waste[x] = float('nan')
                    print 'WRITE Wasted_Value to Storage .............'
                    ### อาจจะเอา if ออกเพื่อสั่งคำนวณใหม่ทั้งหมดก็ได้
                    if Write_Storage == 'Yes':
                        if Wasted_Value_Ratio.empty == True :
                            Write_IEEE1888(Point_ID_Wasted_Ratio,Ratio_Waste[x],Write_Time)
                        if Wasted_Value.empty == True:
                            Write_IEEE1888(Point_ID_Wasted,Total_wasted_energy[x],Write_Time)
                    elif Write_Storage == 'ReWrite':
                        Write_IEEE1888(Point_ID_Wasted_Ratio,Ratio_Waste[x],Write_Time)
                        Write_IEEE1888(Point_ID_Wasted,Total_wasted_energy[x],Write_Time)
                    else: pass
                else:
                    print 'Not enough data ....'
            #except:
                #print 'Can not caluculated .....'
            else:
                print 'Already calculated'
        return Table_AIR_En,Table_PIR,Table_TEMP,sum(Count_Fetch),sum(Count_Storage),sum(End_Time),Total_wasted_energy,Total_Energy,Ratio_Waste
    else:
        print "Wrong Command"
    

def Compare_Wasted_Energy(Mode,Mode2,time,Room,Cal_Mode='Cumsum',Plot='off',Return='No'): #ใช้รูมเป็น List ในกรณีหลายห้อง
    if Mode == 'Unique': # not have Day
        if Mode2 == 'Week': 
            print 'Room : ',Room
            time_now = Check_time()
            lt,qt,Point_ID_Wasted = [],[],[]
            data = {}
            Start = time_now - timedelta(weeks = time)
            for x in range(0,7):
                qt.append((Start + timedelta(days = x)).strftime('%Y-%m-%d 00:00:00'))
                lt.append((Start + timedelta(days = x)).strftime('%Y-%m-%d 23:59:00'))
            ##########################################
            floors =  All_Point_ID['fl'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            building = All_Point_ID['place'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            direction =  All_Point_ID['direction'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            Zone = All_Point_ID.loc[(All_Point_ID['room']=='%s'%Room)]['zone'].unique().tolist()
            for y in Zone:
                Point_ID_Wasted.append('http://khetnon/%s/%s/%s/%s/%s/analytic/wasted_energy/per_day_value'%(building,floors,direction,Room,y))
            Wasted_Value_SUM,Wasted_Value_Time = [],[]
            for z in range(len(qt)) :
                print qt[z]
                Wasted_Value = []
                for Point in Point_ID_Wasted:
                    print Point
                    if Fetch_His(Point,lt[z],qt[z],'Wasted').empty == True:
                        print 'No data'
                        print 'Calculated .....'
                        day = (time_now - datetime.strptime(qt[z], "%Y-%m-%d %H:%M:%S")).days
                        print day
                        Main_Wasted_Energy_Calculation_ALL ('room',day,5,15,25,Room='%s'%Room) #แก้วันก่อน น่าจะยังผิดอยู่
                    Wasted_Value.append(float(Fetch_His(Point,lt[z],qt[z],'Wasted').VALUE))
                Wasted_Value_SUM.append(sum(Wasted_Value))
                Wasted_Value_Time.append(qt[z].split()[0])
            if Cal_Mode=='Cumsum':
                Wasted_Value_SUM = np.cumsum(Wasted_Value_SUM).tolist()
            elif Cal_Mode=='Sum':
                pass
            data = {"VALUE":Wasted_Value_SUM,'TIME':Wasted_Value_Time}
            #data["VALUE"] = Wasted_Value_SUM
            #data["TIME"] = Wasted_Value_Time
            Table = pd.DataFrame(data)
            Table = Table.set_index('TIME')
            if Plot == 'on':
                Graph_Full(Table)
            if Return == 'Yes':
                return Table
        elif Mode2 == 'Month':
            lt,qt,Point_ID_Wasted = [],[],[]
            data = {}
            time_now = datetime.now()
            if time == 0: # 0 mean that month
                month = time_now.month
                year = time_now.year
                Start = datetime.strptime('01%s%s'%(month,year), '%d%m%Y')
                for x in range(0,time_now.day-1):
                    qt.append((Start + timedelta(days = x)).strftime('%Y-%m-%d 00:00:00'))
                    lt.append((Start + timedelta(days = x)).strftime('%Y-%m-%d 23:59:00'))
            else :
                time_now = time_now - timedelta(weeks = 4*time) - timedelta(days = 3)
                last = calendar.monthrange(time_now.year,time_now.month)[1]
                month = time_now.month
                year = time_now.year
                Start = datetime.strptime('01%s%s'%(month,year), '%d%m%Y')
                for x in range(0,last):
                    qt.append((Start + timedelta(days = x)).strftime('%Y-%m-%d 00:00:00'))
                    lt.append((Start + timedelta(days = x)).strftime('%Y-%m-%d 23:59:00'))
            floors =  All_Point_ID['fl'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            building = All_Point_ID['place'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            direction =  All_Point_ID['direction'].loc[(All_Point_ID['room']==Room) ].unique()[0]
            Zone = All_Point_ID.loc[(All_Point_ID['room']=='%s'%Room)]['zone'].unique().tolist()
            for y in Zone:
                Point_ID_Wasted.append('http://khetnon/%s/%s/%s/%s/%s/analytic/wasted_energy/per_day_value'%(building,floors,direction,Room,y))
            Wasted_Value_SUM,Wasted_Value_Time = [],[]
            for z in range(len(qt)) :
                if Fetch_His(Point_ID_Wasted[0],lt[z],qt[z],'Wasted').empty == True:
                    print 'No data'
                    print 'Calculated .....'
                    day = (time_now - datetime.strptime(qt[z], "%Y-%m-%d %H:%M:%S")).days
                    print day
                    Main_Wasted_Energy_Calculation_ALL ('room',day,5,15,25,Room='%s'%Room)
                Wasted_Value = []
                print qt[z]
                print lt[z]
                for b in Point_ID_Wasted:
                    print b
                    Wasted_Value.append(float(Fetch_His(b,lt[z],qt[z],'Wasted').VALUE))
                print Wasted_Value
                Wasted_Value_SUM.append(sum(Wasted_Value))
                Wasted_Value_Time.append(qt[z].split()[0])
                #Wasted_Value_Time.append((time_now - timedelta(days = z+1)).date())
            if Cal_Mode=='Cumsum':
                Wasted_Value_SUM = np.cumsum(Wasted_Value_SUM).tolist()
            elif Cal_Mode=='Sum':
                pass
            data["VALUE"] = Wasted_Value_SUM
            data["TIME"] = Wasted_Value_Time
            Table = pd.DataFrame(data)
            Table = Table.set_index('TIME')
            Data = []
            if Plot == 'on':
                Graph_Full(Table)
            if Return == 'Yes':
                return Table
        elif Mode2 == 'Year':
            Table = {}
            Date = Check_time()
            for x in range(0,12):
                Month = (Date - timedelta(weeks = 4*x)).strftime('%B')
                print Month
                Table[Month] = Compare_Wasted_Energy('Unique','Month',x,Room,Return ='Yes')
            if Plot == 'on':
                Graph_Full(Table)
            if Return == 'Yes':
                return Table
    elif Mode == 'Compare':
        if Mode2 == 'Week':
            Table = {}
            for x in Room:
                if Cal_Mode=='Cumsum':
                    Table[x] = Compare_Wasted_Energy('Unique','Week',time,x,Return = 'Yes')
                elif Cal_Mode=='Sum':
                    Table[x] = Compare_Wasted_Energy('Unique','Week',time,x,Cal_Mode='Sum',Return = 'Yes')
            if Plot == 'on':
                Graph_Full(Table)
            if Return == 'Yes':
                return Table

        elif Mode2 == 'Month':
            Table = {}
            for x in Room:
                if Cal_Mode=='Cumsum':
                    Table[x] = Compare_Wasted_Energy('Unique','Month',time,x,Return ='Yes')
                elif Cal_Mode=='Sum':
                    Table[x] = Compare_Wasted_Energy('Unique','Month',time,x,Cal_Mode='Sum',Return ='Yes')
            if Plot == 'on':
                Graph_Full(Table)
            if Return == 'Yes':
                return Table


# In[ ]:




# In[ ]:




# In[ ]:



