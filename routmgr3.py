"""
Routing Manager (Giving ID / port)
"""
# Server 
import os,sys,logging,time,json,socket,signal,string,threading,queue
import redis, subprocess
from ricxappframe.xapp_frame import RMRXapp, rmr
from ricxappframe.rmr import rmr
from ricsdl.syncstorage import SyncStorage
from ricsdl.exceptions import RejectedByBackend, NotConnected, BackendError
import gc
import tracemalloc

os.environ['DBAAS_SERVICE_PORT'] = '6379'
os.environ['DBAAS_SERVICE_HOST'] = '10.0.2.15'#'10.244.0.18' #'140.123.102.112'
os.environ['RMR_SEED_RT'] = 'test_route_thrd.rt'


# Constants used in the examples below.
MY_NS = 'Routing'
MY_GRP_NS = 'Routing_group'
MY_LOCK_NS = 'my_group_ns'

Temporary_storage_RoutingTable = list()
set_list = list()
portList = list()
broadcast_list = list()
q = queue.Queue(maxsize = 0)



def _try_func_return(func):
    """
    Generic wrapper function to call SDL API function and handle exceptions if they are raised.
    """
    try:
        return func()
    except RejectedByBackend as exp:
        print(f'SDL function {func.__name__} failed: {str(exp)}')
        # Permanent failure, just forward the exception
        raise
    except (NotConnected, BackendError) as exp:
        print(f'SDL function {func.__name__} failed for a temporal error: {str(exp)}')
        # Here we could have a retry logic

