from sqlalchemy import create_engine
from sqlalchemy.engine.base import Engine
from sqlalchemy.engine.url import URL
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


class BuilderDbEngine:

    def __init__(self, engine_: Engine = None, settings_=None, db_config: dict = None, **kwargs):
        self.engine = self.generate_engine(engine_, settings_, db_config, **kwargs)
        self.session_maker = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    @staticmethod
    def generate_url(settings=None, db_config: dict = None, ):
        """
        生成db url, 优先级 db_config > settings > 默认sqlit3
        :param settings: 读取的ini配置文件
        :param db_config: 数据库配置
        :return:
        """
        if db_config:
            return URL(
                drivername="mysql+pymysql",
                username=db_config.get('username', ''),
                password=db_config.get('password', ''),
                host=db_config.get('host', ''),
                port=db_config.get('port', ''),
                database=db_config.get('database', ''),
            )
        if settings and hasattr(settings, 'Mysql'):
            mysql = settings.Mysql
            return URL(
                drivername="mysql+pymysql",
                username=mysql.username,
                password=mysql.password,
                host=mysql.host,
                port=mysql.port,
                database=mysql.database,
            )
        path = settings.Sqlit.path if hasattr(settings, 'Sqlit') else '/sqlit3.db'
        return 'sqlite://{}?check_same_thread=False'.format(path)

    def generate_engine(self, _engine: Engine = None, settings_=None, db_config: dict = None, **kwargs):
        if _engine:
            return _engine
        db_url = self.generate_url(settings_, db_config)
        return create_engine(db_url, **kwargs)

    def get_base(self, cls):
        return declarative_base(bind=self.engine, cls=cls)

    def get_database(self):
        db = self.session_maker()
        try:
            yield db
        finally:
            db.close()
