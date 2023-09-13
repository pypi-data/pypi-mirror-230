# TODO: This is an example file which you should delete after impenting
import requests
from our_url.src.index import UrlCirclez
import os, sys
import json
from logger_local.Logger import Logger
from logger_local.LoggerComponentEnum import LoggerComponentEnum
from our_url.src.brand_name_enum import BrandName
from our_url.src.component_name_enum import ComponentName
from our_url.src.entity_name_enum import EntityName
from our_url.src.action_name_enum import ActionName
from dotenv import load_dotenv
from user_context_remote.user_context import UserContext
load_dotenv()


GROUP_PROFILE_COMPONENT_ID = 211
GROUP_PROFILE_COMPONENT_NAME="group profile remote"
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


class GroupProfile:

    def __init__(self, env_name: str):
        self.url_circlez = UrlCirclez()
        self.logger = Logger.create_logger(object=obj)
        self.brand_name = BrandName.CIRCLEZ.value
        self.env_name = env_name
        self.component = ComponentName.GROUP_PROFILE.value
        self.entity = EntityName.GROUP_PROFILE.value
        


    def create_group_profile(self, group_id: str, relationship_type_id: str):
        self.logger.start("Start create group-rofile-remote")
        try:
            url = self.url_circlez.endpoint_url(
                brand_name = self.brand_name,
                environment_name = self.env_name,
                component = self.component,
                entity = self.entity,
                version = 1,
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
            self.logger.end("End create group-profile-remote")
            return response
        
        except requests.ConnectionError:
            self.logger.exception("Network problem (e.g. failed to connect)")
        except requests.Timeout:
            self.logger.exception("Request timed out")
        except requests.RequestException as e:
            self.logger.exception(f"General error: {str(e)}")
        except Exception as e:
            self.logger.exception(f"An unexpected error occurred: {str(e)}")



    def get_group_profile(self, group_id: str, relationship_type_id: str):
        self.logger.start("Start get group-profile-remote")
        try:
            url = self.url_circlez.endpoint_url(
                brand_name = self.brand_name,
                environment_name = self.env_name,
                component = self.component,
                entity = self.entity,
                version = 1,
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
            self.logger.end("End get group-profile-remote")
            return response

        except requests.ConnectionError:
            self.logger.exception("Network problem (e.g. failed to connect)")
        except requests.Timeout:
            self.logger.exception("Request timed out")
        except requests.RequestException as e:
            self.logger.exception(f"General error: {str(e)}")
        except Exception as e:
            self.logger.exception(f"An unexpected error occurred: {str(e)}")



    def delete_group_profile(self, group_id: str, relationship_type_id: str):
        self.logger.start("Start delete group-profile-remote")
        try:
            url = self.url_circlez.endpoint_url(
                brand_name = self.brand_name,
                environment_name = self.env_name,
                component = self.component,
                entity = self.entity,
                version = 1,
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
            self.logger.end("End delete group-profile-remote")
            return response
        
        except requests.ConnectionError:
            self.logger.exception("Network problem (e.g. failed to connect)")
        except requests.Timeout:
            self.logger.exception("Request timed out")
        except requests.RequestException as e:
            self.logger.exception(f"General error: {str(e)}")
        except Exception as e:
            self.logger.exception(f"An unexpected error occurred: {str(e)}")
            