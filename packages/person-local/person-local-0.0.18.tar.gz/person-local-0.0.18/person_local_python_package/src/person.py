from circles_local_database_python.connector import Connector
from circles_local_database_python.cursor import Cursor
from circles_local_database_python.generic_crud import GenericCRUD
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from logger_local.Logger import Logger
from language_local_python_package.src.language_enum_class import LanguageCode
import datetime

PERSON_LOCAL_PYTHON_COMPONENT_ID = 169
PERSON_LOCAL_PYTHON_COMPONENT_NAME = 'person-local'

object_init = {
    'component_id': PERSON_LOCAL_PYTHON_COMPONENT_ID,
    'component_name':PERSON_LOCAL_PYTHON_COMPONENT_NAME,
    'component_category':LoggerComponentEnum.ComponentCategory.Code.value,
    "developer_email":"jenya.b@circ.zone"
}
logger = Logger.create_logger(object=object_init)



class PersonDto:
    def __init__(self, number: int, gender_id: int, last_coordinate: str, location_id: int) -> None:
        self.number = number
        self.gender_id = gender_id
        self.last_coordinate = last_coordinate
        self.location_id = location_id

class PersonsLocal(GenericCRUD):
    def __init__(self) -> None:
        pass

    def delete_by_person_id( person_id: int ) -> None:
        logger.start(f"Delete person by person id person_id={person_id}",object={"person_id":person_id})
        GenericCRUD(schema_name="person").delete(table_name="person_table", id_column_name="person_id", id_column_value=person_id)
        query = (f"UPDATE person_table SET end_timestamp=CURRENT_TIMESTAMP() WHERE person_id={person_id}")
        try:
            db_connnection = Connector.connect("person")
            db_cursor = db_connnection.cursor()
            db_cursor.execute(query)
            db_connnection.commit()
            logger.end(f"Person deleted person_id= {person_id}", object={'person_id': person_id})
        except Exception as e:
            logger.exception(f"Couldn't get connection to person table", object=e)
            db_connnection.rollback()
            logger.end()
            raise Exception  
        
    def insert(person: PersonDto) -> int:
        logger.start("Insert person", object={
            "number": person.number,
            "gender_id": person.gender_id,
            "last_coordinate": person.last_coordinate,
            "location_id": person.location_id
        })

        #TODO: We should handle also situations when there is no person.number and we need to generate it using database-with-out-orm package number_generator()
        
        query = ("INSERT INTO person_table (number, gender_id, last_coordinate, location_id, start_timestamp) VALUES "
                 "({}, {}, {}, {}, CURRENT_TIMESTAMP)".format(person.number, person.gender_id, person.last_coordinate, person.location_id))
        try:
            db_connnection = Connector.connect("person")
            db_cursor = db_connnection.cursor()
            db_cursor.execute(query)
            db_connnection.commit()
            logger.info("Person inserted successfully.")
            person_id = db_cursor.lastrowid()
            logger.end(f"Person added person_id= {person_id}", object={'person_id': person_id})
            return person_id
        except Exception as e:
            logger.exception(f"Couldn't get connection to person table", object=e)
            db_connnection.rollback()
            logger.end()
            raise Exception  

    def _insert_person_ml(person_id: int, lang_code: LanguageCode,first_name: str,last_name: str) -> int:
        logger.start("Insert person",object={"person_id":person_id,"lang_code": lang_code,"first_name": first_name,"last_name": last_name})
        query = ("INSERT INTO person_ml_table (person_id,lang_code,first_name,last_name) VALUES ({},{},{},{})".format(person_id,lang_code,first_name,last_name))
        try:
            db_connnection = Connector.connect("person")
            db_cursor = db_connnection.cursor()
            db_cursor.execute(query)
            db_connnection.commit()
            logger.end("Person added", object={'person_id': person_id})
            return person_id
        except Exception as e:
            logger.exception(f"Couldn't get connection to person table", object=e)
            db_connnection.rollback()
            logger.end()
            raise Exception

    @staticmethod
    def update_birthday_day(person_id: int, day: int) -> None:
        logger.start(f"Update birthday day by person id person_id={person_id}",object={"person_id":person_id,"day":day})
        """
        person_json = {
            "person_id": person_id,
            "day": day
            }
        GenericCRUD.update(schema_name="person",table_name="person_table",json_data=person_jso,id_column_name="person_id",id_column_value=person_id)
        """
        query = ("UPDATE person_table SET day = {}, birthday_date = CONCAT(YEAR(birthday_date), '-', MONTH(birthday_date), '-', {})"
        "WHERE person_id = {}").format(day, day, person_id)
        try:
            db_connnection = Connector.connect("person")
            db_cursor = db_connnection.cursor()
            db_cursor.execute(query)
            db_connnection.commit()
            logger.end()
        except Exception as e:
            logger.exception(f"Couldn't get connection to person table", object=e)
            db_connnection.rollback()
            logger.end()
            raise Exception

    @staticmethod
    def update_birthday_month(person_id: int, month: int) -> None:
        logger.start(f"Update birthday month by person id person_id={person_id}",object={"person_id":person_id,"month":month})
        """
        #TODO: Call db_conncetion.start_tranaction(), if do not exists, please create this method in the database package
        person_json = {
            "person_id": person_id,
            "month": month
            }
        GenericCRUD.update(schema_name="person",table_name="person_table",json_data=person_json,id_column_name="person_id",id_column_value=person_id)
        """
        query = ("UPDATE person_table SET `month` = {}, birthday_date = CONCAT(YEAR(birthday_date), '-', {}, '-', DAY(birthday_date))"
         "WHERE person_id = {}").format(month, month, person_id)
        try:
            db_connnection = Connector.connect("person")
            db_cursor = db_connnection.cursor()
            db_cursor.execute(query)
            db_connnection.commit()
            logger.end()
        except Exception as e:
            logger.exception(f"Couldn't get connection to person table", object=e)
            db_connnection.rollback()
            logger.end()
            raise Exception

    @staticmethod
    def update_birthday_year(person_id: int, year: int) -> None:
        logger.start(f"Update birthday year by person id person_id={person_id}",object={"person_id":person_id,"year":year})
        """
        new_year = datetime.date(year)
        person_json = {
            "person_id": person_id,
            "year": year,
            "birthday_date": new_year.year
            }
        GenericCRUD.update(schema_name="person",table_name="person_table",json_data=person_json,id_column_name="person_id",id_column_value=person_id)
        
        """
        query = ("UPDATE person_table SET year = {}, birthday_date = CONCAT({}, '-', MONTH(birthday_date), '-', DAY(birthday_date))"
        "WHERE person_id = {}").format(year, year, person_id)
        try:
            db_connnection = Connector.connect("person")
            db_cursor = db_connnection.cursor()
            db_cursor.execute(query)
            db_connnection.commit()
            logger.end()
        except Exception as e:
            logger.exception(f"Couldn't get connection to person table", object=e)
            db_connnection.rollback()
            logger.end()
            raise Exception
    
    @staticmethod
    def update_birthday_date(person_id: int, birthday_date: datetime.date) -> None:
        logger.start(f"Update birthday date by person id person_id={person_id}",object={"person_id":person_id,"birthday_date":birthday_date})
        date = str(birthday_date).split('-')
        person_json = {
            "person_id": person_id,
            "year": int(date[0]),
            "month": int(date[1]),
            "day": int(date[2]),
            "birthday_date": birthday_date
            }
        GenericCRUD(schema_name="person").update(table_name="person_table", json_data=person_json, id_column_name="person_id", id_column_value=person_id)
        logger.end()
        
    @staticmethod
    def update_first_name_by_profile_id( profile_id: int, first_name: str) -> None:
        logger.start(f"Update first name by profile id profile_id={profile_id}",object={"profile_id":profile_id,"first_name":first_name})
        person_json = {
            "person_id": profile_id,
            "first_name": first_name
            }
        GenericCRUD(schema_name="person").update(table_name="person_table", json_data=person_json, id_column_name="person_id", id_column_value=profile_id)
        logger.end()

    @staticmethod
    def update_person_ml_first_name_by_person_id( person_id: int, lang_code: LanguageCode, first_name: str) -> None:
        logger.start(f"Update first name in ml table by person id person_id={person_id}",object={"person_id":person_id, lang_code: LanguageCode, "first_name":first_name})
        person_json = {
            "person_id": person_id,
            "lang_code": lang_code,
            "first_name": first_name
            }
        GenericCRUD(schema_name="person").update(table_name="person_ml_table", json_data=person_json, id_column_name="person_id", id_column_value=person_id)
        logger.end() 

    @staticmethod
    def update_nickname_by_person_id( person_id: int, nickname: str) -> None:
        logger.start(f"Update nickname by person id person_id={person_id}",object={"person_id":person_id,"nickname":nickname})
        person_json = {
            "person_id": person_id,
            "nickname": nickname
            }
        GenericCRUD(schema_name="person").update(xtable_name="person_table", json_data=person_json, id_column_name="person_id", id_column_value=person_id)
        logger.end()

    @staticmethod
    def update_last_name_by_person_id( person_id: int, last_name: str) -> None:
        logger.start(f"Update last name by person id person_id={person_id}",object={"id":id,"last_name":last_name})
        person_json = {
            "person_id": person_id,
            "last_name": last_name
            }
        GenericCRUD(schema_name="person").update(table_name="person_table", json_data=person_json, id_column_name="person_id", id_column_value=person_id)
        logger.end()

    @staticmethod
    def update_person_ml_last_name_by_person_id(person_id: int, lang_code: LanguageCode, last_name: str) -> None:
        logger.start(f"Update last name in ml table by person id person_id={person_id}",object={"person_id":person_id,"last_name":last_name})
        person_json = {
            "person_id": person_id,
            "lang_code": lang_code,
            "last_name": last_name
            }        
        GenericCRUD(schema_name="person").update(table_name="person_ml_table", json_data=person_json, id_column_name="person_id", id_column_value=person_id)
        logger.end()
