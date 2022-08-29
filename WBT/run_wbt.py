#!/usr/bin/env python
# coding: utf-8

# In[ ]:


#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import socket
import sys
import json
#import matlab.engine
import numpy as np
import time

#eng = matlab.engine.start_matlab()

HOST = '10.0.2.15'
PORT = 3900

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind((HOST, PORT))
s.listen(5)

#action = {"MCS_DL": 17, "MCS_UL": 17, "max_DL_HARQ": 1, "max_UL_HARQ": 1, "Repetition": 1.0, "Grantfree_Ind": 0}
action = {"Repetition1": 1.0, "Repetition2": 1.0, "Repetition3": 1.0, "Repetition4": 1.0, "Repetition5": 1.0, 
          "MCS1": 28, "MCS2": 28, "MCS3": 28, "MCS4": 28, "MCS5": 28, 
          "HARQ1": 4, "HARQ2": 4, "HARQ3": 4, "HARQ4": 4, "HARQ5": 4}

print('server start at: %s:%s' % (HOST, PORT))
print('wait for connection...')
#s.settimeout(10)
global send_report_time, receive_control_time, report_control_list, index
send_report_time, receive_control_time = None, None
report_control_list = list()
index = 1

while True:
    print("-----39-----")
    try:
        print("-----41-----")        
        conn, addr = s.accept()
        print('connected by ' + str(addr))
        s.setblocking(False)
        time.sleep(60)
    except:
        pass


    send_time = 1
    print("start run")
    while 1:
        #global send_report_time, receive_control_time, report_control_list, index
        if(index%100==0):
                np.savetxt('./report_control.txt', report_control_list)
        print(time.time(), end='\r')
        try:
            #indata = {'MCS_index':17, 'maxHARQ':2, 'Repetition':1.0}
            conn.settimeout(0.1)
            indata = conn.recv(1024)
            #conn.settimeout(5)
            if len(indata) == 0: # connection closed
                conn.close()
                print('client closed connection.')
                break
            print("XXXXXXXXX")
            print('recv: ' + indata.decode())
            try:
                receive_control_time = time.time()
                report_control_list.append(send_report_time - receive_control_time)
                index += 1
                action = eval(indata.decode())
                print(action)
                #BLER, SINR, Latency, Throughput, DLUL = eng.WBTV2(action, nargout=5)
                #BLER, SINR, Latency = np.array(BLER), np.array(SINR), np.array(Latency)
                reportt = 'Hello!'
                """
                reportt = '{\"BLER\":{'
                var = 0
                while var<len(BLER[0]):
                    reportt = reportt + '\"UE' + str(var+1) + '\":' + str(round(BLER[0][var],6)) + ','
                    var+=1

                reportt = reportt + '},\"SNR\":{'
                var1 = 0
                while var1<len(SINR[0]):
                    reportt = reportt + '\"UE' + str(var1+1) + '\":' + str(round(SINR[0][var1],3)) + ','
                    var1+=1

                reportt = reportt + '},\"Latency\":{'
                var2 = 0
                while var2<len(Latency[0]):
                    reportt = reportt + '\"UE' + str(var2+1) + '\":' + str(round(Latency[0][var2],3)) + ','
                    var2+=1

                reportt = reportt + '}'
                reportt = reportt + ',\"Throughput\":' + str(Throughput)
#                reportt = reportt + '}'

                if DLUL == 1:
                    reportt = reportt + ',\"DL or UL\":\"DL\"}'
                else:
                    reportt = reportt + ',\"DL or UL\":\"UL\"}'
                """
                print(reportt)
                data = json.dumps(reportt)
                try:
                    conn.sendall(bytes(data,encoding="utf-8"))
                    send_report_time = time.time()
                    print("Send report: ", time.time())
                except Exception as e:
                    print(e)
                    print("******** send error ********")
                    break
            except:
                continue

        except IOError:
            #print ("action no change")
            #print(action)
            
            reportt = send_time
            send_time= send_time + 1 
            """
            BLER, SINR, Latency, Throughput, DLUL = eng.WBTV2(action, nargout=5)
            BLER, SINR, Latency = np.array(BLER), np.array(SINR), np.array(Latency)
            reportt = '{\"BLER\":{'
            var = 0
            while var<len(BLER[0]):
                reportt = reportt + '\"UE' + str(var+1) + '\":' + str(round(BLER[0][var],6)) + ','
                var+=1

            reportt = reportt + '},\"SNR\":{'
            var1 = 0
            while var1<len(SINR[0]):
                reportt = reportt + '\"UE' + str(var1+1) + '\":' + str(round(SINR[0][var1],3)) + ','
                var1+=1

            reportt = reportt + '},\"Latency\":{'
            var2 = 0
            while var2<len(Latency[0]):
                reportt = reportt + '\"UE' + str(var2+1) + '\":' + str(round(Latency[0][var2],3)) + ','
                var2+=1

            reportt = reportt + '}'
            reportt = reportt + ',\"Throughput\":' + str(Throughput)
            if DLUL == 1:
                reportt = reportt + ',\"DL or UL\":\"DL\"}'
            else:
                reportt = reportt + ',\"DL or UL\":\"UL\"}'
            """
            #print(reportt)
            data = json.dumps(reportt)
            #print("garbage size=",sys.getsizeof(data)) 
            print("send_time = ", send_time)
            try:
                conn.sendall(data.encode())
                #conn.sendall(bytes(data,encoding="utf-8"))
                send_report_time = time.time()
                print("****** send ******")
            except Exception as e:
                print(e)
                print("******** send error ********")
                break
    #time.sleep(1)
        
#eng.quit()
        

