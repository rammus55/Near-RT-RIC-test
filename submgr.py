"""
Subscription Manager (Subscription, Reset, Subscription Delete)
"""
import os,sys,logging,time,json
from ricxappframe.xapp_frame import RMRXapp
from ricsdl.syncstorage import SyncStorage
from ricsdl.exceptions import RejectedByBackend, NotConnected, BackendError
from ricxappframe.rmr import rmr
import gc
import tracemalloc

os.environ['DBAAS_SERVICE_PORT'] = '6379'
os.environ['DBAAS_SERVICE_HOST'] = '10.0.2.15'#'10.244.0.18' #'140.123.102.112'
os.environ['RMR_SEED_RT'] = 'test_route_thrd.rt'

# Constants used in the examples below.
MY_NS = 'E2setup'
MY_GRP_NS = 'my_group_ns'
MY_LOCK_NS = 'my_group_ns'

set_list = list()
Temporary_storage_subscription = list()

#database part
def _try_func_return(func):
    try:
        return func()
    except RejectedByBackend as exp:
        print(f'SDL function {func.__name__} failed: {str(exp)}')
        raise
    except (NotConnected, BackendError) as exp:
        print(f'SDL function {func.__name__} failed for a temporal error: {str(exp)}')

#initial the subscription manager
def post_init(_self):
    """post init"""
    print("*******************************************\n")
    print("Start to initial Subscription Manager~~~~\n")
    _self.logger.info("Start to initial Subscription Manager~~~~\n")
    print("*******************************************\n")
    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True
    my_ret_dict = _try_func_return(lambda: mysdl.get('Routing', {str('table')}))
    #print("my_ret_dict:", len(my_ret_dict['table']))
    if(len(my_ret_dict)!=0):
        f = open("test_route_thrd.rt", 'w+')
        f.write('newrt|start\n')
        data = eval(my_ret_dict['table'].decode())
        for key in data.keys():
            ip = data[key]['IP']
            port = str(data[key]['port'])
            messagetype = str(data[key]['massage_type'])+port
            f.write('rte|'+messagetype+'|'+ip+':'+port+'\n')
        f.write('newrt|end\n')
        f.seek(0)
        f.close()
        print("Write in routing table succussful!!!")

#saving logging
def save_list():
    file_name = 'E2data.txt'
    f = open(file_name, "w+") 
    for item in set_list:
        f.write(item)
    f.close()

#check function
"""
def check_function(data):

    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True

    NameSpace='E2setup'
    Key='E2setup_group'


    data = eval(_try_func_return(lambda: mysdl.get(NameSpace, {str(Key)}))[Key].decode())
    for  key in data.keys():
"""

#write in local routing table
def write_routing_table(NameSpace,Key):
    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True

    print("Write the xapp information into the routing table!!!\n")
    
    f =open("test_route_thrd.rt",'w+')#it was w+ before
    f.write('newrt|start\n')
    data = eval(_try_func_return(lambda: mysdl.get(NameSpace, {str(Key)}))[Key].decode())
    
    s=sys.getsizeof(data)
    print("data size:",s)

    print("mysql(routing,table:)",data)
    for  key in data.keys():
        ip = data[key]['IP']
        port = str(data[key]['port'])
        messagetype = str(data[key]['massage_type'])+port
        f.write('rte|'+messagetype+'|'+ip+':'+port+'\n')
    f.write('newrt|end\n')
    f.seek(0)
    #txt=f.read()
    #print(txt)
    f.close()
    print("Write in routing table succussful!!!")
    print("Update after 60s.\n")

    del data
    collected = gc.collect()
    print("Garbage collector: collected ",collected)

def error_empty_tm(self,data,sbuf):
    print("****Error occurred****\n")
    print("The payload is",data,"\n")
    val = json.dumps({
    "RAN Function ID":1,
    "Cause":"Unspecified"
    }).encode()
    self.rmr_send(val, 7404000)

def error_empty_xapp(self,data,xapp_port,sbuf):
    print("****Error occurred****\n")
    print("The payload is",data,"\n")
    val = json.dumps({
    "RAN Function ID":1,
    "Cause":"Unspecified"
    }).encode()
    self.rmr_send(val, int("740"+str(xapp_port)))

