from AIBridge.constant.constant import PRIORITY
from AIBridge.setconfig import SetConfig
from AIBridge.exceptions import ConfigException
from AIBridge.database.sql_service import SQL
from AIBridge.database.no_sql_service import Mongodb

config = SetConfig.read_yaml()


def parse_fromat(prompt, format=None, format_structure=None):
    if format:
        prompt = prompt + f"format:{format} valid"
    if format_structure:
        prompt = prompt + f"format_structure:{format_structure}"
    prompt = (
        prompt
        + "Respond only in the exact specified format provided in the prompt,No extra information,No extra space"
    )
    return prompt


def parse_api_key(ai_service):
    if ai_service not in config:
        raise ConfigException("ai_service not found in config file")
    return config[ai_service][0]["key"]


def get_no_sql_obj():
    databse_uri = config["database_uri"]
    if "mongodb" in databse_uri:
        return Mongodb()


def get_database_obj():
    if "database" not in config:
        return SQL()
    elif config["database"] == "nosql":
        return get_no_sql_obj()
    elif config["database"] == "sql":
        return SQL()
