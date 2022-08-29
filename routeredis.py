"""
Routing Redis Manager (DB)
"""

import os,sys,logging,time,json
from ricxappframe.xapp_frame import RMRXapp, rmr
from datetime import datetime
from ricsdl.syncstorage import SyncStorage
from ricsdl.exceptions import RejectedByBackend, NotConnected, BackendError
import redis

os.environ['DBAAS_SERVICE_PORT'] = '6379'
os.environ['DBAAS_SERVICE_HOST'] = '10.0.2.15'#'10.244.0.18' #'140.123.102.112'
os.environ['RMR_SEED_RT'] = 'test_route_thrd.rt'

# Constants used in the examples below.
MY_NS = 'xapp'
MY_GRP_NS = 'my_group_ns'
MY_LOCK_NS = 'my_group_ns'


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
    # connect the redis
    r = redis.Redis(host=os.environ['DBAAS_SERVICE_HOST'], port=os.environ['DBAAS_SERVICE_PORT'], decode_responses=True)
    # set the max memory size
    r.config_set('maxmemory', '1000MB')
    print('Maxmemory for the redis : ', r.config_get('maxmemory'), end='\n')
    #r.config_set('appendonly', 'no')
    print('AOE for the redis : ', r.config_get('appendonly'), end='\n\n')
    print("set OK")
    
    # show the memory information
    dic_memory = r.info('memory')
    list_dic = list(dic_memory)
    print('info memory:')
    for keys in list_dic:
    	print(keys,' : ', dic_memory[keys])    
    print()
    # get data in redis
    _try_func_return(lambda: mysdl.set(MY_NS, {'try': str('this is try').encode()}))			
    my_ret_dict = _try_func_return(lambda: mysdl.get(MY_NS, {'try'}))
    print("store in Redis!!")
    print(MY_NS, " redis_get:",'try',"->",my_ret_dict)

def RoutingTable(self, summary, sbuf):
    MY_NS = 'Routing'
    MY_GRP_NS = 'Routing_group'
    print("It's", MY_NS)
    now = datetime.now()
    current_time = now.strftime("%H:%M:%S")
    
    """callback for 6900"""
    self.logger.info("pong registered 6900 handler called!")
    
    # see comment in ping about this; bytes does not work with the ric mdc logger currently
    print("pong 6900 handler received: {0}".format(summary))
    jpay = json.loads(summary['payload'])
     
    #jpay = eval(jpay)
    print("Payload:",jpay, type(jpay))
    # check memory capicity
    cm = check_memory()

    if(not cm):
        # the memory is full
        print("The memory is full. Please wait.")
        self.rmr_rts(sbuf, new_payload=json.dumps({"NAK": -1, "why": "memory is full","Times":current_time}).encode(), new_mtype=69044600)
        return
    
    # E2Node ID store in redis' set
    """try:
        _try_func_return(lambda: mysdl.add_member(MY_GRP_NS, 'E2 Node ID', {jpay["E2 Node ID"]}))
    except:
        # the message type is wrong
        print("There is something wrong. Please check the RMR message type.")
        self.rmr_rts(sbuf, new_payload=json.dumps({"NAK": -2, "why": "Wrong RMR message type", "Times":current_time}).encode(), new_mtype=6804)
        return"""

    #Use RMR to send ACK and data to the sender
    self.rmr_rts(sbuf, new_payload=json.dumps({"ACK": '1',"Times":current_time, "namespace":MY_NS, "group_namespace":MY_GRP_NS}).encode(), new_mtype=69014600)
    print("send to routing manager")
    self.rmr_free(sbuf)
    print('end\n')


def defh(self, summary, sbuf):
    """default callback"""
    self.logger.info("pong default handler called!")
    print("pong default handler received: {0}".format(summary))
    self.rmr_free(sbuf)

# Creates SDL instance. The call creates connection to the SDL database backend.
mysdl = _try_func_return(SyncStorage)
is_active = mysdl.is_active()
assert is_active is True

 
xapp = RMRXapp(rmr_port=6600, default_handler=defh, post_init=post_init, use_fake_sdl=False)
print('post_init is ', post_init)

xapp.register_callback(RoutingTable, 69006600)


xapp.run()  # will not thread by default
