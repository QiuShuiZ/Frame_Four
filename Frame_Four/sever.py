import socket
import urllib.parse

from utils import log

from routes import route_static
from routes import route_dict
# 用 from import as 来避免重名
from routes_todo import route_dict as todo_route


# 定义一个 class 用于保存请求的数据
class Request(object):
    def __init__(self):
        self.method = 'GET'
        self.path = ''
        self.query = {}
        self.body = ''
        self.headers = {}
        self.cookies = {}

    def add_cookies(self):
        """
        height=181; user=qiu
        """
        cookies = self.headers.get('Cookie', '')
        kvs = cookies.split('; ')
        log('cookie', kvs)
        for kv in kvs:
            if '=' in kv:
                k, v = kv.split('=')
                self.cookies[k] = v

    # 首次调用依次赋值数据self.headers self.cookies
    # 下一次来request时候，先清空self.headers再装数据，然后清空self.cookies再装
    def add_headers(self, header):
        """
        [
            'Accept-Language: zh-CN,zh;q=0.8'
            'Cookie: height=181; user=qiu'
        ]
        """
        # 清空 headers
        self.headers = {}
        lines = header
        for line in lines:
            k, v = line.split(': ', 1)
            self.headers[k] = v
        # 清除 cookies
        self.cookies = {}
        self.add_cookies()

    # form函数用于处理body部分，生成字典数据
    def form(self):
        body = urllib.parse.unquote(self.body)
        args = body.split('&')
        f = {}
        for arg in args:
            k, v = arg.split('=')
            f[k] = v
        return f


request = Request()


def error(request, code=404):
    """
    根据 code 返回不同的错误响应
    目前只有 404
    """

    e = {
        404: b'HTTP/1.x 404 NOT FOUND\r\n\r\n<h1>NOT FOUND</h1>',
    }
    return e.get(code, b'')


def parsed_path(path):
    """
    message=hello&author=qiu
    {
        'message': 'hello',
        'author': 'qiu',
    }
    """
    index = path.find('?')
    if index == -1:
        return path, {}
    else:
        path, query_string = path.split('?', 1)
        args = query_string.split('&')
        query = {}
        for arg in args:
            k, v = arg.split('=')
            query[k] = v
        return path, query


def response_for_path(path):
    path, query = parsed_path(path)
    request.path = path
    request.query = query
    log('path and query', path, query)
    """
    根据 path 调用相应的处理函数
    没有处理的 path 会返回 404
    """
    r = {
        '/static': route_static,
        # '/': route_index,
        # '/login': route_login,
        # '/messages': route_message,
    }
    r.update(route_dict)
    r.update(todo_route)
    response = r.get(path, error)
    return response(request)


def run(host='', port=3000):
    """
    启动服务器
    """
    # 初始化 socket
    # 使用 with 可以保证程序中断的时候正确关闭 socket 释放占用的端口
    log('start at', '{}:{}'.format(host, port))
    with socket.socket() as s:
        s.bind((host, port))
        # 无限循环来处理请求
        while True:
            # 监听 接受 读取请求数据 解码成字符串
            s.listen(3)
            connection, address = s.accept()
            r = connection.recv(1000)
            r = r.decode('utf-8')
            log('ip and request, {}\n{}'.format(address, r))
            # 因为 chrome 会发送空请求导致 split 得到空 list
            # 所以这里判断一下防止程序崩溃
            if len(r.split()) < 2:
                continue
            path = r.split()[1]
            # 设置 request 的 method
            request.method = r.split()[0]
            # 调用add_headers处理整个header（去掉了请求头与body）生成字典数据
            # 字典数据中包含了cookie如 'Cookie: height=181; user=qiu'
            # 所以add_headers包含再次单独处理cookie生成字典数据的函数，绑定self.cookies
            request.add_headers(r.split('\r\n\r\n', 1)[0].split('\r\n')[1:])
            # 把 body 放入 request 中
            request.body = r.split('\r\n\r\n', 1)[1]
            # 用 response_for_path 函数来得到 path 对应的响应内容
            response = response_for_path(path)
            log('debug **', 'sendall')
            # 把响应发送给客户端
            connection.sendall(response)
            log('debug ****', 'close')
            # 处理完请求, 关闭连接
            connection.close()
            log('debug *', 'closed')


if __name__ == '__main__':
    # 生成配置并且运行程序
    config = dict(
        host='',
        port=3000,
    )

    run(**config)