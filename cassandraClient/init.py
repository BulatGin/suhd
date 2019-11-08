from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable
import psycopg2

try:
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
            green_delay smallint,
            red_delay smallint
            PRIMARY KEY ((RID), CID, create_time)
    )''')
    session.execute('''
        CREATE TABLE IF NOT EXISTS traffic_lights.aggregated_record (
            ARID UUID,
            period_start timestamp,
            period_end timestamp,
            period int,
            total_vehicle_count int,
            total_pedestrian_count int,
            CID int,
            TLID int,
            location tuple<double, double>,
            vehicle_count_changes frozen<list<smallint>>,
            pedestrian_count_changes frozen<list<smallint>>,
            green_delay_changes frozen<list<smallint>>,
            red_delay_changes frozen<list<smallint>>,
            PRIMARY KEY ((ARID), TLID, period)
    )
    ''')
except NoHostAvailable as e:
    print("Cassandra not available")


conn = psycopg2.connect("user='postgres' password='postgres' host='database-1.crzusti7h5eb.us-east-1.rds.amazonaws.com' dbname='traffic_lights'")
cur = conn.cursor()

cur.execute('''
    CREATE TABLE IF NOT EXISTS traffic_light (
        TLID serial primary key,
        location point,
        type boolean,
        green_delay smallint,
        red_delay smallint        
    )
''')
cur.execute('''
    CREATE TABLE IF NOT EXISTS camera (
        CID serial primary key,
        TLID integer references traffic_light(TLID)
    ) 
''')
conn.commit()
cur.close()
conn.close()
