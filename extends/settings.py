"""
Project settings
"""
from pathlib import Path
from configparser import ConfigParser
from starlette.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent
# 模板文件位置
TEMPLATES_PATH = Path(__file__).parent.parent / 'apps/templates'

# 明确公共接口
__all__ = [
    'project_settings',
    'BaseSettings',
    'BaseSection'
]


class SectionMetaClass(type):

    def __new__(mcs, name, bases, attrs):
        """
        检查不支持的注解类型
        """
        _super_new = super().__new__
        _supported_types = {
            str: 'str',
            int: 'int',
            float: 'float',
            bool: 'bool',
            list: 'list',
            bytes: 'bytes'
        }
        # 没有注解的需要添加
        if not hasattr(mcs, '__annotations__'):
            setattr(mcs, '__annotations__', {})

        attrs['_supported_types'] = _supported_types
        for attr, val in mcs.__annotations__.items():
            if val not in _supported_types:
                _types = ', '.join(map(lambda t: t.__name__, _supported_types))
                raise AttributeError(
                    f"The type '{val}' for '{attr}' is not supported by settings. "
                    f"Supported types are {_types}."
                )

        return _super_new(mcs, name, bases, attrs)


class BaseSection(object, metaclass=SectionMetaClass):
    """
    配置文件里section的名字要与类名一致
    如：
    [Mariadb]
    host=127.0.0.1

    class Mariadb:
        pass

    注意：定义的option（属性名）不要以下划线开头
    """
    _parser = None
    _allow_undefined = True  # 是否允许未定义的属性

    def __init__(self, allow_undefined=None):
        """
        allow_undefined: 是否允许读取未定义配置项（如果存在，默认转为字符串）
        """
        self._section_name = self.__class__.__name__
        if allow_undefined is not None:
            self._allow_undefined = allow_undefined

    def __getattr__(self, key):
        """
        通过注解类型获取配置的值
        """
        options = self.__annotations__
        option_keys = options.keys()
        section_name = self.__class__.__name__
        if key not in option_keys:
            if self._allow_undefined:
                # build undefined option
                options[key] = str
            else:
                raise AttributeError("No option '%s' defined in section %s." % (key, section_name))
        for option, a_type in options.items():
            if key == option:
                try:
                    value = self._parser.get(section_name, option)
                except Exception as e:
                    raise e
                # type changing
                type_name = self._supported_types.get(a_type)
                try:
                    # try to get the self defined method
                    return object.__getattribute__(self, 'to_' + type_name).__call__(value)
                except AttributeError:
                    pass
                except TypeError:
                    raise TypeError(f'The value "{value}" for option {option} is invalid.')

                if value is None:
                    return value
                # default action
                return a_type.__call__(value)
        return super().__getattribute__(key)

    def __repr__(self):
        return '<%s section object>' % self.__class__.__name__

    def __dict__(self):
        dirs = dict()
        for key, value in self.__annotations__.items():
            dirs[key] = getattr(self, key)
        return dirs

    def add_supported_type(self, _type, type_name):
        assert isinstance(type_name, str)
        self._supported_types.update({_type: type_name})

    @staticmethod
    def to_bool(value: str):
        if value in ('true', 'True'):
            return True
        elif value in ('false', 'False'):
            return False
        raise TypeError


class BaseSettings(object):
    path = None

    def __new__(cls, *args, **kwargs):
        assert cls.path is not None, "The attribute 'path' must be given."
        if not cls.path.exists():
            raise FileNotFoundError(cls.path)
        parser = ConfigParser()
        parser.read(cls.path, encoding='utf-8')
        dicts = filter(
            lambda item: not item[0].startswith('__') and isinstance(item[1], BaseSection),
            cls.__dict__.items())
        for attr, obj in dicts:
            setattr(obj, '_parser', parser)
        return super().__new__(cls, *args, **kwargs)

    def __dir__(self):
        dirs = super().__dir__()
        dirs = [item for item in dirs
                if not item.startswith('_')
                and isinstance(getattr(self, item), BaseSection)]
        return dirs

    def __iter__(self):
        dirs = self.__dir__()
        for item in dirs:
            yield getattr(self, item).__dict__()

    def __repr__(self):
        return '<%s settings object>' % self.__class__.__name__


