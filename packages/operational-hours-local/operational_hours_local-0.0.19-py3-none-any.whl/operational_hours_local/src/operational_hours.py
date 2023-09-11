import json
from logger_local.LoggerComponentEnum import LoggerComponentEnum
import datetime
from typing import List, Dict, Tuple

from dotenv import load_dotenv
load_dotenv()
# The noqa: E402 tells the linter to ignore a "This import should be at the top of the file" warning on that line.
from circles_local_database_python.connector import Connector  # noqa: E402
from logger_local.Logger import Logger  # noqa: E402
from circles_local_database_python.generic_crud import GenericCRUD  # noqa: E402

OPERATIONAL_HOURS_LOCAL_COMPONENT_ID = 158
OPERATIONAL_HOURS_LOCAL_COMPONENT_NAME = 'operational_hours_local/src/operational_hours.py'


obj = {
    'component_id': OPERATIONAL_HOURS_LOCAL_COMPONENT_ID,
    'component_name': OPERATIONAL_HOURS_LOCAL_COMPONENT_NAME,
    'component_category': LoggerComponentEnum.ComponentCategory.Code.value,
    'developer_email': 'tal.g@circ.zone'
}

logger = Logger.create_logger(object=obj)

# OperationalHours class provides methods for all the CRUD operations to the operational_hours db


