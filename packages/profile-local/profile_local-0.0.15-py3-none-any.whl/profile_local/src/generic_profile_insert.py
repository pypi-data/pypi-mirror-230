import json
from typing import Dict
from location_local.src.location_local import LocationLocal
from gender_local.src.gender import Gender
from reaction_local.src.reaction import Reaction
from profile_reaction_local.src.profile_reaction import ProfileReactions
from operational_hours_local.src.operational_hours import OperationalHours
from circles_local_aws_s3_storage_python.CirclesStorage import circles_storage
import circles_local_aws_s3_storage_python.constants  as storage_constants
from dotenv import load_dotenv

try:
    # Works when running the tests from this package
    from constants import *
    from profiles_local import ProfilesLocal
except Exception as e:
    # Works when importing this module from another package
    from profile_local.src.constants import *
    from profile_local.src.profiles_local import ProfilesLocal
load_dotenv()
from user_context_remote.user_context import UserContext # noqa: E402
from logger_local.Logger import Logger  # noqa: E402

logger = Logger.create_logger(object=OBJECT_TO_INSERT_CODE)

TEST_PERSON_ID = 50050341  # Temporary until Person class is ready

UserContext.login()
user_context = UserContext()

def generic_profile_insert(profle_json: str, lang_code: str = user_context.get_curent_lang_code()) -> int:
    GENERIC_INSERT_METHOD_NAME = "generic_insert"
    logger.start(GENERIC_INSERT_METHOD_NAME, object={"profle_json": profle_json})
    data: Dict[str, any] = None
    try:
        data = json.loads(profle_json)
    except json.JSONDecodeError as e:
        logger.exception(GENERIC_INSERT_METHOD_NAME, object={"exception": e})
        raise

    for entry in data["results"]:
        # Insert location to db
        if "location" in entry:
            location_entry: Dict[str, any] = entry["location"]
            location_data: Dict[str, any] = {
                "coordinate": {
                    "latitude": location_entry["coordinate"].get("latitude", None),
                    "longitude": location_entry["coordinate"].get("longitude", None),
                },
                "address_local_language": location_entry.get("address_local_language", None),
                "address_english": location_entry.get("address_english", None),
                "postal_code": location_entry.get("postal_code", None),
                "plus_code": location_entry.get("plus_code", None),
                "neighborhood": location_entry.get("neighborhood", None),
                "county": location_entry.get("county", None),
                "region": location_entry.get("region", None),
                "state": location_entry.get("state", None),
                "country": location_entry.get("country", None)
            }
            location_obj = LocationLocal()
            location_id = location_obj.insert_location(data=location_data, lang_code=lang_code, is_approved=True)

        # Insert person to db
        person_entry: Dict[str, any] = entry['person']
        gender_obj = Gender()
        gender_id = gender_obj.get_gender_id_by_title(person_entry.get('gender', None))
        person_data: Dict[str, any] = {
            'number': person_entry.get('number', None),
            'last_coordinate': person_entry.get('last_coordinate', None),

        }
        # Person class has errors
        person_id = TEST_PERSON_ID  # temporary for test
        '''
        person_id = PersonsLocal.insert(
            person_data.get('number', None),
            gender_id,
            person_data.get('last_coordinate', None),
            person_data.get('location_id', None))
        PersonsLocal.insert_person_ml(
            person_id,
            lang_code,
            person_data.get('first_name'),
            person_data.get('last_name'))
        '''
        # Insert profile to db
        profile_entry: Dict[str, any] = entry['profile']
        profile_data: Dict[str, any] = {
            'profile_name': profile_entry.get('profile_name'),
            'name_approved': profile_entry.get('name_approved'),
            'lang_code': profile_entry.get('lang_code'),
            'user_id': profile_entry.get('user_id'),
            'is_main': profile_entry.get('is_main', None),
            'visibility_id': profile_entry.get('visibility_id'),
            'is_approved': profile_entry.get('is_approved'),
            'profile_type_id': profile_entry.get('profile_type_id', None),
            'preferred_lang_code': profile_entry.get('preferred_lang_code', None),
            'experience_years_min': profile_entry.get('experience_years_min', None),
            'main_phone_id': profile_entry.get('main_phone_id', None),
            'rip': profile_entry.get('rip', None),
            'gender_id': profile_entry.get('gender_id', None),
            'stars': profile_entry.get('stars'),
            'last_dialog_workflow_state_id': profile_entry.get('last_dialog_workflow_state_id')
        }
        profiles_local_obj = ProfilesLocal()
        profile_id = profiles_local_obj.insert(person_id, profile_data)

        # Insert storage to db
        if "storage" in entry:
            storage_data = {
                "path": entry["storage"].get("path", None),
                "filename": entry["storage"].get("filename", None),
                "region": entry["storage"].get("region", None),
                "url": entry["storage"].get("url", None),
                "file_extension": entry["storage"].get("file_extension", None),
                "file_type": entry["storage"].get("file_type", None)
            }
            storage_obj = circles_storage()
            if storage_data["file_type"] == "Profile Image":
                storage_obj.save_image_in_storage_by_url(storage_data["url"], storage_data["filename"], profile_id, storage_constants.PROFILE_IMAGE), 

        # Insert reaction to db
        if "reaction" in entry:
            reaction_data = {
                "value": entry["reaction"].get("value", None),
                "image": entry["reaction"].get("image", None),
                "title": entry["reaction"].get("title", None),
                "description": entry["reaction"].get("description", None),
            }
            reaction_obj = Reaction()
            # TODO: remove profile_id parameter from reaction-local insert method
            reaction_id = reaction_obj.insert_reaction(reaction_data, profile_id, lang_code)
            # Insert profile-reactions to db
            ProfileReactions.insert(reaction_id, profile_id)

        # Insert operational hours to db
        if "operational_hours" in entry:
            operational_hours = OperationalHours.create_hours_array(entry["operational_hours"])
            operational_hours_obj = OperationalHours()
            operational_hours_obj.insert(profile_id, location_id, operational_hours)

    logger.end(GENERIC_INSERT_METHOD_NAME, object={"profile_id": profile_id})
    return profile_id
