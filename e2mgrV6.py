"""
E2 Manager (Control, E2 Setup, indication)
"""
import os
import sys
import logging
import time, threading
import json
from ricxappframe.xapp_frame import RMRXapp
from ricsdl.syncstorage import SyncStorage
from ricsdl.exceptions import RejectedByBackend, NotConnected, BackendError
from ricxappframe.rmr import rmr
from influxdb import InfluxDBClient
import tracemalloc
import gc

os.environ['DBAAS_SERVICE_PORT'] = '6379'
os.environ['DBAAS_SERVICE_HOST'] = '10.0.2.15'#'10.244.0.18' #'140.123.102.112'
os.environ['RMR_SEED_RT'] = 'test_route_thrd.rt'
influxdbIP = '10.98.0.0'
influxdbPort = '8086'

count=0
# Constants used in the examples below.
#MY_NS = 'E2setup'
MY_GRP_NS = 'my_group_ns'
MY_LOCK_NS = 'my_group_ns'

set_list = list()
RAN_fun_id_list = list()
Temporary_storage_E2setup = list()
Temporary_storage_Report = list()
Temporary_storage_Insert = list()


def createTimer():
    t = threading.Timer(2, send_broadcast)
    t.start()

        
def send_broadcast():
    global q
    createTimer()
    size = q.qsize()
    if size > 0:
        pass



# database
def _try_func_return(func):
    try:
        return func()
    except RejectedByBackend as exp:
        #print(f'SDL function {func.__name__} failed: {str(exp)}')
        #raise
        pass
    except (NotConnected, BackendError) as exp:
        pass
        #print(f'SDL function {func.__name__} failed for a temporal error: {str(exp)}')


# initial E2 Manager
def post_init(_self):
    print("***********************************")
    print("E2 Manager born up!!!\n")
    print("E2 Manager start to work~~YA\n")
    print("***********************************\n")
    #createTimerForInflux()

    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True
    #print("***********************************")
    #print("E2 Manager store route table from DB\n")
    my_ret_dict = _try_func_return(lambda: mysdl.get('Routing', {str('table')}))
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
        #print("Write in routing table succussful!!!")  


# saving logging
def save_list():
    file_name = 'E2data.txt'
    f = open(file_name, "w+")
    for item in set_list:
        f.write(item)
    f.close()


def get_Requestor_ID(jpay):
    try:
        xApp_port = jpay['RIC Request ID']['RIC Requestor ID']
        return xApp_port
    except:
        #print("There's no RIC ID element")
        return None


""" Procedure Function Section """
# ************************************************


def error_empty_tm(self, data, sbuf):
    #print("****Error occurred****\n")
    #print("The payload is", data, "\n")
    val = json.dumps({
        "RAN Function ID": 1,
        "Cause": "Unspecified",
        "Procedure Code": 2
    }).encode()
    #entry(self, sbuf, val, 7404000)
    self.rmr_send(val, int('7404000'))
# Check Error Indication(xApp)
def error_empty_xapp(self, data, xApp_port):
    #print("****Error occurred****\n")
    #print("The payload is empty\n")

    val = json.dumps(data).encode()

    self.rmr_send(val, int("740"+str(xApp_port)))

# E2 Setup Failure
def e2_setup_failure(self, sbuf, SocketFD):
    #print("E2 Setup Failure!!\n")
    #print("Send 204 back to E2 Termination\n")
    val = json.dumps({
        "Cause": "Unspecified",
        "Procedure Code": 1,
        "Type of Message": 2,
        "SocketFD": SocketFD
    }).encode()
    #entry(self, sbuf, val, 2044000)
    self.rmr_send(val, int('2004000'))

# **************************************************

# Get SocketFD
def get_SocketFD(jpay):
    try:
        SocketFD = jpay['SocketFD']
        return SocketFD
    except:
        #print("There's no SocketFD element")
        return None

