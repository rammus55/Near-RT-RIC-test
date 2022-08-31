# file /top_data.sh
#!/bin/bash
echo "  PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND">/top.txt
for i in {1..1};do
    top -b -n 5000 -d 1 | grep python>>top.txt
    sleep 5
done