# TODO: This is an example file which you should delete after implementing
from dotenv import load_dotenv

from circles_local_database_python.connector import Connector
from circles_local_database_python.generic_crud import GenericCRUD
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum

load_dotenv()

# Setup the logger: change YOUR_REPOSITORY variable name and value
# YOUR_REPOSITORY_COMPONENT_ID = 0  # ask your team leader for this integer
# YOUR_REPOSITORY_COMPONENT_NAME = "Enter you repository name"
# DEVELOPER_EMAIL = "Enter you circlez.ai email"
# object1 = {
#     'component_id': YOUR_REPOSITORY_COMPONENT_ID,
#     'component_name': YOUR_REPOSITORY_COMPONENT_NAME,
#     'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
#     'developer_email': DEVELOPER_EMAIL
# }
# logger=Logger.create_logger(object=object1)

class ExampleClass(GenericCRUD):
    def __init__(self) -> None:
        pass
   
    
