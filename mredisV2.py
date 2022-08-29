# Redis Manager(Pong.py)

import json
from ricxappframe.xapp_frame import RMRXapp, rmr
from datetime import datetime
from ricsdl.syncstorage import SyncStorage
from ricsdl.exceptions import RejectedByBackend, NotConnected, BackendError
import os,time
import redis

os.environ['DBAAS_SERVICE_PORT'] = '6379'
os.environ['DBAAS_SERVICE_HOST'] = '10.0.2.15'#'10.244.0.18' #'140.123.102.112'
os.environ['RMR_SEED_RT'] = 'test_route_thrd.rt'

def check_memory():
    # connect the redis
    r = redis.Redis(host=os.environ['DBAAS_SERVICE_HOST'], port=os.environ['DBAAS_SERVICE_PORT'], decode_responses=True)
    # show the memory information
    dic_memory = r.info('memory')
    print('usememory for the redis : ', dic_memory['used_memory'])
    print('The bound for the redis : ', int(dic_memory['maxmemory'])*0.9)
    print('Maxmemory for the redis : ', dic_memory['maxmemory'])
    print('fragratio for the redis : ', dic_memory['mem_fragmentation_ratio'])
    if (int(dic_memory['used_memory']) >= int(dic_memory['maxmemory'])*0.9):
        return 0
    else:
        return 1

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

def post_init(_self):
    """post init"""
    print("pong xapp could do some useful stuff here!")
    # connect the redis
    r = redis.Redis(host=os.environ['DBAAS_SERVICE_HOST'], port=os.environ['DBAAS_SERVICE_PORT'], decode_responses=True)
    # set the max memory size
    r.config_set('maxmemory', '1000MB')
    print('Maxmemory for the redis : ', r.config_get('maxmemory'), end='\n\n')
    #r.config_set('appendonly', 'yes')
    print("set OK")
    print("***********************************")
    print("Redis Manager born up!!!\n")
    print("Redis Manager start to work~~YA\n")
    print("***********************************\n")
    # show the memory information
    """dic_memory = r.info('memory')
    list_dic = list(dic_memory)
    print('info memory:')
    for keys in list_dic:
    	print(keys,' : ', dic_memory[keys])    
    print()"""


# E2 setup Procedure    
def E2setup(self, summary, sbuf):
    MY_NS = 'E2setup'
    MY_GRP_NS = 'E2setup_group'
    print("It's", MY_NS)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    """callback for 6200"""
    self.logger.info("pong registered 6200 handler called!")
    
    # see comment in ping about this; bytes does not work with the ric mdc logger currently
    print("pong 6200 handler received: {0}".format(summary))
    jpay = json.loads(summary['payload'])
     
    print("Payload:",jpay, type(jpay))
    # check memory capicity
    cm = check_memory()
    if(not cm):
        # the memory is full
        print("The memory is full. Please wait.")
        #self.rmr_rts(sbuf, new_payload=json.dumps({"NAK": -1, "why": "memory is full","Times":current_time}).encode(), new_mtype=62044200)
        new_payload=json.dumps({"NAK": -1, "why": "memory is full","Times":current_time}).encode()
        self.rmr_send(new_payload,62044200)
        return

    try:
        _try_func_return(lambda: mysdl.add_member(MY_GRP_NS, 'E2 Node ID', {jpay["E2 Node ID"].replace(' ','')}))
        #_try_func_return(lambda: mysdl.set(str(jpay["E2 Node ID"].encode()), {'SocketFD': str(jpay["SocketFD"].encode())}))
    except:
        # the message type is wrong
        print("There is something wrong. Please check the RMR message type.")
        #self.rmr_rts(sbuf, new_payload=json.dumps({"NAK": -2, "why": "Wrong RMR message type", "Times":current_time}).encode(), new_mtype=62044200)
        new_payload=json.dumps({"NAK": -2, "why": "Wrong RMR message type", "Times":current_time}).encode()
        self.rmr_send(new_payload,62044200)
        return
    
    # use RMR to send ACK and data to the sender
    store_columns = ['E2 Node ID', 'RAN Function Definition', 'RAN Function ID ', 'RAN Function Revision', 'SocketFD']
    #self.rmr_rts(sbuf, new_payload=json.dumps({"ACK": jpay["E2 Node ID"],"Times":current_time, "namespace":MY_NS, "columns":store_columns}).encode(), new_mtype=62014200)
    new_payload=json.dumps({"ACK": jpay["E2 Node ID"].replace(' ',''),"Times":current_time, "namespace":MY_NS, "columns":store_columns}).encode()
    self.rmr_send(new_payload,62014200)
    print("send to E2 Manager")
    time.sleep(4)
    
    if True:
    	self.rmr_free(sbuf)
    	set_group =_try_func_return(lambda: mysdl.get_members(MY_GRP_NS, 'E2 Node ID'))
    	print("group:",set_group)
    print('end\n')

