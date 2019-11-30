#!/bin/bash

# to get cookie from master
# sudo cat /var/lib/rabbitmq/.erlang.cookie

printf "$1" | sudo tee /var/lib/rabbitmq/.erlang.cookie

sudo service rabbitmq-server restart

sudo rabbitmqctl stop_app;
sudo rabbitmqctl reset;
sudo rabbitmqctl join_cluster --ram rabbit@ip-172-31-44-69;
sudo rabbitmqctl start_app;