def initial_thread_function(_self, Ask, xapp_temp):
    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True
    try:
        #tracemalloc.start()
        #ncvz_cmd = 'netcat -vz 10.8.0.6 8200'
        #print("initial_thread_function")
        xapp_temp_IP = _self.sdl_get('connecter', str(xapp_temp))
        ncvz_cmd = 'nc -vz ' + str(xapp_temp_IP) + ' ' + str(xapp_temp)
        #print("ncvz_cmd:",ncvz_cmd)
        process = subprocess.Popen(ncvz_cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        process_read = process.stderr.read()
        print("process_read:",process_read.decode())
        #print("\nprocess_read[0]:",str(process_read)[0])
        if process_read.decode()!='':
            _self.rmr_send(Ask, int("901"+str(xapp_temp)))
            _self.logger.info("Send success it~~")
            print("send back to ",xapp_temp)
            """
            garbage = json.dumps({
                '1234567':{'IP':'10.0.2.15', 'massage_type': 200, 'port':4200}, \
                '2234567':{'IP':'10.0.2.15', 'massage_type': 300, 'port':4400}, \
                '3234567':{'IP':'10.0.2.15', 'massage_type': 410, 'port':4400}, \
                '4234567':{'IP':'10.0.2.15', 'massage_type': 401, 'port':4400}, \
                '5234567':{'IP':'10.0.2.15', 'massage_type': 404, 'port':4400}, \
                '6234567':{'IP':'10.0.2.15', 'massage_type': 200, 'port':4200}, \
                '7234567':{'IP':'10.0.2.15', 'massage_type': 300, 'port':4400}, \
                '8234567':{'IP':'10.0.2.15', 'massage_type': 410, 'port':4400}, \
                '9234567':{'IP':'10.0.2.15', 'massage_type': 401, 'port':4400}, \
                '0234567':{'IP':'10.0.2.15', 'massage_type': 404, 'port':4400}, \
                '1234568':{'IP':'10.0.2.15', 'massage_type': 200, 'port':4200}, \
                '2234568':{'IP':'10.0.2.15', 'massage_type': 300, 'port':4400}, \
                '3234568':{'IP':'10.0.2.15', 'massage_type': 410, 'port':4400}, \
                '4234568':{'IP':'10.0.2.15', 'massage_type': 401, 'port':4400}, \
                '5234568':{'IP':'10.0.2.15', 'massage_type': 404, 'port':4400}, \
                '6234568':{'IP':'10.0.2.15', 'massage_type': 200, 'port':4200}, \
                '7234568':{'IP':'10.0.2.15', 'massage_type': 300, 'port':4400}, \
                '8234568':{'IP':'10.0.2.15', 'massage_type': 410, 'port':4400}, \
                '9234568':{'IP':'10.0.2.15', 'massage_type': 401, 'port':4400}, \
                '0234568':{'IP':'10.0.2.15', 'massage_type': 404, 'port':4400}, \
                '1234569':{'IP':'10.0.2.15', 'massage_type': 200, 'port':4200}, \
                '2234569':{'IP':'10.0.2.15', 'massage_type': 300, 'port':4400}, \
                '3234569':{'IP':'10.0.2.15', 'massage_type': 410, 'port':4400}, \
                '4234569':{'IP':'10.0.2.15', 'massage_type': 401, 'port':4400}, \
                '5234569':{'IP':'10.0.2.15', 'massage_type': 404, 'port':4400}, \
                '6234569':{'IP':'10.0.2.15', 'massage_type': 200, 'port':4200}, \
                '7234569':{'IP':'10.0.2.15', 'massage_type': 300, 'port':4400}, \
                '8234569':{'IP':'10.0.2.15', 'massage_type': 410, 'port':4400}, \
                '9234569':{'IP':'10.0.2.15', 'massage_type': 401, 'port':4400}, \
                '0234569':{'IP':'10.0.2.15', 'massage_type': 404, 'port':4400}, \
                '2004200':{'IP':'10.0.2.15', 'massage_type': 200, 'port':4200}, \
                '3004400':{'IP':'10.0.2.15', 'massage_type': 300, 'port':4400}, \
                '4104400':{'IP':'10.0.2.15', 'massage_type': 410, 'port':4400}, \
                '4014400':{'IP':'10.0.2.15', 'massage_type': 401, 'port':4400}, \
                '4044400':{'IP':'10.0.2.15', 'massage_type': 404, 'port':4400}, \
                '5014400':{'IP':'10.0.2.15', 'massage_type': 501, 'port':4400}, \
                '5044400':{'IP':'10.0.2.15', 'massage_type': 504, 'port':4400}, \
                '5104400':{'IP':'10.0.2.15', 'massage_type': 510, 'port':4400}, \
                '6014200':{'IP':'10.0.2.15', 'massage_type': 601, 'port':4200}, \
                '6044200':{'IP':'10.0.2.15', 'massage_type': 604, 'port':4200}, \
                '6104200':{'IP':'10.0.2.15', 'massage_type': 610, 'port':4200}, \
                '7004200':{'IP':'10.0.2.15', 'massage_type': 700, 'port':4200}, \
                '7104200':{'IP':'10.0.2.15', 'massage_type': 710, 'port':4200}, \
                '7204200':{'IP':'10.0.2.15', 'massage_type': 720, 'port':4200}, \
                '7204400':{'IP':'10.0.2.15', 'massage_type': 720, 'port':4400}, \
                '7404200':{'IP':'10.0.2.15', 'massage_type': 740, 'port':4200}, \
                '7404400':{'IP':'10.0.2.15', 'massage_type': 740, 'port':4400}, \
                '8004200':{'IP':'10.0.2.15', 'massage_type': 800, 'port':4200}, \
                '8104200':{'IP':'10.0.2.15', 'massage_type': 810, 'port':4200}, \
                '8104400':{'IP':'10.0.2.15', 'massage_type': 810, 'port':4400}, \
                '8404400':{'IP':'10.0.2.15', 'massage_type': 840, 'port':4400}, \
                '8704200':{'IP':'10.0.2.15', 'massage_type': 870, 'port':4200}, \
                '9004600':{'IP':'10.0.2.15', 'massage_type': 900, 'port':4600}, \
                '9104200':{'IP':'10.0.2.15', 'massage_type': 910, 'port':4200}, \
                '10004200':{'IP':'10.0.2.15', 'massage_type':1000, 'port':4200}, \
                '10004400':{'IP':'10.0.2.15', 'massage_type':1000, 'port':4400}, \
                '10006000':{'IP':'10.0.2.15', 'massage_type':1000, 'port':6000}, \
                '10006600':{'IP':'10.0.2.15', 'massage_type':1000, 'port':6600}, \
                '62006000':{'IP':'10.0.2.15', 'massage_type':6200, 'port':6000}, \
                '62014200':{'IP':'10.0.2.15', 'massage_type':6201, 'port':4200}, \
                '62044200':{'IP':'10.0.2.15', 'massage_type':6204, 'port':4200}, \
                '63006000':{'IP':'10.0.2.15', 'massage_type':6300, 'port':6000}, \
                '63014400':{'IP':'10.0.2.15', 'massage_type':6301, 'port':4400}, \
                '64006000':{'IP':'10.0.2.15', 'massage_type':6400, 'port':6000}, \
                '64014400':{'IP':'10.0.2.15', 'massage_type':6401, 'port':4400}, \
                '64044400':{'IP':'10.0.2.15', 'massage_type':6404, 'port':4400}, \
                '65006000':{'IP':'10.0.2.15', 'massage_type':6500, 'port':6000}, \
                '65014400':{'IP':'10.0.2.15', 'massage_type':6501, 'port':4400}, \
                '65044400':{'IP':'10.0.2.15', 'massage_type':6504, 'port':4400}, \
                '66006000':{'IP':'10.0.2.15', 'massage_type':6600, 'port':6000}, \
                '66014200':{'IP':'10.0.2.15', 'massage_type':6601, 'port':4200}, \
                '66044200':{'IP':'10.0.2.15', 'massage_type':6604, 'port':4200}, \
                '67006000':{'IP':'10.0.2.15', 'massage_type':6700, 'port':6000}, \
                '67014200':{'IP':'10.0.2.15', 'massage_type':6701, 'port':4200}, \
                '67044200':{'IP':'10.0.2.15', 'massage_type':6704, 'port':4200}, \
                '67106000':{'IP':'10.0.2.15', 'massage_type':6710, 'port':6000}, \
                '67114200':{'IP':'10.0.2.15', 'massage_type':6711, 'port':4200}, \
                '67144200':{'IP':'10.0.2.15', 'massage_type':6714, 'port':4200}, \
                '69006600':{'IP':'10.0.2.15', 'massage_type':6900, 'port':6600}, \
                '69014600':{'IP':'10.0.2.15', 'massage_type':6901, 'port':4600}, \
                '69044600':{'IP':'10.0.2.15', 'massage_type':6904, 'port':4600}, \
                '2014000':{'IP':'10.0.2.15', 'massage_type':201, 'port':4000}, \
                '2044000':{'IP':'10.0.2.15', 'massage_type':204, 'port':4000}, \
                '3014000':{'IP':'10.0.2.15', 'massage_type':301, 'port':4000}, \
                '3044000':{'IP':'10.0.2.15', 'massage_type':304, 'port':4000}, \
                '4004000':{'IP':'10.0.2.15', 'massage_type':400, 'port':4000}, \
                '5004000':{'IP':'10.0.2.15', 'massage_type':500, 'port':4000}, \
                '6004000':{'IP':'10.0.2.15', 'massage_type':600, 'port':4000}, \
                '7404000':{'IP':'10.0.2.15', 'massage_type':740, 'port':4000} \
                }).encode()
            _self.rmr_send(garbage, int("22222"+str(xapp_temp)))
            print("garbage size=",sys.getsizeof(garbage)) 
            print("\n")               
            
            #del Ask,garbage
            #gc.collect()
            """
        else:
            _self.logger.info("can't netcat port~~")
            print("send back failure")
        """
        _self.rmr_send(Ask, int("901"+str(xapp_temp)))
        _self.logger.info("Send success it~~")
        
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')

        for stat in top_stats:
            print(stat)
        
        tracemalloc.stop()
        """

    except:
        _self.logger.info("Send fail!!!!!!!!~~\n")
        #pass



def createTimer():
    t = threading.Timer(5, send_broadcast)
    t.start()

def send_broadcast():
    global q
    createTimer()
    size = q.qsize()
    if size > 0:
        new = RMRXapp(default_handler=Routing, rmr_port=4601, post_init=send, use_fake_sdl=False)
        new.run()


def send(_self):
    global q,MY_NS,MY_GRP_NS
    #tracemalloc.start()
    #print("Sending to xApp!!")
    print("Time:",time.ctime()) 
    _self.logger.info("Sending to xApp!!")
    size = q.qsize()
    if size > 0:
        for _ in range(size):
            xapp_temp = q.get()
            if(xapp_temp  not in broadcast_list):
                broadcast_list.append(xapp_temp)
            Ask = json.dumps({
                "Port":xapp_temp,
                "Routing Table":{"Namespace":MY_NS,"Key":"table"},
                "xApp list":{"Namespace":MY_GRP_NS,"Key":"set"}
            }).encode()
            print("Send back to",str(xapp_temp))

            initial_thread = threading.Thread(target=initial_thread_function, args=(_self, Ask, xapp_temp))
            initial_thread.start()
            """
            try:
                _self.rmr_send(Ask, int("901"+str(xapp_temp)))
                _self.logger.info("Send success it~~")
            except:
                _self.logger.info("Send fauil it~~")
            """    
    """ 
    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')

    for stat in top_stats:
        print(stat)
        
    tracemalloc.stop()
    """ 
    _self.stop()


#initail value
"""post init"""
def post_init(_self):

    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True
    if(len(_try_func_return(lambda: mysdl.get('White', {str('text')})))==0):
        # create white text
        NumOfGroup = 15
        mapping = {}
        for num in range(NumOfGroup):
            mapping.update({str(num):{'SocketFD':99999, 'MasterID':-1, 'listport':[8000+num*66+i for i in range(5)]}})
        byte_store_data = str(mapping).encode()
        _try_func_return(lambda: mysdl.set('White', {str('text'): byte_store_data}))
        print('Create white text.')

    ContainerDict = {"4000" : "e2t-service.default.svc.cluster.local", "4200" : "e2mgr-service.default.svc.cluster.local", "4400" : "submgr-service.default.svc.cluster.local", "4600" : "routmgr-service.default.svc.cluster.local" , "6000" : "mredis-service.default.svc.cluster.local", "6600" : "routeredis-service.default.svc.cluster.local" }
    
    print("****************************************\n")
    global portList,MY_NS,MY_GRP_NS,broadcast_list
    print("Routing Manager starting!!")
    _self.logger.info("Routing Manager starting!!")
    createTimer()
    print("---Timer create---")
   
    print("Initial Port....\n")
    for i in range(0,65536):
        portList.append(0)
    
    broadcast_list.append(4200)
    broadcast_list.append(4400)

    # default routing table
    """mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True"""

    MY_NS = 'Routing'
    MY_GRP_NS = 'Routing_group'
    my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, {str('table')}))
    #print("my_ret_dict:", my_ret_dict)
    if(len(my_ret_dict)==0):
        newdata = {'2004200':{'IP':'10.0.2.15', 'massage_type': 200, 'port':4200}, \
                    '3004400':{'IP':'10.0.2.15', 'massage_type': 300, 'port':4400}, \
                    '4104400':{'IP':'10.0.2.15', 'massage_type': 410, 'port':4400}, \
                    '4014400':{'IP':'10.0.2.15', 'massage_type': 401, 'port':4400}, \
                    '4044400':{'IP':'10.0.2.15', 'massage_type': 404, 'port':4400}, \
                    '5014400':{'IP':'10.0.2.15', 'massage_type': 501, 'port':4400}, \
                    '5044400':{'IP':'10.0.2.15', 'massage_type': 504, 'port':4400}, \
                    '5104400':{'IP':'10.0.2.15', 'massage_type': 510, 'port':4400}, \
                    '6014200':{'IP':'10.0.2.15', 'massage_type': 601, 'port':4200}, \
                    '6044200':{'IP':'10.0.2.15', 'massage_type': 604, 'port':4200}, \
                    '6104200':{'IP':'10.0.2.15', 'massage_type': 610, 'port':4200}, \
                    '7004200':{'IP':'10.0.2.15', 'massage_type': 700, 'port':4200}, \
                    '7104200':{'IP':'10.0.2.15', 'massage_type': 710, 'port':4200}, \
                    '7204200':{'IP':'10.0.2.15', 'massage_type': 720, 'port':4200}, \
                    '7204400':{'IP':'10.0.2.15', 'massage_type': 720, 'port':4400}, \
                    '7404200':{'IP':'10.0.2.15', 'massage_type': 740, 'port':4200}, \
                    '7404400':{'IP':'10.0.2.15', 'massage_type': 740, 'port':4400}, \
                    '8004200':{'IP':'10.0.2.15', 'massage_type': 800, 'port':4200}, \
                    '8104200':{'IP':'10.0.2.15', 'massage_type': 810, 'port':4200}, \
                    '8104400':{'IP':'10.0.2.15', 'massage_type': 810, 'port':4400}, \
                    '8404400':{'IP':'10.0.2.15', 'massage_type': 840, 'port':4400}, \
                    '8704200':{'IP':'10.0.2.15', 'massage_type': 870, 'port':4200}, \
                    '9004600':{'IP':'10.0.2.15', 'massage_type': 900, 'port':4600}, \
                    '9104200':{'IP':'10.0.2.15', 'massage_type': 910, 'port':4200}, \
                    '10004200':{'IP':'10.0.2.15', 'massage_type':1000, 'port':4200}, \
                    '10004400':{'IP':'10.0.2.15', 'massage_type':1000, 'port':4400}, \
                    '10006000':{'IP':'10.0.2.15', 'massage_type':1000, 'port':6000}, \
                    '10006600':{'IP':'10.0.2.15', 'massage_type':1000, 'port':6600}, \
                    '62006000':{'IP':'10.0.2.15', 'massage_type':6200, 'port':6000}, \
                    '62014200':{'IP':'10.0.2.15', 'massage_type':6201, 'port':4200}, \
                    '62044200':{'IP':'10.0.2.15', 'massage_type':6204, 'port':4200}, \
                    '63006000':{'IP':'10.0.2.15', 'massage_type':6300, 'port':6000}, \
                    '63014400':{'IP':'10.0.2.15', 'massage_type':6301, 'port':4400}, \
                    '64006000':{'IP':'10.0.2.15', 'massage_type':6400, 'port':6000}, \
                    '64014400':{'IP':'10.0.2.15', 'massage_type':6401, 'port':4400}, \
                    '64044400':{'IP':'10.0.2.15', 'massage_type':6404, 'port':4400}, \
                    '65006000':{'IP':'10.0.2.15', 'massage_type':6500, 'port':6000}, \
                    '65014400':{'IP':'10.0.2.15', 'massage_type':6501, 'port':4400}, \
                    '65044400':{'IP':'10.0.2.15', 'massage_type':6504, 'port':4400}, \
                    '66006000':{'IP':'10.0.2.15', 'massage_type':6600, 'port':6000}, \
                    '66014200':{'IP':'10.0.2.15', 'massage_type':6601, 'port':4200}, \
                    '66044200':{'IP':'10.0.2.15', 'massage_type':6604, 'port':4200}, \
                    '67006000':{'IP':'10.0.2.15', 'massage_type':6700, 'port':6000}, \
                    '67014200':{'IP':'10.0.2.15', 'massage_type':6701, 'port':4200}, \
                    '67044200':{'IP':'10.0.2.15', 'massage_type':6704, 'port':4200}, \
                    '67106000':{'IP':'10.0.2.15', 'massage_type':6710, 'port':6000}, \
                    '67114200':{'IP':'10.0.2.15', 'massage_type':6711, 'port':4200}, \
                    '67144200':{'IP':'10.0.2.15', 'massage_type':6714, 'port':4200}, \
                    '69006600':{'IP':'10.0.2.15', 'massage_type':6900, 'port':6600}, \
                    '69014600':{'IP':'10.0.2.15', 'massage_type':6901, 'port':4600}, \
                    '69044600':{'IP':'10.0.2.15', 'massage_type':6904, 'port':4600}, \
                    '2014000':{'IP':'10.0.2.15', 'massage_type':201, 'port':4000}, \
                    '2044000':{'IP':'10.0.2.15', 'massage_type':204, 'port':4000}, \
                    '3014000':{'IP':'10.0.2.15', 'massage_type':301, 'port':4000}, \
                    '3044000':{'IP':'10.0.2.15', 'massage_type':304, 'port':4000}, \
                    '4004000':{'IP':'10.0.2.15', 'massage_type':400, 'port':4000}, \
                    '5004000':{'IP':'10.0.2.15', 'massage_type':500, 'port':4000}, \
                    '6004000':{'IP':'10.0.2.15', 'massage_type':600, 'port':4000}, \
                    '7404000':{'IP':'10.0.2.15', 'massage_type':740, 'port':4000} \
                   }

        byte_store_data = str(newdata).encode()
        _try_func_return(lambda: mysdl.set(MY_NS, {str('table'): byte_store_data}))
        newset = []
        for i in list(newdata.keys()):
            newset.append(newdata[i]['port'])
            _try_func_return(lambda: mysdl.add_member(MY_GRP_NS, 'set', {newdata[i]['port']}))
        #_try_func_return(lambda: mysdl.add_member(MY_GRP_NS, 'set', {newset}))
        print("Initial: store in Redis\n")

    print("****************************************")

    print("E2 manager store route table from DB----------------------")
    my_ret_dict =   _try_func_return(lambda: mysdl.get('Routing', {str('table')}))
    if (len(my_ret_dict)!=0):
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
        print("write in route table success!")
  
    print("Time:",time.ctime())

