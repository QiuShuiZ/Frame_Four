from models import Model


class User(Model):
    """
        User 是一个保存用户数据的 model
        现在只有两个属性 username 和 password
    """
    def __init__(self, form):
        self.id = form.get('id', None)
        if self.id is not None:
            self.id = int(self.id)
        self.username = form.get('username', '')
        self.password = form.get('password', '')

    def validate_login(self):
        # return self.username == 'qiu' and self.password == '123'
        u = User.find_by(username=self.username)
        return u is not None and u.password == self.password

    def validate_register(self):
        return len(self.username) > 2 and len(self.password) > 2