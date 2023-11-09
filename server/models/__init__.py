from models.service import *
from models.user import *
from models.submission import *
from models.relationship import *
from models.chat import *
from models.index import *

tables_dict = {table.__tablename__: table for table in Base.__subclasses__()}
