#!/bin/bash
# Run this using 'source'

IP1=54.157.33.173
IP2=18.209.177.120
IP3=54.205.245.95
IP1_LOC=172.31.44.69
IP2_LOC=172.31.34.223
IP3_LOC=172.31.41.241

if [ "$1" = "-p" ]; then
    export NODE1=$IP1
    export NODE2=$IP2
    export NODE3=$IP3
    export NODE1_LOC=$IP1_LOC
    export NODE2_LOC=$IP2_LOC
    export NODE3_LOC=$IP3_LOC
elif [ "$1" = "-l" ]; then
    export NODE1=$IP1_LOC
    export NODE2=$IP2_LOC
    export NODE3=$IP3_LOC
else
    echo "Unknown param"
    return
fi

export NODE0=54.163.120.156

if ! grep -q "# AWS nodes ips aliases" ~/.bashrc; then
    echo "# AWS nodes ips aliases" >> ~/.bashrc
    printf "export NODE0=$NODE0\nexport NODE1=$IP1\nexport NODE2=$IP2\nexport NODE3=$IP3\n" >> ~/.bashrc
fi
