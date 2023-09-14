from cjen.nene.properties import required


class DataBaseInfo:
    def __init__(self, info: dict):
        self.info = info

    @property
    @required()
    def user(self): return self.info.get("user")

    @property
    @required()
    def host(self): return self.info.get("host")

    @property
    @required()
    def pwd(self): return self.info.get("pwd")

    @property
    @required()
    def database(self): return self.info.get("database")

    @property
    @required()
    def port(self): return self.info.get("port")

    """
    为了兼容以前传递的字典
    """
    def get(self, key):
        if key == "user": return self.user
        elif key == "host": return self.host
        elif key == "pwd": return self.pwd
        elif key == "database": return self.database
        elif key == "port": return self.port

    @classmethod
    def factory(cls, data_dict: dict):
        return DataBaseInfo(data_dict)






