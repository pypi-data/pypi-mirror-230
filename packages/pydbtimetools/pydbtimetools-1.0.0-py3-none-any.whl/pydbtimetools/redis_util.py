from loguru import logger
import redis
import os
import sys

dir_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(dir_path)
from config import config


class RedisUtil:
    def __init__(self, host:str = None, port:int = None, password:str = None, database:str = None):

        # Redis 连接信息
        self.redis_host = host or config.assign_value('redis.host')['redis.host']
        self.redis_port = port or config.assign_value('redis.port')['redis.port']
        self.redis_password = password or str(config.assign_value('redis.password')['redis.password'])
        self.redis_db = database if database is not None else config.assign_value('redis.database')['redis.database'] or 0
        self.redis_pool = None
        self.redis_connection = None

        try:
            # 创建 Redis 连接池
            self.redis_pool = redis.ConnectionPool(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password,
                db=self.redis_db,
                decode_responses = True   # decode_responses=True，写入value中为str类型，否则为字节型
            )

            # 创建 Redis 连接
            self.redis_connection = redis.Redis(connection_pool=self.redis_pool)
            # 尝试执行一个Redis操作，如果连接失败则抛出异常
            self.redis_connection.ping()
            logger.debug("Connected to Redis successfully.")
        except Exception as e:
            logger.error("Failed to connect to Redis.")


    def zpopmin(self, key, count=1):
        try:
            values = self.redis_connection.zpopmin(key, count)
            return values
        except Exception as e:
            logger.error("Failed to execute ZPOPMIN operation in Redis.")

    def get(self, key):
        try:
            value = self.redis_connection.get(key)
            return value
            logger.debug("Key is got from Redis successfully.")
        except Exception as e:
            logger.error("Failed to get value from Redis.")

    def set(self, key, value):
        try:
            self.redis_connection.set(key, value)
            logger.debug("Value is set in Redis successfully.")
        except Exception as e:
            logger.error("Failed to set value in Redis.")

    def rpush(self, key, data):
        try:
            self.redis_connection.rpush(key, data)
            logger.debug("Value is rpush in Redis successfully.")
        except Exception as e:
            logger.error("Failed to rpush value in Redis.")


    def disconnect(self):
        try:
            self.redis_connection.close()
            logger.debug("Disconnected from Redis.")
        except Exception as e:
            logger.error("Failed to disconnect from Redis.")


if __name__ == '__main__':

    # 创建 RedisConnector 对象
    redis_connector = RedisUtil('36.133.195.12', 26379, 'tydsj@0512')
    # redis_connector = RedisUtil('127.0.0.1', 6379, '123456',1)
    #调用 zpopmin 方法来执行 ZPOPMIN 操作,从名为 my_sorted_set 的有序集合中移除并返回分值最低的 3 个成员，并将其打印出来。
    # values = redis_connector.zpopmin('my_sorted_set', 3)
    # print(values)
    # 进行 Redis 操作
    detail_redis = '{"task_id": "63" ,"sample_name": "康耐视视觉检测系统（上海）有限公司" ,"company_name": "康耐视视觉检测系统（上海）有限公司" ,"credit_code": "913101155574992910" ,"detail_url": "https://www.tianyancha.com/company/677393317"} '
    sample_list = 'RULEID:CompanyID-test:Sample:CaptureNumber'

    redis_connector.rpush(sample_list, detail_redis)
    # value = redis_connector.get('RULEID:CompanyID-test:Sample:CaptureNumber')
    # print(value)

    # 断开连接
    redis_connector.disconnect()
