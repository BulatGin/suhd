#!/bin/bash

printf "Package: erlang*
Pin: version 1:22.1.3-1
Pin-Priority: 1000

Package: esl-erlang
Pin: version 1:21.3.8.8
Pin-Priority: 1000
" | sudo tee /etc/apt/preferences.d/erlang

curl -fsSL https://github.com/rabbitmq/signing-keys/releases/download/2.0/rabbitmq-release-signing-key.asc | sudo apt-key add -

sudo apt-key adv --keyserver "hkps.pool.sks-keyservers.net" --recv-keys "0x6B73A36E6026DFCA"

sudo apt-get install apt-transport-https

if ! ([ -f /etc/apt/sources.list.d/bintray.erlang.list ] && grep -Fq "deb https://dl.bintray.com/rabbitmq/debian" /etc/apt/sources.list.d/bintray.erlang.list); then
    echo "deb https://dl.bintray.com/rabbitmq-erlang/debian xenial erlang" | sudo tee /etc/apt/sources.list.d/bintray.erlang.list
    echo "deb https://dl.bintray.com/rabbitmq/debian bionic main" | sudo tee -a /etc/apt/sources.list.d/bintray.erlang.list
fi

sudo apt-get update

sudo apt-get install -y erlang-base \
                        erlang-asn1 erlang-crypto erlang-eldap erlang-ftp erlang-inets \
                        erlang-mnesia erlang-os-mon erlang-parsetools erlang-public-key \
                        erlang-runtime-tools erlang-snmp erlang-ssl \
                        erlang-syntax-tools erlang-tftp erlang-tools erlang-xmerl


if ! (grep -Fq "rabbitmqcluster" /etc/hosts); then
	printf "
172.31.44.69 rabbitmqnode1.rabbitmqcluster rabbitmqnode1
172.31.34.223 rabbitmqnode2.rabbitmqcluster rabbitmqnode2
172.31.41.241 rabbitmqnode3.rabbitmqcluster rabbitmqnode3
" | sudo tee -a /etc/hosts
fi

sudo apt-get install rabbitmq-server -y --fix-missing

sudo systemctl start rabbitmq-server
sudo systemctl enable rabbitmq-server

sudo rabbitmq-plugins enable rabbitmq_management

sudo rabbitmqctl add_user test test
sudo rabbitmqctl set_user_tags test administrator
sudo rabbitmqctl set_permissions -p / test ".*" ".*" ".*"
