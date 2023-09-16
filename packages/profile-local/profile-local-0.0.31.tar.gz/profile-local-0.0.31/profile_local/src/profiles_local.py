from typing import Dict
try:
    # Works when running the tests from this package
    from constants_profiles_local import *
except Exception as e:
    # Works when importing this module from another package
    from profile_local.constants_profiles_local import *
from dotenv import load_dotenv
load_dotenv()
from circles_local_database_python.generic_crud import GenericCRUD  # noqa: E402
from circles_local_database_python.connector import Connector  # noqa: E402
from logger_local.Logger import Logger  # noqa: E402
from circles_number_generator.src.number_generator import NumberGenerator  # noqa: E402

logger = Logger.create_logger(object=OBJECT_TO_INSERT_CODE)

# Named ProfileLocalClass because Profile is already taken by the class in profile.py in python 3.11 library


class ProfilesLocal(GenericCRUD):

    def __init__(self):
        logger.start()
        self.connector = Connector.connect("profile")
        self.cursor = self.connector.cursor()
        logger.end()

    '''
    person_id: int,
    data: Dict[str, any] = {
        'profile_name': profile_name,
        'name_approved': name_approved,
        'lang_code': lang_code,
        'user_id': user_id,                             #Optional
        'is_main': is_main,                             #Optional
        'visibility_id': visibility_id,
        'is_approved': is_approved,
        'profile_type_id': profile_type_id, #Optional
        'preferred_lang_code': preferred_lang_code,     #Optional
        'experience_years_min': experience_years_min,   #Optional
        'main_phone_id': main_phone_id,                 #Optional
        'rip': rip,                                     #Optional
        'gender_id': gender_id,                         #Optional
        'stars': stars,
        'last_dialog_workflow_state_id': last_dialog_workflow_state_id
    },
    profile_id: int
    '''

    def insert(self, person_id: int, data: Dict[str, any]) -> int:
        logger.start(object={'data': data})

        query_insert_profile_table = "INSERT INTO profile_table(`number`, user_id, person_id, is_main," \
            " visibility_id, is_approved, profile_type_id, preferred_lang_code, experience_years_min," \
            " main_phone_id, rip, gender_id, stars, last_dialog_workflow_state_id)" \
            " VALUE (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s);"
        query_insert_profile_ml_table = "INSERT INTO profile_ml_table(profile_id, lang_code, `name`," \
            " name_approved) VALUES (LAST_INSERT_ID(), %s, %s, %s);"
        number = NumberGenerator.get_random_number("profile", "profile_table", "`number`")
        self.cursor.execute(
            query_insert_profile_table,
            (number, data['user_id'],
             person_id,
             data['is_main'],
             data['visibility_id'],
             data['is_approved'],
             data['profile_type_id'],
             data['preferred_lang_code'],
             data['experience_years_min'],
             data['main_phone_id'],
             data['rip'],
             data['gender_id'],
             data['stars'],
             data['last_dialog_workflow_state_id']))
        profile_id = self.cursor.lastrowid()
        self.cursor.execute(query_insert_profile_ml_table,
                            (data['lang_code'],
                             data['profile_name'],
                             data['name_approved']))
        self.connector.commit()
        logger.end(object={'profile_id': profile_id})
        return profile_id

    '''
    profile_id: int,
    data: Dict[str, any] = {
        'profile_name': profile_name,
        'name_approved': name_approved,
        'lang_code': lang_code,
        'user_id': user_id,                             #Optional
        'is_main': is_main,                             #Optional
        'visibility_id': visibility_id,
        'is_approved': is_approved,
        'profile_type_id': profile_type_id, #Optional
        'preferred_lang_code': preferred_lang_code,     #Optional
        'experience_years_min': experience_years_min,   #Optional
        'main_phone_id': main_phone_id,                 #Optional
        'rip': rip,                                     #Optional
        'gender_id': gender_id,                         #Optional
        'stars': stars,
        'last_dialog_workflow_state_id': last_dialog_workflow_state_id
    }
    person_id: int                                      #Optional
    '''

    def update(self, profile_id: int, data: Dict[str, any]):
        logger.start(object={'profile_id': profile_id, 'data': data})
        query_update_profile_table: str = None
        query_update_profile_table = "UPDATE profile_table SET person_id = %s, user_id = %s, is_main = %s," \
            " visibility_id = %s, is_approved = %s, profile_type_id = %s, preferred_lang_code = %s," \
            " experience_years_min = %s, main_phone_id = %s, rip = %s, gender_id = %s, stars = %s," \
            " last_dialog_workflow_state_id = %s WHERE profile_id = %s;"
        query_update_profile_ml_table = "UPDATE profile_ml_table SET lang_code = %s, `name` = %s, name_approved = %s WHERE profile_id = %s"
        data_to_update = (
            data['person_id'],
            data['user_id'],
            data['is_main'],
            data['visibility_id'],
            data['is_approved'],
            data['profile_type_id'],
            data['preferred_lang_code'],
            data['experience_years_min'],
            data['main_phone_id'],
            data['rip'],
            data['gender_id'],
            data['stars'],
            data['last_dialog_workflow_state_id'],
            profile_id)
        self.cursor.execute(
            query_update_profile_table,
            (data_to_update))
        self.cursor.execute(
            query_update_profile_ml_table,
            (data['lang_code'],
             data['profile_name'],
             data['name_approved'],
             profile_id))

        self.connector.commit()
        logger.end()

    def read_profile(self, profile_id: int) -> Dict[str, any]:
        logger.start(object={'profile_id': profile_id})

        query_get_profile_view = "SELECT user_id, person_id, is_main," \
            " visibility_id, is_approved, profile_type_id, preferred_lang_code," \
            " experience_years_min, main_phone_id, rip, gender_id, stars," \
            " last_dialog_workflow_state_id FROM profile_view WHERE profile_id = %s"
        query_get_profile_ml_view = "SELECT profile_ml_id, lang_code, `name`, name_approved FROM profile_ml_view WHERE profile_id = %s"
        self.cursor.execute(query_get_profile_view, (profile_id,))
        read_profile_view = self.cursor.fetchone()
        self.cursor.execute(query_get_profile_ml_view, (profile_id,))
        read_profile_ml_view = self.cursor.fetchone()
        if read_profile_view is None or read_profile_ml_view is None:
            return None
        user_id, person_id, is_main, visibility_id, is_approved, profile_type_id, preferred_lang_code, experience_years_min, main_phone_id, rip, gender_id, stars, last_dialog_workflow_state_id = read_profile_view
        profile_ml_id, lang_code, name, name_approved = read_profile_ml_view
        read_result = {
            'user_id': user_id, 'person_id': person_id, 'is_main': is_main, 'visibility_id': visibility_id,
            'is_approved': is_approved, 'profile_type_id': profile_type_id, 'preferred_lang_code': preferred_lang_code,
            'experience_years_min': experience_years_min, 'main_phone_id': main_phone_id, 'rip': rip,
            'gender_id': gender_id, 'stars': stars, 'last_dialog_workflow_state_id': last_dialog_workflow_state_id,
            'profile_ml_id': profile_ml_id, 'lang_code': lang_code, 'name': name, 'name_approved': name_approved}
        logger.end(object={'read_result': read_result})
        return read_result

    def delete_by_profile_id(self, profile_id: int):
        logger.start(object={'profile_id': profile_id})

        query_update = "UPDATE profile_table SET end_timestamp = NOW() WHERE profile_id = %s"
        self.cursor.execute(query_update, (profile_id, ))

        self.connector.commit()
        logger.end()
