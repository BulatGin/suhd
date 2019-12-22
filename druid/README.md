# Установка Druid

## Prerequisites
0. *Предполгается, что все делается на ubuntu 16.04 LTS*
1. Необходимы три ноды размера **m5.2xlarge**
2. На каждую ноду должна быть устанвлена java
   ```
   sudo apt update
   sudo apt install default-jdk
   ```


## Установка
Выполняется на каждой ноде
```
# Скачиваем архив
curl -O http://apache-mirror.rbc.ru/pub/apache/incubator/druid/0.16.1-incubating/apache-druid-0.16.1-incubating-bin.tar.gz
# Распаковывает его
tar -xzf apache-druid-0.16.1-incubating-bin.tar.gz
# Переходим в рабочую директорию
cd apache-druid-0.16.1-incubating-bin.tar.gz
```

## Настройка Metadata storage
Внешняя реляционная бд в которой хранятся метаданные

На примере Postgresql

1. Создаем бд в RDS на AWS
2. Подключаемся к ней по psql:  `psql -h <endpoint> -U postgres` и создаем базу и юзера для druid
```
create database druid;
create user druid with encrypted password 'druid';
grant all privileges on database druid to druid;
ALTER DATABASE druid OWNER TO druid;
```
3. Закомментируем строки с derby
4. Меняем настройки в `./conf/druid/cluster/_common/common.runtime.properties` **на всех нодах**
```
# эту строчку не копировать, а добавить "postgresql-metadata-storage" в существующий список
druid.extensions.loadList=["postgresql-metadata-storage"]

druid.metadata.storage.type=postgresql
druid.metadata.storage.connector.connectURI=jdbc:postgresql://<endpoint>/druid
druid.metadata.storage.connector.user=druid
druid.metadata.storage.connector.password=diurd
```

## Настройка Deep storage
Используем S3

1. Создаем S3 bucket в AWS, надо указать имя корзины, все остальные настройки прокликиваем "далее"
2. В vocareum жмем "Account details"
3. Копируем предлагаемое содержание файла в файл `~/.aws/credentials`
4. Меняем настроки в `./conf/druid/cluster/_common/common.runtime.properties` **на всех нодах**
```
# Аналогично дописать в список, а не менять строчку полностью
druid.extensions.loadList=["druid-s3-extensions"]

# Эти строки надо закомментировать
#druid.storage.type=local
#druid.storage.storageDirectory=var/druid/segments

druid.storage.type=s3
druid.storage.bucket=<bucket_name>
druid.storage.baseKey=druid/segments
druid.s3.fileSessionCredentials=/home/ubuntu/.aws/credentials

# Эти строки надо закомментировать
#druid.indexer.logs.type=file
#druid.indexer.logs.directory=var/druid/indexing-logs

druid.indexer.logs.type=s3
druid.indexer.logs.s3Bucket=<bucket_name>
druid.indexer.logs.s3Prefix=druid/indexing-logs
```

## Настройка zookeeper
Можно запускать на Мастер-сервере
1. Найти файл с нужной версией(лучше предпоследней): `http://apache-mirror.rbc.ru/pub/apache/zookeeper/` и скопировать url к нему
2. Скачать и установить
```
curl -O http://apache-mirror.rbc.ru/pub/apache/zookeeper/zookeeper-3.5.5/apache-zookeeper-3.5.5.tar.gz
tar -xzf apache-zookeeper-3.5.5
sudo cp -r apache-zookeeper-3.5.5/ /opt/zookeeper
sudo cd /opt/zookeeper
sudo mkdir data
```
3. Создать конфигурационный файл
```
sudo vi conf/zoo.cfg

tickTime = 2000
dataDir = /opt/zookeeper/data
clientPort = 2181
initLimit = 20
syncLimit = 10
```
4. Запустить сервер
```
sudo ./bin/zkServer.sh start conf/zoo.cfg
```
5. (*)Проверить, что работает `bin/zkCli.sh`
6. Меняем настроки в `./conf/druid/cluster/_common/common.runtime.properties` **на всех нодах**
```
# Если подняли на мастер сервере, иначе другой, отдельный ip для zookeeper'а
druid.zk.service.host=<ip master сервера>:2181
```

## Ip адреса
Есть три сервера master, data и query на трех нодах, соотвественно
* на мастере находится сервис coordinator-overlord
* на data - historial, middleManager
* на query - broker, router

Надо на нодах по отдельности редактировать файл `./conf/druid/cluster/<server_name>/<service_name>/runtime.properties`

Где 

    server_name = {master, data, query}
    service_name = {coordinator-overlord, historial, middleManager, broker, router}

И в этих файлах добавить строку `druid.host=<ip adress>`, где ip_adress - адрес текущего сервера

*В итоге 5 измененных файлов и 3 ip адреса*

## Запуск (Ура!)
1. На сервере master
```
./bin/start-cluster-master-no-zk-server
```

2. На сервере data
```
./bin/start-cluster-data-server
```

3. На сервере query
```
./bin/start-cluster-query-server
```

4. Открыть web-интерфейс по адресу `<query server ip>:8888`

5. Радоваться (если все вышло)