# TODO: This is an example file which you should delete after impenting
import requests
from our_url.src.index import UrlCirclez
import os, sys
import json
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from our_url.src.component_name_enum import ComponentName
from our_url.src.entity_name_enum import EntityName
from our_url.src.action_name_enum import ActionName
from dotenv import load_dotenv
load_dotenv()


GROUP_PROFILE_COMPONENT_ID = 211
GROUP_PROFILE_COMPONENT_NAME="Group Profile Remote Python"
COMPONENT_CATEGORY=LoggerComponentEnum.ComponentCategory.Code.value
COMPONENT_TYPE=LoggerComponentEnum.ComponentType.Remote.value
DEVELOPER_EMAIL="yarden.d@circ.zone"

obj={
    'component_id':GROUP_PROFILE_COMPONENT_ID,
    'component_name':GROUP_PROFILE_COMPONENT_NAME,
    'component_category':COMPONENT_CATEGORY,
    'component_type':COMPONENT_TYPE,
    "developer_email":DEVELOPER_EMAIL
}

BRAND_NAME = os.getenv("BRAND_NAME")
ENVIRONMENT_NAME = os.getenv("ENVIRONMENT_NAME")
GROUP_PROFILE_API_VERSION = 1

class GroupProfile:

    def __init__(self):
        self.url_circlez = UrlCirclez()
        self.logger = Logger.create_logger(object=obj)
        self.brand_name = BRAND_NAME
        self.env_name = ENVIRONMENT_NAME
        


    def create_group_profile(self, group_id: str, relationship_type_id: str):
        self.logger.start("Start create group-rofile-remote")
        try:
            url = self.url_circlez.endpoint_url(
                brand_name = self.brand_name,
                environment_name = self.env_name,
                component = ComponentName.GROUP_PROFILE.value,
                entity = EntityName.GROUP_PROFILE.value,
                version = GROUP_PROFILE_API_VERSION,
                action = ActionName.CREATE_GROUP_PROFILE.value, # "createGroupProfile",
            )
            self.logger.info("Endpoint group profile - createGroupProfile action: " + url)
        
            payload = {
                'groupId': group_id,
                'profileId': str(self.logger.userContext.get_real_profile_id()),
                'relationshipTypeId': relationship_type_id
            }

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.logger.userContext.get_jwt_token()}',
            }

            
            response = requests.post(url, json=payload, headers=headers)
            self.logger.end(f"End create group-profile-remote, response: {str(response)}")
            return response
        
        except requests.ConnectionError as e:
            self.logger.exception("Network problem (e.g. failed to connect)", e)
        except requests.Timeout as e:
            self.logger.exception("Request timed out", e)
        except requests.RequestException as e:
            self.logger.exception(f"General error: {str(e)}", e)
        except Exception as e:
            self.logger.exception(f"An unexpected error occurred: {str(e)}", e)
        
        self.logger.end(f"End create group-profile-remote")



    def get_group_profile(self, group_id: str, relationship_type_id: str):
        self.logger.start("Start get group-profile-remote")
        try:
            url = self.url_circlez.endpoint_url(
                brand_name = self.brand_name,
                environment_name = self.env_name,
                component = ComponentName.GROUP_PROFILE.value,
                entity = EntityName.GROUP_PROFILE.value,
                version = GROUP_PROFILE_API_VERSION,
                action = ActionName.GET_GROUP_PROFILE.value, # "getGroupProfileByGroupIdProfileId",
                query_parameters={
                    'groupId': group_id,
                    'profileId': str(self.logger.userContext.get_real_profile_id()),
                }
            )
            self.logger.info("Endpoint group profile - getGroupProfileByGroupIdProfileId action: " + url)

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.logger.userContext.get_jwt_token()}',
            }

            response = requests.get(url, headers=headers)
            self.logger.end(f"End get group-profile-remote, response: {str(response)}")
            return response

        except requests.ConnectionError as e:
            self.logger.exception("Network problem (e.g. failed to connect)", e)
        except requests.Timeout as e:
            self.logger.exception("Request timed out", e)
        except requests.RequestException as e:
            self.logger.exception(f"General error: {str(e)}", e)
        except Exception as e:
            self.logger.exception(f"An unexpected error occurred: {str(e)}", e)

        self.logger.end(f"End get group-profile-remote")



    def delete_group_profile(self, group_id: str, relationship_type_id: str):
        self.logger.start("Start delete group-profile-remote")
        try:
            url = self.url_circlez.endpoint_url(
                brand_name = self.brand_name,
                environment_name = self.env_name,
                component = ComponentName.GROUP_PROFILE.value,
                entity = EntityName.GROUP_PROFILE.value,
                version = GROUP_PROFILE_API_VERSION,
                action = ActionName.DELETE_GROUP_PROFILE.value, # "deleteGroupProfile",
            )

            self.logger.info("Endpoint group profile - deleteGroupProfile action: " + url)

            payload = {
                'groupId': group_id,
                'profileId': str(self.logger.userContext.get_real_profile_id()),
                'relationshipTypeId': relationship_type_id
            }

            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.logger.userContext.get_jwt_token()}',
            }

            response = requests.put(url, json=payload, headers=headers)
            self.logger.end(f"End delete group-profile-remote, response: {str(response)}")
            return response
        
        except requests.ConnectionError as e:
            self.logger.exception("Network problem (e.g. failed to connect)", e)
        except requests.Timeout as e:
            self.logger.exception("Request timed out", e)
        except requests.RequestException as e:
            self.logger.exception(f"General error: {str(e)}", e)
        except Exception as e:
            self.logger.exception(f"An unexpected error occurred: {str(e)}", e)

        self.logger.end(f"End delete group-profile-remote")
            