from cassandra.cluster import Cluster

cluster = Cluster(['172.31.44.69', '172.31.34.223'])
session = cluster.connect()

session.execute('''
    CREATE KEYSPACE IF NOT EXISTS traffic_lights
    WITH REPLICATION = {'class': 'SimpleStrategy', 'replication_factor': 3}
''')
session.execute('''
    CREATE TABLE IF NOT EXISTS traffic_lights.record (
        RID UUID,
        create_time timestamp,
        vehicle_count smallint,
        pedestrian_count smallint,
        CID int,
        PRIMARY KEY ((RID), CID, create_time)
)''')
