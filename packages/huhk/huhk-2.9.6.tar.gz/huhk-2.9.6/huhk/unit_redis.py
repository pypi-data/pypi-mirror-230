import redis


class Redis:
    def __init__(self, host=None, port=6379, password=None, db=0):
        self.r = None
        self.host = host
        self.port = port
        self.password = password
        self.db = db
        self.connection()

    def connection(self):
        if not self.r:
            self.r = redis.Redis(host=self.host, port=self.port, db=self.db, password=self.password)
        return self.r

    def get(self, key):
        return self.connection().get(key)

    def set(self, key, value, **kwargs):
        return self.connection().set(key, value, **kwargs)

    def delete(self, *names):
        return self.connection().delete(*names)


if __name__ == '__main__':
    r = Redis(host='r-bp1tnpcfs5gtqr7s8kpd.redis.rds.aliyuncs.com', port=6379, password="Geelypk2022", db=1)
    o = r.get("SMS_CODE_INTERVAL_13123920102")
    print(str(o)[-7:-1])