class OperationalHours(GenericCRUD):
    def __init__(self):
        INIT_METHOD_NAME = '__init__'
        logger.start(INIT_METHOD_NAME)
        self.connector = Connector.connect("operational_hours")
        self.cursor = self.connector.cursor()
        logger.end(INIT_METHOD_NAME)

    # location_id is optional
    def insert(self, profile_id: int, location_id: int, hours: List[Dict[str, int]]):
        INSERT_OPERATIONAL_HOURS_METHOD_NAME = "operational_hours.insert"
        logger.start(INSERT_OPERATIONAL_HOURS_METHOD_NAME, object={
                     'profile_id':  profile_id, 'location_id': location_id, 'hours': hours})

        for index, day in enumerate(hours):
            query_insert = "INSERT INTO operational_hours_table(profile_id, location_id, day_of_week, from_time, until_time) VALUES (%s, %s, %s, %s, %s)"
            self.cursor.execute(
                query_insert, (profile_id, location_id, index, day["from_time"], day["until_time"]))
            logger.info("executed query insert")

        self.connector.commit()
        operational_hours_ids = self.get_operational_hours_ids_by_profile_id_location_id(
            profile_id, location_id)
        logger.end(INSERT_OPERATIONAL_HOURS_METHOD_NAME, object={
                   'operational_hours_ids': operational_hours_ids})
        return operational_hours_ids

    # location_id is optional
    def update(self, profile_id: int, location_id: int, hours: List[Dict[str, int]]):
        UPDATE_OPERATIONAL_HOURS_METHOD_NAME = "operational_hours.update"
        logger.start(UPDATE_OPERATIONAL_HOURS_METHOD_NAME, object={
                     'profile_id':  profile_id, 'location_id': location_id, 'hours': hours})
        operational_hours_ids = self.get_operational_hours_ids_by_profile_id_location_id(
            profile_id)

        for index, day in enumerate(hours):
            operational_hours_id = operational_hours_ids[index]
            query_update = "UPDATE operational_hours_table SET day_of_week = %s, from_time = %s, until_time = %s WHERE operational_hours_id = %s"
            if location_id is not None:
                query_update += " AND location_id = %s"
                self.cursor.execute(query_update, (index, day["from_time"],
                                                   day["until_time"], operational_hours_id, location_id))
            else:
                self.cursor.execute(
                    query_update, (index, day["from_time"], day["until_time"], operational_hours_id))

        self.connector.commit()
        logger.end(UPDATE_OPERATIONAL_HOURS_METHOD_NAME)

    def read_operational_hours_by_profile_id(
            self, profile_id: int, location_id: int = None) -> List[
            Tuple[int, int, datetime.timedelta, datetime.timedelta]]:
        READ_OPERATIONAL_HOURS_METHOD_NAME = "read_operational_hours"
        logger.start(READ_OPERATIONAL_HOURS_METHOD_NAME,
                     object={'profile_id':  profile_id, 'location_id': location_id})

        query_get = "SELECT operational_hours_id, day_of_week, from_time, until_time FROM operational_hours_view WHERE profile_id = %s"
        if location_id is not None:
            query_get += " AND location_id = %s"
            self.cursor.execute(query_get, (profile_id, location_id))
        else:
            self.cursor.execute(query_get, (profile_id,))
        rows = self.cursor.fetchall()
        operational_hours = []
        if len(rows) > 0:
            for row in rows:
                operational_hours.append(row)


        operational_hours_json = self._operational_hours_to_json(operational_hours)
        logger.end(READ_OPERATIONAL_HOURS_METHOD_NAME, object={'operational_hours_json': operational_hours_json})
        return operational_hours

    def delete_all_operational_hours_by_profile_id(self, profile_id: int, location_id: int = None):
        DELETE_OPERATIONAL_HOURS_METHOD_NAME = "delete_operational_hours"
        logger.start(DELETE_OPERATIONAL_HOURS_METHOD_NAME,
                     object={'profile_id':  profile_id, 'location_id': location_id})

        query_update = "UPDATE operational_hours_table SET end_timestamp = NOW() WHERE profile_id = %s"
        if location_id is not None:
            query_update += " AND location_id = %s"
            self.cursor.execute(query_update, (profile_id, location_id))
        else:
            self.cursor.execute(query_update, (profile_id,))

        self.connector.commit()
        logger.end(DELETE_OPERATIONAL_HOURS_METHOD_NAME)

    def get_operational_hours_id_by_profile_id_location_id(self, profile_id: int, location_id: int = None) -> int:
        GET_OPERATIONAL_HOURS_ID_METHOD_NAME = "get_operational_hours_id"
        logger.start(GET_OPERATIONAL_HOURS_ID_METHOD_NAME,
                     object={'profile_id':  profile_id, 'location_id': location_id})

        query_get = "SELECT operational_hours_id FROM operational_hours_view WHERE profile_id = %s"
        if location_id is None:
            self.cursor.execute(query_get, (profile_id,))
        else:
            query_get += " AND location_id = %s"
            self.cursor.execute(query_get, (profile_id, location_id))
        rows = self.cursor.fetchall()
        operational_hours_id = None
        if len(rows) > 0:
            operational_hours_id, = rows[0]

        logger.end(GET_OPERATIONAL_HOURS_ID_METHOD_NAME, object={
                   'operational_hours_id':  operational_hours_id})
        return operational_hours_id

    def get_operational_hours_ids_by_profile_id_location_id(
            self, profile_id: int, location_id: int = None) -> List[int]:
        GET_OPERATIONAL_HOURS_IDS_METHOD_NAME = "get_operational_hours_ids"
        logger.start(GET_OPERATIONAL_HOURS_IDS_METHOD_NAME, object={
                     'profile_id': profile_id, 'location_id': location_id})

        query_get = "SELECT operational_hours_id FROM operational_hours_view WHERE profile_id = %s"
        operational_hours_ids: list[int] = []
        if location_id is None:
            self.cursor.execute(query_get, (profile_id,))
        else:
            query_get += " AND location_id = %s"
            self.cursor.execute(query_get, (profile_id, location_id))
        rows = self.cursor.fetchall()
        if len(rows) > 0:
            for row in rows:
                operational_hours_id, = row
                operational_hours_ids.append(operational_hours_id)

        logger.end(GET_OPERATIONAL_HOURS_IDS_METHOD_NAME, object={
                   'operational_hours_ids':  operational_hours_ids})
        return operational_hours_ids

    '''
  There may be a problem, if for example there's hour1 = {"day_of_week" : 2, "from": 8:00, "until": 12:00} and hour2 = {"day_of_week": 2, "from": 15:00, "until": 20:00}
  (A business closed between 12:00 and 15:00) then hour2 will override hour1 in operational_hours = {}.
  '''
    @staticmethod
    def create_hours_array(days_collection: List[Dict[str, int]]):
        CREATE_HOURS_ARRAY_METHOD_NAME = "create_hours_array"
        logger.start(CREATE_HOURS_ARRAY_METHOD_NAME, object={
                     'days_collection':  days_collection})

        operational_hours = []
        for day in days_collection:
            day_of_week = day.get("day_of_week", None)
            logger.info(object={'day_of_week': day_of_week})
            element_to_insert = {
                "from_time": day.get("from_time", None),
                "until_time": day.get("until_time", None)
            }
            operational_hours.insert(int(day_of_week), element_to_insert)

        logger.end(CREATE_HOURS_ARRAY_METHOD_NAME, object={
                   'operational_hours':  operational_hours})
        return operational_hours
    
    # This method is required because the logger can't serialize datetime.timedelta
    def _operational_hours_to_json(self, operational_hours: List[Tuple[int, int, datetime.timedelta, datetime.timedelta]]) -> str:
        OPERATIONAL_HOURS_TO_JSON_METHOD_NAME = "_operational_hours_to_json"
        logger.start(OPERATIONAL_HOURS_TO_JSON_METHOD_NAME)
        
        operational_hours_json = []
        for operational_hour in operational_hours:
            operational_hours_json.append({
                "operational_hours_id": operational_hour[0],
                "day_of_week": operational_hour[1],
                "from_time": str(operational_hour[2]),
                "until_time": str(operational_hour[3])
            })

        operational_hours_json = json.dumps(operational_hours_json)
        
        logger.end(OPERATIONAL_HOURS_TO_JSON_METHOD_NAME)
        return operational_hours_json