#logging write
def save_list():
    file_name = 'messagexApp.txt'
    f = open(file_name, "w+") 
    for item in set_list:
        f.write(item)
    f.close()


#Allocate the xapp Port
def regist_port(xapp_port):
    global portList
    if portList[xapp_port] == 0:
        portList[xapp_port]=1
    else:
        for i in range(8000,65535):
            if portList[i]==0:
                xapp_port=i
                portList[xapp_port]=1
                break

    return xapp_port


def write_routing_table(xapp_p, xapp_ip):
    print("Write the xapp information into the routing table!!!]\n")
    f = open("test_route_thrd.rt",'r+')
    line = f.readlines()
    line[len(line)-1]="\n"
    f.close()
    f =open("test_route_thrd.rt",'w+')
    f.writelines(line)
    f.close()
    f =open("test_route_thrd.rt",'a+')
    table = ["rte|301"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|411"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|414"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|511"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|514"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|611"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|614"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|700"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|710"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|720"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|740"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|841"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|844"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|871"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|874"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|901"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|911"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            "rte|1000"+str(xapp_p)+"|"+str(xapp_ip)+":"+str(xapp_p)+"\n",
            
            "newrt|end\n"]
    f.writelines(table)
    f.seek(0)
    f.close()

    print("Done!!\n")
    

