import redis

REDIS_IP = "127.0.0.1"

REDIS_PORT = 6379

REDIS_PASSWORD = ""


def GetRedisConn():
    conn = redis.Redis(host=REDIS_IP, port=REDIS_PORT, password=REDIS_PASSWORD)
    return conn