class DEFAULT(BaseSection):
    # add more options configured in settings.ini.template
    debug: bool
    log_dir: str
    secret: str


class MySQL(BaseSection):
    host: str
    port: int
    user: str
    password: str
    name: str

    def uri(self, sqldiver: str = 'pymysql', ):
        return f'mysql+{sqldiver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}?charset=utf8mb4'

class PostgreSQL(BaseSection):
    host: str
    port: int
    user: str
    password: str
    name: str

    def uri(self, sqldiver: str = 'postgresql', ):
        return f'postgresql+{sqldiver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}'


class Redis(BaseSection):
    host: str
    port: int
    password: str
    default_db: int
    secondary_db: int

    @property
    def default_location(self):
        return f'redis://:{self.password}@{self.host}:{self.port}/{self.default_db}'

    def uri(self, passwd=None, host=None, port=None, db=None):
        return f'redis://:{passwd or self.password}@{host or self.host}:{port or self.port}/{db or self.default_db}'


class Security(BaseSection):
    api_key: str
    secret_key: str
    event_api_key: str
    event_secret_key: str
    password_level: str
    password_min_length: int
    jwt_secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    refresh_token_expire_minutes: int
    verification_code_expire_minutes: int

    @property
    def password_validators(self):

        # min length validator
        validators = [{'NAME': 'apps.services.password.MinimumLengthValidator'}]
        # password policy validators
        if self.password_level == 'medium':
            validators.append({'NAME': 'apps.services.password.MediumLevelPasswordValidator'})
        elif self.password_level == 'high':
            validators.append({'NAME': 'apps.services.password.HighLevelPasswordValidator'})
        else:
            validators.append({'NAME': 'apps.services.password.LowLevelPasswordValidator'})
        return validators


class Redirect(BaseSection):
    login_url: str
    register_validate_page: str
    reset_password_page: str


class SysSetting:
    #  一些公共的设置
    SECRET_KEY = None
    ALGORITHM = None
    ACCESS_TOKEN_EXPIRE_MINUTES = None
    REFRESH_TOKEN_EXPIRE_MINUTES = None
    PAGE_SIZE = 10
    PAGE_QUERY_PARAM = 'Page'
    PAGE_SIZE_QUERY_PARAM = 'PageSize'
    TEMPLATES = Jinja2Templates(directory=TEMPLATES_PATH)
    AUTHENTICATION_BACKENDS = ['apps.services.backends.DefaultBackend', 'apps.services.backends.GoogleBackend']
    RAM_AUTHENTICATION_BACKENDS = ['apps.services.backends.DefaultBackend']

    @property
    def templates(self):
        return SysSetting.TEMPLATES



class Server(BaseSection):
    http_server_host: str
    http_server_port: int

    

class ProjectSettings(BaseSettings):
    """
    项目设置文件
    """
    path = Path(BASE_DIR).joinpath('settings.ini')
    system: SysSetting = SysSetting()
    default: DEFAULT = DEFAULT()
    mysql: MySQL = MySQL()
    postgres: PostgreSQL = PostgreSQL()
    redis: Redis = Redis()
    security: Security = Security()
    redirect: Redirect = Redirect()
    server: Server = Server()
    def __init__(self):
        self.system.SECRET_KEY = self.security.jwt_secret_key
        self.system.ALGORITHM = self.security.algorithm
        self.system.ACCESS_TOKEN_EXPIRE_MINUTES = self.security.access_token_expire_minutes
        self.system.REFRESH_TOKEN_EXPIRE_MINUTES = self.security.refresh_token_expire_minutes


project_settings = ProjectSettings()
