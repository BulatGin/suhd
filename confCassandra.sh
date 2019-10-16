me=$0
source ./setNodesIps.sh -l
printf "cluster_name: 'Test Cluster'\n
num_tokens: 256\n
seed_provider:
\t- class_name: org.apache.cassandra.locator.SimpleSeedProvider\n
\t\t- seeds: $NODE1, $NODE2, $NODE3\n
listen_address: $me\n
rpc_address: $me\n
endpoint_snitch: GossipingPropertyFileSnitch" > /etc/cassandra/cassandra.yaml

printf "dc=ru\nrack=rack0" > /etc/cassandra/cassandra-rackdc.properties

sudo rm /etc/cassandra/cassandra-topology.properties

sudo service cassandra start