# Subscription Procedure
def subscription(self, summary, sbuf):
    MY_NS = 'subscription'
    MY_GRP_NS = 'subscription_group'
    print("It's", MY_NS)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    """callback for 6400"""
    self.logger.info("pong registered 6400 handler called!")
    
    # see comment in ping about this; bytes does not work with the ric mdc logger currently
    print("pong 6400 handler received: {0}".format(summary))
    jpay = json.loads(summary['payload'])
    print("Payload:",jpay, type(jpay))

    # check memory capicity
    cm = check_memory()
    if(not cm):
        # the memory is full
        print("The memory is full. Please wait.")
        #self.rmr_rts(sbuf, new_payload=json.dumps({"NAK": -1, "why": "memory is full","Times":current_time}).encode(), new_mtype=64044400)
        new_payload=json.dumps({"NAK": -1, "why": "memory is full","Times":current_time}).encode()
        self.rmr_send(new_payload,64044400)
        return

    # subscription ID store in redis' set
    try:    
        _try_func_return(lambda: mysdl.add_member(MY_GRP_NS, 'RIC Requestor ID', {jpay['RIC Request ID']['RIC Requestor ID']}))
    except:
        # the message type is wrong
        print("There is something wrong. Please check the RMR message type.")
        #self.rmr_rts(sbuf, new_payload=json.dumps({"NAK": -2, "why": "Wrong RMR message type", "Times":current_time}).encode(), new_mtype=64044400)
        new_payload=json.dumps({"NAK": -2, "why": "Wrong RMR message type", "Times":current_time}).encode()
        self.rmr_send(new_payload,64044400)
        return
    store_columns = ['Number', 'RIC Request ID', 'RAN Function ID', 'RAN Function Revision', 'RIC Action ID ', 'RIC Subscription Details']
    # use RMR to send ACK and data to the sender
    #self.rmr_rts(sbuf, new_payload=json.dumps({"ACK": jpay['RIC Request ID'],"Times":current_time, "namespace":MY_NS, "columns":store_columns}).encode(), new_mtype=64014400)
    new_payload=json.dumps({"ACK": jpay['RIC Request ID'],"Times":current_time, "namespace":MY_NS, "columns":store_columns}).encode()
    self.rmr_send(new_payload,64014400)
    time.sleep(4)
    
    if jpay['RIC Request ID']['RIC Requestor ID'] >= 5:
    	print()
    	self.rmr_free(sbuf)
    	set_group =_try_func_return(lambda: mysdl.get_members(MY_GRP_NS, 'RIC Requestor ID'))
    	print("group:",set_group)
    print('end\n')

