import pymysql
from dbutils.pooled_db import PooledDB
from loguru import logger
import sys
import os
import pandas as pd
import threading
from typing import Union
dir_path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(dir_path)
from config import config


class MysqlUtil:
    #同时使用多个线程来执行数据库查询操作，可能会导致数据库连接的竞争和性能下降
    #数据库连接池是一组预先创建的数据库连接，可以重复使用来执行数据库操作。使用连接池可以减少数据库连接的创建和关闭开销，并且可以限制并发连接的数量，以避免过多的连接竞争数据库资源。
    def __init__(self, host:str = None, port:int = None, username:str = None, password:str = None, database:str = None, maxconnections:int = None ):
        '''
        # 从配置文件中获取MySQL连接配置信息,并创建连接，若提供参数则按照提供的否则默认
        :param host: host
        :param port: 端口号
        :param username: 用户名
        :param password: 密码
        :param database: 要连接的数据库
        :param maxconnections: 要创建的连接个数
        '''
        self.host = host or config.assign_value('mysql.host')['mysql.host']
        self.port = port or config.assign_value('mysql.port')['mysql.port']
        self.user = username or config.assign_value('mysql.username')['mysql.username']
        self.password = password or str(config.assign_value('mysql.password')['mysql.password'])
        self.database = database or config.assign_value('mysql.database')['mysql.database']
        self.maxconnections = maxconnections or config.assign_value('mysql.maxconnections')['mysql.maxconnections']
        try:
            # 使用PooledDB创建一个连接池
            self.pool = PooledDB(
                pymysql,
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.database,
                port = self.port,
                maxconnections = self.maxconnections
            )
            self.lock = threading.Lock()
            # 测试连接是否成功，如果连接失败会抛出异常
            conn = self.pool.connection()
            conn.close()
            logger.info('Connected to pymysql successfully：{}',
                        'host:' + str(self.host) + ',db:' + str(self.database))
        except Exception as e:
            # 连接失败，抛出异常并记录日志
            logger.error(f"Failed to connect to pymysql ：{e}")
            # 使用sys.exit()函数来结束程序
            sys.exit()


    def get_db_connection(self):
        return self.maxconnections

    def create_table(self, query):
        '''
        创建数据库中不存在的数据表
        :param query:mysql中建表的命令
        :return: None
        '''
        conn = self.pool.connection()
        try:
            cur = conn.cursor()
            cur.execute(query)
            cur.close()
            conn.close()
            logger.debug(f'success executing create：{query}')
        except Exception as e:
            logger.error(f"Error executing create: {e}")



    def execute_insert(self, table: str, data: Union[tuple,list ],columns: tuple = None,threshold:int =1000):
        '''
        向指定的表中插入数据
        :param table: 表名
        :param data: 数据(元组或者是元组组成的列表)
        :param threshold: 多少条数据插入一次(默认1000)
        :return: None
        '''
        conn = self.pool.connection()
        try:
            cur = conn.cursor()
            #executemany()方法要求传入的参数是元组嵌套的列表，列表中每个元组代表一组数据
            if isinstance(data, list):
                # 如果是list形式的数据，批量插入
                placeholders = ', '.join(['%s'] * len(data[0]))
                if columns:
                    column_names = ', '.join(columns)
                    query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                else:
                    query = f"INSERT INTO {table} VALUES ({placeholders})"
                for i in range(0, len(data), threshold):
                    batch_data = data[i:i + threshold]
                    cur.executemany(query, batch_data)
            else:
                # 否则，单条插入
                placeholders = ', '.join(['%s'] * len(data))
                if columns:
                    column_names = ', '.join(columns)
                    query = f"INSERT INTO {table} ({column_names}) VALUES ({placeholders})"
                else:
                    query = f"INSERT INTO {table} VALUES ({placeholders})"
                cur.execute(query, data)
            conn.commit()
            cur.close()
            conn.close()
            logger.debug(f'success executing insert：{query}')
        except Exception as e:
            # 发生异常时回滚
            conn.rollback()
            logger.error(f"Error executing insert: {e}")
            return None


    def execute_update(self, query, data: list = False,threshold: int = 1000):
        '''
        更新数据
        :param query:更新语句
        :param data: 要参照的数据，默认为False
        :param threshold: 超过1000条，则每1000条更新一次
        :return: None
        '''
        conn = self.pool.connection()
        try:
            cur = conn.cursor()
            if data:
                for i in range(0, len(data), threshold):
                    batch_data = data[i:i + threshold]
                    cur.executemany(query, batch_data)
            else:
                cur.execute(query)
            conn.commit()

            cur.close()
            conn.close()
            logger.debug(f'Success executing update: {query}')
        except Exception as e:
            # 发生错误时回滚事务
            conn.rollback()
            logger.error(f"Error executing update: {e}")

    def execute_query(self, query: str,columns:bool = None):
        '''
        查询数据
        :param query:mysql中查询数据的命令
        :param columns:是否生成DataFrame,默认不生成
        :return: 结果集，默认是二维元组，可以生成DataFrame
        '''
        try:
            conn = self.pool.connection()
            cur = conn.cursor()
            cur.execute(query)
            if columns:
                if cur.rowcount == 0:
                    # 查询结果为空，手动创建一个空的 DataFrame
                    result_data = pd.DataFrame(columns=[item[0] for item in cur.description])
                else:
                    result_data = pd.DataFrame(list(cur.fetchall()))
                    des = cur.description
                    result_data.columns = [item[0] for item in des]
            else:
                result_data = cur.fetchall()
            cur.close()
            conn.close()
            logger.debug(f'success executing ：{query}')
            return result_data
        except Exception as e:
            # 记录日志并返回空值
            logger.error(f"Error executing : {e}")
            return None


    def execute_query_count(self, query: str):
        '''
        查询数据量，返回一个整数
        :param query: 查询语句
        :return: int 数据量
        '''
        result_data = self.execute_query(query)
        result_count = result_data[0][0]
        return result_count



