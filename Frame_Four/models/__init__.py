import json

"""
 使用json格式序列化/反序列化字典或者列表
"""


from utils import log


def save(data, path):
    """
    本函数把一个dict或者list写入文件
    data为dict或者list path是保存文件的路径
    """
    # indent是缩进 ensure_ascii=False用于保存中文
    s = json.dumps(data, indent=2, ensure_ascii=False)
    with open(path, 'w+', encoding='utf-8') as f:
        log('save', path, s, data)
        f.write(s)


def load(path):
    """
    本函数从一个文件中载入数据并且转换为dict 或者 list
    path 是保存文件的路径
    """
    with open(path, 'r', encoding='utf-8') as f:
        s = f.read()
        log('load', s)
        return json.loads(s)


# Model是用于存储数据的基类
class Model(object):
    # 得到一个类的路径
    @classmethod
    def db_path(cls):
        classname = cls.__name__
        path = 'db/{}.txt'.format(classname)
        return path

    @classmethod
    def new(cls, form):
        m = cls(form)
        return m

    # 寻找一个其 实例value值与关键字参数value值相等的实例
    @classmethod
    def find_by(cls, **kwargs):
        log('kwargs, ', kwargs)
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        all = cls.all()
        for m in all:
            # getattr(m, k) 等价于 m.__dict__[k]
            if v == m.__dict__[k]:
                return m
        return None

    # 寻找多个其 实例value值与关键字参数value值相等的实例
    @classmethod
    def find_all(cls, **kwargs):
        """
        用法如下，kwargs 是只有一个元素的 dict
        u = User.find_by(username='qiu')
        """
        log('kwargs, ', kwargs)
        k, v = '', ''
        for key, value in kwargs.items():
            k, v = key, value
        all = cls.all()
        data = []
        for m in all:
            # getattr(m, k) 等价于 m.__dict__[k]
            if v == m.__dict__[k]:
                data.append(m)
        return data

    @classmethod
    def all(cls):
        # 得到一个类的所有存储实例，列表形式
        path = cls.db_path()
        models = load(path)
        ms = [cls.new(m) for m in models]
        return ms

    def save(self):
        # save函数用于把一个Model的实例保存到文件中
        # 得到一个类的所有存储实例
        models = self.all()
        log('models', models)
        if self.__dict__.get('id') is None:
            if len(models) > 0:
                # 不是第一个数据
                self.id = models[-1].id + 1
            else:
                # 是第一个数据
                self.id = 1
            models.append(self)
        else:
            # 有ID说明数据已经存在数据文件中
            # 那么就 找到这条数据并且替换
            index = -1
            for i, m in enumerate(models):
                if m.id == self.id:
                    index = i
                    break
            # 查看是否找到下标，如果找到就替换掉
            if index > -1:
                models[index] = self
        # 整体思路为得到类中全部存储实例，把生成所有存储的实例
        # 的列表中加入新的实例，更新列表。然后再循环实例列表生成每个
        # 实例的字典形式数据列表。把此数据列表存入到指定文件路径中
        # __dict__是包含了对象的所有属性和值的字典
        l = [m.__dict__ for m in models]
        path = self.db_path()
        save(l, path)

    # 实例调用remove则抓取实例的父类所有数据进行操作处理，之后再次保存到文件夹
    def remove(self):
        models = self.all()
        if self.__dict__.get('id') is not None:
            # 有 id 说明已经是存在于数据文件中的数据
            # 那么就找到这条数据并替换之
            index = -1
            for i, m in enumerate(models):
                if m.id == self.id:
                    index = i
                    break
            # 看看是否找到下标
            # 如果找到，就替换掉这条数据
            if index > -1:
                del models[index]
        # 保存
        l = [m.__dict__ for m in models]
        path = self.db_path()
        save(l, path)

    # route_message函数中[str(m) for m in message_list] 生成数据呈现给页面
    def __repr__(self):
        classname = self.__class__.__name__
        properties = ['{}: {{}}'.format(k, v) for k, v in self.__dict__.items()]
        s = '\n'.join(properties)
        return '< {}\n{} >\n'.format(classname, s)