# Report Procedure
def report(self, summary, sbuf):
    MY_NS = 'report'
    MY_GRP_NS = 'report_group'
    print("It's", MY_NS)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    """callback for 6700"""
    self.logger.info("pong registered 6700 handler called!")
    
    # see comment in ping about this; bytes does not work with the ric mdc logger currently
    print("pong 6700 handler received: {0}".format(summary))
    jpay = json.loads(summary['payload'])
    print("Payload:",jpay, type(jpay))

    # check memory capicity
    cm = check_memory()
    if(not cm):
        # the memory is full
        print("The memory is full. Please wait.")
        #self.rmr_rts(sbuf, new_payload=json.dumps({"NAK": -1, "why": "memory is full","Times":current_time}).encode(), new_mtype=67044200)
        new_payload=json.dumps({"NAK": -1, "why": "memory is full","Times":current_time}).encode()
        self.rmr_send(new_payload,67044200)
        return

    # subscription ID store in redis' set
    try:    
        _try_func_return(lambda: mysdl.add_member(MY_GRP_NS, 'RIC Requestor ID', {jpay["RIC Requestor ID"]}))
    except:
        # the message type is wrong
        print("There is something wrong. Please check the RMR message type.")
        #self.rmr_rts(sbuf, new_payload=json.dumps({"NAK": -2, "why": "Wrong RMR message type", "Times":current_time}).encode(), new_mtype=67044200)
        new_payload=json.dumps({"NAK": -2, "why": "Wrong RMR message type", "Times":current_time}).encode()
        self.rmr_send(new_payload,67044200)
        return
    store_columns = ['RIC Request ID', 'RIC Instance ID', 'RAN Function ID', 'RIC Action ID', 'RIC Indication Type', 'RIC Indication Header', 'RIC Indication Message']
    # use RMR to send ACK and data to the sender
    #self.rmr_rts(sbuf, new_payload=json.dumps({"ACK": jpay["RIC Requestor ID"],"Times":current_time, "namespace":MY_NS, "columns":store_columns}).encode(), new_mtype=67014200)
    new_payload=json.dumps({"ACK": jpay["RIC Requestor ID"],"Times":current_time, "namespace":MY_NS, "columns":store_columns}).encode()
    self.rmr_send(new_payload,67014200)
    #time.sleep(4)
    
    if jpay["RIC Requestor ID"] >= 5:
    	print()
    	self.rmr_free(sbuf)
    	set_group =_try_func_return(lambda: mysdl.get_members(MY_GRP_NS, 'RIC Requestor ID'))
    	print("group:",set_group)
    print('end\n')

# Insert Report Procedure
def insert(self, summary, sbuf):
    MY_NS = 'insert'
    MY_GRP_NS = 'insert_group'
    print("It's", MY_NS)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    """callback for 6710"""
    self.logger.info("pong registered 6710 handler called!")
    
    # see comment in ping about this; bytes does not work with the ric mdc logger currently
    print("pong 6700 handler received: {0}".format(summary))
    jpay = json.loads(summary['payload'])
    print("Payload:",jpay, type(jpay))

    # check memory capicity
    cm = check_memory()
    if(not cm):
        # the memory is full
        print("The memory is full. Please wait.")
        #self.rmr_rts(sbuf, new_payload=json.dumps({"NAK": -1, "why": "memory is full","Times":current_time}).encode(), new_mtype=6704)
        new_payload=json.dumps({"NAK": -1, "why": "memory is full","Times":current_time}).encode()
        self.rmr_send(new_payload,6704)
        return

    # subscription ID store in redis' set
    try:    
        _try_func_return(lambda: mysdl.add_member(MY_GRP_NS, 'RIC Requestor ID', {jpay["RIC Requestor ID"]}))
    except:
        # the message type is wrong
        print("There is something wrong. Please check the RMR message type.")
        #self.rmr_rts(sbuf, new_payload=json.dumps({"NAK": -2, "why": "Wrong RMR message type", "Times":current_time}).encode(), new_mtype=6714)
        new_payload=json.dumps({"NAK": -2, "why": "Wrong RMR message type", "Times":current_time}).encode()
        self.rmr_send(new_payload,6714)
        return
    store_columns = ['RIC Request ID', 'RIC Instance ID', 'RAN Function ID', 'RIC Action ID', 'RIC Indication Type', 'RIC Indication Header', 'RIC Indication Message', 'Call process ID']
    # use RMR to send ACK and data to the sender
    #self.rmr_rts(sbuf, new_payload=json.dumps({"ACK": jpay["RIC Requestor ID"],"Times":current_time, "namespace":MY_NS, "columns":store_columns}).encode(), new_mtype=6711)
    new_payload=json.dumps({"ACK": jpay["RIC Requestor ID"],"Times":current_time, "namespace":MY_NS, "columns":store_columns}).encode()
    self.rmr_send(new_payload,6711)
    time.sleep(4)
    
    if jpay["RIC Requestor ID"] >= 5:
    	print()
    	self.rmr_free(sbuf)
    	set_group =_try_func_return(lambda: mysdl.get_members(MY_GRP_NS, 'RIC Requestor ID'))
    	print("group:",set_group)
    print('end\n')

