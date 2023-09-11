from enum import Enum


# TODO: We should order them by alphabet of the Entity

class ActionName(Enum):
    
    # Authentication
    LOGIN = "login"
    VALIDATE_JWT = 'validateJwt'

    # Event
    GET_EVENT_BY_ID = "getEventById"
    CREATE_EVENT = "createEvent"
    UPDATE_EVENT_BY_ID = "updateEventById"
    DELETE_EVENT_BY_ID = "deleteEventById"

    # Gender-detection
    ANALYZE_FACIAL_IMAGE = "analyzeFacialImage"

    # Group
    GET_ALL_GROUPS = "getAllGroups"
    GET_GROUP_BY_NAME = "getGroupByName"
    GET_GROUP_BY_ID = "getGroupById"

    # Logger
    ADD_LOG = "add"

    # Timeline
    TIMELINE = "timeline"

    # User
    CREATE_USER = "createUser"
    UPDATE_USER = "updateUser"

    # Group-profile
    CREATE_GROUP_PROFILE = "createGroupProfile"
    DELETE_GROUP_PROFILE = "deleteGroupProfile"
    GET_GROUP_PROFILE = "getGroupProfileByGroupIdProfileId"

    

    

    
    
    