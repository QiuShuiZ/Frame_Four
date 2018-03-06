# coding=utf-8
from utils import log
from models.message import Message
from models.user import User

import random
# message_list 存储了所有的message
message_list = []
session = {}


def template(name):
    path = 'templates/' + name
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


def random_str():
    # 生成一个随机字符串
    seed = "asdhbaoisdhnoafshjsoidfpouqwer"
    s = ''
    for i in range(16):
        random_index = random.randint(0, len(seed) - 2)
        s += seed[random_index]
    return s


def response_with_headers(headers, code=200):
    """
Content-Type: text/html
Set-Cookie: user=qiu
    """
    header = 'HTTP/1.1 {}  OK\r\n'.format(code)
    header += ''.join(['{}: {}\r\n'.format(k, v) for k, v in headers.items()])
    return header


def route_index(request):
    """
     主页的处理函数，返回主页的响应
    """
    header = 'HTTP/1.1 210 OK\r\nContent-Type: text/html\r\n'
    body = template('index.html')
    username = current_user(request)
    body = body.replace('{{username}}', username)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def current_user(request):
    session_id = request.cookies.get('user', '')
    username = session.get(session_id, '游客')
    # username = request.cookies.get('user', '游客')
    return username


def redirect(url):
    """
     浏览器收到302响应会在HTTP header里面找
     location字段并且获取一个url
     301永久性重定向，302临时重定向
    """
    headers = {
        'Location': url,
    }
    # 增加location字段并且生成HTTP响应返回，没有HTTP BODY部分
    r = response_with_headers(headers, 302) + '\r\n'
    return r.encode('utf-8')


def route_login(request):
    headers = {
        'Content-Type': 'text/html',
        # 'Set-Cookie': 'height=181; qiu=1; pwd=2; Path=/',
    }
    username = current_user(request)
    if request.method == 'post':
        form = request.form()
        u = User.new(form)
        if u.validate_login():
            # 设置一个随机字符串当令牌
            session_id = random_str()
            session[session_id] = u.username
            headers['Set-Cookie'] = 'user={}'.format(session_id)
            result = '登陆成功'
        else:
            result = '用户名或密码错误'
    else:
        result = ''
    body = template('login.html')
    body = body.replace('{{result}}', result)
    body = body.replace('{{username}}', username)
    header = response_with_headers(headers)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


# 注册函数抓取request请求，生成实例同时保存到类名.txt文件下
def route_register(request):
    header = 'HTTP/1.1 210 OK\r\nContent-Type: text/html\r\n'
    if request.method == 'post':
        """
         HTTP BODY username=qiu123&password=123 经过
         request.form()函数之后会变成一个字典
        """
        form = request.form()
        # 类调用new方法生成实例，在类的定义中就是接受参数form
        u = User.new(form)
        if u.validate_reginster():
            u.save()
            result = '注册成功<br><pre>{}</pre>'.format(User.all())
        else:
            result = '用户名或者密码长度必须大于2'
    else:
        result = ''
    body = template('register.html')
    body = body.replace('{{result}}', result)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def route_message(request):
    log('本次请求的 method', request.method)
    username = current_user(request)
    if username == '游客':
        log("**debug, route msg 未登录")
        return redirect('/')
    if request.method == 'POST':
        form = request.form()
        msg = Message.new(form)
        log('post', form)
        message_list.append(msg)
        # 应该在这里保存message_list
    header = 'HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n'
    body = template('html_basic.html')
    msgs = '<br>'.join([str(m) for m in message_list])
    body = body.replace('{{message}}', msgs)
    r = header + '\r\n' + body
    return r.encode(encoding='utf-8')


def route_static(request):
    """
    静态资源处理函数，读取图片并且生成响应返回。
    """
    filename = request.query.get('file', 'doge.gif')
    path = 'static/' + filename
    with open(path, 'rb') as f:
        header = b'HTTP/1.1 200 OK\r\nContent-Type: image/gif\r\n'
        img = header + b'\r\n' + f.read()
        return img


route_dict = {
    '/': route_index,
    '/login': route_login,
    '/register': route_register,
    '/messages': route_message,
}