#write routing table into database
def write_in_db(self,sbuf,xapp_p,xapp_ip):
    global Temporary_storage_RoutingTable
    print("Write into the database!!!\n")
    #store routing table in redis
    data = {int("301"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':301, 'port':xapp_p},
            int("411"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':411, 'port':xapp_p},
            int("414"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':414, 'port':xapp_p},
            int("511"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':511, 'port':xapp_p},
            int("514"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':514, 'port':xapp_p},
            int("611"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':611, 'port':xapp_p},
            int("614"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':614, 'port':xapp_p},
            int("700"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':700, 'port':xapp_p},
            int("710"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':710, 'port':xapp_p},
            int("720"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':720, 'port':xapp_p},
            int("740"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':740, 'port':xapp_p},
            int("841"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':841, 'port':xapp_p},
            int("844"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':844, 'port':xapp_p},
            int("871"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':871, 'port':xapp_p},
            int("874"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':874, 'port':xapp_p},
            int("901"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':901, 'port':xapp_p},
            int("910"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':910, 'port':xapp_p},
            int("911"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':911, 'port':xapp_p},
            int("914"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':914, 'port':xapp_p},
            int("1000"+str(xapp_p)):{'IP':str(xapp_ip), 'massage_type':1000, 'port':xapp_p}
    }
    dataSize = sys.getsizeof(data)
    send2routeredis = {"routingtable":1, "paysize":dataSize}
    val = json.dumps(send2routeredis).encode()
    Temporary_storage_RoutingTable.append(data)
    self.rmr_send(val, 69006600)
    #del A, val
    #gc.collect()

def Routing(self, summary, sbuf):
    global portList,MY_NS,MY_GRP_NS,q,broadcast_list
    jpay = json.loads(summary['payload'])
    message= summary['message type']
    print("HIIII~~~~\n")
    pass

#When received the message
def Routing_function(self, summary, sbuf):
    global portList,MY_NS,MY_GRP_NS,q,broadcast_list
    mysdl = _try_func_return(SyncStorage)
    is_active = mysdl.is_active()
    assert is_active is True
    
    jpay = json.loads(summary['payload'])
    message= summary['message type']
     

    if message== 9004600:
        self.logger.info("Received the 900 ID/Port Request!!")
        print("Received the 900 ID/Port Request!!\n")
        print("900 Payload:",jpay,"\n")

        #allocate the RIC ID
        if jpay['Port']!= 0 and jpay['Port']!= "":
            IP = jpay['Ip']
            Port = jpay['Port']
            print("####IP###",IP)
            #pingStr = str(IP)+','+str(Port) 
            #_try_func_return(lambda: mysdl.set('connecter', {str(Port): str(IP).encode()}))
            #_try_func_return(lambda: mysdl.add_member('connecter', str(Port), {IP}))
            self.sdl_set('connecter', str(Port), IP)
            #test=self.sdl_get('connecter', str(Port)) 
            #print("connecter ip",test)
            # Limit the number of new xApps
            use_upperbound = 2
            mysdl = _try_func_return(SyncStorage)
            is_active = mysdl.is_active()
            assert is_active is True
            xAppID = int(str(jpay['Port'])[-4:])
            group_index = str((xAppID -8000)//66)
            warn_msg = 'This port is irregularity.'
            white_text = eval(_try_func_return(lambda: mysdl.get('White', {str('text')}))['text'].decode())
            try:
                white_text = white_text[group_index]
                #white_text = eval(_try_func_return(lambda: mysdl.get('White', {str('text')}))['text'].decode())
                print('group_index:', group_index, ' white_text: ', white_text)
                if(jpay['Port'] not in white_text['listport']):
                    print('warn_msg 1: ', warn_msg)
                    return
            except:
                print('warn_msg 2: ', warn_msg)
                return

            # Overwrite IP for xApp in routing table if any xApp's IP changed.
            xApp_group = list(_try_func_return(lambda: mysdl.get_members('Routing_group', 'set')))
            xApp_group = [xApp_group[i].decode() for i in range(len(xApp_group))]
            print('xApp_group: ', xApp_group)
            if(str(jpay['Port']) in xApp_group):
                IP_Routing_Table = eval(_try_func_return(lambda: mysdl.get('Routing', {str('table')}))['table'].decode())
                print('******check IP******')
                if(IP_Routing_Table[str(301)+str(jpay['Port'])]['IP'] != IP):
                    print('****** IP is different ******')
                    print('IPb: ', IP_Routing_Table[str(301)+str(jpay['Port'])]['IP'], ' IPa: ', IP)
                    overwrite_msgtype = [301, 411, 414, 511, 514, 611, 614, 700, 710, 720, 740, 841, 844, 871, 874, 901, 910, 911, 914, 1000]
                    for msg in overwrite_msgtype:
                        IP_Routing_Table[str(msg)+str(jpay['Port'])]['IP'] = IP
                    byte_store_data = str(IP_Routing_Table).encode()
                    _try_func_return(lambda: mysdl.set('Routing', {str('table'): byte_store_data}))
                    write_routing_table(jpay['Port'],IP) # The text will be more bigger than before forever, if we don't delete the old record.
                    print('******Overwrite Routing Table Successfully.******')
                else:
                    print('****** IP is same ******')
                q.put(int(jpay['Port']))
                print("Sending broadcast to others components!!")
                self.logger.info("Sending broadcast to others components!!")
            	#broadcast to others components
                routing = json.dumps({
                                      "Routing Table":{"Namespace":MY_NS,"Key":"table"},
                                     }).encode()
                print("Broadcast:",broadcast_list)
                for i in range(len(broadcast_list)):
                    self.rmr_send(routing, int("1000"+str(broadcast_list[i])))
                self.logger.info("Send it~~")
                return
                
            """IP_NumberOfxApp = list(_try_func_return(lambda: mysdl.get_members('IP_xApp', str(IP)))) #type of list
            print("IP_NumberOfxApp:", IP_NumberOfxApp, len(IP_NumberOfxApp))
            if(len(IP_NumberOfxApp) > use_upperbound):
                print('This IP ', IP, ' has reached the upper limit.')
                # Do you want to notify xApp that the limit has been exceeded ?
                return"""

            # regist port
            xapp_port_ok = regist_port(jpay['Port'])
            
            # Number of new xApps
            _try_func_return(lambda: mysdl.add_member('IP_xApp', str(IP), {xapp_port_ok}))

            #read lines write in the local routing table
            write_routing_table(xapp_port_ok,IP)
            write_in_db(self,sbuf,xapp_port_ok,IP)
            q.put(xapp_port_ok)
            print("Done and wait for 6901!!\n")

        else:
            print("Wrong Syntax!!!!!!\n")

        print("Time:",time.ctime())

    elif message == 69014600:
        mysdl = _try_func_return(SyncStorage)
        is_active = mysdl.is_active()
        assert is_active is True
        print("Got 6901 Ack!!!!!\n")
        print("6901 Payload:",jpay,"\n")
        #print("6901 Received: {0}".format(summary)+"\n")
                
        # Wrong message			
        if((message % 10) == 4):
            if(jpay['NAK'] is -2):				
                print("There is something wrong. Please check the RMR message type.")
                os._exit(0)
            elif(jpay['NAK'] is -1):
                print("The memory is full. Please wait.")
                os._exit(0)

        MY_NS = jpay['namespace']
        MY_GRP_NS = jpay['group_namespace']
        print("MY_NS:", MY_NS)
        # store data in redis
        olddata = eval(_try_func_return(lambda: mysdl.get(MY_NS, {str('table')}))['table'].decode())
        print("Store it!!\n")
        #print('before ', MY_NS, " redis_get:",str('table'),"->",olddata)
        try:    
            tmpdata = Temporary_storage_RoutingTable.pop(0)
        except:
            print("The Temporary_storage_RoutingTable is empty")
            return
        
        for key in list(tmpdata.keys()):
            #print(key)
            port = tmpdata[key]['port']
            IP = tmpdata[key]['IP']
            mstype = tmpdata[key]['massage_type']
            tmpmstype = str(mstype)
            key_name = tmpmstype + str(port)
            newdata = {key_name:{'IP':IP, 'massage_type':mstype, 'port':port}}
            olddata.update(newdata)
            #print('mid ', MY_NS, " redis_get:",str('table'),"->",olddata)
            byte_store_data = str(olddata).encode()
            _try_func_return(lambda: mysdl.set(MY_NS, {str('table'): byte_store_data}))
            _try_func_return(lambda: mysdl.add_member(MY_GRP_NS, 'set', {port}))

        print("store in Redis")

        # get data in redis
        """
        my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, {str('table')}))
        print('after', MY_NS, " redis_get:",str('table'),"->",my_ret_dict)
        set_group =_try_func_return(lambda: mysdl.get_members(MY_GRP_NS, 'set'))
        print("group:",set_group)
        """
        
        print("Sending broadcast to others components!!")
        self.logger.info("Sending broadcast to others components!!")
        #broadcast to others components
        routing = json.dumps({
            "Routing Table":{"Namespace":MY_NS,"Key":"table"},
        }).encode()
        
        print("Broadcast:",broadcast_list)
        for i in range(len(broadcast_list)):
            self.rmr_send(routing, int("1000"+str(broadcast_list[i])))
        
        self.logger.info("Send it~~")

        print("Time:",time.ctime())

    else:
        print("Got the default message~~\n")
        print("Default Payload:",summary,"\n")

    #del routing
    #gc.collect()
    self.rmr_free(sbuf)


xapp = RMRXapp(default_handler=Routing, rmr_port=4600, post_init=post_init, use_fake_sdl=False)
xapp.register_callback(Routing_function, 9004600)
xapp.register_callback(Routing_function, 69014600)
xapp.run()  # will not thread by default

