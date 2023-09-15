from pymongo import MongoClient
from loguru import logger
import datetime
import os
import sys
from pymongo.errors import DuplicateKeyError

dir_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(dir_path)
from config import config

class MongoDBUtil:
    def __init__(self, host: str = None, port: int = None, username: str = None, password: str = None, database: str = None):

        # 从配置文件中获取 MongoDB 连接信息
        self.host = host or config.assign_value('mongo.host')['mongo.host']
        self.port = port or config.assign_value('mongo.port')['mongo.port']
        self.username = username or config.assign_value('mongo.username')['mongo.username']
        self.password = password or str(config.assign_value('mongo.password')['mongo.password'])
        self.db_name = database or config.assign_value('mongo.database')['mongo.database']

        try:
            self.client = MongoClient(self.host, self.port, username=self.username, password=self.password,serverSelectionTimeoutMS=2000)  # 设置连接超时时间为2秒
            #pymongo库的MongoClient类在连接MongoDB时，并不会立即进行身份验证。它只在实际执行数据库操作时才会验证身份
            self.client.server_info()  # 执行一个简单的数据库操作以验证连接和身份验证
            self.db = self.client[self.db_name]
            logger.info('Connected to MongoDB successfully. host: {}, db: {}'.format(self.host, self.db_name))
        except Exception as e:
            logger.error('Failed to connect to MongoDB.')
            raise e


    def insert(self, collection, data):
        '''
        插入数据
        :param collection:集合名称
        :param data: 数据集
        :return:
        '''
        try:
            self.db[collection].insert_one(data)
            logger.debug(f'success executing insert：{collection}')
        except Exception as e:
            logger.error(f"Error executing insert: {e}")

    def query(self, collection, query_filter=None):
        '''
        查询数据
        :param collection:集合名称
        :param query_filter: 查询条件
        :return:
        '''
        try:
            if query_filter is None:
                documents = self.db[collection].find()
            else:
                documents = self.db[collection].find(query_filter)
            logger.debug(f'success executing query：{documents}')
            return list(documents)
        except Exception as e:
            logger.error(f"Error executing query: {e}")

    def update(self, collection, query_filter, new_data):
        '''
        更新数据
        :param collection: 集合名称
        :param query_filter: 更新条件
        :param new_data: 新数据
        :return:
        '''
        try:
            self.db[collection].update_many(query_filter, {"$set": new_data})
            logger.debug(f'Success executing update: {collection}')
        except Exception as e:
            logger.error(f"Error executing update: {e}")

    def disconnect(self):
        '''
        断开连接
        :return:None
        '''
        try:
            self.client.close()
            logger.debug("Disconnected from MongoDB.")
        except Exception as e:
            logger.error(f"Failed to disconnect from MongoDB.{e}")

    def create_set(self, collection_name, project_type):
        '''
        创建集合
        :param collection_name: 集合名称，判断集合是否存在存在
        :param project_type: 判断项目类型
        :return:
        '''
        # 判断集合是否存在
        collection_names = self.db.list_collection_names()
        # 若集合存在
        if collection_name in collection_names:
            new_collection = self.db[collection_name]
        # 若集合不存在 创建集合
        else:
            if project_type == 'Baidu':
                new_collection = self.db[collection_name].create_index([("url", 1)], unique=True)  # 尝试创建唯一索引
            else:
                new_collection = self.db[collection_name]
            logger.debug(datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' >>> [Create]:', new_collection)
        return new_collection


if __name__ == '__main__':

    # 创建MongoDB对象
    mongo = MongoDBUtil()

    # 插入数据
    data = {'name': 'John', 'age': 30, 'city': 'New York'}
    mongo.insert('users', data)

    # 查询数据
    result = mongo.query('users', {'age': {'$gt': 25}})
    print(result)

    # 更新数据
    filter = {'name': 'John'}
    new_data = {'age': 35, 'city': 'Los Angeles'}
    mongo.update('stu', filter, new_data)

    # 断开连接
    mongo.disconnect()