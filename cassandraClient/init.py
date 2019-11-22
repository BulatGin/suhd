import random

from cassandra.cluster import Cluster
from cassandra.cluster import NoHostAvailable
import psycopg2
from psycopg2.extras import execute_values

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

def gen_TL_rows():
    lst = []
    for i in range(2500):
        loc = (random.uniform(100.0, 103.0), random.uniform(100.0, 103.0))
        lst.append((str(loc), False, random.randint(5, 121), random.randint(5, 121)))
        lst.append((str(loc), True, random.randint(5, 121), random.randint(5, 121)))
    return lst

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
execute_values(cur, '''INSERT INTO traffic_light (location, type, green_delay, red_delay) VALUES %s''', gen_TL_rows())
execute_values(cur, '''INSERT INTO camera (TLID) VALUES %s''', [(i,) for i in range(1, 5001)] + [(i,) for i in range(1, 5001)])
conn.commit()
cur.close()
conn.close()