# When FD disconnection, mredis send E2setup table's namespace to E2 manager
def FD_E2(self, summary, sbuf):
    MY_NS = 'E2setup'
    MY_GRP_NS = 'E2setup_group'
    print("It's", MY_NS)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    """callback for 6400"""
    self.logger.info("pong registered 6400 handler called!")
    
    # see comment in ping about this; bytes does not work with the ric mdc logger currently
    print("pong 6400 handler received: {0}".format(summary))
    jpay = json.loads(summary['payload'])
    print("Payload:",jpay, type(jpay))
    #self.rmr_rts(sbuf, new_payload=json.dumps({"ACK": jpay["E2 Node ID"],"Times":current_time, "namespace":MY_NS}).encode(), new_mtype=8214200)  # need to update mtype
    new_payload=json.dumps({"ACK": jpay["E2 Node ID"].replace(' ',''),"Times":current_time, "namespace":MY_NS}).encode()
    self.rmr_send(new_payload,8214200)
    time.sleep(2)
    
# When FD disconnection, mredis send subscription table's namespace to subscription manager
def FD_subscription(self, summary, sbuf):
    MY_NS = 'subscription'
    MY_GRP_NS = 'subscription_group'
    print("It's", MY_NS)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    """callback for 6400"""
    self.logger.info("pong registered 6400 handler called!")
    
    # see comment in ping about this; bytes does not work with the ric mdc logger currently
    print("pong 6400 handler received: {0}".format(summary))
    jpay = json.loads(summary['payload'])
    print("Payload:",jpay, type(jpay))
    #self.rmr_rts(sbuf, new_payload=json.dumps({"ACK": jpay["RIC Requestor ID"],"Times":current_time, "namespace":MY_NS}).encode(), new_mtype=8414400)  # need to update mtype
    new_payload=json.dumps({"ACK": jpay["RIC Requestor ID"],"Times":current_time, "namespace":MY_NS}).encode()
    self.rmr_send(new_payload,8414400)
    time.sleep(2)

def defh(self, summary, sbuf):
    """default callback"""
    self.logger.info("pong default handler called!")
    print("pong default handler received: {0}".format(summary))
    self.rmr_free(sbuf)

# Creates SDL instance. The call creates connection to the SDL database backend.
mysdl = _try_func_return(SyncStorage)
is_active = mysdl.is_active()
assert is_active is True

 
xapp = RMRXapp(rmr_port=6000, default_handler=defh, post_init=post_init, use_fake_sdl=False)
print('post_init is ', post_init)
massage_type_list = [62006000,63006000,64006000,65006000,66006000,67006000,68006000,67106000]
for mstype in massage_type_list:
    if(mstype == 62006000):
        xapp.register_callback(E2setup, mstype)
    elif(mstype == 64006000):
        xapp.register_callback(subscription, mstype)
    elif(mstype == 67006000):
        xapp.register_callback(report, mstype)
    elif(mstype == 67106000):
        xapp.register_callback(insert, mstype)
    elif(mstype == 8406000):
        xapp.register_callback(FD_subscription, mstype)
    elif(mstype == 8206000):
        xapp.register_callback(FD_E2, mstype)
    else:
        continue
xapp.run()  # will not thread by default
