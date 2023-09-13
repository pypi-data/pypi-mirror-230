import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')
import pytest
from src.group_profile import GroupProfile, UrlCirclez, BrandName, ComponentName, EntityName, ActionName
from logger_local import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from dotenv import load_dotenv
load_dotenv()

GROUP_PROFILE_URL = "https://wh1toflnza.execute-api.us-east-1.amazonaws.com/play1/api/v1/group-profile/"

TEST_ENV_NAME = 'play1'
TEST_GROUP_ID = "1"
TEST_RELATIONSHIP_TYPE_ID = "1"

TEST_FAIL_GROUP_ID = "20"
TEST_FAIL_RELATIONSHIP_TYPE_ID = "44"



@pytest.fixture
def group_profile():
    GP = GroupProfile(env_name=TEST_ENV_NAME)
    yield GP


def test_create_group_profile(group_profile: GroupProfile):
    response = group_profile.create_group_profile(TEST_GROUP_ID, TEST_RELATIONSHIP_TYPE_ID)
    group_profile.logger.info("Response: " + response.text + "\n")
    assert response.status_code == 201
    content = response.json()
    assert 'success' in content


def test_fail_create_group_profile(group_profile: GroupProfile):
    '''
        Trying to create already-exist item.
    '''
    response = group_profile.create_group_profile(TEST_GROUP_ID, TEST_RELATIONSHIP_TYPE_ID)
    group_profile.logger.info("Response: " + response.text + "\n")
    assert response.status_code == 400


def test_get_group_profile(group_profile: GroupProfile):
    response = group_profile.get_group_profile(TEST_GROUP_ID, TEST_RELATIONSHIP_TYPE_ID)
    group_profile.logger.info("Response: " + response.text + "\n")
    assert response.status_code == 200
    content = response.json()
    assert 'success' in content


def test_delete_group_profile(group_profile: GroupProfile):
    response = group_profile.delete_group_profile(TEST_GROUP_ID, TEST_RELATIONSHIP_TYPE_ID)
    group_profile.logger.info("Response: " + response.text + "\n")
    assert response.status_code == 200
    content = response.json()
    assert 'success' in content


# TEST FAILURES
def test_fail_get_group_profile(group_profile: GroupProfile):
    '''
        Trying to get non-exist item.
    '''
    response = group_profile.get_group_profile(TEST_GROUP_ID, TEST_RELATIONSHIP_TYPE_ID)
    group_profile.logger.info("Response: " + response.text + "\n")
    assert response.status_code == 404


def test_fail_delete_group_profile(group_profile: GroupProfile):
    '''
        Trying to delete non-exist item.
    '''
    response = group_profile.delete_group_profile(TEST_GROUP_ID, TEST_RELATIONSHIP_TYPE_ID)
    group_profile.logger.info("Response: " + response.text + "\n")
    assert response.status_code == 400
