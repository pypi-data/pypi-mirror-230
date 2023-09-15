import yaml
import os

def read_yaml():
    conf = dict()
    dir_path = os.path.abspath(os.path.dirname(__file__))
    with open(dir_path+'\config.yaml', encoding='utf-8') as f:
        conf = yaml.load(f.read(), Loader=yaml.FullLoader)
    if 'config-active' in conf.keys() and os.path.exists(dir_path + "\config-"+conf.get('config-active')+".yaml"):
        with open(dir_path + "\config-"+conf.get('config-active')+".yaml", encoding='utf-8') as f:
            conf = yaml.load(f.read(), Loader=yaml.FullLoader)
    return conf

def aop_get_config_data(func):
    def wrapper(*args, **kwargs):
        # 获取key
        configKey = func(*args, **kwargs)
        configValue = read_yaml()
        # 判断字典是否包含子字典
        resultDict = flatten_dict(configValue)
        if configKey != None:
            for key in list(resultDict.keys()):
                if configKey not in key:
                    del resultDict[key]
        return resultDict
    return wrapper

def flatten_dict(data, parent_key='', sep='.'):
    items = []
    for key, value in data.items():
        new_key = f"{parent_key}{sep}{key}" if parent_key else key
        if isinstance(value, dict):
            items.extend(flatten_dict(value, new_key, sep=sep).items())
        else:
            items.append((new_key, value))
    return dict(items)

# 获取配置项信息
@aop_get_config_data
def assign_value(keyMap=None):
    confiigvalue = keyMap
    return confiigvalue

if __name__ == '__main__':
    # print(assign_value())
    # print(assign_value('mongo.password'))
    # print(assign_value('mysql.username.clean'))
    # print(assign_value('mysql.username'))
    # print(assign_value('mysql.password'))
    # print(assign_value('mysql'))
    # print(assign_value())
    # print(assign_value('mongo.password'))
    print(read_yaml())

