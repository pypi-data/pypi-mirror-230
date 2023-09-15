import datetime
import time
import pandas as pd
import locale

class BaseTimeUtils:
    @staticmethod
    def curtime_to_str(format_str = '%Y-%m-%d %H:%M:%S'):
        '''
        将当前时间转换为str对象
        :param format_str: 格式，默认'%Y-%m-%d %H:%M:%S'
        :return: str对象
        '''
        return datetime.datetime.now().strftime(format_str)

    @staticmethod
    def curtime_to_datetime(format_str = '%Y-%m-%d %H:%M:%S'):
        '''
        将当前时间转换为datetime对象
        :param format_str: 格式，默认'%Y-%m-%d %H:%M:%S'
        :return: str对象
        '''
        current_time = datetime.datetime.now()
        formatted_time = current_time.strftime(format_str)
        datetime_obj = datetime.datetime.strptime(formatted_time,format_str)
        return datetime_obj


    @staticmethod
    def add_days(dt, days):
        """
        在给定的datetime对象上添加指定的天数
        """
        return dt + datetime.timedelta(days=days)

    @staticmethod
    def subtract_days(dt, days):
        """
        在给定的datetime对象上减去指定的天数
        """
        return dt - datetime.timedelta(days=days)

    @staticmethod
    def str_to_datetime(time_str, format_str = '%Y-%m-%d %H:%M:%S'):
        """
        将字符串转换为datetime对象
        """
        return datetime.datetime.strptime(time_str, format_str)

    @staticmethod
    def datetime_to_str(dt, format_str = '%Y-%m-%d %H:%M:%S'):
        """
        将datetime对象转换为字符串
        """
        return dt.strftime(format_str)

#------------------------日期格式转换------------------------------

def date_parser(time_str):
    # 设置默认编码为 UTF-8
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    current_time = datetime.datetime.now()
    # 采集时间-x小时
    if '小时前' in time_str:
        hours = int(time_str.split('小时前')[0])
        processed_time = current_time - datetime.timedelta(hours=hours)
    # 采集时间
    elif '今天' in time_str:
        processed_time = current_time
    # 采集时间-1天
    elif '昨天' in time_str:
        processed_time = current_time - datetime.timedelta(days=1)
    # 采集时间-2天
    elif '前天' in time_str:
        processed_time = current_time - datetime.timedelta(days=2)
    # 采集时间-x天
    elif '天前' in time_str:
        days = int(time_str.split('天前')[0])
        processed_time = current_time - datetime.timedelta(days=days)
    # 其它情况（年月日/月日）
    else:
        # 月日 补今年年份
        if '年' not in time_str:
            year = current_time.strftime('%Y')
            time_str = year + '年' + time_str.split(' ')[0]
        # 年月日 不变
        else:
            time_str = time_str.split(' ')[0]
        processed_time = datetime.datetime.strptime(time_str, '%Y年%m月%d日')
    return processed_time.strftime('%Y年%m月%d日')


def yiou_date(date):
    today = datetime.date.today()
    replacements = {
        '昨天': today + datetime.timedelta(days=-1),
        '前天': today + datetime.timedelta(days=-2)
    }

    for keyword, replacement in replacements.items():
        if keyword in date:
            date = date.replace(keyword, replacement.strftime("%Y-%m-%d"))

    return date

def checkertime_parser(time_str):
    '''
    将提供的时间转换为日期对象格式
    :param time_str:
    :return:
    '''
    current_time = datetime.datetime.now()
    # 判断时间字符串的类型
    if '年' in time_str and '月' in time_str and '日' in time_str:
        # 如果时间字符串包含年、月、日，则做相应的处理
        time_format = '%Y年%m月%d日'
    elif '-' in time_str:
        # 如果时间字符串包含冒号，则做相应的处理
        time_format = '%Y-%m-%d'
    else:
        # 其他情况，直接返回当前时间
        return current_time
    # 根据时间字符串的类型，将其转换为日期时间对象
    processed_time = datetime.datetime.strptime(time_str, time_format)
    return processed_time

#-------------检查资讯时间是否在给定的时间范围内-----------------------
def check_new_time(new_time, start_time, end_time):
    # 处理发布时间字符串
    processed_new_time = checkertime_parser(new_time)
    # 将开始时间和结束时间的类型转换为日期类型
    start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d")
    end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d")
    # 判断资讯发布时间是否在时间范围内
    if start_time <= processed_new_time <= end_time:
        return True
    else:
        return False


# -----------不同格式的时间戳转换------------
def date_time(timeNum):
    if timeNum is not None:
        # 1970年之前的时间戳为负数，转换为yyyy-mm-dd
        if str(timeNum)[0] is '-':
            timeStamp = float(timeNum / 1000)
            dt = datetime.datetime(1970, 1, 1) + datetime.timedelta(seconds=timeStamp)
            date = dt.strftime('%Y-%m-%d')
            return date
        else:
            date = conversion_date(timeNum)
            return date
    else:
        timeNum = ''
        return timeNum


def conversion_date(tm):
    # 10位时间戳转换为yyyy-mm-dd
    if len(str(tm)) == 10:
        timeStamp = float(tm)
    # 其他位数时间戳转换为yyyy-mm-dd
    else:
        # 12位时间戳转换为yyyy-mm-dd
        if len(str(tm)) == 12:
            tm = tm + 3600000
        timeStamp = float(tm / 1000)
    timeArray = time.localtime(timeStamp)
    da = time.strftime("%Y-%m-%d", timeArray)
    return da




if __name__ == '__main__':
    #不同格式的时间戳转换
    timestamp = 1626157075  # 12位时间戳
    converted_date = conversion_date(timestamp)
    print(converted_date)  # 输出：2021-07-13

    #当前时间转换为datetime对象
    today = BaseTimeUtils.curtime_to_datetime()
    print(today)
    # 在给定的datetime对象上添加或减去指定天数
    new_dt = BaseTimeUtils.add_days(today, 5)
    print(new_dt)
    new_dt1 = BaseTimeUtils.subtract_days(today, 3)
    print(new_dt1)

    # 字符串转换为datetime对象
    time_str = "2023-07-04 10:30:22"  # 示例时间字符串
    dt = BaseTimeUtils.str_to_datetime(time_str)
    print(dt)
    print(type(dt))
    # datetime对象转换为字符串
    time_str = BaseTimeUtils.datetime_to_str(dt)
    print(time_str)


    ## 日期格式转换
    processed_date = date_parser('3小时前')
    print(processed_date)  # 输出当前时间减去3小时后的日期

    processed_date = date_parser('昨天')
    print(processed_date)  # 输出昨天的日期

    processed_date = date_parser('2天前')
    print(processed_date)  # 输出当前时间减去2天后的日期

    processed_date = date_parser('今天 %H:%M:%S')
    print(processed_date)  # 输出当天的日期


    ###检查资讯时间是否在给定的时间范围内
    # 调用check_new_time方法进行时间检查
    # new_time = "2023-07-17"  # 待检查的时间
    new_time = "2023年07月17日"
    start_time = "2023-07-01"  # 时间范围的开始时间
    end_time = "2023-07-10"  # 时间范围的结束时间

    result = check_new_time(new_time, start_time, end_time)
    print(result)