#Send to E2 termination (from xapp)
def send2E2T(self, summary, sbuf):
    global Temporary_storage_subscription
    jpay = json.loads(summary['payload'])
    message= str(summary['message type'])
    message= int(message[0:3])
    jpay_string = summary['payload']
    try:
        xApp_port = jpay['RIC Request ID']['RIC Requestor ID']
    except:
        print("There's no RIC ID element")

    if jpay_string !="":

        #Subscription Request
        if message== 410:
            self.logger.info("Got 410 handler called!")
            print("Got the Subscription Request!!\n")
            print("410 Received:",jpay,"\n")

            mysdl = _try_func_return(SyncStorage)
            is_active = mysdl.is_active()
            assert is_active is True

            xApp_ID = int(jpay['RIC Request ID']['RIC Requestor ID'])
            group_index = str((xApp_ID - 8000)//66)
            white_text = eval(_try_func_return(lambda: mysdl.get('White', {str('text')}))['text'].decode())
            if(int(white_text[group_index]['MasterID'])!=-1 or int(white_text[group_index]['SocketFD'])!=99999):# and white_text[group_index]['MasterID']!=xApp_ID):
                print('Already subscription before')
                RequestIDjson={'RIC Action ID':jpay['RIC Subscription Details']['Sequence of Actions']['RIC Action ID'], 
                               'Cause':{'Failure_message':'Already subscription before', 
                                        'xAppID':white_text[group_index]['MasterID'],
                                        'SocketFD':white_text[group_index]['SocketFD']} 
                              }
                val = json.dumps(RequestIDjson).encode()
                self.rmr_send(val, int("414"+str(xApp_ID)))
                self.rmr_free(sbuf)
                return

            # get Socket FD information from E2 Setup Table
            # Table 2 -> IP:number of using FD (namespace='IP', key=str(IP))
            use_upperbound = 5
            e2_setup_group =list(_try_func_return(lambda: mysdl.get_members('E2setup_group', 'E2 Node ID')))
            for member in e2_setup_group:
                member = member.decode()
                print("members:",member,",type:",type(member))
                print("e2_setup_group[-1]:",e2_setup_group[-1],",type:",type(e2_setup_group[-1]))
                try:
                    tmp_e2_setup_table = _try_func_return(lambda: mysdl.get('E2setup', {str(member)})) #type of dictionary
                    print("E2 Subscription mysdl.get('E2setup', {str(member)}):",tmp_e2_setup_table)
                    e2_setup_table = eval(tmp_e2_setup_table[str(member)].decode())  #type of dictionary
                except:
                    continue
                # Confirm whether the limit is exceeded
                if(e2_setup_table['xAppID'] == 99999):  # 99999 represent that no one chooses this FD
                    # Confirm whether the limit is exceeded
                    print("e2_setup_table['xAppID'] == 99999(e2_setup_table):",e2_setup_table)
                    xApp_ID = jpay['RIC Request ID']['RIC Requestor ID']
                    IP_Routing_Table = eval(_try_func_return(lambda: mysdl.get('Routing', {str('table')}))['table'].decode())['411'+str(xApp_ID)]
                    IP = IP_Routing_Table['IP']
                    print("e2_setup_table['SocketFD']",e2_setup_table['SocketFD'])
                    _try_func_return(lambda: mysdl.add_member('IP', str(IP), {e2_setup_table['SocketFD']}))
                    IP_NumberOfFD = list(_try_func_return(lambda: mysdl.get_members('IP', str(IP)))) #type of list
                    print("IP_NumberOfFD list:", IP_NumberOfFD)
                    if(len(IP_NumberOfFD) > use_upperbound): 
                        _try_func_return(lambda: mysdl.remove_member('IP', str(IP), {e2_setup_table['SocketFD']}))
                        print('This IP ', IP, ' has reached the upper limit.')
                        # Do you want to notify xApp that the limit has been exceeded ?
                        return
                    e2_setup_table['xAppID'] = jpay['RIC Request ID']["RIC Requestor ID"]
                    byte_e2_setup_table = str(e2_setup_table).encode()
                    _try_func_return(lambda: mysdl.set('E2setup', {str(e2_setup_table['E2 Node ID'].replace(' ','')): byte_e2_setup_table}))  #update E2 Setup Table
                    # create master ID in white text
                    white_text[group_index]['MasterID'] = jpay['RIC Request ID']["RIC Requestor ID"]
                    white_text[group_index]['SocketFD'] = e2_setup_table['SocketFD']
                    byte_white_text = str(white_text).encode()
                    _try_func_return(lambda: mysdl.set('White', {str('text'): byte_white_text}))
                    print("@@mysdl.get('E2setup':",_try_func_return(lambda: mysdl.get('E2setup', {str(member)})))  
                    break
                if(int(member) == int(e2_setup_group[-1])):
                    print('Situation 2：No SocketFD can be used')
                    RequestIDjson={'RIC Action ID':jpay['RIC Subscription Details']['Sequence of Actions']['RIC Action ID'], 
                                   'Cause':{'Failure_message':'No SocketFD can be used.',
                                            'xAppID' : jpay['RIC Request ID']['RIC Requestor ID'],
                                            'SocketFD':jpay['SocketFD']
                                    } 
                    }
                    val = json.dumps(RequestIDjson).encode()
                    self.rmr_send(val, int("414"+str(xApp_ID)))
                    self.rmr_free(sbuf)
                    return  # There is no FD can be used
            try:
                jpay.update({'SocketFD':e2_setup_table['SocketFD']})
            except:
                print('Situation 1：No SocketFD can be used')
                RequestIDjson={'RIC Action ID':jpay['RIC Subscription Details']['Sequence of Actions']['RIC Action ID'], 
                               'Cause':{'Failure_message':'No SocketFD can be used.'} 
                              }
                val = json.dumps(RequestIDjson).encode()
                self.rmr_send(val, int("414"+str(xApp_ID)))
                self.rmr_free(sbuf)
                return

            # Ask to store in Redis        
            dataSize = sys.getsizeof(jpay_string)
            print('Size of integer:', dataSize)
            jpay['SocketFD']= int(_try_func_return(lambda: mysdl.get(jpay['SocketFD'], {str('SocketFD')}))['SocketFD'].decode())
            
            val = json.dumps(jpay).encode()
            
            #entry(self, sbuf, val, 4004000)
            print("Send it to RMR Manager!!\n")
            #print("181 jpay: ", jpay)
            """
            val = json.dumps({
                "RIC Requestor ID":jpay['RIC Request ID']["RIC Requestor ID"], 
                "paysize":dataSize
            }).encode()
            """
            self.rmr_send(val, 64006000)
            if len(val)!= 0:
                time.sleep(2)
                entry(self, sbuf, val, 4004000)
            
            Temporary_storage_subscription.append(jpay_string)

            self.rmr_free(sbuf)

        #Subscription delete request
        if message== 510:
            self.logger.info("Got 510 handler called!")
            print("Got the 510 Subscription Delete Request!!\n")
            print("510 Received:",jpay,"\n")

            val = json.dumps(jpay).encode()
            entry(self, sbuf, val, 5004000)

            self.rmr_free(sbuf)

    else:
        error_empty_xapp(self,jpay_string,xApp_port,sbuf)
        self.rmr_free(sbuf)

    print("\n")

#Send to xapp
def send2xApp(self, summary, sbuf):
    global xApp_port
    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True

    jpay = summary['payload']
    message= str(summary['message type'])
    message= int(message[0:3])
    data = jpay.decode('utf-8')

    if data != "":
        print("Data is OK\n")
        payload =  data[data.index("{") + 1:data.rindex("}")]
        payload = "{"+ payload + "}"
        jpay = json.loads(payload)
        print("data:",payload,"type:",type(payload))
        datadic = eval(payload.replace("\\",""))
        try:
            xApp_port = jpay['RIC Request ID']['RIC Requestor ID']
        except:
            print("There's no RIC ID element")
        
        #Reset Request
        if message== 300:
            self.logger.info("Got 300 Subscription Response!")
            print("Got the 300 Subscription Response!!\n")
            print("300 Received:",jpay,"\n")
            val = json.dumps(jpay).encode()
            self.rmr_send(val, int("301"+str(xApp_port)))
            self.rmr_free(sbuf)


        #Subscription Response
        if message== 401:
            self.logger.info("Got 401 Subscription Response!")
            print("Got the 401 Subscription Response!!\n")
            print("401 Received:",jpay,"\n")
            
            #Check Data
            #c, fault=CheckSubCorrect(summary['payload'])

            print("Not Null\n")
            
            storedata = eval(_try_func_return(lambda: mysdl.get(MY_NS, {str(jpay['RIC Request ID']['RIC Requestor ID'])}))[str(jpay['RIC Request ID']['RIC Requestor ID'])].decode())
            storedata.update({'status':'accomplish'})
            print("storedata: ", storedata)
            store_data = str(storedata)
            byte_send_data = store_data.encode()
            _try_func_return(lambda: mysdl.set(MY_NS, {str(jpay['RIC Request ID']['RIC Requestor ID']): byte_send_data}))
            print("change in Redis!!")
            my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, {str(jpay['RIC Request ID']['RIC Requestor ID'])}))
            print(MY_NS, " redis_get:",str(jpay['RIC Request ID']['RIC Requestor ID']),"->",my_ret_dict)
            jpay['namespcae']=MY_NS
            #Send to xApp
            
            RequestID=jpay['RIC Request ID']['RIC Requestor ID']
            #RequestFD=jpay['E2 Node ID'].replace(' ','')
            
            xApp_ID = int(jpay['RIC Request ID']['RIC Requestor ID'])
            group_index = str((xApp_ID - 8000)//66)
            white_text = eval(_try_func_return(lambda: mysdl.get('White', {str('text')}))['text'].decode())
            RequestFD = white_text[group_index]['SocketFD'] 
            RequestIDjson={'RIC Request ID':RequestID,'SocketFD':RequestFD}
            val = json.dumps(RequestIDjson).encode()
            
            self.rmr_send(val, int("411"+str(xApp_port)))
            self.rmr_free(sbuf)


        #Subscription Failure
        if message == 404:
            self.logger.info("Got 404 Subscription Failure!")
            print("Got the 404 Subscription Failure!!\n")
            print("404 Received:",jpay,"\n")
            """
            # Delete Subscription table from Redis if Subscription Failure
            mysdl = _try_func_return(SyncStorage)
            is_active = mysdl.is_active()
            assert is_active is True
            _try_func_return(lambda: mysdl.remove(MY_NS, {str(jpay['RIC Request ID']['RIC Requestor ID'])}))

            # Remove member from table2
            xApp_ID = datadic['RIC Request ID']['RIC Requestor ID']
            IP_Routing_Table = eval(_try_func_return(lambda: mysdl.get('Routing', {str('table')}))['table'].decode())['411'+str(xApp_ID)]
            IP = IP_Routing_Table['IP']
            SocketFD = datadic['SocketFD']
            _try_func_return(lambda: mysdl.remove_member('IP', str(IP), {SocketFD}))
            e2_setup_group =list(_try_func_return(lambda: mysdl.get_members('E2setup_group', 'E2 Node ID')))
            for member in e2_setup_group:
                member = member.decode()
                try:
                    tmp_e2_setup_table = _try_func_return(lambda: mysdl.get('E2setup', {str(member)})) #type of dictionary
                    print("404tmp_e2_setup_table:",tmp_e2_setup_table)
                    e2_setup_table = eval(tmp_e2_setup_table[str(member)].decode())  #type of dictionary
                except:
                    continue
                # Confirm whether the limit is exceeded
                if(e2_setup_table['SocketFD'] == SocketFD):
                    print("!!!!!!!HERE!!!!!!!!!!!!!")
                    print("e2_setup_table['SocketFD']:",e2_setup_table['SocketFD'],",'SocketFD':",SocketFD)
                    e2_setup_table['xAppID'] = 99999
                    byte_e2_setup_table = str(e2_setup_table).encode()
                    _try_func_return(lambda: mysdl.set('E2setup', {str(e2_setup_table['E2 Node ID']): byte_e2_setup_table}))  #update E2 Setup Table
                    print("404@@mysdl.get('E2setup':",_try_func_return(lambda: mysdl.get('E2setup', {str(member)})))
                    break
            """
            print("Send 414 Subscription Failure to xApp\n")
            val = json.dumps(jpay).encode()
            self.rmr_send(val, int("414"+str(xApp_port)))
            self.rmr_free(sbuf)


        #Subscription Delete Response
        if message== 501:
            self.logger.info("Got 501 handler called!")
            print("Got the 501 Subscription Delete Response!!\n")
            print("501 Received:",jpay,"\n")
            """
            #Check Data
            #c, fault=CheckSubCorrect(summary['payload'])

            #Check the mistake
                   
            print("Not Null\n")
            mysdl = _try_func_return(SyncStorage)
            is_active = mysdl.is_active()
            assert is_active is True

            _try_func_return(lambda: mysdl.remove(MY_NS, {str(datadic['RIC Request ID']['RIC Requestor ID'])}))

            # Remove member from table2
            xApp_ID = datadic['RIC Request ID']['RIC Requestor ID']
            IP_Routing_Table = eval(_try_func_return(lambda: mysdl.get('Routing', {str('table')}))['table'].decode())['411'+str(xApp_ID)]
            IP = IP_Routing_Table['IP']
            SocketFD = datadic['SocketFD']
            _try_func_return(lambda: mysdl.remove_member('IP', str(IP), {SocketFD}))
            e2_setup_group =list(_try_func_return(lambda: mysdl.get_members('E2setup_group', 'E2 Node ID')))
            for member in e2_setup_group:
                member = member.decode()
                try:
                    tmp_e2_setup_table = _try_func_return(lambda: mysdl.get('E2setup', {str(member)})) #type of dictionary
                    e2_setup_table = eval(tmp_e2_setup_table[str(member)].decode())  #type of dictionary
                except:
                    continue
                # Confirm whether the limit is exceeded
                if(e2_setup_table['SocketFD'] == SocketFD):
                    e2_setup_table['xAppID'] = 99999
                    byte_e2_setup_table = str(e2_setup_table).encode()
                    _try_func_return(lambda: mysdl.set('E2setup', {str(e2_setup_table['E2 Node ID']): byte_e2_setup_table}))  #update E2 Setup Table
                    break

            val = json.dumps(jpay).encode()
            self.rmr_send(val, int("511"+str(xApp_port)))
            """
            self.rmr_free(sbuf)
            
        #Subscription Delete Failure
        if message == 504:
            self.logger.info("Got 504 Subscription Delete Failure!")
            print("Got the 504 Subscription Delete Failure!!\n")
            print("504 Received:",jpay,"\n")

            print("Send 514 Subscription Delete Failure to xApp\n")
            val = json.dumps(jpay).encode()
            self.rmr_send(val, int("514"+str(xApp_port)))
            self.rmr_free(sbuf)

        #E2 Node Disconnected
        if message == 720:
            self.logger.info("Got 720 E2 Node Disconnected!")
            print("Got the 720 E2 Node Disconnected!!\n")
            print("720 Received:",jpay,"\n")
            val = json.dumps(jpay).encode()
            self.rmr_send(val, int("720"+str(xApp_port)))
            self.rmr_free(sbuf)

    else:
        error_empty_tm(self,"empty",sbuf)

#send to E2termination(send)
def entry(self, sbuf, data, message):

    # Init rmr
    mrc = rmr.rmr_init(b"9998", rmr.RMR_MAX_RCV_BYTES, 0x00)
    while rmr.rmr_ready(mrc) == 0:
            time.sleep(1)
            print("Not yet ready")
    rmr.rmr_set_stimeout(mrc, 2)
    sbuf = rmr.rmr_alloc_msg(mrc, 256)
    try:
        val = data.encode('utf-8')
        #print("Val",val)
    except :
        val = data
        #print("Val",val)


    rmr.set_payload_and_length(val, sbuf)
    rmr.generate_and_set_transaction_id(sbuf)
    sbuf.contents.state = 0
    sbuf.contents.mtype = message
    print("Send summary: {}".format(rmr.message_summary(sbuf)))
    sbuf = rmr.rmr_send_msg(mrc, sbuf)
    print("Post send summary: {}".format(rmr.message_summary(sbuf)))



    #store the data into database
def db(self, summary, sbuf):
    global MY_NS
    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True
    print("\n")

    jpay = json.loads(summary['payload'])
    message= str(summary['message type'])
    message= int(message[0:4])
    print("Got the 6401 message!!!!!!!!!\n")
    print("6401 Received:",jpay,"\n")

    # Wrong message
    if((message % 10) == 4):
        if(jpay['NAK'] == -2):				
            print("There is something wrong. Please check the RMR message type.")
            os._exit(0)
        elif(jpay['NAK'] == -1):
            print("The memoory is full. Please wait.")
            os._exit(0)


    MY_NS = jpay['namespace']
    print("MY_NS:", MY_NS)
    # store receive in redis
    try:
        data = Temporary_storage_subscription.pop(0)
        datadic = eval(data)
        print("datadic:",datadic)
    except:
        print("The Temporary_storage_subscription is empty")
        return
    storedata = {}
    for col in jpay["columns"]:
        try:
            storedata.update({str(col):datadic[col]})
        except:
            continue
    storedata.update({'status':'not accomplish'})
    print("storedata:",storedata)
    store_data = str(storedata)#str([E2NodeID, RANFuncID, RANFuncDef, RANFuncRev]) # jpay["E2NodeID"], jpay["RANFuncID"], jpay["RANFuncDef"], jpay["RANFuncRev"]		
    byte_send_data = store_data.encode()#bytes(store_data, encoding='utf-8')
    _try_func_return(lambda: mysdl.set(MY_NS, {str(storedata['RIC Request ID']['RIC Requestor ID']): byte_send_data}))

    # get data in redis			
    my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, {str(storedata['RIC Request ID']['RIC Requestor ID'])}))
    print("store in Redis!!")
    print(MY_NS, " redis_get:",str(storedata['RIC Request ID']['RIC Requestor ID']),"->",my_ret_dict)


    self.rmr_free(sbuf)