# Check Failure
def failure_check(self, sbuf, data, procedure, SocketFD):

    if procedure == "setup":
        if data['E2 Node ID'] == "" or data['RAN Function ID'] == "" or data['RAN Function Definition'] == "" or data['RAN Function Revision'] == "":
            e2_setup_failure(self, sbuf, SocketFD)
            return False

        for i in range(len(RAN_fun_id_list)):
            if data['RAN Function ID'] == RAN_fun_id_list[i]:
                e2_setup_failure(self, sbuf, SocketFD)
                return False

        return True

    elif procedure == "control":
        check_SocketFD = -1

        if data['RAN Function ID'] == "" or data['RIC Control Header'] == "" or data['RIC Control Message'] == "":
            error_empty_xapp(self, data, get_Requestor_ID(data))
            return False, check_SocketFD
        """else:
            return True, check_SocketFD"""
        
        # check SockFD's correctness
        mysdl = _try_func_return(SyncStorage)
        is_active = mysdl.is_active()
        assert is_active is True

        xApp_ID = int(data['RIC Request ID']['RIC Requestor ID'])
        group_index = str((xApp_ID - 8000)//66)
        warn_msg = 'This port is irregularity.'
        white_text = eval(_try_func_return(lambda: mysdl.get('White', {str('text')}))['text'].decode())
        try:
            white_text = white_text[group_index]
            #print('group_index:', group_index, ' white_text: ', white_text)
            if(xApp_ID not in white_text['listport']):
                #print('warn_msg 1: ', warn_msg) # This port is not in the group
                return False, check_SocketFD
            if(data['SocketFD'] != white_text['SocketFD']): # The SocketFD is wrong
                check_SocketFD = white_text['SocketFD']
        except:
            #print('warn_msg 2: ', warn_msg) # This port is not in the white text table
            return False, check_SocketFD
        return True, check_SocketFD

# write in local routing table
def write_routing_table(NameSpace, Key):
    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True

    #print("Write xApp information into routing table!!!\n")

    f = open("test_route_thrd.rt", 'w+')
    f.write('newrt|start\n')
    data = eval(_try_func_return(lambda: mysdl.get(
        NameSpace, {str(Key)}))[Key].decode())
    for key in data.keys():
        ip = data[key]['IP']
        port = str(data[key]['port'])
        messagetype = str(data[key]['massage_type'])+port
        f.write('rte|'+messagetype+'|'+ip+':'+port+'\n')
    f.write('newrt|end\n')
    f.seek(0)
    # txt=f.read()
    # #print(txt)
    f.close()
    #print("Write in routing table succussful!!!")
    #print("Update after 60s.\n")

def Request_Report(self, RIC_ID, SocketFD, xappIP):
    # xApp needs to get report data from E2 manager.
    # connect to influxdb
    client = InfluxDBClient(influxdbIP, influxdbPort, 'root', '', 'reportdb')
    tables = 'report_' + str(RIC_ID) + str(SocketFD)
    
    # get data from influxdb
    result = client.query('select * from ' + tables)
    ##print("influxdb data:", list(result.get_points()))
    report_data = list(result.get_points())
    # send to xApp
    val = json.dumps(
        {"ACK": RIC_ID, "Report Data": report_data}).encode()
    
    try:
        #print("870 Time:",time.ctime())
        #print("sdl ip:",RIC_ID)
        hostname = xappIP
        response = os.system("ping -c 1 " + hostname)
        #and then check the response...
        if response == 0:
            #print("UP Time:",time.ctime())
            self.rmr_send(val, int("871"+str(RIC_ID)))
        else:
            pass
            #print('down Time',time.ctime())
    except:
        #print("870 else")
        pass

    #self.rmr_send(val, int('871'+str(RIC_ID)))


# Send to E2 termination
def Send2E2T(self, summary, sbuf):
    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True
 
    
    jpay = json.loads(summary['payload'])
    message = str(summary['message type'])
    message = int(message[0:3])
    SocketFD = get_SocketFD(jpay)

    # Control Request
    if message == 610:
        """
        mysdl = _try_func_return(SyncStorage)
        is_active = mysdl.is_active()
        assert is_active is True
        """
        if len(str(SocketFD))<5:
            pass
        else:
            #self.logger.info("E2 Manager 610 handler called!")
            print("Control Request: ", time.time())
            #print("Got the 610 Control Request!!\n")
            check, check_SocketFD = failure_check(self, sbuf, jpay, "control", SocketFD)
            if(check_SocketFD != -1):
                jpay['SocketFD'] = check_SocketFD
            if check:
                jpay['SocketFD']= int(_try_func_return(lambda: mysdl.get(str(jpay['SocketFD']), {str('SocketFD')}))['SocketFD'].decode())
                #print("610 payload:", jpay, "\n")
                val = json.dumps(jpay).encode()
                self.rmr_send(val, int('6004000'))
                #entry(self, sbuf, val, 6004000)
                #print("Send it\n")

    self.rmr_free(sbuf)
"""
def report_thread(self, xappID, xApp_port)
    t = threading.Timer(1, send_broadcast)
    t.start()
"""
"""
def report_thread_function(self, xappID, xApp_port, val):
    try:
        #print("Time:",time.ctime())
        #print("sdl ip:",xappID)
        hostname = xappID
        response = os.system("ping -c 1 " + hostname)
        
        #and then check the response...
        if response == 0:
            #print("UP Time:",time.ctime())
            self.rmr_send(val, int("700"+str(xApp_port)))
        else:
            pass
            #print('down Time',time.ctime())

    except:
        #print("else")
        pass

    
    #global q
    #createTimer()
    #size = q.qsize()
    #if size > 0:
    #    new = RMRXapp(default_handler=Routing, rmr_port=4601, post_init=send, use_fake_sdl=False)
    #    new.run()
"""

global eport_time_before
eport_time_before = 0
sum_report_time=0
report_time=0
# Send to xApp
def Send2xApp(self, summary, sbuf):
    global xApp_port,sum_report_time,report_time
    """global count"""
    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True
    
    #tracemalloc.start()

    jpay = summary['payload']
    message = str(summary['message type'])
    message = int(message[0:3])
    print("700 jpay:",jpay)
    data = jpay.decode('utf-8')

    if data != "":
        #print("Data is OK\n")
        payload = data[data.index("{") + 1:data.rindex("}")]
        payload = "{" + payload + "}"
        #print("data:", payload, "type:", type(payload))
        #print("##message:",message)
        #print("\njpay",jpay)
        
        dataSize = sys.getsizeof(jpay)
        jpay = json.loads(payload)

        xApp_port = get_Requestor_ID(jpay)

        
        
 
        ##print("jpay['Procedure Code']:",jpay['Procedure Code'])
        ##print("jpay['RIC Indication Message']:",jpay['RIC Indication Message)'])
       
        #dataSize = sys.getsizeof(jpay)
        #jpay = json.loads(payload)

        #xApp_port = get_Requestor_ID(jpay)


        # Control Response
        if message == 601:
            #self.logger.info("E2 Manager 601 Response!")
            print("Receive Control ACK: ", time.time())
            #print("Got the 601 Control Response (ACK)!!\n")
            #print("601 Payload:", jpay, "\n")
            jpay = jpay['RIC Control Status']
            if jpay == 0:
                jpay='Success'
            else:
                jpay='False'
            """
            xApp_ID = int(jpay['RIC Request ID']['RIC Requestor ID'])
            group_index = str((xApp_ID - 8000)//66)
            white_text = eval(_try_func_return(lambda: mysdl.get('White', {str('text')}))['text'].decode())
            #RequestFD = white_text[group_index]['SocketFD']
            jpay['SocketFD']= white_text[group_index]['SocketFD']
            """
            val = json.dumps(jpay).encode()
            #print("601 Payload val#@:",val)
            
            messagetype = int("611"+str(xApp_port))
            self.rmr_send(val, messagetype)
            print("Send Control ACK: ", time.time())

        # Control Failure
        if message == 604:
            self.logger.info("E2 Manager 604 Control Failure!")
            #print("Got the 604 Control Failure!!\n")
            #print("604 Received:", jpay, "\n")

            #print("Send 614 Control Failure to xApp")
            val = json.dumps(jpay).encode()
            self.rmr_send(val, int("614"+str(xApp_port)))

        # Indication Report
        if message == 700:
#            global report_time_before
#            try:
#                report_time_after = time.time()
#                #print("report_time_after is OK !!!")
#                report_time = report_time_after - report_time_before
#                #print("report_time is OK !!!")
#                report_time_before = report_time_after
#                #print("report_time_before is OK !!!")
#            except:
#                print("Enter except")
#                report_time_before = time.time()
#                report_time = 0
            #if count==250:
            #os.execl(sys.executable, sys.executable, *sys.argv)
#            self.logger.info("\n\nGot 700 Indication Report! \nTime: " + str(report_time))
#            print("Reporting period: ", report_time)
            #print("Got the 700 Indication Report!!\n")
            #print("Receive report: ", time.time())
            Receive_report = time.time()
            #print("700 Received:", jpay, "\n")
            #print('Size of integer:', dataSize)

            """val = json.dumps({
                "RIC Requestor ID": jpay['RIC Request ID']['RIC Requestor ID'],
                "paysize": dataSize
            }).encode()

            self.rmr_send(val, 67006000)
            Temporary_storage_Report.append(jpay)"""
            #report_influxdb = dbreport(jpay, message)
            store_thread = threading.Thread(target=dbreport, args=(jpay, message,))
            store_thread.start()
            #print("Send 700 Indication Report to xApp")
            InicationMs=jpay['RIC Indication Message']
            #InicationMs.update({'Time':time.time()})
            val = json.dumps(InicationMs).encode()
            
            #my_ret_dict = _try_func_return(lambda: mysdl.get(str('connecter'), {str(xApp_port)}))
            ##xappID = list(_try_func_return(lambda: mysdl.get_members('connecter', str(jpay['RIC Request ID']['RIC Requestor ID']))))
            #xappID = self.sdl_get('connecter', str(jpay['RIC Request ID']['RIC Requestor ID'])) # '10.0.2.15'

            #report_thread(self, xappID, xApp_port)
            """
            report_thread = threading.Timer(1, report_thread_function)
            report_thread.start()
            """
#            report_thread = threading.Thread(target=report_thread_function, args=(self, xappID, xApp_port, val))
#            report_thread.start()
            self.rmr_send(val, int("700"+str(xApp_port)))

            report_time = report_time + 1
            sum_report_time = sum_report_time+time.time()-Receive_report
            #print("Send report: ", time.time())
            print("average Receive_report->Send report: ", sum_report_time/report_time)
            del val
            gc.collect()
            #collect_stats = gc.get_stats()
            #print("collect stats = ", collect_stats)
            
            store_thread.join()
            """
            try:
                #print("Time:",time.ctime())
                #print("sdl ip:",xappID)
                hostname = xappID
                response = os.system("ping -c 1 " + hostname)
                #and then check the response...
                if response == 0:
                    #print("UP Time:",time.ctime())
                    self.rmr_send(val, int("700"+str(xApp_port)))
                else:
                    pass
                    #print('down Time',time.ctime())

            except:
                #print("else")
                pass
            """
            #self.rmr_send(val, int("700"+str(xApp_port)))
            #print("@@@count:",count)
            """count +=1"""
        # Indication Insert
        if message == 710:
            self.logger.info("Got 710 Indication Insert!")
            #print("Got 710 Indication Insert!!\n")
            #print("710 Received:", jpay, "\n")

            """val = json.dumps({
                "RIC Requestor ID": jpay['RIC Request ID']['RIC Requestor ID'],
                "paysize": dataSize
            }).encode()

            self.rmr_send(val, 67106000)
            Temporary_storage_Insert.append(jpay)"""
            #report_influxdb = dbreport(jpay, message)
            
            #print("Send 710 Indication Insert to xApp")
            val = json.dumps(jpay).encode()
            self.rmr_send(val, int("710"+str(xApp_port)))

        # Indication Insert
        if message == 720:
            self.logger.info("Got 720 E2 Node Disconnected!")
            #print("Got 720 E2 Node Disconnected!!\n")
            #print("720 Received:", jpay, "\n")
            val = json.dumps(jpay).encode()
            self.rmr_send(val, int("720"+str(xApp_port)))


        # Error Indication
        if message == 740:
            self.logger.info("Got 740 Error Indication !")
            #print("Got 740 Error Indication !!\n")
            #print("740 Received:", jpay, "\n")

            #print("Send 740 Error Indication to xApp")
            val = json.dumps(jpay).encode()

            self.rmr_send(val, int("710"+str(xApp_port)))

        # Report Query
        if message == 870:
            self.logger.info("Got 870 Report Query!")
            #print("Got 870 Report Query!!\n")
            #print("870 Received:", jpay, "\n")
            #SocketFD = jpay['SocketFD']
            xApp_port_SPC = jpay['RIC Requestor ID']#xApp_ID
            xappIP = self.sdl_get('connecter', str(jpay['RIC Requestor ID']))

            """
            group_index = str((xApp_port_SPC - 8000)//66)
            white_text = eval(_try_func_return(lambda: mysdl.get('White', {str('text')}))['text'].decode())
            SocketFD = white_text[group_index]['SocketFD']
            """
            
            #query_report_thread = threading.Thread(target=query_report_thread_function, args=(self, xApp_port_SPC, jpay))
            #query_report_thread.start()

            try:
                SocketFD = _try_func_return(lambda: mysdl.get(jpay['SocketFD'], {str('SocketFD')}))['SocketFD'].decode()
                Request_Report(self, xApp_port_SPC, SocketFD, xappIP)
            except:
                pass
                #print("\n")


        self.rmr_free(sbuf)

    else:
        error_empty_tm(self, "empty", sbuf)
    """
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    for stat in top_stats:
        print(stat)

    tracemalloc.stop()
    """


# Default Setting
def e2_process(self, summary, sbuf):
    jpay = summary['payload']
    message = str(summary['message type'])
    message = int(message[0:3])
    data = jpay.decode('utf-8')

    if data != "":
        #print("Data is OK\n")
        payload = data[data.index("{") + 1:data.rindex("}")]
        payload = "{" + payload + "}"
        dataSize = sys.getsizeof(jpay)
        jpay = json.loads(payload)
        SocketFD = get_SocketFD(jpay)

        # Recieve E2 setup request --> Response 201
        if message == 200:
            mysdl = _try_func_return(SyncStorage)
            is_active = mysdl.is_active()
            assert is_active is True
    
            #self.logger.info("Got 200 E2 Setup Request!")
            #print("Got 200 E2 Setup Request!!")
            print("200 Received:", jpay, "\n")
            #print("payload length:", len(data))
            #print('size of integer:', sys.getsizeof(jpay))
            dataSize = sys.getsizeof(data)

            #check = failure_check(self, sbuf, jpay, "setup", SocketFD)
            check = True
            if check:
                val = json.dumps({
                    "E2 Node ID": jpay['E2 Node ID'].replace(' ',''),
                    "paysize": dataSize,
                    "SocketFD":jpay['SocketFD']
                }).encode()
                #print("Send 6200 to RIC Redis Manager\n")
                self.rmr_send(val, 62006000)
                Temporary_storage_E2setup.append(jpay) 
                #RAN_fun_id_list.append(jpay['RAN Function ID'])

        # Error indication
        elif message == 740:
            self.logger.info("Got 740 Error Indication!")
            #print("Got 740 Error Indication!\n")
            #print("740 Received:", jpay, "\n")

        # Service Update
        elif message == 800:
            self.logger.info("Got 800 Service Update!")
            #print("Got 800 Service Update!\n")
            #print("800 Received:", jpay, "\n")

            try:
                mode = jpay["RAN Functions Added"]
            except:
                try:
                    mode = jpay["RAN Functions Modified"]
                except:
                    mode = jpay["RAN Functions Deleted"]

            #print("Mode", mode, "\n")

            val = json.dumps(jpay).encode()
            #entry(self, sbuf, val, 8014000)
            self.rmr_send(val, int('8014000'))
        #Restart E2 manager
        elif message == 100:
            self.logger.info("Received the 1000 Routing Restart!!")
            #print("Received the 1000 Routing Restart!!\n")
            #print("1000 Received:", jpay, "\n")

            NS = jpay['Routing Table']['Namespace']
            key1 = jpay['Routing Table']['Key']

            write_routing_table(NS, key1)

        else:
            self.logger.info("Default Callback!")
            #print("Default handler received: {0}".format(summary))

        self.rmr_free(sbuf)

    else:
        #print("Received: {0}".format(summary))
        error_empty_tm(self, "empty", sbuf)
        self.rmr_free(sbuf)


#Send to E2 Termination
def entry(self, sbuf, data, message):

    # Init rmr
    mrc = rmr.rmr_init(b"9998", rmr.RMR_MAX_RCV_BYTES, 0x00)
    while rmr.rmr_ready(mrc) == 0:
        time.sleep(1)
        #print("Not yet ready")
    rmr.rmr_set_stimeout(mrc, 2)
    sbuf = rmr.rmr_alloc_msg(mrc, 1024)
    val=data
    
    try:
        val = data.encode('utf-8')

    except:
        val = data
    
    #print("val control request:",val) 
    rmr.set_payload_and_length(val, sbuf)
    rmr.generate_and_set_transaction_id(sbuf)
    sbuf.contents.state = 0
    sbuf.contents.mtype = message
    #print("Send summary: {}".format(rmr.message_summary(sbuf)))
    sbuf = rmr.rmr_send_msg(mrc, sbuf)
    #print("Post send summary: {}".format(rmr.message_summary(sbuf)))
    #print("\n")


# Store the data into database
def db(self, summary, sbuf):
    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True

    jpay = json.loads(summary['payload'])
    message = summary['message type']
    #print("Got the 6201 message!!!!!!!!!\n")
    #print("6201 Received:", jpay)

    # Wrong message
    if((message % 10) == 4):
        if(jpay['NAK'] == -2):
            #print("There is something wrong. Please check the RMR message type.")
            os._exit(0)
        elif(jpay['NAK'] == -1):
            #print("The memoory is full. Please wait.")
            os._exit(0)

    MY_NS = jpay['namespace']
    #print("MY_NS:", MY_NS)
    #_try_func_return(lambda: mysdl.set(str(jpay["E2 Node ID"].encode()), {'SocketFD': str(jpay["SocketFD"].encode())}))

    # Store data in redis
    try:
        tmpdata = Temporary_storage_E2setup.pop(0)
    except:
        #print("The Temporary_storage_E2setup is empty")
        return
    _try_func_return(lambda: mysdl.set(str(tmpdata["E2 Node ID"]).replace(' ','') , {'SocketFD': str(tmpdata["SocketFD"]).encode()}))
    #print("Send 201 back to E2 Termination\n")
                
    val = json.dumps({
        "Global RIC ID": 1,
        "RAN Function ID": tmpdata['RAN Function ID'],
        "Procedure Code": 1,
        "Type of Message": 1,
        "SocketFD":  tmpdata['SocketFD']
    }).encode()
    #print("to E2_agent val:",val)
    #entry(self, sbuf, val, 2014000)
    self.rmr_send(val, int('2014000'))
    print("to E2_agent val:",val)

    storedata = {}
    for col in jpay["columns"]:
        try:
            storedata.update({str(col): tmpdata[col]})
        except:
            pass
    storedata.update({'xAppID': 99999})
    storedata.update({"SocketFD":storedata['E2 Node ID'].replace(' ','')})
    store_data = str(storedata)
    byte_send_data = store_data.encode()
    _try_func_return(lambda: mysdl.set(
        MY_NS, {str(storedata['E2 Node ID'].replace(' ','')): byte_send_data}))
    #print("Store in Redis\n")

    # Get data in redis
    my_ret_dict = _try_func_return(lambda: mysdl.get(
        MY_NS, {str(storedata['E2 Node ID'].replace(' ',''))}))
    #print(MY_NS, " redis_get:", str(storedata['E2 Node ID'].replace(' ','')), "->", my_ret_dict)

    self.rmr_free(sbuf)


store_time=0
sum_time=0
#Report (database)
def dbreport(jpay, message):
    global client, store_time, sum_time
    start_ = time.time()
    print("**** Enter the dbreport ****")
    if(message == 700):
        #print("700 enter dbreport:", jpay)
        MY_NS = 'report'
        store_columns = ['RIC Request ID', 'RIC Instance ID', 'RAN Function ID', 'RIC Action ID', 'RIC Indication Type', 'RIC Indication Header', 'RIC Indication Message']
    elif(message == 710):
        #print("710 enter dbreport:", jpay)
        MY_NS = 'insert'
        store_columns = ['RIC Request ID', 'RIC Instance ID', 'RAN Function ID', 'RIC Action ID', 'RIC Indication Type', 'RIC Indication Header', 'RIC Indication Message', 'Call process ID']
    #print("MY_NS:", MY_NS)

    storedata = {}
    for col in store_columns:
        try:
            storedata.update({str(col): jpay[col]})
        except:
            pass

    store_data = str(storedata)
    #print("Store Data", storedata)
    
    # please decision that these still send to xApp? orange words under this line.
    """
    val = json.dumps({"ACK": storedata['RIC Request ID']['RIC Requestor ID'],
                      "RIC Requestor ID": storedata['RIC Request ID']['RIC Requestor ID'],
                      "namespace": MY_NS}).encode()
    self.rmr_send(val, 67006000)
    """
    
    # store data in influxdb

    #client = InfluxDBClient(influxdbIP, influxdbPort, 'root', '', 'reportdb')
    #print("database: ", client.get_list_database())  # 顯示所有數據庫名稱
    # client.create_database('testdb') # 創建數據庫
    # #print(client.get_list_database()) # 顯示所有數據庫名稱
    """
    retention_policy = 'exist_Time'
    try:
        client.create_retention_policy(retention_policy, '1h', 3, default=True)
    except:
        #print("Error:not successful create new retention policy.")
    """
    FD = jpay['SocketFD']
    tables = 'report_'+str(storedata['RIC Request ID']['RIC Requestor ID'])# + str(FD)
    
    # This block is for test
    #latency : ms, reliability : percentage, throughput : Gbps
    # procedure": "Indication Report"
    

    #print("storedata['RIC Request ID']['RIC Requestor ID']:",storedata['RIC Request ID']['RIC Requestor ID'])
    #print("type storedata['RIC Request ID']['RIC Requestor ID']:",storedata['RIC Request ID']['RIC Requestor ID'])
    json_body = []
    
    json_body.append(str(tables)+",procedure="+str(MY_NS)+" RIC_Requestor_ID="+str(storedata['RIC Request ID']['RIC Requestor ID'])+",RIC_Instance_ID="+str(storedata['RIC Request ID']['RIC Instance ID'])+",RAN_Function_ID="+str(storedata['RAN Function ID'])+",RIC_Action_ID="+str(storedata['RIC Action ID'])+",RIC_Indication_Type="+str(storedata['RIC Indication Type'])+",RIC_Indication_Header="+str(storedata['RIC Indication Header'])+",RIC_Indication_Message="+str(storedata['RIC Indication Message']))
    """
    json_body.append("{measurement},procedure={procedure} RIC_Requestor_ID={RIC_Requestor_ID},RIC_Instance_ID={RIC_Instance_ID},RAN_Function_ID={RAN_Function_ID},RIC_Action_ID={RIC_Action_ID},RIC_Indication_Type={RIC_Indication_Type},RIC_Indication_Header={RIC_Indication_Header},RIC_Indication_Message={RIC_Indication_Message}"
                .format(measurement='tables',
                        procedure='MY_NS',
                        RIC_Requestor_ID=int(storedata['RIC Request ID']['RIC Requestor ID']),
                        RIC_Instance_ID=int(storedata['RIC Request ID']['RIC Instance ID']),
                        RAN_Function_ID=int(storedata['RAN Function ID']),
                        RIC_Action_ID=int(storedata['RIC Action ID']),
                        RIC_Indication_Type=int(storedata['RIC Indication Type']),
                        RIC_Indication_Header=int(storedata['RIC Indication Header']),
                        RIC_Indication_Message=str(storedata['RIC Indication Message'])))        
    """
    client.write_points(json_body, batch_size=5000, protocol='line',retention_policy=retention_policy)
    
    end_ = time.time()
    store_time = store_time + 1
    sum_time = sum_time + end_- start_
    print("average storedb time = ", sum_time/store_time)
    #print("-----------------store in influxdb------------------")
    #result = client.query('select * from ' + tables)
    #print("influxdb data:", list(result.get_points()))
    """
    # please decision that these still send to xApp? orange words under this line.
    if message == 6701:
        #print("Send 700 Indication Report to xApp")
        self.rmr_send(val, int("700"+str(xApp_port)))

    elif message == 6711:
        #print("Send 710 Indication Insert to xApp")
        self.rmr_send(val, int("710"+str(xApp_port)))
    return list(result.get_points())
    """


client = InfluxDBClient(influxdbIP, influxdbPort, 'root', '', 'reportdb')
client.create_database('reportdb')  # 創建數據庫
retention_policy = 'exist_Time'
try:
    client.create_retention_policy(retention_policy, '1h', 3, default=True)
except:
    pass
    #print("Error:not successful create new retention policy.")



xapp = RMRXapp(default_handler=e2_process, rmr_port=4200,post_init=post_init, use_fake_sdl=False)


#--------------------------------------------
xapp.register_callback(Send2E2T, 6104200)  # control request
xapp.register_callback(Send2xApp, 6014200)  # control response
xapp.register_callback(Send2xApp, 6044200)  # control failure
#--------------------------------------------
xapp.register_callback(Send2xApp, 7004200)  # report
xapp.register_callback(Send2xApp, 7104200)  # insert
#--------------------------------------------
xapp.register_callback(Send2xApp, 7004200)  # report
xapp.register_callback(Send2xApp, 7204200)  # disconnected
xapp.register_callback(Send2xApp, 8704200)  # Report Query
#--------------------------------------------
xapp.register_callback(db, 62014200)  # db
xapp.register_callback(db, 62044200)  # db
xapp.register_callback(db, 66014200)  # db
xapp.register_callback(db, 66044200)  # db
#--------------------------------------------
xapp.register_callback(dbreport, 67014200)  # dbreport
xapp.register_callback(dbreport, 67044200)  # dbreport
xapp.register_callback(dbreport, 67114200)  # dbreport
xapp.register_callback(dbreport, 67144200)  # dbreport

xapp.run()  # will not thread by default
