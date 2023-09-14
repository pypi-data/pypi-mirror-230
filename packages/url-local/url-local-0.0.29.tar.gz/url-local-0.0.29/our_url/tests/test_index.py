import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
from src.index import *
import pytest

def test_user_registration_endpointUrl_without_parameter():
    url = UrlCirclez.endpoint_url(BrandName.CIRCLEZ.value, EnvironmentName.DVLP1.value, ComponentName.USER_REGISTRATION.value, EntityName.USER_REGISTRATION.value, 1, ActionName.CREATE_USER.value)

    assert url == 'https://lczo7l194b.execute-api.us-east-1.amazonaws.com/dvlp1/api/v1/user-registration/createUser'

def test_endpointUrl_without_parameters():
    url = UrlCirclez.endpoint_url(BrandName.CIRCLEZ.value, EnvironmentName.DVLP1.value, ComponentName.GROUP.value, EntityName.GROUP.value, 1, ActionName.GET_ALL_GROUPS.value)

    assert url == 'https://t91y4nxsye.execute-api.us-east-1.amazonaws.com/dvlp1/api/v1/group/getAllGroups'

def test_group_ndpointUrl_with_many_parameter():
    url = UrlCirclez.endpoint_url(BrandName.CIRCLEZ.value, EnvironmentName.DVLP1.value, ComponentName.GROUP.value, EntityName.GROUP.value, 1, ActionName.GET_ALL_GROUPS.value, path_parameters={'id': 1, 'lang_code': 'en'})

    assert url == 'https://t91y4nxsye.execute-api.us-east-1.amazonaws.com/dvlp1/api/v1/group/getAllGroups/1/en'


def test_group_endpointUrl_with_query_path_parameter_and_query_parameter():
    url = UrlCirclez.endpoint_url(BrandName.CIRCLEZ.value, EnvironmentName.DVLP1.value, ComponentName.GROUP.value, EntityName.GROUP.value, 1, ActionName.GET_ALL_GROUPS.value, path_parameters={"lang_code": 'en' }, query_parameters={ "name": 'spo', 'other': 'other' })

    
    assert url == "https://t91y4nxsye.execute-api.us-east-1.amazonaws.com/dvlp1/api/v1/group/getAllGroups/en?name=spo&other=other"

def test_auth_endpointUrl_without_parameters():
    url = UrlCirclez.endpoint_url(BrandName.CIRCLEZ.value, EnvironmentName.DVLP1.value, ComponentName.AUTHENTICATION.value, EntityName.AUTH_LOGIN.value, 1, ActionName.LOGIN.value)

    assert url == "https://i4wp5o2381.execute-api.us-east-1.amazonaws.com/dvlp1/api/v1/auth/login"

def test_auth_endpointUrl_without_parameters_gender_detection():
    url = UrlCirclez.endpoint_url(BrandName.CIRCLEZ.value, EnvironmentName.PLAY1.value, ComponentName.GENDER_DETECTION.value, EntityName.GENDER_DETECTION.value, 1, ActionName.ANALYZE_FACIAL_IMAGE.value)
    assert url == "https://353sstqmj5.execute-api.us-east-1.amazonaws.com/play1/api/v1/gender-detection/analyzeFacialImage"


def test_auth_endpointUrl_without_strange_brand_name():
    with pytest.raises(ValueError) as excinfo:
        url = UrlCirclez.endpoint_url("Strang Brand Name", EnvironmentName.PLAY1.value, ComponentName.GENDER_DETECTION.value, EntityName.GENDER_DETECTION.value, 1, ActionName.ANALYZE_FACIAL_IMAGE.value)
    assert str(excinfo.value) == "Invalid BRAND_NAME \"Strang Brand Name\""

def test_auth_endpointUrl_without_strange_circlez_with_strange_environment_name():
    with pytest.raises(ValueError) as excinfo:
        url = UrlCirclez.endpoint_url(BrandName.CIRCLEZ.value, "Stange environment in Circlez", ComponentName.GENDER_DETECTION.value, EntityName.GENDER_DETECTION.value, 1, ActionName.ANALYZE_FACIAL_IMAGE.value)
    assert str(excinfo.value) == "Invalid ENVIRONMENT_NAME \"Stange environment in Circlez\" in BRAND_NAME=Circlez"

def test_create_group_profile_without_parameters():
    url = UrlCirclez.endpoint_url(BrandName.CIRCLEZ.value, EnvironmentName.PLAY1.value, ComponentName.GROUP_PROFILE.value, EntityName.GROUP_PROFILE.value, 1, ActionName.CREATE_GROUP_PROFILE.value)
    assert url == "https://wh1toflnza.execute-api.us-east-1.amazonaws.com/play1/api/v1/group-profile/createGroupProfile"

def test_get_group_profile_without_parameters():
    url = UrlCirclez.endpoint_url(BrandName.CIRCLEZ.value, EnvironmentName.PLAY1.value, ComponentName.GROUP_PROFILE.value, EntityName.GROUP_PROFILE.value, 1, ActionName.GET_GROUP_PROFILE.value)
    assert url == "https://wh1toflnza.execute-api.us-east-1.amazonaws.com/play1/api/v1/group-profile/getGroupProfileByGroupIdProfileId"

def test_delete_group_profile_without_parameters():
    url = UrlCirclez.endpoint_url(BrandName.CIRCLEZ.value, EnvironmentName.PLAY1.value, ComponentName.GROUP_PROFILE.value, EntityName.GROUP_PROFILE.value, 1, ActionName.DELETE_GROUP_PROFILE.value)
    assert url == "https://wh1toflnza.execute-api.us-east-1.amazonaws.com/play1/api/v1/group-profile/deleteGroupProfile"

test_user_registration_endpointUrl_without_parameter()