#check the mistake 
def CheckSubCorrect(data):
    CheckList_Sub = ["subscriptionID", "RICReqID", "RANFuncID", "RANFuncRev", "RICActID"]
    RICReqID = ["RICRequestorID", "RICInstanceID"]
    fault = []
    check = 1
    for i in CheckList_Sub:
        if(i == "RICReqID"):
            for j in RICReqID:
                try:
                    tmp = data[i][j]
                except:
                    fault.append(j)
                    check = 0
            continue
        try:
            tmp = data[i]
        except:
            fault.append(i)
            check = 0
    
    return check, fault,tmp

def sub_process(self, summary, sbuf):

    jpay = summary['payload']
    message= str(summary['message type'])
    message= int(message[0:3])
    data = jpay.decode('utf-8')

    if data != "":
        print("Data is OK\n")
        payload =  data[data.index("{") + 1:data.rindex("}")]
        payload = "{"+ payload + "}"
        jpay = json.loads(payload)
        print("data:",payload,"type:",type(payload))
        #datadic = eval(payload.replace("\\",""))
    
        #E2 Reset Request
        if message== 300:
            self.logger.info("Got 300 E2 Reset Request!")
            print("Got 300 E2 Reset Request!\n")
            print("300 Received:",jpay,"\n")
            Cause = jpay["Cause"]
            print("Cause",Cause,"\n")


        #Error indication
        elif message== 740:
            self.logger.info("Got 740 Error Indication!")
            print("Got 740 Error Indication!\n")
            print("740 Received:",jpay,"\n")

        #restart RMR manager
        elif message == 100:
            self.logger.info("Received the 1000 Routing Restart!!")
            print("Received the 1000 Routing Restart!!\n")
            print("1000 Received:",jpay,"\n")

            print("Call to restart!!!\n")
            NS = jpay['Routing Table']['Namespace']
            key1 = jpay['Routing Table']['Key']

            write_routing_table(NS,key1)
        
        else:
            self.logger.info("Default Callback!")
            print("Default handler received: {0}".format(summary))

        self.rmr_free(sbuf)

    else:
        print("Received: {0}".format(summary))
        error_empty_tm(self,"empty",sbuf)


xapp = RMRXapp(default_handler=sub_process, rmr_port=4400, post_init=post_init, use_fake_sdl=False)

#--------------------------------------------
xapp.register_callback(send2E2T, 4104400)
xapp.register_callback(send2xApp, 4014400)
xapp.register_callback(send2xApp, 4044400)
#--------------------------------------------
xapp.register_callback(send2E2T, 5104400)
xapp.register_callback(send2xApp, 5014400)
xapp.register_callback(send2xApp, 5044400)
#--------------------------------------------
xapp.register_callback(send2xApp, 7004200)
xapp.register_callback(send2E2T, 8104400)
xapp.register_callback(send2E2T, 8704400)
#--------------------------------------------
xapp.register_callback(db, 64014400)
xapp.register_callback(db, 64044400)
xapp.register_callback(db, 65014400)
xapp.register_callback(db, 65044400)
#--------------------------------------------
xapp.run()  # will not thread by default
