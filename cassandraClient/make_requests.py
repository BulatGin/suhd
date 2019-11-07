import random
import time
import uuid

from cassandra.cluster import Cluster

cluster = Cluster(['172.31.44.69', '172.31.34.223'])
session = cluster.connect()

# for i in range(5000):
#     session.execute(f'''
#         INSERT INTO traffic_lights.record
#         (RID, create_time, vehicle_count, pedestrian_count, CID)
#         VALUES (
#             {str(uuid.uuid4())},
#             toTimestamp(now()),
#             {random.randint(0, 100)},
#             {random.randint(0, 200)},
#             {random.randint(0, 10_000)}
#         )
#     ''')

N = 100_000

start = time.time()
for i in range(N):
    session.execute(f'''
        INSERT INTO traffic_lights.record
        (RID, create_time, vehicle_count, pedestrian_count, CID)
        VALUES (
            {str(uuid.uuid4())},
            toTimestamp(now()),
            {random.randint(0, 100)},
            {random.randint(0, 200)},
            {random.randint(0, 10_000)}
        )
    ''')
end = time.time()
diff = end - start
print(f'Total time: {diff}\nOne transaction time: {diff / N}\nTPS: {N / diff}')
