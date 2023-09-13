from .bigtangerine import BigTangerine
from cjen.nene.database_pool import DatabasePool
from .nene.database_info import DataBaseInfo


class DBBigTangerine(BigTangerine):
    def __init__(self, database_info):
        super().__init__()
        self.database_info = DataBaseInfo.factory(database_info )if type(database_info) == dict else database_info
        self.context["cursor"] = DatabasePool.cursor(host=self.database_info.host,
                                                     port=self.database_info.port,
                                                     user=self.database_info.user,
                                                     pwd=self.database_info.pwd,
                                                     database=self.database_info.database)
