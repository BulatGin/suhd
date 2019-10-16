echo "-------INSTALL JAVA-------"

sudo apt-get purge -y --auto-remove openjdk*
sudo apt-get install -y openjdk-8-jre-headless

echo "-----JAVA VERSION CHECK------"
java -version

echo "----------INSTALL PYTHON 2----------"

sudo apt-get install -y python-minimal

echo "------PYTHON VERSION CHECK------"
python --version

echo "-----------INSTALL CASSANDRA---------"

if ! ([ -f /etc/apt/sources.list.d/cassandra.sources.list] && grep -Fq "deb http://www.apache.org/dist/cassandra/debian 36x main" /etc/apt/sources.list.d/cassandra.sources.list); then
    echo "deb http://www.apache.org/dist/cassandra/debian 36x main" | sudo tee -a /etc/apt/sources.list.d/cassandra.sources.list
fi

curl https://www.apache.org/dist/cassandra/KEYS | sudo apt-key add -

sudo apt-get update
sudo apt-get purge -y cassandra
sudo apt-get install -y cassandra

echo "------TEST RUN------"
nodetool status