if __name__ == '__main__':

    #自己填写mysql连接信息
    mysql_util = MysqlUtil('36.133.195.12',23306,'data_cleaning','Tydsj@0516','data_clean_db',2)
    # 默认从配置文件中读取连接配置信息
    # mysql_util = MysqlUtil()

    #创建表
    # 两两匹配度关系数据入库 match_result_name 表
    match_result_query = f"CREATE TABLE `stu_test`  ( \
  `id` int(11) NOT NULL, \
  `name` varchar(45) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL, \
  `shortname` varchar(45) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL, \
  `age` varchar(45) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL, \
  `class` varchar(45) CHARACTER SET utf8 COLLATE utf8_bin NULL DEFAULT NULL, \
  PRIMARY KEY (`id`) USING BTREE \
) ENGINE = InnoDB CHARACTER SET = utf8 COLLATE = utf8_bin ROW_FORMAT = Dynamic;"
    mysql_util.create_table(match_result_query)

    #插入数据
    #插入数据，指定列名
    columns = ("id", "name", "class")
    data = [(1,'张三','一班'),(2,'李四','二班'),(3,'王五','一班')]
    mysql_util.execute_insert("stu_test", data, columns=columns)
    #  按照表的列名顺序提供值
    data2 = [(4,'张深','小宝',18,'一班'),(5,'王明','明明',18,'二班'),(6,'汪东兴',None,18,'一班')]
    mysql_util.execute_insert('stu_test', data2)

    #更新  用sql更新语句，可以使用data批量更新，也可以直接使用update语句
    # 1.使用data更新
    cleaned_data_all_list = [('张2322',1),('张21',2)]
    # 更新表 需要建立索引，否则花费时间较长
    mysql_util.execute_update('update stu_test set name=%s where id=%s', cleaned_data_all_list)
    # 2.直接规定的语句
    mysql_util.execute_update('update stu_test set age=12')

    # 查询
    sample_id_list_sql = f"select * FROM stu_test"
    #1.结果以二维元组形式展示
    df1 = mysql_util.execute_query(sample_id_list_sql)
    print(df1)
    #2.结果以dataFramae形式展示
    df2 = mysql_util.execute_query(sample_id_list_sql,True)
    print(df2)


    #查询数据量
    sample_id_list_sql = f"select count(*) FROM stu_test"
    result1 = mysql_util.execute_query_count(sample_id_list_sql)
    print(result1)








