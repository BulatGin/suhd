me=$1
source ./setNodesIps.sh -l
sudo service cassandra stop
sudo rm -rf /var/lib/cassandra/data/system/*
printf "cluster_name: 'Test Cluster'
num_tokens: 256
seed_provider:
    - class_name: org.apache.cassandra.locator.SimpleSeedProvider
      parameters:
          - seeds: $NODE1,$NODE2,$NODE3
listen_address: $me
rpc_address: $me
endpoint_snitch: GossipingPropertyFileSnitch\n" | sudo tee -a /etc/cassandra/cassandra.yaml

printf "dc=ru\nrack=rack0\n" | sudo tee -a /etc/cassandra/cassandra-rackdc.properties

sudo rm /etc/cassandra/cassandra-topology.properties

sudo service cassandra start
