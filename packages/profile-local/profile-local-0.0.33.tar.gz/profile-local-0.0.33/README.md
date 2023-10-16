# Installation and upgrade
To install this package run "pip install profile-local".
To upgrade this package run "pip install --upgrade profile-local".

# Import 
from profile_local.generic_profile_insert import generic_profile_insert

# Use example
data =  {
            'location': LOCATION_DATA,
            'profile': PROFILE_DATA,
            'storage': STORAGE_DATA,
            'reaction': REACTION_DATA,
            'operational_hours': OPERATIONAL_HOURS
}

Where LOCATION_DATA, PROFILE_DATA, STORAGE_DATA, REACTION_DATA, OPERATIONAL_HOURS are dictionaries with the relevant data for the table
i.e. for profile_table:
PROFILE_DATA = {
    'profile_name': NAME,
    'name_approved': NAME_APPROVED,
    'lang_code': LANG_CODE,
    'user_id': USER_ID,     # Optional
    'is_main': IS_MAIN,     # Optional
    'visibility_id': VISIBILITY_ID,
    'is_approved': IS_APPROVED,
    'profile_type_id': PROFILE_TYPE_ID,     # Optional
    'preferred_lang_code': PREFERRED_LANG_CODE,     # Optional
    'experience_years_min': EXPERIENCE_YEARS_MIN,       # Optional
    'main_phone_id': MAIN_PHONE_ID,     # Optional
    'rip': RIP,     # Optional
    'gender_id': GENDER_ID,     # Optional
    'stars': STARS,
    'last_dialog_workflow_state_id': LAST_DIALOG_WORKFLOW_STATE_ID
}

Then call json.dumps:
data_json=json.dumps(data)

Now we can call the generic_profile_insert function:
profile_id = generic_profile_insert(data_json)

If the function inserted a profile successfully it returns the profile_id of the inserted profile.
The function doesn't have to always insert a profile, for example you can use it to insert only a location with
data =  {
            'location': LOCATION_DATA,
}

and then the returned profile_id will be 'None'.