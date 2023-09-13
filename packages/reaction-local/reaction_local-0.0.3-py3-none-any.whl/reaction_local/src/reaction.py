from typing import Dict
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from dotenv import load_dotenv

load_dotenv()
from logger_local.Logger import Logger  # noqa: E402
from circles_local_database_python.connector import Connector  # noqa: E402

REACTION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID = 168
REACTION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME = 'reaction_local/tests/test_reaction.py'

object_to_insert = {
    'component_id': REACTION_LOCAL_PYTHON_PACKAGE_COMPONENT_ID,
    'component_name': REACTION_LOCAL_PYTHON_PACKAGE_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

logger = Logger.create_logger(object=object_to_insert)

class Reaction:
    def __init__(self):
        INIT_METHOD_NAME = "__init__"
        logger.start(INIT_METHOD_NAME)
        self.connector = Connector.connect("reaction")
        self.cursor = self.connector.cursor()
        logger.end(INIT_METHOD_NAME)

    def insert_reaction(self, reaction_data: Dict[str, any], profile_id: int, lang_code: str) -> int:
        INSERT_REACTION_METHOD_NAME = "insert_reaction"
        logger.start(INSERT_REACTION_METHOD_NAME, object={'reaction_data': reaction_data, 'profile_id': profile_id, 'lang_code': lang_code})

        title : str = str(reaction_data["title"])
        query_get = "SELECT reaction_type_id FROM reaction.reaction_type_ml_table WHERE title = %s"
        self.cursor.execute(query_get, (title,))
        rows = self.cursor.fetchall()
        reaction_type_id: int = None
        if len(rows) > 0:
            reaction_type_id, = rows[0]

        if not reaction_type_id:
            sql_insert_reaction_type = "INSERT INTO reaction_type_table SELECT NULL;"
            self.cursor.execute(sql_insert_reaction_type)
            self.connector.commit()

            sql_last_insert_id = "SELECT LAST_INSERT_ID();"
            self.cursor.execute(sql_last_insert_id)
            row = self.cursor.fetchone()
            last_insert_id = row[0]
            sql_insert_reaction_type_ml = "INSERT INTO reaction_type_ml_table(reaction_type_id, lang_code, name) VALUES (%s, %s, %s);"
            params = (last_insert_id, 'en', 'Your_Name_Here')
            self.cursor.execute(sql_insert_reaction_type_ml, params)


        query_insert = "INSERT INTO reaction_table(`value`, image, reaction_type_id) VALUES (%s, %s, %s)"
        self.cursor.execute(query_insert, (reaction_data["value"], reaction_data["image"], reaction_type_id))
        
        reaction_id = self.cursor.lastrowid()
        query_insert_ml = "INSERT INTO reaction_ml_table(reaction_id, lang_code, title, description, name_approved) VALUES (%s, %s, %s, %s, %s)"
        self.cursor.execute(query_insert_ml, (reaction_id, lang_code, reaction_data["title"], reaction_data["description"], True))

        self.connector.commit()

        logger.end(INSERT_REACTION_METHOD_NAME)
        return reaction_id

    def update_reaction(self, reaction_id: int, reaction_data: Dict[str, any]):
        UPDATE_REACTION_METHOD_NAME = "update_reaction"
        logger.start(UPDATE_REACTION_METHOD_NAME, object={'reaction_data': reaction_data, 'reaction_id': reaction_id})
        
        query_update = "UPDATE reaction_table SET `value` = %s, image = %s WHERE reaction_id = %s"
        self.cursor.execute(query_update, (reaction_data["value"], reaction_data["image"], reaction_id))

        query_insert_ml = "UPDATE reaction_ml_table SET title = %s, description = %s, name_approved = %s WHERE reaction_id = %s"
        self.cursor.execute(query_insert_ml, (reaction_data["title"], reaction_data["description"], True, reaction_id))
        
        self.connector.commit()
        logger.end(UPDATE_REACTION_METHOD_NAME)

    def read_reaction(self, reaction_id: int) -> (int, int, str, int, int, str, str, str):
        READ_REACTION_METHOD_NAME = "read_reaction"
        logger.start(READ_REACTION_METHOD_NAME, object={'reaction_id': reaction_id})

        query_get = "SELECT `value`, image, reaction_type_id, reaction_ml_id, lang_code, title, description FROM reaction_ml_view WHERE reaction_id = %s"
        self.cursor.execute(query_get, (reaction_id,))
        row = self.cursor.fetchone()
        if not row:
            return None
        value, image, reaction_type_id, reaction_ml_id, lang_code, title, description = row

        logger.end(READ_REACTION_METHOD_NAME, object = {'reaction_id': reaction_id, 'value': value, 'image': image, 'reaction_type_id': reaction_type_id, 'reaction_ml_id': reaction_ml_id, 'lang_code': lang_code, 'title': title, 'description': description})
        return reaction_id, value, image, reaction_type_id, reaction_ml_id, lang_code, title, description
    
    def delete_reaction(self, reaction_id: int):
        DELETE_REACTION_METHOD_NAME = "delete_reaction"
        logger.start(DELETE_REACTION_METHOD_NAME, object={'reaction_id': reaction_id})

        query_update = "UPDATE reaction_table SET end_timestamp = NOW() WHERE reaction_id = %s"
        self.cursor.execute(query_update, (reaction_id,))

        self.connector.commit()
        logger.end(DELETE_REACTION_METHOD_NAME)

    
    @staticmethod
    def get_reaction_from_entry(entry: Dict[str, Dict[str, any]]) -> Dict[str, any]:
        GET_REACTION_FROM_ENTRY_METHOD_NAME = "get_reaction_from_entry"
        logger.start(GET_REACTION_FROM_ENTRY_METHOD_NAME, object={'entry': entry})
        
        reaction = {
            "value": entry["reaction"].get("value", None),
            "image": entry["reaction"].get("image", None),
            "title": entry["reaction"].get("title", None)
        }
        
        logger.end(GET_REACTION_FROM_ENTRY_METHOD_NAME, object={'reaction': reaction})
        return reaction
