from sys import platform
import requests
import pandas as pd
import os
import json
from urllib.parse import urlparse
from typing import List
import time
from datetime import datetime

# Async
import asyncio
from functools import wraps, partial
from utilities.async_utils import async_wrap




class Vv:
    def __init__(self):
        self.vaultURL = None
        self.vaultUserName = None
        self.vaultPassword = None
        self.vaultConnection = None
        self.sessionId = None
        self.vaultId: str = None
        self.vaultDNS: str = None
        self.APIheaders = None
        self.APIversionList = []
        self.LatestAPIversion = 'v21.3'
#         self.vaultObjects = None
#         self.all_references_metadata = None
#         self.all_references_names = None
#         self.vault_references_all = None



    def authenticate(self, 
                     vaultURL=None, 
                     vaultUserName=None, 
                     vaultPassword=None, 
                     sessionId=None,
                     vaultId=None,
                     if_return=False, *args, **kwargs):
        """
        TODO: Docs
        """

        self.LatestAPIversion = 'v21.3'
        
        self.vaultURL = self.vaultURL if vaultURL is None else vaultURL
        self.vaultUserName = self.vaultUserName if vaultUserName is None else vaultUserName
        self.vaultPassword = self.vaultPassword if vaultPassword is None else vaultPassword
        self.sessionId = self.sessionId if sessionId is None else sessionId
        self.vaultId = self.vaultId if vaultId is None else vaultId
        
        url_parse = urlparse(self.vaultURL)
        if len(url_parse.scheme) == 0:
            self.network_protocol = 'https'
            if len(url_parse.path) > 0:
                self.vaultDNS = url_parse.path
                self.vaultURL = self.network_protocol + '://' + url_parse.path

        if len(url_parse.scheme) > 0:
            self.network_protocol = url_parse.scheme
            if len(url_parse.netloc) > 0:
                self.vaultDNS = url_parse.netloc
                self.vaultURL = url_parse.scheme + '://' + url_parse.netloc

        if (self.vaultURL is None) or (len(self.vaultURL) == 0):
            raise Exception('vaultURL is required')
        
        if (self.vaultUserName and self.vaultPassword and self.vaultURL):
            pload = {'username': self.vaultUserName,'password': self.vaultPassword}
            self.vaultConnection = requests.post(f'{self.vaultURL}/api/{self.LatestAPIversion}/auth',data = pload)
            if self.vaultConnection.json()['responseStatus'] == 'FAILURE':
                exceptionMessage = ""
                exceptionMessage += "Error: " + self.vaultConnection.json()['responseMessage'] + "\n"
                exceptionMessage += self.vaultConnection.json()['errorType'] + "\n"
                for error in self.vaultConnection.json()['errors']:
                    exceptionMessage += error['type'] + ": " + error['message'] + "\n"
                raise Exception(exceptionMessage)
            
            self.sessionId = self.vaultConnection.json()['sessionId']
            self.vaultId = self.vaultConnection.json()['vaultId']
            
        self.APIheaders = {'Authorization': self.sessionId}
        self.APIversionList = []
        
        # Error checking whether the required parameters are passed in
        # The check happens here because this is where all the self assignments has completed
        if (not (self.vaultId and self.sessionId and self.vaultURL)) and (not (self.vaultUserName and self.vaultPassword and  self.vaultURL)):
            raise Exception("Please provide either vaultId, sessionId and vaultURL or vaultUserName, vaultPassword and vaultURL")
        
        for API in requests.get(self.vaultURL +'/api', headers=self.APIheaders).json()['values'].keys():
            self.APIversionList.append(float(API.replace("v", "")))
        self.APIversionList.sort()
        self.LatestAPIversion = "v" + str(self.APIversionList[-1])
        
        if if_return:
            return {'vaultURL':self.vaultURL, 
                    'vaultUserName':self.vaultUserName, 
                    'vaultPassword':self.vaultPassword, 
                    'vaultConnection':self.vaultConnection, 
                    'sessionId':self.sessionId, 
                    'APIheaders':self.APIheaders, 
                    'APIversionList':self.APIversionList, 
                    'LatestAPIversion':self.LatestAPIversion}


        
    def query(self, query):
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/query"
        
        self.LatestAPIversion = 'v21.3'
        
        h = {
        "X-VaultAPI-DescribeQuery":"true",
        "Content-Type":"application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        params = {
        "q":query
        }

        r = requests.get(url, headers=h, params=params).json()

        if r['responseStatus'] == 'FAILURE':
            raise Exception(r['errors'])
        else:
            r = pd.DataFrame(r['data'])
        
        return r
    
    def bulk_query(self, query):
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/query"
        
        self.LatestAPIversion = 'v21.3'
        
        h = {
        "X-VaultAPI-DescribeQuery":"true",
        "Content-Type":"application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        params = {
        "q":query
        }

        r = requests.get(url, headers=h, params=params).json()

        if r['responseStatus'] == 'FAILURE':
            raise Exception(r['errors'])
        
        output = pd.DataFrame(r['data'])
        
        try:
            next_page_url = r['responseDetails']['next_page'][:-4]
            more_pages = True
            page_count = 1000
            
            while more_pages:
                r = pd.DataFrame(requests.get(f"{self.vaultURL}"+ next_page_url+ str(page_count), headers=h).json()['data'])
                if len(r) == 0:
                    more_pages = False
                else:
                    output = pd.concat([output,r],ignore_index=True).copy()
                    page_count += 1000
        except:
            pass
        
        return output
    
    def object_field_metadata(self, object_api_name):
        
        self.LatestAPIversion = 'v21.3'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/vobjects/{object_api_name}"
        r = requests.get(url, headers = self.APIheaders).json()['object']['fields']
        return pd.DataFrame(r)
    
    def describe_objects(self):
        
        self.LatestAPIversion = 'v21.3'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/vobjects"
        r = requests.get(url, headers = self.APIheaders).json()['objects']
        return pd.DataFrame(r).sort_values(by='name')
    
    def retrieve_picklist_values(self, picklist_name):
        """
        Note: This is not the picklist field's API name, but the picklist (to which the picklist field looks up to) API name.
        For example, the picklist field "specialty_1__v", "specialty_2__v" and "specialty_3__v" all look up to the picklist "specialty__v".
        """
        
        self.LatestAPIversion = 'v21.3'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/picklists/{picklist_name}"
        r = requests.get(url, headers = self.APIheaders).json()
        if r['responseStatus'] == 'SUCCESS':
            if 'picklistValues' in r.keys():
                result = pd.DataFrame(r['picklistValues'])
                result['picklist_api_name'] = picklist_name
                return result
            else:
                print(f"Warning: Picklist {picklist_name} does not contain any values.")
                result = pd.DataFrame(columns=['name','label','picklist_api_name'])
                return result
        else:
            raise Exception(r['errors'][0]['type'] + ": " + r['errors'][0]['message'])
    
    
    ###############################################################
    # Async Functions
    ###############################################################
    
    async def async_bulk_retrieve_picklist_values(self, queries: List[str]) -> pd.DataFrame:
        """_summary_: This function is the async version of the retrieve_picklist_values function. It is used to retrieve multiple picklist values in parallel.

        Args:
            queries (List[str]): List of picklist API names

        Returns:
            _type_: pd.DataFrame
        """
        async_queries = async_wrap(self.retrieve_picklist_values)
        result_list = await asyncio.gather(*[async_queries(query) for query in queries])
        result_length = 0
        for result in result_list:
            result_length += len(result)
        
        if result_length > 0:
            result = pd.concat(result_list, ignore_index=True)
        else:
            result = pd.DataFrame(columns=['name','label','picklist_api_name'])
            
        return result
    

    ###############################################################
    # Authentication
    ###############################################################
    
    
    # Untested
    def authenticate_with_username_password(self, username, password, vaultDNS=None):
        """
        Authenticate your account using your Vault user name and password to obtain Vault Session ID.
        
        Documentation URL: https://developer.veevavault.com/api/23.2/#user-name-and-password
        
        :param username: Your Vault user name assigned by your administrator.
        :param password: Your Vault password associated with your assigned Vault user name.
        :param vaultDNS: The DNS of the Vault for which you want to generate a session. Optional.
        :return: JSON response containing session ID and related details.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/auth"
        
        data = {
            "username": username,
            "password": password
        }
        
        if vaultDNS:
            data["vaultDNS"] = vaultDNS
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        response = requests.post(url, data=data, headers=headers).json()
        
        if response.get('responseStatus') == "SUCCESS":
            self.sessionId = response.get('sessionId')
            self.vaultId = str(response.get('vaultId'))
        
        return response.json()

    # Untested
    def authenticate_with_oauth_openid_connect(self, oath_oidc_profile_id, vaultDNS=None, client_id=None, access_token=None):
        """
        Authenticate your account using OAuth 2.0 / Open ID Connect token to obtain a Vault Session ID.
        API Documentation: https://developer.veevavault.com/api/23.2/#oauth-2-0-openid-connect

        Parameters:
        oath_oidc_profile_id (str): The ID of your OAuth2.0 / Open ID Connect profile.
        vaultDNS (str, optional): The DNS of the Vault for which you want to generate a session. Defaults to None.
        client_id (str, optional): The ID of the client application at the Authorization server. Defaults to None.
        access_token (str): The access token for authorization.

        Returns:
        dict: Response from the API call
        """
        
        self.LatestAPIversion = 'v23.2'
        url = f"https://login.veevavault.com/auth/oauth/session/{oath_oidc_profile_id}"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json"
        }
        
        data = {}
        if vaultDNS:
            data["vaultDNS"] = vaultDNS
        if client_id:
            data["client_id"] = client_id
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            self.sessionId = response.json().get('sessionId')
            self.vaultId = str(response.json().get('vaultId'))
        
        return response.json()

    # Untested
    def retrieve_api_version(self):
        """
        Retrieve all supported versions of the Vault REST API.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-api-versions

        Returns:
        dict: Response from the API call containing the available API versions
        """
        
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/"
        
        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            self.APIversionList = list(response.json().get('values').keys())
        
        return response.json()

    # Untested
    def authentication_type_discovery(self, username, client_id=None):
        """
        Discover the authentication type of a user. This API allows applications to dynamically adjust the login requirements per user, 
        and support either username/password or OAuth2.0 / OpenID Connect authentication schemes.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-api-versions

        Args:
        username (str): The user’s Vault user name.
        client_id (str, optional): The user’s mapped Authorization Server client_id. Applies only to the SSO and OAuth / OpenID Connect Profiles auth_type.

        Returns:
        dict: Response from the API call containing information about the user's authentication type and profiles (if any).
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"https://login.veevavault.com/auth/discovery"
        params = {
            "username": username,
            "client_id": client_id
        }
        
        headers = {
            "Accept": "application/json",
            "X-VaultAPI-AuthIncludeMsal": "true"
        }
        
        response = requests.post(url, headers=headers, params=params)
        return response.json()

    # Untested
    def authentication_type_discovery(self, username, client_id=None):
        """
        Discover the authentication type of a user. This API allows applications to dynamically adjust the login requirements per user, 
        and support either username/password or OAuth2.0 / OpenID Connect authentication schemes.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-api-versions

        Args:
        username (str): The user’s Vault user name.
        client_id (str, optional): The user’s mapped Authorization Server client_id. Applies only to the SSO and OAuth / OpenID Connect Profiles auth_type.

        Returns:
        dict: Response from the API call containing information about the user's authentication type and profiles (if any).
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"https://login.veevavault.com/auth/discovery"
        params = {
            "username": username,
            "client_id": client_id
        }
        
        headers = {
            "Accept": "application/json",
            "X-VaultAPI-AuthIncludeMsal": "true"
        }
        
        response = requests.post(url, headers=headers, params=params)
        return response.json()
    
    # Untested
    def session_keep_alive(self):
        """
        Given an active sessionId, keep the session active by refreshing the session duration.
        A Vault session remains active as long as some activity (either through the UI or API) happens within the 
        maximum inactive session duration defined by your Vault Admin.
        API Documentation: https://developer.veevavault.com/api/23.2/#session-keep-alive
        
        Returns:
        dict: Response from the API call indicating the success status.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/keep-alive"
        
        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        
        response = requests.post(url, headers=headers)
        return response.json()

    # Untested
    def validate_session_user(self, exclude_vault_membership=False, exclude_app_licensing=False):
        """
        Given a valid session ID, this request returns information for the currently authenticated user.
        In case of an invalid session ID, it returns an INVALID_SESSION_ID error. This method acts similar to a whoami request.
        API Documentation: https://developer.veevavault.com/api/23.2/#validate-session-user
        
        Parameters:
        exclude_vault_membership (bool): If set to true, vault_membership fields are omitted from the response. Defaults to False.
        exclude_app_licensing (bool): If set to true, app_licensing fields are omitted from the response. Defaults to False.
        
        Returns:
        dict: Information of the currently authenticated user or an error message for invalid session ID.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users/me"
        
        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        
        params = {
            "exclude_vault_membership": exclude_vault_membership,
            "exclude_app_licensing": exclude_app_licensing
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()
    
    # Untested
    def salesforce_delegated_requests(self, sfdc_session_token, my_sfdc_domain, vault_endpoint, auth=None, ext_url=None, ext_ns=None):
        """
        Makes a request to the Vault API using Salesforce™ session token, following Salesforce™ Delegated Authentication procedure. 
        Learn more at: https://developer.veevavault.com/api/23.2/#salesforce-trade-delegated-requests
        
        Prerequisites:
        - A valid Vault user with a Security Policy enabled for Salesforce.com™ Delegated Authentication must exist.
        - The trusted 18-character Salesforce.com™ Org ID must be provided.
        - A user with a matching username in Salesforce.com™ Org ID must exist.
        
        Parameters:
        sfdc_session_token (str): Salesforce™ session token.
        my_sfdc_domain (str): Salesforce™ URL used to validate the session token.
        vault_endpoint (str): The Vault endpoint to make the request to.
        auth (str, optional): Salesforce™ session token, can be used as an alternative to setting in headers. Defaults to None.
        ext_url (str, optional): Salesforce™ URL for validation, alternative to setting in headers. Defaults to None.
        ext_ns (str, optional): Set to 'sfdc' to indicate Salesforce™ as the authorization provider, alternative to setting in headers. Defaults to None.
        
        Returns:
        Response: API Response object.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/{vault_endpoint}"
        
        headers = {
            "Authorization": sfdc_session_token,
            "X-Auth-Provider": "sfdc",
            "X-Auth-Host": my_sfdc_domain
        }
        
        params = {
            "auth": auth,
            "ext_url": ext_url,
            "ext_ns": ext_ns
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    # Untested
    def retrieve_delegations(self):
        """
        Retrieves the vaults where the currently authenticated user has delegate access. 
        This information can be used to initiate a delegated session. Learn more about the feature at: 
        https://developer.veevavault.com/api/23.2/#delegated-access
        
        Returns:
        dict: A dictionary containing details of the vaults the user has delegate access to, if any.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/delegation/vaults"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()

    ###############################################################
    # Domain Information
    ###############################################################

    def retrieve_domain_information(self, include_application=True):
        """
        Allows domain admins to retrieve a list of all Vaults present in their domain. 
        More details can be found at: 
        https://developer.veevavault.com/api/23.2/#retrieve-domain-information

        Args:
        include_application (bool): If set to true, the response includes information about 
        the Vault application type. Defaults to true.

        Returns:
        dict: A dictionary containing the response details with information about the domain and vaults.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/domain"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        params = {
            "include_application": include_application
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def retrieve_domains(self):
        """
        Allows non-domain admins to retrieve a list of all their domains, including the domain of the current Vault. This data can be used as a valid domain value when creating a sandbox Vault. More details can be found at:
        https://developer.veevavault.com/api/23.2/#retrieve-domains

        Returns:
        dict: A dictionary containing the response details with information about the domains.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/domains"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()

    #######################################################
    # Vault Query Language (VQL)
    #######################################################

    def submit_query(self, query, describe_query=True, record_properties=None):
        """
        Allows an application to invoke a query call where it passes in a Vault Query Language (VQL) statement to specify the object to query, the fields to retrieve, and any optional filters to narrow down the results. Further information can be found at:
        https://developer.veevavault.com/api/23.2/#submitting-a-query
        
        Args:
        query (str): A VQL statement specifying the object to query, the fields to retrieve, and any optional filters.
        describe_query (bool, optional): Set to true to include static field metadata in the response for the data record. Defaults to True.
        record_properties (str, optional): Optionally include the record properties object in the response. Possible values are "all", "hidden", "redacted", and "weblink". Defaults to None.

        Returns:
        dict: A dictionary containing the response from the query call including details about the fields retrieved and data records found.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/query"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "X-VaultAPI-DescribeQuery": str(describe_query).lower()
        }
        
        if record_properties:
            headers["X-VaultAPI-RecordProperties"] = record_properties
        
        data = {
            "q": query
        }
        
        response = requests.post(url, headers=headers, data=data)
        return response.json()



    #######################################################
    # Metadata Definition Language (MDL)
    #######################################################

    def execute_mdl_script(self, mdl_script):
        """
        Executes the given MDL script on a Vault. This synchronous endpoint allows various operations like CREATE, RECREATE, RENAME, ALTER, and DROP to be performed through MDL scripts. More details can be found at:
        https://developer.veevavault.com/api/23.2/#execute-mdl-script
        
        Args:
        mdl_script (str): The MDL script to be executed as a raw string. The script should start with one of the valid MDL commands (CREATE, RECREATE, RENAME, ALTER, DROP).
        
        Returns:
        dict: A dictionary containing the response details from the execution of the MDL script.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/mdl/execute"

        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(url, headers=headers, data=mdl_script)
        return response.json()

    def execute_mdl_script_async(self, mdl_script):
        """
        Executes the given MDL script on a Vault asynchronously. This endpoint is used particularly when operating on 10,000+ high volume object records and performing certain operations as mentioned in the documentation. The method returns details of the initiated job which can be used to track the execution status. Refer to the documentation for more details:
        https://developer.veevavault.com/api/23.2/#execute-mdl-script-asynchronously
        
        Args:
        mdl_script (str): The MDL script to be executed as a raw string. The script should start with one of the valid MDL commands (CREATE, RECREATE, RENAME, ALTER, DROP).
        
        Returns:
        dict: A dictionary containing the response details from the execution of the MDL script, including job_id and url to check the status of the execution.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/mdl/execute_async"

        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(url, headers=headers, data=mdl_script)
        return response.json()


    def retrieve_async_mdl_script_results(self, job_id):
        """
        Retrieves the results of an asynchronously executed MDL script. This method can be used to query Vault to determine the results of the MDL script execution request, including any errors. Refer to the documentation for more details:
        https://developer.veevavault.com/api/23.2/#retrieve-asynchronous-mdl-script-results
        
        Args:
        job_id (int): The job_id field value that was returned from the Execute MDL Script Asynchronously request.
        
        Returns:
        dict: A dictionary containing the response details from the executed MDL script, which includes details of script execution and statement execution.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/mdl/execute_async/{job_id}/results"

        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()

    def cancel_hvo_deployment(self, job_id):
        """
        Cancels a high volume object (HVO) deployment in the Vault. The deployment can only be cancelled if it has not begun execution. Refer to the documentation for more details:
        https://developer.veevavault.com/api/23.2/#cancel-hvo-deployment
        
        Args:
        job_id (int): The job ID obtained from the response of initiating an HVO deployment or executing an MDL script asynchronously.
        
        Returns:
        dict: A dictionary containing the response details of the cancel request.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/mdl/execute_async/{job_id}/cancel"

        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.post(url, headers=headers)
        return response.json()

    def retrieve_all_component_metadata(self):
        """
        Retrieves the metadata of all component types in the Vault. The method returns a list of dictionaries with details for each component type in the currently authenticated Vault. Refer to the documentation for more details:
        https://developer.veevavault.com/api/23.2/#retrieve-all-component-metadata
        
        Returns:
        list: A list of dictionaries containing metadata details for each component type.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/components"

        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_component_type_metadata(self, component_type):
        """
        Retrieves the metadata of a specific component type in the Vault. The method returns a dictionary containing detailed metadata for the specified component type. Refer to the documentation for more details:
        https://developer.veevavault.com/api/23.2/#retrieve-component-type-metadata
        
        Args:
        component_type (str): The name of the component type (e.g., "Picklist", "Docfield", "Doctype", etc.).
        
        Returns:
        dict: A dictionary containing detailed metadata for the specified component type.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/components/{component_type}"

        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_component_record_collection(self, component_type):
        """
        Retrieves all records for a specific component type in the Vault. This method returns a list of dictionaries containing details for each record of the specified component type. Refer to the documentation for more details:
        https://developer.veevavault.com/api/23.2/#component-record-collection
        
        Args:
        component_type (str): The name of the component type (e.g., "Picklist", "Docfield", "Doctype", etc.).
        
        Returns:
        list: A list of dictionaries containing details of each record for the specified component type.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/configuration/{component_type}"

        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()

    def retrieve_component_record(self, component_type_and_record_name):
        """
        Retrieves the metadata of a specific component record either in JSON or XML format. This method returns a dictionary containing detailed information about the specified component record. Refer to the documentation for more details:
        https://developer.veevavault.com/api/23.2/#retrieve-component-record-xml-json
        
        Args:
        component_type_and_record_name (str): The combination of the component type name and the record name to retrieve the metadata from. The format is {Componenttype}.{record_name}, for example, "Picklist.color__c".
        
        Returns:
        dict: A dictionary containing details of the specified component record.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/configuration/{component_type_and_record_name}"

        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()

    def retrieve_component_record_mdl(self, component_type_and_record_name):
        """
        Retrieves metadata of a specific component record as MDL format. This method returns the RECREATE MDL statement which contains metadata for the specified component record. Refer to the documentation for more details:
        https://developer.veevavault.com/api/23.2/#retrieve-component-record-mdl
        
        Args:
        component_type_and_record_name (str): The combination of the component type name and the record name to retrieve metadata from, in the format {Componenttype}.{record_name}, for example, "Picklist.color__c".

        Returns:
        str: A RECREATE MDL statement containing metadata for the specified component record.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/mdl/components/{component_type_and_record_name}"

        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.text

    def upload_content_file(self, file_path):
        """
        Uploads a content file to be referenced by a component in the Vault. The file gets stored in a generic files staging area where it remains until referenced by a component. For more details, refer to the documentation: 
        https://developer.veevavault.com/api/23.2/#upload-content-file
        
        Args:
        file_path (str): The local file path of the content file to be uploaded. For example, 'C:\\Quote.pdf'.
        
        Returns:
        dict: A dictionary containing details of the uploaded file including name, format, size, and sha1 checksum.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/mdl/files"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }
        
        with open(file_path, 'rb') as file:
            files = {'file': file}
            response = requests.post(url, headers=headers, files=files)
            return response.json()


    def retrieve_content_file(self, component_type_and_record_name):
        """
        Retrieves the content file of a specified component. For more information, refer to the API documentation: 
        https://developer.veevavault.com/api/23.2/#retrieve-content-file
        
        Args:
        component_type_and_record_name (str): The component type of the record followed by the name of the record from which to retrieve the content file. The format is {Componenttype}.{record_name}. For example, 'Formattedoutput.my_formatted_output__c'.
        
        Returns:
        dict: A dictionary containing details of the retrieved content file including name, original name, format, size, and sha1 checksum.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/mdl/components/{component_type_and_record_name}/files"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()



    #######################################################
    # Documents
    #######################################################

    def retrieve_all_document_fields(self):
        """
        Retrieves all standard and custom document fields and field properties. For more information, refer to the API documentation: 
        https://developer.veevavault.com/api/23.2/#retrieve-all-document-fields
        
        Returns:
        dict: A dictionary containing all standard and custom document fields and their properties.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/v23.2/metadata/objects/documents/properties"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()

    def retrieve_common_document_fields(self, doc_ids):
        """
        Retrieves all document fields and field properties which are common to (shared by) a specified set of documents. 
        This allows you to determine which document fields are eligible for bulk update.
        For more information, refer to the API documentation: 
        https://developer.veevavault.com/api/23.2/#retrieve-common-document-fields

        Parameters:
        doc_ids (str): A comma-separated list of document id field values.

        Returns:
        dict: A dictionary containing all fields shared by the specified documents.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/v23.2/metadata/objects/documents/properties/find_common"

        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        data = {
            "docIds": doc_ids
        }

        response = requests.post(url, headers=headers, data=data)
        return response.json()

    def retrieve_all_document_types(self):
        """
        Retrieves all document types present in the vault. These represent the top-level of the document type/subtype/classification hierarchy.
        For more details, visit the API documentation:
        https://developer.veevavault.com/api/23.2/#retrieve-all-document-types

        Returns:
        dict: A dictionary containing the details of all document types configured in the vault.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/v23.2/metadata/objects/documents/types"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_document_type(self, doc_type):
        """
        Retrieve all metadata from a specified document type, potentially including all of its subtypes.
        For more details, visit the API documentation:
        https://developer.veevavault.com/api/23.2/#retrieve-document-type

        Args:
        doc_type (str): The document type to retrieve metadata for.

        Returns:
        dict: A dictionary containing the metadata of the specified document type.
        """

        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/v23.2/metadata/objects/documents/types/{doc_type}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()



    def retrieve_document_subtype(self, doc_type, doc_subtype):
        """
        Retrieve all metadata from a document subtype, including all of its classifications (when available).
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-subtype

        :param doc_type: The document type, see Retrieve Document Types.
        :param doc_subtype: The document subtype, see Retrieve Document Type.
        :return: JSON response with metadata of the document subtype.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/documents/types/{doc_type}/subtypes/{doc_subtype}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_document_classification(self, doc_type, doc_subtype, classification):
        """
        Retrieve all metadata from a document classification.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-classification

        :param doc_type: The document type, see Retrieve Document Types.
        :param doc_subtype: The document subtype, see Retrieve Document Type.
        :param classification: The document classification, see Retrieve Document Subtype.
        :return: JSON response with metadata of the document classification.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/documents/types/{doc_type}/subtypes/{doc_subtype}/classifications/{classification}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_all_documents(self, named_filter=None, scope=None, versionscope=None, search=None, limit=None, sort=None, start=None):
        """
        Retrieve the latest version of documents and binders to which you have access.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-all-documents

        :param named_filter: Filters the results based on the named filter option ('My Documents', 'Favorites', 'Recent Documents', 'Cart').
        :param scope: Scope of the search ('contents' or 'all').
        :param versionscope: Scope of the versions to retrieve ('all' for all versions, None for latest version).
        :param search: Search keyword to filter documents based on searchable document fields.
        :param limit: Limit the number of documents to display (default is up to 200 documents per page).
        :param sort: Sort order for the documents (e.g., 'name__v DESC').
        :param start: The starting record number (default is 0).
        :return: JSON response with a list of documents and binders along with their fields and values.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        params = {
            "named_filter": named_filter,
            "scope": scope,
            "versionscope": versionscope,
            "search": search,
            "limit": limit,
            "sort": sort,
            "start": start
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()


    def retrieve_document(self, doc_id):
        """
        Retrieve all metadata from a document.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-document
        :param doc_id: The document id field value.
        :return: JSON response containing document metadata.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_document_versions(self, doc_id):
        """
        Retrieve all versions of a document.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-versions
        :param doc_id: The document id field value.
        :return: JSON response containing all available versions of the specified document.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_document_version(self, doc_id, major_version, minor_version):
        """
        Retrieve all fields and values configured on a document version.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-version
        :param doc_id: The document id field value.
        :param major_version: The document major version number field value.
        :param minor_version: The document minor version number field value.
        :return: JSON response containing all fields and values for the specified version of the document.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()


    def download_document_file(self, doc_id, lockDocument=False):
        """
        Download the latest version of the source file from the document.
        API Documentation: https://developer.veevavault.com/api/23.2/#download-document-file
        :param doc_id: The document id field value.
        :param lockDocument: Set to true to Check Out this document before retrieval. Default is False.
        :return: A file with the document content.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/file"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        params = {"lockDocument": lockDocument}
        
        response = requests.get(url, headers=headers, params=params)
        
        filename = re.findall('filename="(.+)"', response.headers.get('Content-Disposition'))[0]
        
        with open(filename, 'wb') as file:
            file.write(response.content)
        
        return filename

    def download_document_version_file(self, doc_id, major_version, minor_version):
        """
        Download the file of a specific document version.
        API Documentation: https://developer.veevavault.com/api/23.2/#download-document-version-file
        :param doc_id: The document id field value.
        :param major_version: The document major_version_number__v field value.
        :param minor_version: The document minor_version_number__v field value.
        :return: A file with the document content of the specified version.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/file"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        
        filename = re.findall('filename="(.+)"', response.headers.get('Content-Disposition'))[0]
        
        with open(filename, 'wb') as file:
            file.write(response.content)
        
        return filename


    #######################################################
    # Documents
    ## Create Documents
    #######################################################

    def create_single_document(self, file_path, name_v, type_v, lifecycle_v, subtype_v=None, classification_v=None, major_version_number_v=None, minor_version_number_v=None, external_id_v=None, product_v=None, options=None):
        """
        Create a single document in the Vault with various options.
        API Documentation: https://developer.veevavault.com/api/23.2/#create-single-document
        
        :param file_path: The filepath of the source document, if creating from an uploaded file. (optional)
        :param name_v: The name of the new document.
        :param type_v: The label of the document type to assign to the new document.
        :param lifecycle_v: The label of the document lifecycle to assign to the new document.
        :param subtype_v: The label of the document subtype, if applicable. (optional)
        :param classification_v: The label of the document classification, if applicable. (optional)
        :param major_version_number_v: The major version number to assign to the new document. (optional)
        :param minor_version_number_v: The minor version number to assign to the new document. (optional)
        :param external_id_v: The external id to assign to the new document. (optional)
        :param product_v: The product id to assign to the new document. (optional)
        :param options: A dictionary containing additional parameters for PromoMats or other types of documents. (optional)
        :return: A dictionary containing the response details.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }
        
        data = {
            "name__v": name_v,
            "type__v": type_v,
            "lifecycle__v": lifecycle_v
        }
        
        if subtype_v:
            data["subtype__v"] = subtype_v
        if classification_v:
            data["classification__v"] = classification_v
        if major_version_number_v:
            data["major_version_number__v"] = major_version_number_v
        if minor_version_number_v:
            data["minor_version_number__v"] = minor_version_number_v
        if external_id_v:
            data["external_id__v"] = external_id_v
        if product_v:
            data["product__v"] = product_v
        if options:
            data.update(options)
        
        files = {}
        if file_path:
            files['file'] = open(file_path, 'rb')
        
        response = requests.post(url, headers=headers, data=data, files=files)
        return response.json()


    def create_multiple_documents(self, csv_file_path, headers=None):
        """
        This method allows you to create multiple documents at once with a CSV input file. 
        The maximum CSV input file size is 1GB and the maximum batch size is 500.
        Note that this API does not support adding multi-value relationship fields by name.

        API documentation: https://developer.veevavault.com/api/23.2/#create-multiple-documents

        Args:
            csv_file_path (str): The path to the CSV file containing the document details.
            headers (dict, optional): Additional headers to include in the request.

        Returns:
            dict: The response from the API.

        Usage:
            >>> vv = Vv()
            >>> vv.create_multiple_documents("path/to/your/csvfile.csv")
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/batch"
        default_headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }

        if headers:
            default_headers.update(headers)

        with open(csv_file_path, 'rb') as file:
            response = requests.post(url, headers=default_headers, data=file)
        
        return response.json()



    #######################################################
    # Documents
    ## Update Documents
    #######################################################

    def update_single_document(self, doc_id, data, headers=None):
        """
        This method allows you to update editable field values on the latest version of a single document. 
        To update more than one document, it is best practice to use the bulk API.

        API documentation: https://developer.veevavault.com/api/23.2/#update-single-document

        Args:
            doc_id (int): The ID of the document to update.
            data (dict): A dictionary containing the field values to update.
            headers (dict, optional): Additional headers to include in the request.

        Returns:
            dict: The response from the API.

        Usage:
            >>> vv = Vv()
            >>> vv.update_single_document(534, {"language__v": "English", "product__v": 1357662840171, "audience__vs": "consumer__vs"})
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}"
        default_headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        if headers:
            default_headers.update(headers)

        response = requests.put(url, headers=default_headers, data=data)

        return response.json()


    def update_multiple_documents(self, data, headers=None, file_path=None):
        """
        This method allows you to bulk update editable field values on multiple documents. 
        You can only update the latest version of each document.
        
        The maximum CSV input file size is 1GB and the maximum batch size is 1,000.
        
        API documentation: https://developer.veevavault.com/api/23.2/#update-single-document

        Args:
            data (dict or str): A dictionary containing name-value pairs to be updated or the path to a CSV file with the updates.
            headers (dict, optional): Additional headers to include in the request.
            file_path (str, optional): The path to a CSV file containing updates (if data is not a dictionary).

        Returns:
            dict: The response from the API.

        Usage:
            >>> vv = Vv()
            >>> vv.update_multiple_documents({"docIds": "771,772,773", "archive__v": "true"}, file_path="path/to/file.csv")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/batch"
        
        default_headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv" if file_path else "application/x-www-form-urlencoded",
            "Accept": "text/csv"
        }

        if headers:
            default_headers.update(headers)

        if file_path:
            with open(file_path, 'rb') as f:
                response = requests.put(url, headers=default_headers, data=f)
        else:
            response = requests.put(url, headers=default_headers, data=data)

        return response.json()


    def reclassify_single_document(self, doc_id, type_v, lifecycle_v, reclassify=True, subtype_v=None, classification_v=None, document_number_v=None, status_v=None):
        """
        This method allows you to reclassify a single document, enabling the change of document type 
        or the assignment of a document type to an unclassified document.
        
        API documentation: https://developer.veevavault.com/api/23.2/#reclassify-single-document

        Args:
            doc_id (str): The ID of the document to reclassify.
            type_v (str): The name of the document type.
            lifecycle_v (str): The name of the document lifecycle.
            reclassify (bool): Set to true to reclassify the document. Defaults to true.
            subtype_v (str, optional): The name of the document subtype, if applicable.
            classification_v (str, optional): The name of the document classification, if applicable.
            document_number_v (str, optional): The document number for the reclassified document. Use with X-VaultAPI-MigrationMode header.
            status_v (str, optional): Specifies the lifecycle state for the reclassified document. Use with X-VaultAPI-MigrationMode header.

        Returns:
            dict: The response from the API.

        Usage:
            >>> vv = Vv()
            >>> vv.reclassify_single_document("775", "Promotional Piece", "Promotional Piece", subtype_v="Advertisement", classification_v="Web")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        data = {
            "type__v": type_v,
            "lifecycle__v": lifecycle_v,
            "reclassify": reclassify
        }

        if subtype_v:
            data["subtype__v"] = subtype_v
        if classification_v:
            data["classification__v"] = classification_v
        if document_number_v:
            data["document_number__v"] = document_number_v
            headers["X-VaultAPI-MigrationMode"] = "true"
        if status_v:
            data["status__v"] = status_v
            headers["X-VaultAPI-MigrationMode"] = "true"

        response = requests.put(url, headers=headers, data=data)

        return response.json()


    def reclassify_multiple_documents(self, csv_file_path):
        """
        This method allows you to reclassify multiple documents in bulk, enabling the change of document type 
        or the assignment of document types to unclassified documents. The details of the documents to be reclassified 
        should be specified in a CSV file.

        API documentation: https://developer.veevavault.com/api/23.2/#reclassify-multiple-documents

        Args:
            csv_file_path (str): The path to the CSV file containing the details of the documents to be reclassified.

        Returns:
            dict: The response from the API, including the status and IDs of the reclassified documents.

        Usage:
            >>> vv = Vv()
            >>> vv.reclassify_multiple_documents("C:\\Vault\\Documents\\reclassify_documents.csv")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/batch/actions/reclassify"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "text/csv"
        }

        with open(csv_file_path, 'rb') as file:
            response = requests.put(url, headers=headers, data=file)

        return response.text

    def update_document_version(self, doc_id, major_version, minor_version, data):
        """
        This method allows you to update editable field values on a specific version of a document in the Vault.

        API documentation: https://developer.veevavault.com/api/23.2/#update-document-version

        Args:
            doc_id (int): The ID of the document to be updated.
            major_version (int): The major version number of the document to be updated.
            minor_version (int): The minor version number of the document to be updated.
            data (dict): A dictionary containing the field values to be updated.

        Returns:
            dict: The response from the API, including the status and the ID of the updated document.

        Usage:
            >>> vv = Vv()
            >>> vv.update_document_version(534, 2, 0, {"language__v": "English", "product__v": "1357662840171", "audience__c": "consumer__c"})
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        response = requests.put(url, headers=headers, data=data)

        return response.json()


    def create_multiple_document_versions(self, file_path, id_param=None):
        """
        This method allows you to create or add document versions in bulk in the Vault.

        API documentation: https://developer.veevavault.com/api/23.2/#create-multiple-document-versions

        Args:
            file_path (str): The filepath of your source files which contains details for new versions to be created.
            id_param (str, optional): If you’re identifying documents in your input by a unique field, use this parameter to specify the field name.

        Returns:
            dict: The response from the API, including the status and details of the created document versions.

        Usage:
            >>> vv = Vv()
            >>> vv.create_multiple_document_versions("path/to/your/file.csv", id_param="external_id__v")
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/versions/batch"
        if id_param:
            url += f"?idParam={id_param}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "application/json",
            "X-VaultAPI-MigrationMode": "true"
        }

        with open(file_path, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)

        return response.json()

    def create_single_document_version(self, doc_id, create_draft, file_path=None, description=None, suppress_rendition=False):
        """
        Adds a new draft version of an existing document in the Vault. You can either use the existing source file or upload a new one.

        API documentation: https://developer.veevavault.com/api/23.2/#create-single-document-version

        Args:
            doc_id (int): The ID of the document to which a new draft version will be added.
            create_draft (str): Specify whether to create a draft from the latest content or uploaded content.
            file_path (str, optional): The filepath of the source document, required when createDraft is 'uploadedContent'.
            description (str, optional): Description for the new draft version. Maximum 1500 characters.
            suppress_rendition (bool, optional): Set to true to suppress automatic generation of the viewable rendition.

        Returns:
            dict: The response from the API, indicating the success or failure of the draft creation.

        Usage:
            >>> vv = Vv()
            >>> vv.create_single_document_version(534, "latestContent", description="Description for the new draft")
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}"
        if suppress_rendition:
            url += "?suppressRendition=true"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }

        data = {
            "createDraft": create_draft
        }
        if description:
            data["description__v"] = description

        if create_draft == "uploadedContent" and file_path:
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(url, headers=headers, data=data, files=files)
        else:
            response = requests.post(url, headers=headers, data=data)

        return response.json()



    #######################################################
    # Documents
    ## Delete Documents
    #######################################################

    def delete_single_document(self, document_id):
        """
        Deletes all versions of a specified document including all source files and viewable renditions.

        API documentation: https://developer.veevavault.com/api/23.2/#delete-single-document

        Args:
            document_id (int): The system-assigned ID of the document to delete.

        Returns:
            dict: The response from the API, indicating the success or failure of the deletion.

        Usage:
            >>> vv = Vv()
            >>> vv.delete_single_document(534)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{document_id}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.delete(url, headers=headers)

        return response.json()


    def delete_multiple_documents(self, input_file_path, id_param=None):
        """
        Deletes all versions of multiple documents including all source files and viewable renditions.

        API documentation: https://developer.veevavault.com/api/23.2/#delete-multiple-documents

        Args:
            input_file_path (str): The path to the CSV or JSON file containing the details of the documents to be deleted.
            id_param (str, optional): If identifying documents by a unique field, add this parameter to specify the field name.

        Returns:
            dict: The response from the API, indicating the success or failure of the deletion.

        Usage:
            >>> vv = Vv()
            >>> vv.delete_multiple_documents("C:\\Vault\\Documents\\delete_documents.csv", id_param="external_id__v")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/batch"
        if id_param:
            url += f"?idParam={id_param}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }

        with open(input_file_path, 'rb') as f:
            response = requests.delete(url, headers=headers, data=f)

        return response.json()


    def delete_single_document_version(self, doc_id, major_version, minor_version):
        """
        Deletes a specific version of a document, including the version’s source file and viewable rendition. Other versions of the document remain unchanged.

        API documentation: https://developer.veevavault.com/api/23.2/#delete-single-document-version

        Args:
            doc_id (int): The document ID field value.
            major_version (int): The document major version number field value.
            minor_version (int): The document minor version number field value.

        Returns:
            dict: The response from the API, indicating the success or failure of the deletion.

        Usage:
            >>> vv = Vv()
            >>> vv.delete_single_document_version(534, 0, 2)
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.delete(url, headers=headers)

        return response.json()


    def delete_multiple_document_versions(self, input_file_path, id_param=None):
        """
        Deletes specific versions of multiple documents, including the versions’ source files and viewable renditions.

        API documentation: https://developer.veevavault.com/api/23.2/#delete-multiple-document-versions

        Args:
            input_file_path (str): The path to the CSV or JSON file containing the details of the document versions to be deleted.
            id_param (str, optional): If identifying documents in the input by a unique field, add this parameter to specify the field name. Defaults to None.

        Returns:
            dict: The response from the API, indicating the success or failure of the deletion of each document version.

        Usage:
            >>> vv = Vv()
            >>> vv.delete_multiple_document_versions("C:\\Vault\\Documents\\delete_document_versions.csv", id_param="external_id__v")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/versions/batch"
        if id_param:
            url += f"?idParam={id_param}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }

        with open(input_file_path, 'rb') as f:
            response = requests.delete(url, headers=headers, data=f)

        return response.json()


    def retrieve_deleted_document_ids(self, start_date=None, end_date=None):
        """
        Retrieves the IDs of documents that were deleted within the past 30 days.

        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-deleted-document-ids

        Args:
            start_date (str, optional): Specify a date (no more than 30 days past) after which to look for deleted documents. 
                                        Dates must be in YYYY-MM-DDTHH:MM:SSZ format. Defaults to None.
            end_date (str, optional): Specify a date (no more than 30 days past) before which to look for deleted documents. 
                                    Dates must be in YYYY-MM-DDTHH:MM:SSZ format. Defaults to None.

        Returns:
            dict: The response from the API, indicating the details of deleted documents.

        Usage:
            >>> vv = Vv()
            >>> vv.retrieve_deleted_document_ids("2023-08-01T00:00:00Z", "2023-08-30T23:59:59Z")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/deletions/documents"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        params = {}
        if start_date:
            params['start_date'] = start_date
        if end_date:
            params['end_date'] = end_date
        
        response = requests.get(url, headers=headers, params=params)

        return response.json()


    #######################################################
    # Documents
    ## Document Locks
    #######################################################

    def retrieve_document_lock_metadata(self):
        """
        Retrieves the metadata of the lock attributes associated with documents.

        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-lock-metadata

        Returns:
            dict: The response from the API, containing metadata details of the lock attributes.

        Usage:
            >>> vv = Vv()
            >>> vv.retrieve_document_lock_metadata()
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/documents/lock"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)

        return response.json()


    def create_document_lock(self, doc_id):
        """
        Creates a lock on a specified document, preventing other users from locking or checking out the document. 
        The operation is similar to checking out a document, but without the file attached in the response for download.

        API documentation: https://developer.veevavault.com/api/23.2/#create-document-lock

        Args:
            doc_id (int): The ID of the document to lock.

        Returns:
            dict: The response from the API, generally indicating the success status of the lock operation.

        Usage:
            >>> vv = Vv()
            >>> vv.create_document_lock(534)
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/lock"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.post(url, headers=headers)

        return response.json()


    def retrieve_document_lock(self, doc_id):
        """
        Retrieves the lock status of a specified document. 
        If the document is locked, the response will include the user ID of the person who locked it and the date and time of the lock. 
        If the document is not locked, the lock fields will not be returned in the response.

        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-lock

        Args:
            doc_id (int): The ID of the document to retrieve the lock status for.

        Returns:
            dict: The response from the API containing the lock details or indicating that no lock is present.

        Usage:
            >>> vv = Vv()
            >>> vv.retrieve_document_lock(534)
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/lock"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)

        return response.json()


    def delete_document_lock(self, doc_id):
        """
        Deletes the lock on a specified document, allowing other users to lock or check out the document.
        
        API documentation: https://developer.veevavault.com/api/23.2/#delete-document-lock
        
        Args:
            doc_id (int): The ID of the document for which the lock is to be deleted.

        Returns:
            dict: The response from the API indicating the status of the delete operation.

        Usage:
            >>> vv = Vv()
            >>> vv.delete_document_lock(534)
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/lock"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.delete(url, headers=headers)

        return response.json()


    #######################################################
    # Documents
    ## Document Renditions
    #######################################################

    def retrieve_document_renditions(self, doc_id):
        """
        Retrieves the renditions of a specified document.
        
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-renditions
        
        Args:
            doc_id (int): The ID of the document for which the renditions are to be retrieved.

        Returns:
            dict: A dictionary containing the rendition types and URLs for the renditions of the specified document.

        Usage:
            >>> vv = Vv()
            >>> vv.retrieve_document_renditions(534)
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/renditions"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)

        return response.json()


    def retrieve_document_version_renditions(self, doc_id, major_version, minor_version):
        """
        Retrieves the renditions of a specified document version.
        
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-version-renditions
        
        Args:
            doc_id (int): The ID of the document for which the renditions are to be retrieved.
            major_version (int): The major version number of the document.
            minor_version (int): The minor version number of the document.

        Returns:
            dict: A dictionary containing the rendition types and URLs for the renditions of the specified document version.

        Usage:
            >>> vv = Vv()
            >>> vv.retrieve_document_version_renditions(534, 2, 0)
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/renditions"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)

        return response.json()


    def download_document_rendition_file(self, doc_id, rendition_type, steady_state=None, protected_rendition=None):
        """
        Downloads the rendition file from the latest version of a document.

        API documentation: https://developer.veevavault.com/api/23.2/#download-document-rendition-file

        Args:
            doc_id (int): The ID of the document for which the rendition file is to be downloaded.
            rendition_type (str): The type of the rendition file to download.
            steady_state (bool, optional): Set to true to download a rendition from the latest steady state version of the document. Defaults to None.
            protected_rendition (bool, optional): If your Vault is configured to use protected renditions, set to false to download the non-protected rendition. If omitted, defaults to true. Defaults to None.

        Returns:
            Response object: The HTTP Response object.

        Usage:
            >>> vv = Vv()
            >>> vv.download_document_rendition_file(534, 'viewable_rendition__v', steady_state=True, protected_rendition=False)
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/renditions/{rendition_type}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        params = {
            "steadyState": steady_state,
            "protectedRendition": protected_rendition
        }

        response = requests.get(url, headers=headers, params=params)

        return response.json()


    def download_document_version_rendition_file(self, doc_id, major_version, minor_version, rendition_type, protected_rendition=None):
        """
        Downloads a rendition for a specified version of a document.

        API documentation: https://developer.veevavault.com/api/23.2/#download-document-version-rendition-file

        Args:
            doc_id (int): The ID of the document for which the rendition file is to be downloaded.
            major_version (int): The major version number of the document.
            minor_version (int): The minor version number of the document.
            rendition_type (str): The type of the rendition file to download.
            protected_rendition (bool, optional): If your Vault is configured to use protected renditions, set to false to download the non-protected rendition. If omitted, defaults to true. Defaults to None.

        Returns:
            Response object: The HTTP Response object.

        Usage:
            >>> vv = Vv()
            >>> vv.download_document_version_rendition_file(534, 2, 0, 'viewable_rendition__v', protected_rendition=False)
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/renditions/{rendition_type}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        params = {
            "protectedRendition": protected_rendition
        }

        response = requests.get(url, headers=headers, params=params)

        return response.json()

    def add_multiple_document_renditions(self, file_path, idParam=None, largeSizeAsset=None):
        """
        Adds multiple document renditions in bulk. This function requires the renditions to be loaded to the file staging server first.

        API documentation: https://developer.veevavault.com/api/23.2/#add-multiple-document-renditions

        Args:
            file_path (str): The filepath of the CSV file which contains details of the renditions to be added. The CSV should be in UTF-8 encoding and comply with RFC 4180 format.
            idParam (str, optional): If you’re identifying documents in your input by a unique field, add this parameter. Defaults to None.
            largeSizeAsset (bool, optional): Set to true if adding renditions of the Large Size Asset type. Defaults to None.

        Returns:
            Response object: The HTTP Response object.

        Usage:
            >>> vv = Vv()
            >>> vv.add_multiple_document_renditions("path/to/your/file.csv", idParam="external_id__v", largeSizeAsset=True)
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/renditions/batch"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "application/json",
            "X-VaultAPI-MigrationMode": "true"
        }

        params = {
            "idParam": idParam,
            "largeSizeAsset": largeSizeAsset
        }

        with open(file_path, 'rb') as f:
            response = requests.post(url, headers=headers, params=params, data=f)

        return response.json()


    def add_single_document_rendition(self, doc_id, rendition_type, file_path):
        """
        Adds a single document rendition to the vault. If you need to add more than one document rendition, consider using the bulk API.

        API documentation: https://developer.veevavault.com/api/23.2/#add-single-document-rendition

        Args:
            doc_id (str): The document ID field value.
            rendition_type (str): The type of document rendition.
            file_path (str): The path to the file to be uploaded.

        Returns:
            Response object: The HTTP Response object.

        Usage:
            >>> vv = Vv()
            >>> vv.add_single_document_rendition("534", "imported_rendition__c", "path/to/your/CholeCap-Document.pdf")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/renditions/{rendition_type}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }

        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(url, headers=headers, files=files)

        return response.json()


    def upload_document_version_rendition(self, doc_id, major_version, minor_version, rendition_type, file_path):
        """
        Uploads a rendition for a specified version of a document. 

        API documentation: https://developer.veevavault.com/api/23.2/#upload-document-version-rendition

        Args:
            doc_id (str): The document ID field value.
            major_version (str): The major version number of the document.
            minor_version (str): The minor version number of the document.
            rendition_type (str): The type of document rendition.
            file_path (str): The path to the file to be uploaded.

        Returns:
            Response object: The HTTP Response object.

        Usage:
            >>> vv = Vv()
            >>> vv.upload_document_version_rendition("534", "1", "0", "imported_rendition__c", "path/to/your/CholeCap-Document.pdf")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/renditions/{rendition_type}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }

        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(url, headers=headers, files=files)

        return response.json()


    def replace_document_rendition(self, doc_id, rendition_type, file_path):
        """
        Replaces a rendition of the latest version of a document.

        API documentation: https://developer.veevavault.com/api/23.2/#replace-document-rendition

        Args:
            doc_id (str): The document ID field value.
            rendition_type (str): The type of document rendition.
            file_path (str): The path to the file to be uploaded.

        Returns:
            Response object: The HTTP Response object.

        Usage:
            >>> vv = Vv()
            >>> vv.replace_document_rendition("534", "imported_rendition__c", "path/to/your/CholeCap-Document.pdf")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/renditions/{rendition_type}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }

        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.put(url, headers=headers, files=files)

        return response.json()


    def replace_document_version_rendition(self, doc_id, major_version, minor_version, rendition_type, file_path):
        """
        Replaces a rendition of a specified version of a document.

        API documentation: https://developer.veevavault.com/api/23.2/#replace-document-version-rendition

        Args:
            doc_id (str): The document ID field value.
            major_version (str): The document major version number.
            minor_version (str): The document minor version number.
            rendition_type (str): The type of document rendition.
            file_path (str): The path to the file to be uploaded.

        Returns:
            Response object: The HTTP Response object.

        Usage:
            >>> vv = Vv()
            >>> vv.replace_document_version_rendition("534", "2", "0", "imported_rendition__c", "path/to/your/CholeCap-Document.pdf")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/renditions/{rendition_type}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }

        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.put(url, headers=headers, files=files)

        return response.json()


    def delete_multiple_document_renditions(self, csv_file_path):
        """
        Deletes multiple document renditions in bulk.

        API documentation: https://developer.veevavault.com/api/23.2/#delete-multiple-document-renditions

        Args:
            csv_file_path (str): The path to the CSV file containing details of the document renditions to delete.

        Returns:
            Response object: The HTTP Response object.

        Usage:
            >>> vv = Vv()
            >>> vv.delete_multiple_document_renditions("C:\\Vault\\Documents\\delete_document_renditions.csv")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/renditions/batch"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }

        with open(csv_file_path, 'rb') as f:
            response = requests.delete(url, headers=headers, data=f)

        return response.json()


    def delete_single_document_rendition(self, document_id, rendition_type):
        """
        Deletes a single document rendition. On SUCCESS, Vault deletes the rendition of specified type from the latest document version.

        API documentation: https://developer.veevavault.com/api/23.2/#delete-single-document-rendition

        Args:
            document_id (str): The document ID field value.
            rendition_type (str): The document rendition type.

        Returns:
            Response object: The HTTP Response object.

        Usage:
            >>> vv = Vv()
            >>> vv.delete_single_document_rendition("534", "imported_rendition__vs")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{document_id}/renditions/{rendition_type}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.delete(url, headers=headers)

        return response.json()


    def delete_document_version_rendition(self, doc_id, major_version, minor_version, rendition_type):
        """
        Deletes the rendition of the given type from the specified version of the document.

        API documentation: https://developer.veevavault.com/api/23.2/#delete-document-version-rendition

        Args:
            doc_id (str): The document ID field value.
            major_version (str): The document major_version_number__v field value.
            minor_version (str): The document minor_version_number__v field value.
            rendition_type (str): The document rendition type.

        Returns:
            Response object: The HTTP Response object.

        Usage:
            >>> vv = Vv()
            >>> vv.delete_document_version_rendition("534", "2", "0", "imported_rendition__c")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/renditions/{rendition_type}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.delete(url, headers=headers)

        return response.json()



    #######################################################
    # Documents
    ## Document Attachments
    #######################################################

    def determine_if_document_has_attachments(self, doc_id):
        """
        Determines if a document has attachments. The method sends a GET request to the specified URL and retrieves the information on any attachments associated with the specified document ID.

        API documentation: https://developer.veevavault.com/api/23.2/#determine-if-a-document-has-attachments

        Args:
            doc_id (str): The document ID field value.

        Returns:
            dict: A dictionary with details about the attachments (if any).

        Usage:
            >>> vv = Vv()
            >>> vv.determine_if_document_has_attachments("565")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_document_attachments(self, doc_id):
        """
        Retrieves the attachments of a specified document. The method sends a GET request to the specified URL and retrieves details about the document's attachments including id, filename, format, size, MD5 checksum, version details, and the creator's details.

        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-attachments

        Args:
            doc_id (str): The document ID field value.

        Returns:
            dict: A dictionary containing details of the document's attachments.

        Usage:
            >>> vv = Vv()
            >>> vv.retrieve_document_attachments("565")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_document_version_attachments(self, doc_id, major_version, minor_version):
        """
        Retrieves the attachments of a specific version of a document. Sends a GET request to the specified URL and retrieves details about the attachments including ID, filename, format, size, MD5 checksum, version details, and the creator's details.
        
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-version-attachments
        
        Args:
            doc_id (str): The document ID field value.
            major_version (str): The document major version number field value.
            minor_version (str): The document minor version number field value.
        
        Returns:
            dict: A dictionary containing details of the document version's attachments.
        
        Usage:
            >>> vv = Vv()
            >>> vv.retrieve_document_version_attachments("17", "0", "1")
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/attachments"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_document_attachment_versions(self, doc_id, attachment_id):
        """
        Retrieves versions of a specific document attachment. Sends a GET request to the specified URL and retrieves details about the versions including version number and URL.
        
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-attachment-versions
        
        Args:
            doc_id (str): The document ID field value.
            attachment_id (str): The attachment ID field value.
        
        Returns:
            dict: A dictionary containing details of the document attachment versions.
        
        Usage:
            >>> vv = Vv()
            >>> vv.retrieve_document_attachment_versions("565", "566")
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments/{attachment_id}/versions"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_document_version_attachment_versions(self, doc_id, major_version, minor_version, attachment_id, attachment_version=None):
        """
        Retrieves specific versions of an attachment on a specific version of a document. 
        If attachment_version is omitted, it retrieves all versions of the specified attachment.

        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-version-attachment-versions

        Args:
            doc_id (str): The document id field value.
            major_version (str): The document major_version_number__v field value.
            minor_version (str): The document minor_version_number__v field value.
            attachment_id (str): The id of the document attachment to retrieve.
            attachment_version (str, optional): The version of the attachment to retrieve. Defaults to None.

        Returns:
            dict: A dictionary containing details of the document version attachment versions.

        Usage:
            >>> vv = Vv()
            >>> vv.retrieve_document_version_attachment_versions("17", "0", "1", "39", "1")
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/attachments/{attachment_id}/versions"
        if attachment_version:
            url += f"/{attachment_version}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_document_attachment_metadata(self, doc_id, attachment_id):
        """
        Retrieves the metadata of a specific document attachment. The metadata contains various details including file name, format, size, checksum and more.

        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-attachment-metadata

        Args:
            doc_id (str): The document id field value.
            attachment_id (str): The attachment id field value.

        Returns:
            dict: A dictionary containing the metadata of the document attachment.

        Usage:
            >>> vv = Vv()
            >>> vv.retrieve_document_attachment_metadata("565", "566")
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments/{attachment_id}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()

    def retrieve_document_attachment_version_metadata(self, doc_id, attachment_id, attachment_version):
        """
        Retrieves the metadata of a specific version of a document attachment. This metadata contains details including file name, format, size, checksum and more.

        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-attachment-version-metadata

        Args:
            doc_id (str): The document id field value.
            attachment_id (str): The attachment id field value.
            attachment_version (str): The attachment version field value.

        Returns:
            dict: A dictionary containing the metadata of the specific version of the document attachment.

        Usage:
            >>> vv = Vv()
            >>> vv.retrieve_document_attachment_version_metadata("565", "566", "2")
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments/{attachment_id}/versions/{attachment_version}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        return response.json()


    def download_document_attachment(self, doc_id, attachment_id):
        """
        Downloads the latest version of the specified attachment from the document. The filename in the response can be used to name the local file.

        API documentation: https://developer.veevavault.com/api/23.2/#download-document-attachment

        Args:
            doc_id (str): The document id field value.
            attachment_id (str): The attachment id field value.

        Returns:
            bytes: The content of the file as bytes.

        Usage:
            >>> vv = Vv()
            >>> file_content = vv.download_document_attachment("565", "567")
            >>> with open("filename_from_response.pdf", "wb") as file:
            >>>     file.write(file_content)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments/{attachment_id}/file"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.content


    def download_document_attachment_version(self, doc_id, attachment_id, attachment_version):
        """
        Downloads the specified version of the attachment from the document. The filename in the response can be used to name the local file.

        API documentation: https://developer.veevavault.com/api/23.2/#download-document-attachment-version

        Args:
            doc_id (str): The document id field value.
            attachment_id (str): The attachment id field value.
            attachment_version (str): The attachment version__v field value.

        Returns:
            bytes: The content of the file as bytes.

        Usage:
            >>> vv = Vv()
            >>> file_content = vv.download_document_attachment_version("565", "567", "1")
            >>> with open("filename_from_response.pdf", "wb") as file:
            >>>     file.write(file_content)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments/{attachment_id}/versions/{attachment_version}/file"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.content


    def download_document_version_attachment_version(self, doc_id, major_version, minor_version, attachment_id, attachment_version):
        """
        Downloads the specified attachment version from the specified document version. The filename in the response can be used to name the local file.

        API documentation: https://developer.veevavault.com/api/23.2/#download-document-version-attachment-version

        Args:
            doc_id (str): The document id field value.
            major_version (str): The document major_version_number__v field value.
            minor_version (str): The document minor_version_number__v field value.
            attachment_id (str): The id field value of the attachment.
            attachment_version (str): The version of the attachment.

        Returns:
            bytes: The content of the file as bytes.

        Usage:
            >>> vv = Vv()
            >>> file_content = vv.download_document_version_attachment_version("56", "0", "1", "14", "3")
            >>> with open("filename_from_response.pdf", "wb") as file:
            >>>     file.write(file_content)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/attachments/{attachment_id}/versions/{attachment_version}/file"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.content


    def download_all_document_attachments(self, doc_id):
        """
        Downloads the latest version of all attachments from the specified document. The attachments are packaged in a ZIP file and the file name from the response can be used to name the local file.

        API documentation: https://developer.veevavault.com/api/23.2/#download-all-document-attachments

        Args:
            doc_id (str): The document id field value.

        Returns:
            bytes: The content of the zip file as bytes.

        Usage:
            >>> vv = Vv()
            >>> zip_content = vv.download_all_document_attachments("565")
            >>> with open("filename_from_response.zip", "wb") as file:
            >>>     file.write(zip_content)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments/file"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.content


    def download_all_document_version_attachments(self, doc_id, major_version, minor_version):
        """
        Downloads the latest version of all attachments from the specified version of the document. The file name from the response can be used to name the local file.

        API documentation: https://developer.veevavault.com/api/23.2/#download-all-document-version-attachments

        Args:
            doc_id (str): The document id field value.
            major_version (str): The document major_version_number__v field value.
            minor_version (str): The document minor_version_number__v field value.

        Returns:
            bytes: The content of the attachments as bytes.

        Usage:
            >>> vv = Vv()
            >>> content = vv.download_all_document_version_attachments("56", "0", "1")
            >>> with open("filename_from_response", "wb") as file:
            >>>     file.write(content)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/attachments/file"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        return response.content


    def delete_single_document_attachment(self, doc_id, attachment_id):
        """
        Deletes the specified attachment and all of its versions.

        API documentation: https://developer.veevavault.com/api/23.2/#delete-single-document-attachment

        Args:
            doc_id (str): The document id field value.
            attachment_id (str): The attachment id field value.

        Returns:
            dict: The JSON response from the API call.

        Usage:
            >>> vv = Vv()
            >>> response = vv.delete_single_document_attachment("565", "567")
            >>> print(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments/{attachment_id}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        
        return response.json()


    def delete_single_document_attachment_version(self, doc_id, attachment_id, attachment_version):
        """
        Deletes the specified version of the specified attachment.

        API documentation: https://developer.veevavault.com/api/23.2/#delete-single-document-attachment-version

        Args:
            doc_id (str): The document id field value.
            attachment_id (str): The attachment id field value.
            attachment_version (str): The attachment version__v field value.

        Returns:
            dict: The JSON response from the API call.

        Usage:
            >>> vv = Vv()
            >>> response = vv.delete_single_document_attachment_version("565", "567", "3")
            >>> print(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments/{attachment_id}/versions/{attachment_version}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.delete(url, headers=headers)
        response.raise_for_status()
        
        return response.json()


    def delete_multiple_document_attachments(self, input_file, content_type='text/csv', accept='text/csv', id_param=None):
        """
        Delete multiple document attachments in bulk with a JSON or CSV input file. 
        This works for version-specific attachments and attachments at the document level.

        API documentation: https://developer.veevavault.com/api/23.2/#delete-multiple-document-attachments

        Args:
            input_file (str): The path to the input file (CSV or JSON) with details of attachments to be deleted.
            content_type (str): The content type of the input file, either 'application/json' or 'text/csv'. Defaults to 'text/csv'.
            accept (str): The format of the response, either 'application/json', 'text/csv', or 'application/xml'. Defaults to 'text/csv'.
            id_param (str, optional): If you’re identifying attachments in your input by external id, 
                                    add this parameter with the value 'external_id__v'. Defaults to None.

        Returns:
            dict: The JSON response from the API call.

        Usage:
            >>> vv = Vv()
            >>> response = vv.delete_multiple_document_attachments("C:\\Vault\\Documents\\delete_attachments.csv")
            >>> print(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/attachments/batch"
        if id_param:
            url += f"?idParam={id_param}"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": content_type,
            "Accept": accept
        }

        with open(input_file, 'rb') as file:
            response = requests.delete(url, headers=headers, data=file)
            response.raise_for_status()
        
        return response.json()


    def create_document_attachment(self, doc_id, file_path):
        """
        Create an attachment on the latest version of a document. If the attachment 
        already exists, Vault uploads the attachment as a new version of the existing attachment. 

        API documentation: https://developer.veevavault.com/api/23.2/#create-document-attachment

        Args:
            doc_id (str): The document id field value.
            file_path (str): The path to the attachment file to be uploaded.

        Returns:
            dict: The JSON response from the API call.

        Usage:
            >>> vv = Vv()
            >>> response = vv.create_document_attachment("565", "path/to/my_attachment_file.png")
            >>> print(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }

        with open(file_path, 'rb') as file:
            files = {'file': (os.path.basename(file_path), file)}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
        
        return response.json()


    def create_multiple_document_attachments(self, input_file_path):
        """
        Create multiple document attachments in bulk with a JSON or CSV input file. You must first load the attachments 
        to the file staging server. This works for version-specific attachments and attachments at the document level. 

        API documentation: https://developer.veevavault.com/api/23.2/#create-multiple-document-attachments

        Args:
            input_file_path (str): The file path to the CSV or JSON input file.

        Returns:
            dict: The JSON response from the API call.

        Usage:
            >>> vv = Vv()
            >>> response = vv.create_multiple_document_attachments("path/to/create_attachments.csv")
            >>> print(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/attachments/batch"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "text/csv"
        }

        with open(input_file_path, 'rb') as file:
            response = requests.post(url, headers=headers, data=file)
            response.raise_for_status()
        
        return response.json()


    def restore_document_attachment_version(self, doc_id, attachment_id, attachment_version):
        """
        Restores a specific version of an existing attachment to make it the latest version.

        API documentation: https://developer.veevavault.com/api/23.2/#restore-document-attachment-version

        Args:
            doc_id (str): The document id field value.
            attachment_id (str): The attachment id field value.
            attachment_version (str): The attachment version__v field value.

        Returns:
            dict: The JSON response from the API call.

        Usage:
            >>> vv = Vv()
            >>> response = vv.restore_document_attachment_version("565", "567", "2")
            >>> print(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments/{attachment_id}/versions/{attachment_version}?restore=true"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.post(url, headers=headers)
        response.raise_for_status()
        
        return response.json()


    def update_document_attachment_description(self, doc_id, attachment_id, description):
        """
        Updates the description of an attachment on the latest version of a document.

        API documentation: https://developer.veevavault.com/api/23.2/#update-document-attachment-description

        Args:
            doc_id (str): The document id field value.
            attachment_id (str): The attachment id field value.
            description (str): The new description for the attachment, maximum character length is 1000.

        Returns:
            dict: The JSON response from the API call.

        Usage:
            >>> vv = Vv()
            >>> response = vv.update_document_attachment_description("565", "567", "This is my description for this attachment.")
            >>> print(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/attachments/{attachment_id}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        data = {
            "description__v": description
        }
        
        response = requests.put(url, headers=headers, data=data)
        response.raise_for_status()
        
        return response.json()

    def update_multiple_document_attachment_descriptions(self, input_file_path, id_param=None):
        """
        Updates the descriptions of multiple document attachments in bulk using a JSON or CSV input file.

        API documentation: https://developer.veevavault.com/api/23.2/#update-multiple-document-attachment-descriptions

        Args:
            input_file_path (str): The file path to the JSON or CSV input file.
            id_param (str, optional): The parameter to identify attachments by external ID instead of regular id. 
                                    If identifying attachments by external id, add idParam=external_id__v to the request endpoint.

        Returns:
            dict: The JSON response from the API call.

        Usage:
            >>> vv = Vv()
            >>> response = vv.update_multiple_document_attachment_descriptions("C:\\Vault\\Documents\\update_attachments.csv")
            >>> print(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/attachments/batch"
        if id_param:
            url += f"?idParam={id_param}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }
        
        with open(input_file_path, 'rb') as file:
            response = requests.put(url, headers=headers, data=file)
            response.raise_for_status()
        
        return response.json()


    #######################################################
    # Documents
    ## Document Annotations
    #######################################################

    def download_document_annotations(self, doc_id):
        """
        Downloads the annotations of the specified version document rendition.

        API documentation: https://developer.veevavault.com/api/23.2/#download-document-annotations

        Args:
            doc_id (str): The ID of the document whose annotations need to be downloaded.

        Returns:
            bytes: The PDF data containing the annotations.

        Usage:
            >>> vv = Vv()
            >>> response = vv.download_document_annotations("14")
            >>> with open("annotations.pdf", "wb") as file:
            >>>     file.write(response)
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/annotations"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.content


    def download_document_version_annotations(self, doc_id, major_version, minor_version):
        """
        Downloads the annotations of the specified document version.

        API documentation: https://developer.veevavault.com/api/23.2/#download-document-version-annotations

        Args:
            doc_id (str): The ID of the document.
            major_version (str): The major version number of the document.
            minor_version (str): The minor version number of the document.

        Returns:
            bytes: The PDF data containing the annotations.

        Usage:
            >>> vv = Vv()
            >>> response = vv.download_document_version_annotations("14", "2", "1")
            >>> with open("version_annotations.pdf", "wb") as file:
            >>>     file.write(response)
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/annotations"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.content


    def retrieve_anchor_ids(self, doc_id):
        """
        Retrieves all anchor IDs from a specific document.

        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-anchor-ids

        Args:
            doc_id (str): The ID of the document to retrieve anchor IDs from.

        Returns:
            dict: A dictionary containing the details of the retrieved anchor IDs.

        Usage:
            >>> vv = Vv()
            >>> response = vv.retrieve_anchor_ids("10")
            >>> for anchor_data in response['anchorDataList']:
            >>>     print(f"Anchor ID: {anchor_data['anchorId']}, Name: {anchor_data['anchorName']}, Author: {anchor_data['noteAuthor']}, Page: {anchor_data['pageNumber']}")
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/anchors"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.json()


    def retrieve_document_version_notes_as_csv(self, doc_id, major_version, minor_version):
        """
        Retrieves notes in CSV format for any document that has a viewable rendition and at least one annotation. 
        
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-version-notes-as-csv

        Args:
            doc_id (str): The document id field value.
            major_version (str): The document major version number.
            minor_version (str): The document minor version number.

        Returns:
            csv: A CSV containing the annotation metadata.

        Usage:
            >>> vv = Vv()
            >>> response = vv.retrieve_document_version_notes_as_csv("10", "1", "0")
            >>> with open('notes.csv', 'w') as file:
            >>>     file.write(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/doc-export-annotations-to-csv"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "text/csv"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.text


    def retrieve_video_annotations(self, doc_id, major_version, minor_version):
        """
        Retrieves annotations on a video document.
        
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-video-annotations

        Args:
            doc_id (str): The video document id field value.
            major_version (str): The video document major version number.
            minor_version (str): The video document minor version number.

        Returns:
            csv: A CSV containing the video annotation metadata including replies and ordered by time signature.

        Usage:
            >>> vv = Vv()
            >>> response = vv.retrieve_video_annotations("14", "2", "1")
            >>> with open('video_annotations.csv', 'w') as file:
            >>>     file.write(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/export-video-annotations"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "text/csv"
        }

        response = requests.get(url, headers=headers)
        response.raise_for_status()

        return response.text


    def upload_document_annotations(self, doc_id, file_path):
        """
        Uploads document annotations.
        
        API documentation: https://developer.veevavault.com/api/23.2/#upload-document-annotations

        Args:
            doc_id (str): The document id field value.
            file_path (str): The path to the document file that contains the annotations to be uploaded.

        Returns:
            dict: A dictionary containing details about the upload status including the number of replies, failures, and new annotations.

        Usage:
            >>> vv = Vv()
            >>> response = vv.upload_document_annotations("548", "path/to/document2016.pdf")
            >>> print(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/annotations"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
        
        return response.json()


    def upload_document_version_annotations(self, doc_id, major_version, minor_version, file_path):
        """
        Uploads annotations for a specific version of a document.
        
        API documentation: https://developer.veevavault.com/api/23.2/#upload-document-version-annotations

        Args:
            doc_id (str): The document id field value.
            major_version (str): The document major_version_number__v field value.
            minor_version (str): The document minor_version_number__v field value.
            file_path (str): The path to the document file that contains the annotations to be uploaded.

        Returns:
            dict: A dictionary containing details about the upload status including the number of replies, failures, and new annotations.

        Usage:
            >>> vv = Vv()
            >>> response = vv.upload_document_version_annotations("548", "2", "1", "path/to/document2016.pdf")
            >>> print(response)
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/annotations"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }
        
        with open(file_path, 'rb') as f:
            files = {'file': (os.path.basename(file_path), f)}
            response = requests.post(url, headers=headers, files=files)
            response.raise_for_status()
        
        return response.json()



    #######################################################
    # Documents
    ## Document Relationships
    #######################################################

    def retrieve_document_type_relationships(self, document_type):
        """
        Retrieves all relationships from a specified document type.
        
        API Documentation:
        https://developer.veevavault.com/api/23.2/#retrieve-document-type-relationships
        
        Args:
        document_type (str): The type of the document. See Retrieve Document Types API for the list of document types.
        
        Returns:
        dict: A dictionary containing the relationship details.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/documents/types/{document_type}/relationships"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_document_relationships(self, doc_id, major_version, minor_version):
        """
        Retrieves all relationships from a specific document. For more details, visit: 
        https://developer.veevavault.com/api/23.2/#retrieve-document-relationships
        
        Parameters:
        doc_id (str): The document id field value.
        major_version (str): The document major_version_number__v field value.
        minor_version (str): The document minor_version_number__v field value.

        Returns:
        dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/relationships"
        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        response = requests.get(url, headers=headers)
        return response.json()


    def create_single_document_relationship(self, document_id, major_version_number, minor_version_number, target_doc_id, relationship_type, target_major_version=None, target_minor_version=None):
        """
        Creates a new relationship on a document. For more details, visit:
        https://developer.veevavault.com/api/23.2/#create-single-document-relationship
        
        Parameters:
        document_id (str): The document id field value.
        major_version_number (str): The document major_version_number__v field value.
        minor_version_number (str): The document minor_version_number__v field value.
        target_doc_id (str): The document id of the target document.
        relationship_type (str): The relationship type retrieved from the Document Relationships Metadata call above.
        target_major_version (str, optional): The major version number of the target document to which the source document will be bound.
        target_minor_version (str, optional): The minor version number of the target document to which the source document will be bound.

        Returns:
        dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{document_id}/versions/{major_version_number}/{minor_version_number}/relationships"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        data = {
            "target_doc_id__v": target_doc_id,
            "relationship_type__v": relationship_type
        }
        if target_major_version:
            data["target_major_version__v"] = target_major_version
        if target_minor_version:
            data["target_minor_version__v"] = target_minor_version

        response = requests.post(url, headers=headers, data=data)
        return response.json()


    def create_multiple_document_relationships(self, input_file_path, content_type="text/csv", accept="text/csv", id_param=None):
        """
        Creates new relationships on multiple documents. For more details, visit:
        https://developer.veevavault.com/api/23.2/#create-multiple-document-relationships

        Parameters:
        input_file_path (str): The path to the input file (JSON or CSV) containing details for creating document relationships.
        content_type (str, optional): The Content-Type header value. It can be "application/json" or "text/csv". Defaults to "text/csv".
        accept (str, optional): The Accept header value. It can be "application/json" or "text/csv". Defaults to "text/csv".
        id_param (str, optional): A query parameter to create relationships based on a unique field. Defaults to None.

        Returns:
        dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/relationships/batch"
        if id_param:
            url += f"?idParam={id_param}"
        
        headers = {
            "Content-Type": content_type,
            "Accept": accept,
            "Authorization": self.sessionId
        }

        with open(input_file_path, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
        
        return response.json()


    def retrieve_document_relationship(self, doc_id, major_version, minor_version, relationship_id):
        """
        Retrieves the details of a specific document relationship. For more details, visit:
        https://developer.veevavault.com/api/23.2/#retrieve-document-relationship

        Parameters:
        doc_id (int): The document ID.
        major_version (int): The major version number of the document.
        minor_version (int): The minor version number of the document.
        relationship_id (int): The ID of the relationship to be retrieved.

        Returns:
        dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/relationships/{relationship_id}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def delete_single_document_relationship(self, doc_id, major_version, minor_version, relationship_id):
        """
        Deletes a single document relationship. For more details, visit:
        https://developer.veevavault.com/api/23.2/#delete-single-document-relationship

        Parameters:
        doc_id (int): The document ID.
        major_version (int): The major version number of the document.
        minor_version (int): The minor version number of the document.
        relationship_id (int): The ID of the relationship to be deleted.

        Returns:
        dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/versions/{major_version}/{minor_version}/relationships/{relationship_id}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        
        response = requests.delete(url, headers=headers)
        
        return response.json()


    def delete_multiple_document_relationships(self, file_path):
        """
        Deletes multiple document relationships. For more details, visit:
        https://developer.veevavault.com/api/23.2/#delete-multiple-document-relationships

        Parameters:
        file_path (str): The file path of the CSV file containing relationship IDs to be deleted.

        Returns:
        dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/relationships/batch"
        
        headers = {
            "Content-Type": "text/csv",
            "Accept": "text/csv",
            "Authorization": self.sessionId
        }
        
        with open(file_path, 'rb') as file:
            response = requests.delete(url, headers=headers, data=file)
        
        return response.json()



    #######################################################
    # Documents
    ## Export Documents
    #######################################################

    def export_documents(self, document_ids, source=True, renditions=False, allversions=False):
        """
        Export a set of documents to your Vault’s file staging server. For more information, refer to:
        https://developer.veevavault.com/api/23.2/#export-documents-1

        Parameters:
        document_ids (list): List of document IDs to export.
        source (bool, optional): To include or exclude source files. Defaults to True.
        renditions (bool, optional): To include or exclude renditions. Defaults to False.
        allversions (bool, optional): To include all versions or only the latest version. Defaults to False.

        Returns:
        dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/batch/actions/fileextract"
        url += f"?source={'true' if source else 'false'}&renditions={'true' if renditions else 'false'}&allversions={'true' if allversions else 'false'}"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        
        payload = json.dumps([{"id": str(id)} for id in document_ids])
        
        response = requests.post(url, headers=headers, data=payload)
        
        return response.json()


    def export_document_versions(self, document_versions, source=True, renditions=False):
        """
        Export a specific set of document versions to your Vault’s file staging server. For more information, refer to:
        https://developer.veevavault.com/api/23.2/#export-document-versions

        Parameters:
        document_versions (list of dict): List of dictionaries containing details of the document versions to export. Each dictionary should have keys: 'id', 'major_version_number__v', and 'minor_version_number__v'.
        source (bool, optional): To include or exclude source files. Defaults to True.
        renditions (bool, optional): To include or exclude renditions. Defaults to False.

        Returns:
        dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/versions/batch/actions/fileextract"
        url += f"?source={'true' if source else 'false'}&renditions={'true' if renditions else 'false'}"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        
        payload = json.dumps(document_versions)
        
        response = requests.post(url, headers=headers, data=payload)
        
        return response.json()

    def retrieve_document_export_results(self, job_id):
        """
        Retrieve the results of a document export job from your Vault. For more information, refer to:
        https://developer.veevavault.com/api/23.2/#retrieve-document-export-results

        Parameters:
        job_id (str): The ID of the export job to retrieve results for.

        Returns:
        dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/batch/actions/fileextract/{job_id}/results"
        
        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()



    #######################################################
    # Documents
    ## Document Events
    #######################################################



    def retrieve_document_event_types_and_subtypes(self):
        """
        Retrieve the types and subtypes of document events configured in your Vault. For more information, refer to:
        https://developer.veevavault.com/api/23.2/#retrieve-document-event-types-and-subtypes

        Returns:
        dict: A dictionary containing the response data with the list of event types and subtypes.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/documents/events"
        
        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_document_event_subtype_metadata(self, event_type, event_subtype):
        """
        Retrieve the metadata for a specific document event subtype in your Vault. For more information, refer to:
        https://developer.veevavault.com/api/23.2/#retrieve-document-event-subtype-metadata

        Args:
        event_type (str): The event type (e.g., distribution__v).
        event_subtype (str): The event subtype (e.g., approved_email__v).

        Returns:
        dict: A dictionary containing the metadata for the specified event subtype.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/documents/events/{event_type}/types/{event_subtype}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()

    def create_document_event(self, document_id, major_version, minor_version, event_type, event_subtype, classification, external_id):
        """
        Create a new document event in your Vault. For more information, refer to:
        https://developer.veevavault.com/api/23.2/#create-document-event

        Args:
        document_id (int): The document id field value.
        major_version (int): The document major version number field value.
        minor_version (int): The document minor version number field value.
        event_type (str): The event type (e.g., distribution__v).
        event_subtype (str): The event subtype (e.g., approved_email__v).
        classification (str): The event classification (e.g., download__v).
        external_id (str): The external id for the event.

        Returns:
        dict: A dictionary containing the response status of the event creation.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{document_id}/versions/{major_version}/{minor_version}/events"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        
        data = {
            "event_type__v": event_type,
            "event_subtype__v": event_subtype,
            "classification__v": classification,
            "external_id__v": external_id
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        return response.json()


    def retrieve_document_events(self, document_id):
        """
        Retrieve the events associated with a specific document in the vault. For more details, refer to:
        https://developer.veevavault.com/api/23.2/#retrieve-document-events

        Args:
        document_id (int): The ID of the document to retrieve events for.

        Returns:
        dict: A dictionary containing the response status and the list of event objects.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{document_id}/events"

        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }

        response = requests.get(url, headers=headers)
        
        return response.json()


    #######################################################
    # Documents
    ## Document Templates
    #######################################################

    def retrieve_document_template_metadata(self):
        """
        Retrieve the metadata which defines the shape of document templates in your Vault. 
        For more details, refer to: 
        https://developer.veevavault.com/api/23.2/#retrieve-document-template-metadata

        Returns:
        dict: A dictionary containing the response status and the metadata details of document templates.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/documents/templates"

        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }

        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_document_template_collection(self):
        """
        Retrieve all document templates present in the Vault. 
        For more information, refer to:
        https://developer.veevavault.com/api/23.2/#retrieve-document-template-collection

        Returns:
        dict: A dictionary containing the response status and details of all document templates in the Vault.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/templates"

        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }

        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_document_template_attributes(self, template_name):
        """
        Retrieve the attributes from a specific document template in the Vault. 
        For more information, refer to: 
        https://developer.veevavault.com/api/23.2/#retrieve-document-template-attributes

        Args:
        template_name (str): The name__v field value of the document template.

        Returns:
        dict: A dictionary containing the response status and attributes of the specified document template.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/templates/{template_name}"

        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }

        response = requests.get(url, headers=headers)
        
        return response.json()

    def download_document_template_file(self, template_name):
        """
        Download the file of a specific document template.
        For more information, refer to: 
        https://developer.veevavault.com/api/23.2/#download-document-template-file

        Args:
        template_name (str): The name__v field value of the document template.

        Returns:
        Response object: A Response object containing the file stream of the specified document template.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/templates/{template_name}/file"

        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }

        response = requests.get(url, headers=headers, stream=True)
        
        with open(f"{template_name}.pdf", 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        return response.json()


    def create_single_document_template(self, label__v, type__v, active__v, file_path, subtype__v=None, classification__v=None, is_controlled__v=None, template_doc_id__v=None):
        """
        Create one document template in the Vault.
        For more information, refer to:
        https://developer.veevavault.com/api/23.2/#create-single-document-template

        Args:
        label__v (str): The label of the new document template. This is the name users will see among the available templates in the UI.
        type__v (str): The name of the document type to which the template will be associated.
        active__v (bool): Set to true or false to indicate whether the new document template should be set to active.
        file_path (str): The file path of the document template to be uploaded. Maximum allowed size is 4GB.
        subtype__v (str, optional): The name of the document subtype to which the template will be associated. This is only required if associating the template with a document subtype.
        classification__v (str, optional): The name of the document classification to which the template will be associated. This is only required if associating the template with a document classification.
        is_controlled__v (bool, optional): Set to true to indicate this template is a controlled document template.
        template_doc_id__v (str, optional): The document id value to use as the Template Document for this controlled document template.

        Returns:
        Response object: A Response object containing the API response.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/templates"

        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json",
            "Content-Type": "multipart/form-data"
        }

        data = {
            "label__v": label__v,
            "type__v": type__v,
            "active__v": active__v
        }
        if subtype__v:
            data["subtype__v"] = subtype__v
        if classification__v:
            data["classification__v"] = classification__v
        if is_controlled__v is not None:
            data["is_controlled__v"] = is_controlled__v
        if template_doc_id__v:
            data["template_doc_id__v"] = template_doc_id__v

        files = {'file': open(file_path, 'rb')}
        
        response = requests.post(url, headers=headers, data=data, files=files)

        return response.json()


    def update_multiple_document_templates(self, file_path):
        """
        Update up to 500 document templates in the Vault.
        For more details, visit:
        https://developer.veevavault.com/api/23.2/#update-multiple-document-templates

        Args:
        file_path (str): The path to the input file (CSV or JSON) containing details of the document templates to be updated.

        Returns:
        dict: A dictionary containing the API response.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/templates"

        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }

        with open(file_path, 'rb') as f:
            response = requests.put(url, headers=headers, data=f)

        return response.json()


    def delete_basic_document_template(self, template_name):
        """
        Delete a basic document template from the Vault. Controlled document templates cannot be deleted using this API endpoint.
        For more details, visit:
        https://developer.veevavault.com/api/23.2/#delete-basic-document-template

        Args:
        template_name (str): The name__v field value of the document template to be deleted.

        Returns:
        dict: A dictionary containing the API response.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/templates/{template_name}"

        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.delete(url, headers=headers)

        return response.json()


    #######################################################
    # Documents
    ## Document Tokens
    #######################################################

    def document_tokens(self, doc_ids, expiry_date_offset=None, download_option=None, channel=None, token_group=None, steady_state=None):
        """
        Generates document access tokens needed by the external viewer to view documents outside of Vault.
        For more details, visit:
        https://developer.veevavault.com/api/23.2/#document-tokens

        Args:
        doc_ids (str): A comma-separated string of document id values for which to generate tokens.
        expiry_date_offset (int, optional): The number of days after which the tokens will expire. Defaults to 10 years if not specified.
        download_option (str, optional): Set to 'PDF', 'source', 'both', or 'none' to specify download options in the external viewer. Defaults to document settings if not specified.
        channel (str, optional): The website object record id value that corresponds to the distribution channel. Defaults to 'Approved Email' if not specified.
        token_group (str, optional): A string to group together generated tokens for multiple documents to display in the same viewer. Can be up to 255 characters in length.
        steady_state (bool, optional): If true, generates a token for the latest steady state version of a document. Defaults to false.

        Returns:
        dict: A dictionary containing the API response.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/tokens"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        data = {
            "docIds": doc_ids,
            "expiryDateOffset": expiry_date_offset,
            "downloadOption": download_option,
            "channel": channel,
            "tokenGroup": token_group,
            "steadyState": steady_state
        }

        response = requests.post(url, headers=headers, data=data)

        return response.json()


    #######################################################
    # Binders
    #######################################################

    #######################################################
    # Binders
    ## Retrieve Binders
    #######################################################

    def retrieve_all_binders(self):
        """
        Retrieve a list of all binders in the Vault. Binders are a kind of document and can be distinguished from regular documents using the 'binder__v' field set to true or false.
        For more details, visit: https://developer.veevavault.com/api/23.2/#retrieve-all-binders

        Returns:
        dict: A dictionary containing the API response with details of all binders.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()

    def retrieve_binder(self, binder_id, depth='root'):
        """
        Use this endpoint to retrieve all fields and values configured on a specific binder in your Vault (using the binder ID).
        The response includes the "first level" of the binder section node structure. To retrieve additional levels in the 
        binder section node structure, use one of the depth parameters described in the documentation.
        Documentation: https://developer.veevavault.com/api/23.2/#retrieve-binder
        
        Parameters:
        binder_id (str): The binder id field value.
        depth (str): To retrieve all information in all levels of the binder, set this to 'all'. 
                    By default, only one level ('root') is returned.
        
        Returns:
        dict: A dictionary containing the details of the binder.
        """
        
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}"
        headers = {
            'Authorization': self.sessionId,
            'Accept': 'application/json'
        }
        params = {'depth': depth}
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def retrieve_all_binder_versions(self, binder_id):
        """
        Retrieve all versions of a binder. 

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-all-binder-versions

        :param binder_id: The binder id field value.
        :type binder_id: str
        :return: A list of available versions for the specified binder.
        :rtype: list
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/versions"
        headers = {'Accept': 'application/json', 'Authorization': self.sessionId}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json().get('versions')
        else:
            return response.json().get('responseStatus')


    def retrieve_binder_version(self, binder_id, major_version, minor_version):
        """
        Retrieve the fields and values configured on a specific version of a specific binder.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-binder-version

        :param binder_id: The binder id field value.
        :type binder_id: str
        :param major_version: The binder major_version_number__v field value.
        :type major_version: str
        :param minor_version: The binder minor_version_number__v field value.
        :type minor_version: str
        :return: Fields and values of the specified binder version.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/versions/{major_version}/{minor_version}"
        headers = {'Accept': 'application/json', 'Authorization': self.sessionId}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')


    #######################################################
    # Binders
    ## Create Binders
    #######################################################

    def create_binder(self, binder_data, async_indexing=False):
        """
        Use this request to create a new binder in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#create-binder

        :param binder_data: A dictionary containing binder data with keys matching the API's field names (e.g., name__v, type__v).
        :type binder_data: dict
        :param async_indexing: To process the indexing asynchronously, set to True. Default is False.
        :type async_indexing: bool
        :return: Response from the API, contains status and created binder ID.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders"
        if async_indexing:
            url += "?async=true"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': self.sessionId
        }

        response = requests.post(url, data=binder_data, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')


    def create_binder_from_template(self, template_name, binder_data):
        """
        Use this request to create a new binder in your Vault from a template.

        API Documentation: https://developer.veevavault.com/api/23.2/#create-binder-from-template

        :param template_name: The name of the template to use for creating the binder, as returned from the document metadata.
        :type template_name: str
        :param binder_data: A dictionary containing binder data with keys matching the API's field names (e.g., name__v, type__v).
        :type binder_data: dict
        :return: Response from the API, contains status and created binder ID.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': self.sessionId
        }
        
        binder_data['fromTemplate'] = template_name
        
        response = requests.post(url, data=binder_data, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')

    def create_binder_version(self, binder_id):
        """
        Use this method to create a new version of a binder in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#create-binder-version

        :param binder_id: The ID of the binder for which a new version will be created.
        :type binder_id: str or int
        :return: Response from the API, contains status and version details.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}"
        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId
        }

        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')



    #######################################################
    # Binders
    ## Update Binders
    #######################################################

    def update_binder(self, binder_id, data):
        """
        Use this method to update the details of a binder in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#update-binder

        :param binder_id: The ID of the binder to be updated.
        :type binder_id: str or int
        :param data: A dictionary containing the data fields to be updated in the binder.
        :type data: dict
        :return: Response from the API, contains status and ID of the updated binder.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': self.sessionId
        }

        response = requests.put(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')


    def reclassify_binder(self, binder_id, reclassify_data):
        """
        Use this method to reclassify an existing binder in your Vault. Reclassification allows changing the document type 
        of an existing binder. You can only reclassify the latest version of a specified binder and one binder at a time.

        API Documentation: https://developer.veevavault.com/api/23.2/#reclassify-binder

        :param binder_id: The ID of the binder to be reclassified.
        :type binder_id: str or int
        :param reclassify_data: A dictionary containing the reclassify parameters and other editable fields.
        :type reclassify_data: dict
        :return: Response from the API, contains status and ID of the reclassified binder.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': self.sessionId
        }

        response = requests.put(url, headers=headers, data=reclassify_data)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')


    def update_binder_version(self, binder_id, major_version, minor_version, update_data):
        """
        This method is used to update a specific version of a binder in your Vault. The necessary parameters 
        are the binder ID and the major and minor version numbers.

        API Documentation: https://developer.veevavault.com/api/23.2/#update-binder-version

        :param binder_id: The ID of the binder to be updated.
        :type binder_id: str or int
        :param major_version: The major version number of the binder.
        :type major_version: str or int
        :param minor_version: The minor version number of the binder.
        :type minor_version: str or int
        :param update_data: A dictionary containing the parameters to update.
        :type update_data: dict
        :return: Response from the API, contains status and ID of the updated binder.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/versions/{major_version}/{minor_version}"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': self.sessionId
        }

        response = requests.put(url, headers=headers, data=update_data)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')


    def refresh_binder_auto_filing(self, binder_id):
        """
        This method triggers auto-filing for a specific binder. It is only available in eTMF Vaults on binders
        configured with the TMF Reference Models. It mimics the Refresh Auto-Filing action available in the UI.

        API Documentation: https://developer.veevavault.com/api/23.2/#refresh-binder-auto-filing

        :param binder_id: The ID of the binder to refresh auto-filing.
        :type binder_id: str or int
        :return: Response from the API, indicates the success of the operation.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/actions"
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': self.sessionId
        }
        data = {
            'action': 'refresh_auto_filing'
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')



    #######################################################
    # Binders
    ## Delete Binders
    #######################################################

    def delete_binder(self, binder_id):
        """
        This method allows you to delete a specified binder from the vault. The method sends a DELETE request to the Vault API
        to remove the binder identified by the binder_id parameter.

        API Documentation: https://developer.veevavault.com/api/23.2/#delete-binder

        :param binder_id: The ID of the binder to be deleted.
        :type binder_id: str or int
        :return: Response from the API, indicating the status of the delete operation.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}"
        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId
        }

        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')

    def delete_binder_version(self, binder_id, major_version, minor_version):
        """
        This method enables the deletion of a specific version of a binder. The binder is identified using binder_id, 
        major_version, and minor_version parameters.

        API Documentation: https://developer.veevavault.com/api/23.2/#delete-binder-version

        :param binder_id: The ID of the binder to be modified.
        :type binder_id: str or int
        :param major_version: The major version number of the binder.
        :type major_version: str or int
        :param minor_version: The minor version number of the binder.
        :type minor_version: str or int
        :return: Response from the API, denoting the status of the deletion process.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/versions/{major_version}/{minor_version}"
        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId
        }

        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')




    #######################################################
    # Binders
    ## Export Binders
    #######################################################

    def export_binder(self, binder_id, major_version=None, minor_version=None, source=True, renditiontype=None, docversion=None, attachments=None, fields=None, docfield=True):
        """
        This method allows you to export a binder from the Vault. You can specify various parameters to control
        the details of the exported content, such as whether to include source files, specific rendition types,
        document versions, attachments, and specific field values. 

        API Documentation: https://developer.veevavault.com/api/23.2/#export-binder

        :param binder_id: The ID of the binder to be exported.
        :type binder_id: str or int
        :param major_version: (Optional) The major version number of the binder. If not specified, the latest version is exported.
        :type major_version: str or int, optional
        :param minor_version: (Optional) The minor version number of the binder. This parameter is used in conjunction with the major_version parameter.
        :type minor_version: str or int, optional
        :param source: (Optional) Whether to include source files in the export. Default is True.
        :type source: bool, optional
        :param renditiontype: (Optional) The type of renditions to be included in the export.
        :type renditiontype: str, optional
        :param docversion: (Optional) Specify the versions of the documents to be included in the export.
        :type docversion: str, optional
        :param attachments: (Optional) Specify whether to include binder attachments in the export, and which versions to include.
        :type attachments: str, optional
        :param fields: (Optional) A comma-separated list of document field values to be included in the export.
        :type fields: str, optional
        :param docfield: (Optional) Whether to include document metadata in the export. Default is True.
        :type docfield: bool, optional
        :return: Response from the API, containing details of the export job initiated.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        params = {}
        if not source:
            params['source'] = 'false'
        if renditiontype:
            params['renditiontype'] = renditiontype
        if docversion:
            params['docversion'] = docversion
        if attachments:
            params['attachments'] = attachments
        if fields:
            params['fields'] = fields
        if not docfield:
            params['docfield'] = 'false'

        endpoint = f"/api/{self.LatestAPIversion}/objects/binders/{binder_id}"
        if major_version is not None and minor_version is not None:
            endpoint += f"/versions/{major_version}/{minor_version}"
        endpoint += "/actions/export"
        url = f"{self.vaultURL}{endpoint}"

        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId
        }

        response = requests.post(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')


    def export_binder_sections(self, binder_id, major_version, minor_version, node_ids, input_file_format='csv'):
        """
        This method allows you to export specific sections and documents from a binder in your Vault. You need to provide a list of node IDs (section or document IDs) to specify which parts of the binder to export. This method will initiate an export job in the Vault, and you can later check the status of this job using the URL and job ID provided in the response.

        API Documentation: https://developer.veevavault.com/api/23.2/#export-binder-sections

        :param binder_id: The ID of the binder to export sections from.
        :type binder_id: str or int
        :param major_version: The major version number of the binder.
        :type major_version: str or int
        :param minor_version: The minor version number of the binder.
        :type minor_version: str or int
        :param node_ids: A list of node IDs specifying the sections and documents to export.
        :type node_ids: list of str or int
        :param input_file_format: Format of the input file, either 'csv' or 'json'. Default is 'csv'.
        :type input_file_format: str, optional
        :return: Response from the API, containing details of the export job initiated.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/versions/{major_version}/{minor_version}/actions/export"

        headers = {
            'Authorization': self.sessionId,
            'Accept': 'application/json'
        }

        if input_file_format.lower() == 'csv':
            headers['Content-Type'] = 'text/csv'
            data = '\n'.join(map(str, node_ids))
        else: # input_file_format is 'json'
            headers['Content-Type'] = 'application/json'
            data = json.dumps({'id': node_ids})

        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')


    def retrieve_binder_export_results(self, job_id):
        """
        This method retrieves the results of a previously initiated binder export job. You need to provide the job ID of the export job to get the results. The method returns details of the export including the path to the exported binder file.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-binder-export-results

        :param job_id: The ID of the export job whose results are to be retrieved.
        :type job_id: str or int
        :return: Response from the API, containing details of the exported binder.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/actions/export/{job_id}/results"

        headers = {
            'Authorization': self.sessionId,
            'Accept': 'application/json'
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return response.json().get('responseStatus')


    def download_exported_binder_files(self, file_path):
        """
        This method allows you to download the exported binder files from the file staging server. Ensure that the export job has been completed successfully and the API user has the necessary permissions to access the file staging server.

        API Documentation: https://developer.veevavault.com/api/23.2/#download-exported-binder-files-via-file-staging-server

        :param file_path: The path/location of the downloaded binder ZIP file retrieved from the export results.
        :type file_path: str
        :return: None
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}{file_path}"

        headers = {
            'Authorization': self.sessionId,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            with open('downloaded_binder.zip', 'wb') as file:
                file.write(response.content)
        else:
            print(f"Failed to download the file. Status code: {response.status_code}")



    #######################################################
    # Binders
    ## Binder Relationships
    #######################################################

    def retrieve_binder_relationship(self, binder_id, major_version, minor_version, relationship_id):
        """
        Retrieve information about a specific binder relationship using its ID. This method returns details such as the source document ID, relationship type, creation date, etc.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-binder-relationship

        :param binder_id: The ID of the binder.
        :type binder_id: str
        :param major_version: The major version number of the binder.
        :type major_version: int
        :param minor_version: The minor version number of the binder.
        :type minor_version: int
        :param relationship_id: The ID of the binder relationship.
        :type relationship_id: int
        :return: Response JSON containing the details of the binder relationship.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/versions/{major_version}/{minor_version}/relationships/{relationship_id}"
        
        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to retrieve binder relationship. Status code: {response.status_code}"}

    def create_binder_relationship(self, binder_id, major_version, minor_version, target_doc_id, relationship_type, target_major_version=None, target_minor_version=None):
        """
        Create a relationship between a binder and a target document in the Vault. You can specify the versions of the target document to create a relationship with a specific version.

        API Documentation: https://developer.veevavault.com/api/23.2/#create-binder-relationship

        :param binder_id: The ID of the binder.
        :type binder_id: str
        :param major_version: The major version number of the binder.
        :type major_version: int
        :param minor_version: The minor version number of the binder.
        :type minor_version: int
        :param target_doc_id: The document ID of the target document.
        :type target_doc_id: int
        :param relationship_type: The relationship type for creating the binder relationship.
        :type relationship_type: str
        :param target_major_version: The major version number of the target document (optional).
        :type target_major_version: int, optional
        :param target_minor_version: The minor version number of the target document (optional).
        :type target_minor_version: int, optional
        :return: Response JSON containing the status of the creation operation and the ID of the created relationship.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/versions/{major_version}/{minor_version}/relationships"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }
        
        data = {
            'target_doc_id__v': target_doc_id,
            'relationship_type__v': relationship_type,
        }
        
        if target_major_version is not None:
            data['target_major_version__v'] = target_major_version
        
        if target_minor_version is not None:
            data['target_minor_version__v'] = target_minor_version

        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to create binder relationship. Status code: {response.status_code}"}


    def delete_binder_relationship(self, binder_id, major_version, minor_version, relationship_id):
        """
        Deletes a specified relationship from a binder in the Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#delete-binder-relationship

        :param binder_id: The ID of the binder.
        :type binder_id: str
        :param major_version: The major version number of the binder.
        :type major_version: int
        :param minor_version: The minor version number of the binder.
        :type minor_version: int
        :param relationship_id: The ID of the relationship to be deleted.
        :type relationship_id: int
        :return: Response JSON containing the status of the deletion operation and the ID of the deleted relationship.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/versions/{major_version}/{minor_version}/relationships/{relationship_id}"
        
        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }
        
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to delete binder relationship. Status code: {response.status_code}"} 


    #######################################################
    # Binders
    ## Binder Sections
    #######################################################
    def retrieve_binder_sections(self, binder_id, section_id=None):
        """
        Retrieve all sections (documents and subsections) in a binder's top-level root node or sub-level node.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-binder-sections

        :param binder_id: The binder id field value.
        :type binder_id: str
        :param section_id: Optional: The section id to retrieve sections from a sub-level node. If not included, all sections from the binder’s top-level root node will be returned.
        :type section_id: str, optional
        :return: Response JSON containing details of all sections (documents and subsections) in a binder's top-level root node or sub-level node.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/sections"
        if section_id:
            url += f"/{section_id}"

        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }
        
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to retrieve binder sections. Status code: {response.status_code}"} 


    def retrieve_binder_version_section(self, binder_id, major_version, minor_version, section_id=None):
        """
        For a specific version, retrieve all sections (documents and subsection) in a binder’s top-level root node or sub-level node.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-binder-version-section

        :param binder_id: The binder id field value.
        :type binder_id: str
        :param major_version: The binder major version number field value.
        :type major_version: str
        :param minor_version: The binder minor version number field value.
        :type minor_version: str
        :param section_id: Optional: The section id to retrieve sections from a sub-level node. If not included, all sections from the binder’s top-level root node will be returned.
        :type section_id: str, optional
        :return: Response JSON containing details of all sections (documents and subsections) in a binder's top-level root node or sub-level node for the specified version.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/versions/{major_version}/{minor_version}/sections"
        if section_id:
            url += f"/{section_id}"
        
        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }

        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to retrieve binder version section. Status code: {response.status_code}"} 

    def create_binder_section(self, binder_id, name, section_number=None, parent_id=None, order=None):
        """
        Create a new section in a binder.

        API Documentation: https://developer.veevavault.com/api/23.2/#create-binder-section

        :param binder_id: The binder id field value.
        :type binder_id: str
        :param name: Specify a name for the new section.
        :type name: str
        :param section_number: Optional: Enter a numerical value for the new section.
        :type section_number: str, optional
        :param parent_id: Optional: If the new section is going to be a subsection, enter the Node ID of the parent section. If left blank, the new section will become a top-level section in the binder. 
        :type parent_id: str, optional
        :param order: Optional: Enter a number reflecting the position of the section within the binder or parent section.
        :type order: int, optional
        :return: Response JSON containing the Node ID of the newly created section.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/sections"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }

        data = {
            'name__v': name,
        }
        if section_number:
            data['section_number__v'] = section_number
        if parent_id:
            data['parent_id__v'] = parent_id
        if order:
            data['order__v'] = order

        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to create binder section. Status code: {response.status_code}"} 

    def update_binder_section(self, binder_id, node_id, name=None, section_number=None, order=None, parent_id=None):
        """
        Update a section in a binder.

        API Documentation: https://developer.veevavault.com/api/23.2/#update-binder-section

        :param binder_id: The binder id field value.
        :type binder_id: str
        :param node_id: The binder node id of the section.
        :type node_id: str
        :param name: Optional: Change the name of the binder section.
        :type name: str, optional
        :param section_number: Optional: Update the section number value.
        :type section_number: str, optional
        :param order: Optional: Enter a number reflecting the position of the section within the binder or parent section.
        :type order: int, optional
        :param parent_id: Optional: To move the section to a different section in the binder, include the value of the parent node where it will be moved.
        :type parent_id: str, optional
        :return: Response JSON containing the Node ID of the updated section.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/sections/{node_id}"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }
        
        data = {}
        if name:
            data['name__v'] = name
        if section_number:
            data['section_number__v'] = section_number
        if order:
            data['order__v'] = order
        if parent_id:
            data['parent_id__v'] = parent_id

        response = requests.put(url, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to update binder section. Status code: {response.status_code}"}


    def delete_binder_section(self, binder_id, section_id):
        """
        Delete a section from a binder.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#delete-binder-section

        :param binder_id: The binder id field value.
        :type binder_id: str
        :param section_id: The binder node id field value.
        :type section_id: str
        :return: Response JSON containing the Node ID of the deleted section.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/sections/{section_id}"
        
        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }
        
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to delete binder section. Status code: {response.status_code}"}



    #######################################################
    # Binders
    ## Binder Documents
    #######################################################

    def add_document_to_binder(self, binder_id, document_id, parent_id=None, order=None, binding_rule=None, major_version_number=None, minor_version_number=None):
        """
        Add a document to a binder.

        API Documentation: https://developer.veevavault.com/api/23.2/#add-document-to-binder

        :param binder_id: The binder id field value.
        :type binder_id: str
        :param document_id: ID of the document being added to the binder.
        :type document_id: str
        :param parent_id: Section ID of the parent section (optional).
        :type parent_id: str, optional
        :param order: Position of the document within the binder or section (optional).
        :type order: int, optional
        :param binding_rule: The binding rule indicating which version of the document will be linked to the binder (optional).
        :type binding_rule: str, optional
        :param major_version_number: Major version of the document to be linked (optional).
        :type major_version_number: int, optional
        :param minor_version_number: Minor version of the document to be linked (optional).
        :type minor_version_number: int, optional
        :return: Response JSON containing the Node ID of the added document.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/documents"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }
        
        data = {
            'document_id__v': document_id,
            'parent_id__v': parent_id,
            'order__v': order,
            'binding_rule__v': binding_rule,
            'major_version_number__v': major_version_number,
            'minor_version_number__v': minor_version_number,
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to add document to binder. Status code: {response.status_code}"}


    def move_document_in_binder(self, binder_id, section_id, order=None, parent_id=None):
        """
        Move a document to a different position within a binder.

        API Documentation: https://developer.veevavault.com/api/23.2/#move-document-in-binder

        :param binder_id: The binder id field value.
        :type binder_id: str
        :param section_id: The binder node id field value.
        :type section_id: str
        :param order: A number reflecting the new position of the document within the binder or section (optional).
        :type order: int, optional
        :param parent_id: Value of the new parent node to move the document to a different section or to the binder's root node (optional).
        :type parent_id: str, optional
        :return: Response JSON containing the new node ID of the document.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/documents/{section_id}"

        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }

        data = {
            'order__v': order,
            'parent_id__v': parent_id,
        }

        response = requests.put(url, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to move document in binder. Status code: {response.status_code}"}


    def remove_document_from_binder(self, binder_id, section_id):
        """
        Remove a document from a binder.

        API Documentation: https://developer.veevavault.com/api/23.2/#remove-document-from-binder

        :param binder_id: The binder id field value.
        :type binder_id: str
        :param section_id: The binder node id field value.
        :type section_id: str
        :return: Response JSON containing the Node ID of the deleted document.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/documents/{section_id}"

        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }

        response = requests.delete(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to remove document from binder. Status code: {response.status_code}"}




    #######################################################
    # Binders
    ## Binder Templates
    #######################################################

    def retrieve_binder_template_metadata(self):
        """
        Retrieve the metadata which defines the shape of binder templates in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-binder-template-metadata

        :return: Response JSON containing metadata of binder templates.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/binders/templates"

        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to retrieve binder template metadata. Status code: {response.status_code}"}

    def retrieve_binder_template_node_metadata(self):
        """
        Retrieve the metadata which defines the shape of binder template nodes in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-binder-template-node-metadata

        :return: Response JSON containing metadata of binder template nodes.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/binders/templates/bindernodes"

        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to retrieve binder template node metadata. Status code: {response.status_code}"} 

    def retrieve_binder_template_collection(self):
        """
        Retrieve the collection of all binder templates in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-binder-template-collection

        :return: Response JSON containing the collection of binder templates.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/templates"

        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to retrieve binder template collection. Status code: {response.status_code}"} 


    def retrieve_binder_template_attributes(self, template_name):
        """
        Retrieve the attributes of a specific binder template in your Vault.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-binder-template-attributes

        :param template_name: The binder template name__v field value.
        :type template_name: str
        :return: Response JSON containing the attributes of the specified binder template.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/templates/{template_name}"

        headers = {
            'Accept': 'application/json',
            'Authorization': self.sessionId,
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            return {'error': f"Failed to retrieve binder template attributes. Status code: {response.status_code}"}


    def retrieve_binder_template_node_attributes(self, template_name):
        """
        Retrieves the attributes of each node (folder/section) of a specific binder template in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-binder-template-node-attributes

        :param template_name: The binder template name__v field value.
        :return: A JSON object containing the attributes of each node of a specific binder template in the Vault.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/templates/{template_name}/bindernodes"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()


    def create_binder_template(self, label_v, type_v, active_v, name_v=None, subtype_v=None, classification_v=None):
        """
        Create a new binder template in your Vault.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#create-binder-template
        
        Parameters:
        label_v (str): The label of the new binder template. This is the name users will see among the available binder templates in the UI.
        type_v (str): The name of the document type to which the template will be associated.
        active_v (bool): Set to true or false to indicate whether or not the new binder template should be set to active, i.e., available for selection when creating a binder.
        name_v (str, optional): The name of the new binder template. If not included, Vault will use the specified label_v value to generate a value for the name_v field.
        subtype_v (str, optional): The name of the document subtype to which the template will be associated. This is only required if associating the template with a document subtype.
        classification_v (str, optional): The name of the document classification to which the template will be associated. This is only required if associating the template with a document classification.
        
        Returns:
        response (dict): The response from the API call.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/templates"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        data = {
            "label__v": label_v,
            "type__v": type_v,
            "active__v": str(active_v).lower()
        }
        
        if name_v:
            data["name__v"] = name_v
        if subtype_v:
            data["subtype__v"] = subtype_v
        if classification_v:
            data["classification__v"] = classification_v
        
        response = requests.post(url, headers=headers, data=data).json()
        
        return response.json()

    def bulk_create_binder_templates(self, file_path):
        """
        Bulk create from 1-500 new binder templates in your Vault.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#bulk-create-binder-templates
        
        Parameters:
        file_path (str): The path to the CSV file containing the data of the binder templates to be created.
        
        Returns:
        response (dict): The response from the API call.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/templates"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }
        
        with open(file_path, 'rb') as file:
            response = requests.post(url, headers=headers, data=file).json()
        
        return response.json()


    def create_binder_template_node(self, template_name, file_path):
        """
        Create nodes in an existing binder template.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#create-binder-template-node
        
        Parameters:
        template_name (str): The binder template name__v field value.
        file_path (str): The path to the CSV file containing the data of the binder nodes to be created.
        
        Returns:
        response (dict): The response from the API call.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/templates/{template_name}/bindernodes"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }
        
        with open(file_path, 'rb') as file:
            response = requests.post(url, headers=headers, data=file).json()
        
        return response.json()


    def update_binder_template(self, template_name, payload):
        """
        Update an existing binder template in your Vault.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#update-binder-template
        
        Parameters:
        template_name (str): The binder template name__v field value.
        payload (dict): The data containing the fields to update. 
        
        Returns:
        response (str): The response from the API call in text/csv format.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/templates/{template_name}"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "text/csv"
        }
        
        response = requests.put(url, headers=headers, data=payload).text
        
        return response.json()


    def bulk_update_binder_templates(self, file_path):
        """
        Bulk update from 1-500 binder templates in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#bulk-update-binder-templates
        
        Parameters:
        file_path (str): The path to the CSV input file with details of binder templates to be updated.
        
        Returns:
        response (json): The response from the API call, which includes the status and details of each update.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/templates"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "text/csv",
            "Accept": "text/csv"
        }
        
        with open(file_path, 'rb') as f:
            response = requests.put(url, headers=headers, data=f).json()
        
        return response.json()


    def replace_binder_template_nodes(self, template_name, input_data):
        """
        Replace all binder nodes in an existing binder template. This action removes all existing nodes and replaces them with those specified in the input.

        API Documentation: https://developer.veevavault.com/api/23.2/#replace-binder-template-nodes
        
        Parameters:
        template_name (str): The binder template name__v field value.
        input_data (str or dict): The input data in JSON format or the path to the CSV file containing the nodes to be replaced.
        
        Returns:
        response (json): The response from the API call, which indicates the success or failure of the operation.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/templates/{template_name}/bindernodes"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if isinstance(input_data, dict):
            response = requests.put(url, headers=headers, json=input_data).json()
        else:
            with open(input_data, 'rb') as f:
                headers["Content-Type"] = "text/csv"
                response = requests.put(url, headers=headers, data=f).json()
        
        return response.json()


    def delete_binder_template(self, template_name):
        """
        Delete an existing binder template from your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#delete-binder-template
        
        Parameters:
        template_name (str): The binder template name__v field value.
        
        Returns:
        response (json): The response from the API call, which indicates the success or failure of the operation.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/templates/{template_name}"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.delete(url, headers=headers).json()
        
        return response.json()


    #######################################################
    # Binders
    ## Binding Rules
    #######################################################

    def update_binding_rule(self, binder_id, binding_rule__v=None, binding_rule_override__v=None):
        """
        Update a binding rule in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#update-binding-rule

        Parameters:
        binder_id (str): The binder id field value.
        binding_rule__v (str): Optional. Indicates which binding rule to apply. Options are: 'default', 'steady-state', or 'current'.
        binding_rule_override__v (bool): Optional. Indicates if the specified binding rule should override documents or sections which already have binding rules set.

        Returns:
        response (json): The response from the API call, which indicates the success or failure of the operation.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/binding_rule"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "binding_rule__v": binding_rule__v,
            "binding_rule_override__v": binding_rule_override__v
        }
        
        response = requests.put(url, headers=headers, data=data).json()
        
        return response.json()


    def update_binder_section_binding_rule(self, binder_id, node_id, binding_rule__v=None, binding_rule_override__v=None):
        """
        Update a binding rule for a specific section in a binder in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#update-binder-section-binding-rule

        Parameters:
        binder_id (str): The binder id field value.
        node_id (str): The binder node id field value.
        binding_rule__v (str): Optional. Indicates which binding rule to apply. Options are: 'default', 'steady-state', or 'current'.
        binding_rule_override__v (bool): Optional. Indicates if the specified binding rule should override documents or sections which already have binding rules set.

        Returns:
        response (json): The response from the API call, which indicates the success or failure of the operation, along with the Node ID of the updated section.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/sections/{node_id}/binding_rule"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "binding_rule__v": binding_rule__v,
            "binding_rule_override__v": binding_rule_override__v
        }
        
        response = requests.put(url, headers=headers, data=data).json()
        
        return response.json()


    def update_binder_document_binding_rule(self, binder_id, node_id, binding_rule__v=None, major_version_number__v=None, minor_version_number__v=None):
        """
        Update the binding rule for a document node within a binder in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#update-binder-document-binding-rule

        Parameters:
        binder_id (str): The binder id field value.
        node_id (str): The binder node id field value.
        binding_rule__v (str): Optional. Indicates which binding rule to apply. Options are: 'default', 'steady-state', 'current', or 'specific'.
        major_version_number__v (int): Optional. Required if binding_rule is 'specific'. Indicates the major version of the document to be linked.
        minor_version_number__v (int): Optional. Required if binding_rule is 'specific'. Indicates the minor version of the document to be linked.

        Returns:
        response (json): The response from the API call, which indicates the success or failure of the operation, along with the Node ID of the updated document node within the binder.
        """
        
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/documents/{node_id}/binding_rule"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "binding_rule__v": binding_rule__v,
            "major_version_number__v": major_version_number__v,
            "minor_version_number__v": minor_version_number__v
        }
        
        response = requests.put(url, headers=headers, data=data).json()
        
        return response.json()



    #######################################################
    # Vault Objects
    #######################################################


    def retrieve_object_metadata(self, object_name, loc=False):
        """
        Retrieve all metadata configured on a standard or custom Vault Object.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-metadata
        
        Parameters:
        object_name (str): The object name__v field value. For example, product__v, country__v, custom_object__c.
        loc (bool): Set to true to retrieve the localized_data array, which contains the localized (translated) strings 
                    for the label and label_plural object fields. If omitted, defaults to false and localized Strings are not included.
                    
        Returns:
        dict: Response data containing metadata information.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/vobjects/{object_name}"
        headers = {
            'Accept': 'application/json',
            'Authorization': f"{self.sessionId}"
        }
        
        params = {
            'loc': loc
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()


    def retrieve_object_field_metadata(self, object_name, object_field_name, loc=False):
        """
        Retrieves metadata for a specified field of a specified object in the vault. 
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-field-metadata
        
        Parameters:
            object_name (str): The object name__v field value (e.g., product__v, country__v, custom_object__c).
            object_field_name (str): The object field name value (e.g., id, name__v, external_id__v).
            loc (bool): Set to true to retrieve the localized_data array. Defaults to false.
            
        Returns:
            dict: A dictionary containing the metadata of the specified object field.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/vobjects/{object_name}/fields/{object_field_name}"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        params = {
            "loc": loc
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def retrieve_object_collection(self, loc=False):
        """
        Retrieve all Vault objects in the authenticated Vault.
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-collection
        
        Parameters:
            loc (bool): Set to true to retrieve localized (translated) strings for the label and label_plural object fields. Defaults to false.
        
        Returns:
            dict: A dictionary containing a summary of key information for all standard and custom Vault Objects configured in your Vault.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/vobjects"
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        params = {
            "loc": loc
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.json()
        else:
            response.raise_for_status()


    def retrieve_object_record_collection(self, object_name, fields=None, limit=None, offset=None, sort=None):
        """
        Retrieves all records for a specific Vault Object.
        
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-record-collection
        
        Args:
            object_name (str): The object name__v field value. For example, product__v, country__v, custom_object__c.
            fields (str, optional): To specify fields to retrieve, include the parameter fields={FIELD_NAMES}. Defaults to None.
            limit (int, optional): The number of records to return per page, maximum 200. Defaults to None.
            offset (int, optional): The starting point for the return of the records. Defaults to None.
            sort (str, optional): The sorting parameter in the format "field_name order". For example, "name__v desc". Defaults to None.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}"
        
        params = {}
        if fields:
            params['fields'] = fields
        if limit:
            params['limit'] = limit
        if offset:
            params['offset'] = offset
        if sort:
            params['sort'] = sort

        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def retrieve_object_record(self, object_name, object_record_id):
        """
        Retrieves metadata configured on a specific object record in your Vault.
        
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-record
        
        Args:
            object_name (str): The object name__v field value (product__v, country__v, custom_object__c, etc.).
            object_record_id (str): The object record id field value.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def create_object_records(self, object_name, data, content_type='text/csv', accept='text/csv', additional_headers=None):
        """
        Create Vault object records in bulk using the specified endpoint. For detailed documentation refer to:
        https://developer.veevavault.com/api/23.2/#create-object-records
        
        Args:
            object_name (str): The name of the object (e.g., product__v).
            data (str): The data to be sent in the request body (file path or JSON).
            content_type (str, optional): The content type of the request. Defaults to 'text/csv'.
            accept (str, optional): The accept header specifying the response format. Defaults to 'text/csv'.
            additional_headers (dict, optional): Additional headers to be included in the request. Defaults to None.
        
        Returns:
            dict: The response data in dictionary format.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": content_type,
            "Accept": accept,
        }
        
        if additional_headers:
            headers.update(additional_headers)
        
        with open(data, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
        
        return response.json()


    def update_object_records(self, object_name, data, id_param=None, migration_mode=None):
        """
        Updates object records in bulk. You can use this method to update user records (user__sys).

        API Documentation: https://developer.veevavault.com/api/23.2/#update-object-records

        Args:
            object_name (str): The name of the object, for example, product__v.
            data (dict): The data to update in either JSON or CSV format.
            id_param (str, optional): To identify objects in your input by a unique field, add idParam={field_name} to the request endpoint. Defaults to None.
            migration_mode (bool, optional): If set to true, Vault bypasses entry criteria, entry actions, validation rules, and reference constraints when updating object records. Defaults to None.

        Returns:
            dict: The response from the API.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if migration_mode is not None:
            headers["X-VaultAPI-MigrationMode"] = str(migration_mode)
        
        response = requests.put(url, headers=headers, json=data)
        if id_param:
            url += f"?idParam={id_param}"
            response = requests.put(url, headers=headers, json=data)
        
        return response.json()


    def delete_object_records(self, object_name, data, id_param=None):
        """
        Deletes object records in bulk. This method cannot be used to delete user__sys records. 
        Use the update_object_records method to set the status__v field to inactive for user__sys records.

        API Documentation: https://developer.veevavault.com/api/23.2/#delete-object-records

        Args:
            object_name (str): The name of the object, e.g., product__v.
            data (dict): The data to delete in either JSON or CSV format, containing ids or external_ids.
            id_param (str, optional): If you’re identifying objects in your input by a unique field, add this parameter. Defaults to None.

        Returns:
            dict: The response from the API.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        if id_param:
            url += f"?idParam={id_param}"
        
        response = requests.delete(url, headers=headers, json=data)
        
        return response.json()

    def cascade_delete_object_record(self, object_name, object_record_id):
        """
        This asynchronous method deletes a single parent object record and all related children and grandchildren.

        API Documentation: https://developer.veevavault.com/api/23.2/#cascade-delete-object-record

        Args:
            object_name (str): The name of the object to delete.
            object_record_id (str): The ID of the specific object record to delete.

        Returns:
            dict: The response from the API, including job ID and URL to track the status of the deletion.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/actions/cascadedelete"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.post(url, headers=headers)
        
        return response.json()



    def retrieve_cascade_delete_results(self, object_name, job_status, job_id):
        """
        This method retrieves the results of a cascade delete job. Before submitting this request:
        - You must have previously requested a cascade delete job (via the API) which is no longer active.
        - You must have a valid job_id value, retrieved from the response of the cascade delete request.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-results-of-cascade-delete-job

        Args:
            object_name (str): The name of the object which was deleted.
            job_status (str): Possible values are 'success' or 'failure'. It is used to determine the job status.
            job_id (str): The ID of the job, retrieved from the response of the job request.

        Returns:
            Response: The response from the API with the details of the deleted records.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/cascadedelete/results/{object_name}/{job_status}/{job_id}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "text/csv"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.text



    #######################################################
    # Vault Objects
    ## Object Types
    #######################################################

    def retrieve_details_from_all_object_types(self):
        """
        This method retrieves details from all object types. It lists all object types and all fields configured on each object type.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-details-from-all-object-types

        Returns:
            Response: The response from the API with the details of all object types and fields configured on each type.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/configuration/Objecttype"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_details_from_specific_object(self, object_name_and_object_type):
        """
        This method retrieves details from a specific object. It lists all object types and all fields configured on each object type for the specified object.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-details-from-a-specific-object

        Args:
            object_name_and_object_type (str): The object name followed by the object type in the format Objecttype.{object_name}.{object_type}. 

        Returns:
            Response: The response from the API listing all object types and fields configured on the specific object.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/configuration/{object_name_and_object_type}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()

    def change_object_type(self, object_name, payload):
        """
        This method is used to change the object types assigned to object records. Field values which exist on both the original and new object type will carry over to the new type. All other field values will be removed as only fields on the new type are valid. You can set field values on the new object type in the payload input.

        API Documentation: https://developer.veevavault.com/api/23.2/#change-object-type

        Args:
            object_name (str): The name of the object.
            payload (dict): A dictionary containing at least the "id" and "object_type__v" keys. The "id" key should map to the ID of the object record and the "object_type__v" key should map to the ID of the new object type.

        Returns:
            Response: The response from the API after attempting to change the object type.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/actions/changetype"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        return response.json()





    #######################################################
    # Vault Objects
    ## Object Roles
    #######################################################




    def retrieve_object_record_roles(self, object_name, record_id, role_name=None):
        """
        This method is used to retrieve manually assigned roles on an object record along with the users and groups assigned to those roles.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-record-roles

        Args:
            object_name (str): The name of the object.
            record_id (str): The ID of the document, binder, or object record.
            role_name (str, optional): Role name to filter for a specific role, e.g., owner__v. Defaults to None.

        Returns:
            Response: The response from the API containing the roles and their details.
        """
        self.LatestAPIversion = 'v23.2'
        
        role_name_path = f"/{role_name}" if role_name else ""
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{record_id}/roles{role_name_path}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def assign_users_groups_to_roles_on_object_records(self, object_name, request_body):
        """
        This method allows to assign users and groups to roles on an object record in bulk.

        API Documentation: https://developer.veevavault.com/api/23.2/#assign-users-amp-groups-to-roles-on-object-records

        Args:
            object_name (str): The name of the object where you want to update records.
            request_body (str or dict): JSON or CSV input file as string or dictionary. User and group assignments are 
                                        ignored if they are invalid, inactive, or already exist.
        
        Returns:
            Response: The response from the API, which includes the object record ID on success.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/roles"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(url, headers=headers, data=json.dumps(request_body))
        
        return response.json()


    def remove_users_groups_from_roles_on_object_records(self, object_name, request_body):
        """
        This method allows to remove users and groups from roles on an object record in bulk.

        API Documentation: https://developer.veevavault.com/api/23.2/#remove-users-amp-groups-from-roles-on-object-records

        Args:
            object_name (str): The name of the object where you want to remove roles.
            request_body (str or dict): JSON or CSV input file as string or dictionary. Users and groups are ignored if they are 
                                        invalid or inactive.
        
        Returns:
            Response: The response from the API, which includes the object record ID on success.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/roles"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.delete(url, headers=headers, data=json.dumps(request_body))
        
        return response.json()





    #######################################################
    # Vault Objects
    ## Object Record Attachments
    #######################################################

    def determine_if_attachments_are_enabled_on_an_object(self, object_name):
        """
        This method helps to determine if attachments are enabled on a specific object.

        API Documentation: https://developer.veevavault.com/api/23.2/#determine-if-attachments-are-enabled-on-an-object

        Args:
            object_name (str): The value of object name__v field (like product__v, country__v, custom_object__c, etc.).
        
        Returns:
            Response: API response which includes details such as if "allow_attachments" is set to true and other object metadata.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/vobjects/{object_name}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_object_record_attachments(self, object_name, object_record_id):
        """
        Retrieve a list of all attachments on a specific object record.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-record-attachments

        Args:
            object_name (str): The value of object name__v field (like product__v, country__v, custom_object__c, etc.).
            object_record_id (str): The object record id field value.

        Returns:
            Response: API response which includes details such as a list of attachments along with their respective details and versions.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()



    def retrieve_object_record_attachment_metadata(self, object_name, object_record_id, attachment_id):
        """
        Retrieve the metadata of a specific attachment on a specific object record.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-record-attachment-metadata

        Args:
            object_name (str): The value of the object name__v field (like product__v, country__v, custom_object__c, etc.).
            object_record_id (str): The object record id field value.
            attachment_id (str): The attachment id field value.

        Returns:
            Response: API response which includes metadata details of the specified attachment.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments/{attachment_id}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_object_record_attachment_versions(self, object_name, object_record_id, attachment_id):
        """
        Retrieve all versions of a specific attachment on a specific object record.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-record-attachment-versions

        Args:
            object_name (str): The value of the object name__v field (like product__v, country__v, custom_object__c, etc.).
            object_record_id (str): The object record id field value.
            attachment_id (str): The attachment id field value.

        Returns:
            Response: API response which includes version details of the specified attachment.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments/{attachment_id}/versions"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_object_record_attachment_version_metadata(self, object_name, object_record_id, attachment_id, attachment_version):
        """
        Retrieve the metadata of a specific version of an attachment on a specific object record.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-record-attachment-version-metadata

        Args:
            object_name (str): The value of the object name__v field (like product__v, country__v, custom_object__c, etc.).
            object_record_id (str): The object record id field value.
            attachment_id (str): The attachment id field value.
            attachment_version (str): The attachment version__v field value.

        Returns:
            Response: API response which includes metadata of the specified attachment version.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments/{attachment_id}/versions/{attachment_version}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()

    def download_object_record_attachment_file(self, object_name, object_record_id, attachment_id):
        """
        Download the file of a specific attachment on a specific object record.

        API Documentation: https://developer.veevavault.com/api/23.2/#download-object-record-attachment-file

        Args:
            object_name (str): The value of the object name__v field (like product__v, country__v, custom_object__c, etc.).
            object_record_id (str): The object record id field value.
            attachment_id (str): The attachment id field value.

        Returns:
            Response: The API response containing the attachment file.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments/{attachment_id}/file"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, stream=True)
        
        with open('downloaded_attachment_file', 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return "File downloaded successfully"


    def download_object_record_attachment_version_file(self, object_name, object_record_id, attachment_id, attachment_version):
        """
        Downloads a specific version of an attachment file from a specific object record.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#download-object-record-attachment-version-file
        
        Args:
            object_name (str): The value of the object name__v field (like product__v, country__v, custom_object__c, etc.).
            object_record_id (str): The object record id field value.
            attachment_id (str): The attachment id field value.
            attachment_version (str): The attachment version__v field value.

        Returns:
            str: Message indicating the success of the file download.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments/{attachment_id}/versions/{attachment_version}/file"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, stream=True)
        
        with open('downloaded_attachment_version_file', 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return "File downloaded successfully"


    def download_all_object_record_attachment_files(self, object_name, object_record_id):
        """
        Downloads the latest version of all attachment files from a specific object record, packaged in a ZIP file.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#download-all-object-record-attachment-files
        
        Args:
            object_name (str): The value of the object name__v field (like product__v, country__v, custom_object__c, etc.).
            object_record_id (str): The object record id field value.

        Returns:
            str: Message indicating the success of the file download.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments/file"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, stream=True)
        
        with open('downloaded_all_attachment_files.zip', 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        
        return "File downloaded successfully"


    def create_object_record_attachment(self, object_name, object_record_id, file_path):
        """
        Creates a single object record attachment. If the attachment already exists, Vault uploads the attachment 
        as a new version of the existing attachment. The maximum allowed file size is 4GB.

        API Documentation: https://developer.veevavault.com/api/23.2/#create-object-record-attachment
        
        Args:
            object_name (str): The value of the object name__v field (like product__v, country__v, custom_object__c, etc.).
            object_record_id (str): The object record id field value.
            file_path (str): The path to the file to be uploaded.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        files = {'file': open(file_path, 'rb')}
        
        response = requests.post(url, headers=headers, files=files)
        
        return response.json()



    def create_multiple_object_record_attachments(self, object_name, input_file_path, content_type='text/csv', accept='application/json'):
        """
        Creates multiple object record attachments in bulk using a JSON or CSV input file. The attachments are first 
        loaded to the file staging server. The maximum input file size is 1GB, and the maximum batch size is 500.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#create-multiple-object-record-attachments

        Args:
            object_name (str): The value of the object name__v field (like veterinary_patient__c, product__v, etc.).
            input_file_path (str): The path to the input file (CSV or JSON) containing details of attachments to be created.
            content_type (str): The content type of the input file, either 'application/json' or 'text/csv'. Defaults to 'text/csv'.
            accept (str): The response format, either 'application/json' or 'application/xml'. Defaults to 'application/json'.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/attachments/batch"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": content_type,
            "Accept": accept
        }
        
        with open(input_file_path, 'rb') as input_file:
            data = input_file.read()
        
        response = requests.post(url, headers=headers, data=data)
        
        return response.json()


    def restore_object_record_attachment_version(self, object_name, object_record_id, attachment_id, attachment_version):
        """
        Restores a specific version of an attachment on an object record.

        API Documentation: https://developer.veevavault.com/api/23.2/#restore-object-record-attachment-version

        Args:
            object_name (str): The value of the object name__v field (like product__v, country__v, etc.).
            object_record_id (str): The object record id field value.
            attachment_id (str): The attachment id field value.
            attachment_version (str): The attachment version__v field value.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments/{attachment_id}/versions/{attachment_version}?restore=true"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.post(url, headers=headers)
        
        return response.json()

    def update_object_record_attachment_description(self, object_name, object_record_id, attachment_id, description):
        """
        Updates the description of a specific attachment on an object record.

        API Documentation: https://developer.veevavault.com/api/23.2/#update-object-record-attachment-description

        Args:
            object_name (str): The value of the object name__v field (like product__v, country__v, etc.).
            object_record_id (str): The object record id field value.
            attachment_id (str): The attachment id field value.
            description (str): The new description for the attachment. The maximum length is 1000 characters.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments/{attachment_id}"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        data = {
            "description__v": description
        }
        
        response = requests.put(url, headers=headers, data=data)
        
        return response.json()



    def update_multiple_object_record_attachment_descriptions(self, object_name, input_file_path, content_type='text/csv', accept='application/json'):
        """
        Update multiple object record attachment descriptions in bulk using a JSON or CSV input file.

        API Documentation: https://developer.veevavault.com/api/23.2/#update-multiple-object-record-attachment-descriptions

        Args:
            object_name (str): The object name__v field value (e.g., veterinary_patient__c).
            input_file_path (str): The path to the input CSV or JSON file.
            content_type (str, optional): The content type of the input file, either 'application/json' or 'text/csv'. Defaults to 'text/csv'.
            accept (str, optional): The response format, either 'application/json' or 'application/xml'. Defaults to 'application/json'.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/attachments/batch"

        headers = {
            "Authorization": self.sessionId,
            "Content-Type": content_type,
            "Accept": accept
        }

        with open(input_file_path, 'rb') as f:
            response = requests.put(url, headers=headers, data=f)

        return response.json()


    def delete_object_record_attachment(self, object_name, object_record_id, attachment_id, accept='application/json'):
        """
        Deletes a single object record attachment.

        API Documentation: https://developer.veevavault.com/api/23.2/#delete-object-record-attachment

        Args:
            object_name (str): The object name__v field value (e.g., product__v, country__v, custom_object__c, etc.).
            object_record_id (str): The object record id field value.
            attachment_id (str): The attachment id field value.
            accept (str, optional): The response format, either 'application/json' or 'application/xml'. Defaults to 'application/json'.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments/{attachment_id}"

        headers = {
            "Authorization": self.sessionId,
            "Accept": accept
        }

        response = requests.delete(url, headers=headers)
        
        return response.json()


    def delete_multiple_object_record_attachments(self, object_name, attachments_data, content_type='application/json', accept='application/json', id_param=None):
        """
        Deletes multiple object record attachments in bulk with a JSON or CSV input file. 

        API Documentation: https://developer.veevavault.com/api/23.2/#delete-multiple-object-record-attachments

        Args:
            object_name (str): The object name__v field value (e.g., veterinary_patient__c, product__v, etc.).
            attachments_data (str): JSON or CSV formatted string containing details of the attachments to be deleted.
            content_type (str, optional): The format of the input data, either 'application/json' or 'text/csv'. Defaults to 'application/json'.
            accept (str, optional): The response format, either 'application/json' or 'application/xml'. Defaults to 'application/json'.
            id_param (str, optional): If identifying attachments by external id, add idParam=external_id__v to the request endpoint. Defaults to None.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/attachments/batch"
        if id_param:
            url += f"?idParam={id_param}"

        headers = {
            "Authorization": self.sessionId,
            "Accept": accept,
            "Content-Type": content_type
        }

        response = requests.delete(url, headers=headers, data=attachments_data)
        
        return response.json()


    def delete_object_record_attachment_version(self, object_name, object_record_id, attachment_id, attachment_version, accept='application/json'):
        """
        Deletes a specific version of an object record attachment.

        API Documentation: https://developer.veevavault.com/api/23.2/#delete-object-record-attachment-version

        Args:
            object_name (str): The object name__v field value (e.g., product__v, country__v, etc.).
            object_record_id (str): The object record id field value.
            attachment_id (str): The attachment id field value.
            attachment_version (str): The attachment version__v field value.
            accept (str, optional): The response format, either 'application/json' or 'application/xml'. Defaults to 'application/json'.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/attachments/{attachment_id}/versions/{attachment_version}"

        headers = {
            "Authorization": self.sessionId,
            "Accept": accept
        }

        response = requests.delete(url, headers=headers)
        
        return response.json()






    #######################################################
    # Vault Objects
    ## Object Page Layouts
    #######################################################

    def retrieve_page_layouts(self, object_name, accept='application/json'):
        """
        Retrieves all page layouts associated with the specified object.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-page-layouts

        Args:
            object_name (str): The name of the object from which to retrieve page layouts.
            accept (str, optional): The response format, either 'application/json' or 'application/xml'. Defaults to 'application/json'.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/vobjects/{object_name}/page_layouts"

        headers = {
            "Authorization": self.sessionId,
            "Accept": accept
        }

        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_page_layout_metadata(self, object_name, layout_name, accept='application/json'):
        """
        Retrieves the metadata for the specified page layout.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-page-layout-metadata

        Args:
            object_name (str): The name of the object from which to retrieve page layout metadata.
            layout_name (str): The name of the page layout from which to retrieve metadata.
            accept (str, optional): The response format, either 'application/json' or 'application/xml'. Defaults to 'application/json'.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/vobjects/{object_name}/page_layouts/{layout_name}"

        headers = {
            "Authorization": self.sessionId,
            "Accept": accept
        }

        response = requests.get(url, headers=headers)
        
        return response.json()

    async def retrieve_all_page_layout_metadata_for_object(self, object_name):
        """
        Asynchronously retrieves all page layout metadata for a specified object.

        This function performs the following steps:
        1. Retrieves all page layouts for the specified object.
        2. Converts the retrieved page layouts data to a pandas DataFrame.
        3. Retrieves the metadata for each page layout asynchronously.
        4. Converts the retrieved page layout metadata to a pandas DataFrame.
        
        Args:
            object_name (str): The name of the object for which to retrieve the page layout metadata.

        Returns:
            pd.DataFrame: A DataFrame containing the page layout metadata for the specified object.

        Usage:
            >>> page_layouts_df = asyncio.run(retrieve_all_page_layout_metadata_for_object('my_object_name'))
        """
        page_layouts = self.retrieve_page_layouts(object_name)['data']
        page_layouts_df = pd.DataFrame(page_layouts)
        
        async_retrieve_page_layout_metadata = async_wrap(self.retrieve_page_layout_metadata)
        
        page_layout_names = page_layouts_df['name'].tolist()
        
        page_layout_metadata = await asyncio.gather(*[async_retrieve_page_layout_metadata(object_name, page_layout_name) for page_layout_name in page_layout_names])
        page_layout_metadata = [x['data'] for x in page_layout_metadata]
        
        page_layouts_df = pd.DataFrame(page_layout_metadata)
        
        return page_layouts_df



    #######################################################
    # Vault Objects
    ## Deep Copy Object Record
    #######################################################

    def deep_copy_object_record(self, object_name, object_record_ID, override_fields=None, content_type='application/json', accept='application/json'):
        """
        Performs a deep copy of an object record, including all of its related child and grandchild records.

        API Documentation: https://developer.veevavault.com/api/23.2/#deep-copy-object-record

        Args:
            object_name (str): The name of the parent object to copy (e.g., product__v).
            object_record_ID (str): The ID of the specific object record to copy.
            override_fields (dict, optional): A dictionary with field names to override field values in the source record. Defaults to None.
            content_type (str, optional): The content type of the request, either 'application/json' or 'text/csv'. Defaults to 'application/json'.
            accept (str, optional): The response format, either 'application/json' or 'application/xml'. Defaults to 'application/json'.

        Returns:
            dict: The API response as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_ID}/actions/deepcopy"

        headers = {
            "Authorization": self.sessionId,
            "Content-Type": content_type,
            "Accept": accept
        }

        response = requests.post(url, headers=headers, json=override_fields)
        
        return response.json()

    def retrieve_deep_copy_job_results(self, object_name, job_id, job_status, accept='text/csv'):
        """
        Retrieves the results of a deep copy job request. The function can query Vault to determine 
        the results of a deep copy request.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-results-of-deep-copy-job

        Args:
            object_name (str): The name of the deep copied object.
            job_id (str): The ID of the job, retrieved from the response of the job request.
            job_status (str): The status of the job, possible values are 'success' or 'failure'.
            accept (str, optional): The response format, defaults to 'text/csv'.

        Returns:
            Response: The API response.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/deepcopy/results/{object_name}/{job_status}/{job_id}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": accept
        }

        response = requests.post(url, headers=headers)
        
        return response.json()





    #######################################################
    # Vault Objects
    ## Retrieve
    #######################################################

    def retrieve_deleted_object_record_id(self, object_name, start_date=None, end_date=None, limit=1000, offset=0):
        """
        Retrieves the IDs of object records that have been deleted from the Vault within the past 30 days. The IDs remain 
        retrievable for 30 days post-deletion. The results can be narrowed down to a specific date and time range 
        within the past 30 days using optional parameters.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-deleted-object-record-id

        Args:
            object_name (str): The object name__v field value (e.g., product__v, country__v, custom_object__c, etc.).
            start_date (str, optional): A date (within the past 30 days) post which the API looks for deleted records. 
                Dates must be formatted as YYYY-MM-DDTHH:MM:SSZ. Defaults to None.
            end_date (str, optional): A date (within the past 30 days) before which the API looks for deleted records. 
                Dates must be formatted as YYYY-MM-DDTHH:MM:SSZ. Defaults to None.
            limit (int, optional): The maximum number of records per page in the response (between 1 and 1000). 
                Defaults to 1000.
            offset (int, optional): The offset for pagination, determining the starting point of the records 
                in the response. Defaults to 0.

        Returns:
            Response: The API response.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/deletions/vobjects/{object_name}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit,
            "offset": offset
        }

        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def retrieve_limits_on_objects(self):
        """
        Retrieves the limitations imposed on the number of object records that can be created for each object 
        (product__v, study__v, custom_object__c, etc.) in the Vault. Additionally, it retrieves the limit on the 
        number of custom objects that can be created in the Vault and the remaining number available for creation.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-limits-on-objects

        Returns:
            Response: The API response containing details about the limits on objects.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/limits"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()




    #######################################################
    # Vault Objects
    ## Update Corporate Currency Fields
    #######################################################


    def update_corporate_currency_fields(self, object_name, record_id=None):
        """
        Updates the corporate currency fields of an object record based on the rate of the currency denoted by
        the local_currency__sys field of the specified record. It handles scenarios like when admins change 
        the Corporate Currency setting for the vault or update the Rate setting for the local currency used by a record.

        API Documentation: https://developer.veevavault.com/api/23.2/#update-corporate-currency-fields

        Args:
            object_name (str): The object name__v field value (for example, product__v).
            record_id (str, optional): The object record id field value. If not provided, Vault updates corporate fields of 
                                    all records for the object.

        Returns:
            Response: The API response containing details about the job initiated for updating the corporate currency fields.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/actions/updatecorporatecurrency"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        payload = {}
        if record_id:
            payload['id'] = record_id

        response = requests.put(url, headers=headers, json=payload)
        
        return response.json()


    #######################################################
    # Document Roles
    #######################################################


    def retrieve_roles(self, doc_or_binder, id, role_name=None):
        """
        Retrieve all available roles on a document or binder along with the users and groups assigned to them.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-roles

        Args:
            doc_or_binder (str): Specify whether to retrieve values for "documents" or "binders".
            id (int): The id of the document, binder, or object record.
            role_name (str, optional): Include a role name to filter for a specific role, e.g., "owner__v".

        Returns:
            Response: The API response containing the details of the roles assigned to the specified document or binder.
        """
        self.LatestAPIversion = 'v23.2'

        role_name_endpoint = f"/{role_name}" if role_name else ""
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/{doc_or_binder}/{id}/roles{role_name_endpoint}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()


    def assign_users_and_groups_to_roles(self, document_id, roles_data):
        """
        Assign users and groups to roles on a single document or binder.

        API Documentation: https://developer.veevavault.com/api/23.2/#assign-users-amp-groups-to-roles-on-a-single-document

        Args:
            document_id (int): The document or binder id field value.
            roles_data (dict): A dictionary with name-value pairs of all users or groups with their corresponding roles 
                            in the form {Role_name}.{USERS or GROUPS}: "ID1,ID2,ID3". 
                            For example, {'reviewer__v.users': "3003,4005"}.

        Returns:
            Response: The API response containing details of users and groups successfully assigned to roles on the document or binder.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{document_id}/roles"

        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        response = requests.post(url, headers=headers, data=roles_data)
        
        return response.json()


    def assign_users_and_groups_to_roles_bulk(self, csv_file_path):
        """
        Assign users and groups to roles on multiple documents or binders in bulk.

        API Documentation: https://developer.veevavault.com/api/23.2/#assign-users-amp-groups-to-roles-on-multiple-documents

        Args:
            csv_file_path (str): The path to the CSV file containing the assignment data.

        Returns:
            Response: The API response containing details of users and groups successfully assigned to roles on multiple documents or binders.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/roles/batch"

        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "text/csv",
            "Accept": "text/csv"
        }

        with open(csv_file_path, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)

        return response.json()


    def remove_users_and_groups_from_role(self, doc_id, role_name_and_user_or_group, user_or_group_id):
        """
        Remove users and groups from roles on a single document or binder.

        API Documentation: https://developer.veevavault.com/api/23.2/#remove-users-amp-groups-from-roles-on-a-single-document

        Args:
            doc_id (str): The ID value of the document or binder from which to remove roles.
            role_name_and_user_or_group (str): The name of the role and user or group from which to remove. The format is {role_name}.{user_or_group}.
            user_or_group_id (str): The ID value of the user or group to remove from the role.

        Returns:
            Response: The API response containing the status and details of the removal process.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/roles/{role_name_and_user_or_group}/{user_or_group_id}"

        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.delete(url, headers=headers)
        
        return response.json()


    def remove_users_and_groups_from_roles_on_multiple_documents(self, csv_file_path):
        """
        Remove users and groups from roles on a document or binder in bulk.

        API Documentation: https://developer.veevavault.com/api/23.2/#remove-users-and-groups-from-roles-on-multiple-documents

        Args:
            csv_file_path (str): The path to the CSV file containing the details of the users and groups to be removed.

        Returns:
            Response: The API response containing the status and details of the removal process.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/roles/batch"

        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "text/csv",
            "Accept": "text/csv"
        }

        with open(csv_file_path, 'rb') as f:
            response = requests.delete(url, headers=headers, data=f)
        
        return response.json()






    #######################################################
    # Workflows
    #######################################################


    def retrieve_workflows(self, object_v=None, record_id_v=None, participant=None, status_v=None, offset=None, page_size=None, loc=None):
        """
        Retrieve all workflow instances for a specific object and object record or from a specific workflow participant.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-workflows

        Args:
            object_v (str, optional): To retrieve all workflows configured on an object, include the Vault object name__v. Required when the participant parameter is not used.
            record_id_v (str, optional): To retrieve all workflows configured on an object, include the object record id field value. Required when the participant parameter is not used.
            participant (str, optional): To retrieve all workflows available to a particular user, include the user id field value. Required when the object__v and record_id__v parameters are not used.
            status_v (str, optional): To retrieve all workflows with specific statuses, include one or more status name__v field values.
            offset (int, optional): Used to paginate the results, specifying the amount of offset from the first record returned.
            page_size (int, optional): Used to paginate the results, specifying the number of records to display per page.
            loc (bool, optional): When localized strings are available, set to true to retrieve them.

        Returns:
            Response: The API response containing details of the workflows matching the query parameters.
        """
        self.LatestAPIversion = 'v23.2'
        
        params = {
            "object__v": object_v,
            "record_id__v": record_id_v,
            "participant": participant,
            "status__v": status_v,
            "offset": offset,
            "page_size": page_size,
            "loc": loc
        }
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers, params=params)
        
        return response.json()



    def retrieve_workflow_details(self, workflow_id, loc=None):
        """
        Retrieve the details for a specific workflow.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-workflow-details

        Args:
            workflow_id (int): The ID of the workflow to retrieve details for.
            loc (bool, optional): When localized (translated) strings are available, set to true to retrieve them.

        Returns:
            Response: The API response containing details of the specified workflow.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/{workflow_id}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        params = {
            "loc": loc
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def retrieve_workflow_actions(self, workflow_id, loc=None):
        """
        Retrieve all available workflow actions that can be initiated on a specific workflow.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-workflow-actions

        Args:
            workflow_id (int): The ID of the workflow to retrieve actions for.
            loc (bool, optional): When localized (translated) strings are available, set to true to retrieve them.

        Returns:
            Response: The API response containing a list of available actions for the specified workflow.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/{workflow_id}/actions"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        params = {
            "loc": loc
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def retrieve_workflow_action_details(self, workflow_id, workflow_action):
        """
        Retrieve details about a specific workflow action, including any prompts necessary to complete the action.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-workflow-action-details

        Args:
            workflow_id (int): The ID of the workflow.
            workflow_action (str): The name of the workflow action.

        Returns:
            Response: The API response containing details about the specified workflow action.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/{workflow_id}/actions/{workflow_action}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def initiate_workflow_action(self, workflow_id, workflow_action, body_parameters):
        """
        Initiate a specific action on a particular workflow. The necessary parameters should be specified in the body_parameters dictionary.

        API Documentation: https://developer.veevavault.com/api/23.2/#initiate-workflow-action

        Args:
            workflow_id (int): The ID of the workflow.
            workflow_action (str): The name of the workflow action.
            body_parameters (dict): A dictionary containing the necessary parameters to initiate the workflow action.

        Returns:
            Response: The API response indicating the status of the action initiation.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/{workflow_id}/actions/{workflow_action}"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=body_parameters)
        
        return response.json()




    #######################################################
    # Workflows
    ## Workflow Tasks
    #######################################################


    def retrieve_workflow_tasks(self, query_parameters):
        """
        Retrieve all available workflow tasks based on the specified query parameters.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-workflow-tasks

        Args:
            query_parameters (dict): A dictionary containing the query parameters to filter the tasks.

        Returns:
            Response: The API response containing the list of available workflow tasks.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/tasks"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, params=query_parameters)
        
        return response.json()


    def retrieve_workflow_task_details(self, task_id, loc=None):
        """
        Retrieve the details of a specific workflow task.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-workflow-task-details

        Args:
            task_id (int): The ID of the workflow task to retrieve details for.
            loc (bool, optional): Set to true to retrieve localized strings if available. Defaults to None.

        Returns:
            Response: The API response containing the details of the specified workflow task.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/tasks/{task_id}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        params = {}
        if loc is not None:
            params['loc'] = loc
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def retrieve_workflow_task_actions(self, task_id):
        """
        Retrieve all available actions that can be initiated on a given workflow task.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-workflow-task-actions

        Args:
            task_id (int): The ID of the workflow task to retrieve actions for.

        Returns:
            Response: The API response containing the available actions for the specified workflow task.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/tasks/{task_id}/actions"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_workflow_task_action_details(self, task_id, task_action):
        """
        Retrieve the details of a specific workflow task action. The response lists the details of the task action, including all fields required to initiate the action.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-workflow-task-action-details

        Args:
            task_id (int): The task ID field value.
            task_action (str): The name of the task action retrieved from Retrieve Workflow Task Actions.

        Returns:
            Response: The API response containing the details of the specified workflow task action.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/tasks/{task_id}/actions/{task_action}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def initiate_workflow_task_action(self, task_id, task_action, data):
        """
        Initiate a workflow task action. Note that the API does not support initiating task actions requiring eSignatures.

        API Documentation: https://developer.veevavault.com/api/23.2/#initiate-workflow-task-action

        Args:
            task_id (int): The task ID field value.
            task_action (str): The name of the task action retrieved from Retrieve Workflow Task Actions.
            data (dict): A dictionary containing the required parameters depending on the action being initiated.
                        The keys should represent parameter names such as "verdict", "reason", "capacity", etc., 
                        and the values should be the respective values for those parameters.

        Returns:
            Response: The API response indicating the status of the initiated action.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/tasks/{task_id}/actions/{task_action}"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        return response.json()




    #######################################################
    # Workflows
    ## Bulk Active Workflow Actions
    #######################################################

    def retrieve_bulk_workflow_actions(self):
        """
        Retrieve all available workflow actions that can be initiated on a workflow which the authenticated user has permissions to view or initiate and can be initiated through the API.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-bulk-workflow-actions

        Returns:
            Response: The API response containing a list of available workflow actions for a Vault.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/object/workflow/actions"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_bulk_workflow_action_details(self, action_name):
        """
        Once you’ve retrieved the available workflow actions, use this method to retrieve the details for a specific workflow action.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-bulk-workflow-action-details

        Args:
            action_name (str): The name of the workflow action retrieved from Retrieve Bulk Workflow Actions.

        Returns:
            Response: The API response containing the details for the specified workflow action.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/object/workflow/actions/{action_name}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def initiate_workflow_actions_on_multiple_workflows(self, action, workflow_ids, cancellation_comment=None, current_task_assignee=None, new_task_assignee=None, user_ids=None, task_ids=None, new_workflow_owner=None, current_workflow_owner=None):
        """
        Use this method to initiate a workflow action on multiple workflows. This starts an asynchronous job whose status you can check with the Retrieve Job Status endpoint.

        API Documentation: https://developer.veevavault.com/api/23.2/#initiate-workflow-actions-on-multiple-workflows

        Args:
            action (str): The name of the workflow action. Retrieved from Retrieve Bulk Workflow Actions.
            workflow_ids (str): A comma-separated list of workflow_id__v field values (Maximum 500 workflows). Required for cancelworkflows action.
            cancellation_comment (str, optional): Comment for cancellation. Only applicable for cancelworkflows action.
            current_task_assignee (str, optional): The user ID of the user whose tasks you wish to reassign. Required for reassigntasks action.
            new_task_assignee (str, optional): The user ID of the user who will receive the newly assigned tasks. Required for reassigntasks action.
            user_ids (str, optional): A comma-separated list of user IDs to cancel tasks by user ID. Applicable for canceltasks action.
            task_ids (str, optional): A comma-separated list of task IDs to cancel tasks by task ID. Applicable for canceltasks action.
            new_workflow_owner (str, optional): The ID of the user who will become the new workflow owner. Required for replaceworkflowowner action.
            current_workflow_owner (str, optional): The ID of the current workflow owner. Required for replaceworkflowowner action.

        Returns:
            Response: The API response containing the job_id for the initiated action.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/object/workflow/actions/{action}"
        
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        data = {
            "workflow_ids": workflow_ids,
            "cancellation_comment": cancellation_comment,
            "current_task_assignee": current_task_assignee,
            "new_task_assignee": new_task_assignee,
            "user_ids": user_ids,
            "task_ids": task_ids,
            "new_workflow_owner": new_workflow_owner,
            "current_workflow_owner": current_workflow_owner
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        return response.json()



    #######################################################
    # Document Lifecycle & Workflows
    #######################################################

    #######################################################
    # Document Lifecycle & Workflows
    ## Document & Binder User Actions
    #######################################################

    def retrieve_user_actions(self, documents_or_binders, id, major_version, minor_version):
        """
        Retrieve all available user actions on a specific version of a document or binder based on the conditions mentioned in the API documentation. The method returns the available user actions that the authenticated user has permissions to view or initiate, can be initiated through the API, and are not currently in an active workflow.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-user-actions

        Args:
            documents_or_binders (str): Specify whether to retrieve values for "documents" or "binders".
            id (int): The ID of the document or binder.
            major_version (int): The major version number of the document or binder.
            minor_version (int): The minor version number of the document or binder.

        Returns:
            Response: The API response containing the list of available user actions (lifecycle_actions__v) that can be initiated on the specified version of the document or binder.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/{documents_or_binders}/{id}/versions/{major_version}/{minor_version}/lifecycle_actions"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()



    def retrieve_user_actions_multiple_documents_or_binders(self, documents_or_binders, doc_ids):
        """
        Retrieve all available user actions on specific versions of multiple documents or binders based on the criteria mentioned in the API documentation. The method returns the list of available lifecycle actions that can be initiated on the specified versions of multiple documents or binders, except those that are currently in an active workflow.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-user-actions-on-multiple-documents-or-binders

        Args:
            documents_or_binders (str): Specify whether to retrieve values for "documents" or "binders".
            doc_ids (str): A comma-separated list of document or binder IDs and their major and minor version numbers in the format {doc_id:major_version:minor_version}. For example, "22:0:1,21:1:0,20:1:0".

        Returns:
            Response: The API response containing the list of available lifecycle actions (lifecycle_actions__v) that can be initiated on the specified versions of multiple documents or binders.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/{documents_or_binders}/lifecycle_actions"

        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        data = {
            "docIds": doc_ids
        }

        response = requests.post(url, headers=headers, data=data)

        return response.json()


    def retrieve_entry_criteria(self, documents_or_binders, id, major_version, minor_version, name_v):
        """
        Retrieves the entry criteria for a specific user action on documents or binders. 
        Entry criteria are the conditions that must be met before initiating a certain action.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-entry-criteria

        Parameters:
        documents_or_binders (str): Choose to retrieve values for documents or binders.
        id (int): The ID of the document or binder to retrieve user actions from.
        major_version (int): The major version number of the document or binder.
        minor_version (int): The minor version number of the document or binder.
        name_v (str): The lifecycle name__v field value to retrieve entry criteria from.

        Returns:
        dict: A dictionary containing the response details of the API call.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/{documents_or_binders}/{id}/versions/{major_version}/{minor_version}/lifecycle_actions/{name_v}/entry_requirements"
        headers = {"Authorization": f"{self.sessionId}", "Accept": "application/json"}
        response = requests.get(url, headers=headers)
        return response.json()



    def initiate_user_action(self, documents_or_binders, id, major_version, minor_version, name_v, data=None):
        """
        Initiates a user action on documents or binders in the vault. Before initiating, 
        the applicable entry criteria for the action should be retrieved.

        API Documentation: https://developer.veevavault.com/api/23.2/#initiate-user-action

        Parameters:
        documents_or_binders (str): Choose to initiate an action on documents or binders.
        id (int): The ID of the document or binder to initiate the user action on.
        major_version (int): The major version number of the document or binder.
        minor_version (int): The minor version number of the document or binder.
        name_v (str): The name__v field value representing the action to initiate.
        data (dict, optional): Additional parameters to add to the request as name-value pairs, default is None.

        Returns:
        dict: A dictionary containing the response details of the API call.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/{documents_or_binders}/{id}/versions/{major_version}/{minor_version}/lifecycle_actions/{name_v}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        response = requests.put(url, headers=headers, data=data)
        return response.json()


    def download_controlled_copy_job_results(self, lifecycle_and_state_and_action, job_id):
        """
        Downloads the results of a controlled copy job as a file stream. This endpoint is intended 
        for use by integrations requesting and routing controlled copies of content as a system 
        integrations account on behalf of users.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#download-controlled-copy-job-results
        
        Parameters:
        lifecycle_and_state_and_action (str): The name__v values for the lifecycle, state, 
        and action in the format {lifecycle_name}.{state_name}.{action_name}. Retrieve this value 
        from the job status using the href under "rel": "artifacts".
        
        job_id (str): The ID of the job, returned from the original job request. Find this ID in 
        the Initiate User Action response.
        
        Returns:
        file: A file stream of the controlled copy job results.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/actions/{lifecycle_and_state_and_action}/{job_id}/results"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers, stream=True)
        with open(f"Download Issued Batch Record - {datetime.utcnow().strftime('%Y-%m-%dT%H-%M-%S.%fZ')}.zip", "wb") as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        return "File downloaded successfully"


    def initiate_bulk_user_actions(self, docIds, lifecycle, state, user_action_name):
        """
        Initiates bulk user actions on multiple documents or binders. Only a single workflow will start 
        for all selected and valid documents.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#initiate-bulk-user-actions
        
        Parameters:
        docIds (str): A comma-separated list of document or binder IDs along with major and minor version 
                    numbers (e.g., "222:0:1,223:0:1,224:0:1").
        lifecycle (str): The name of the document or binder lifecycle.
        state (str): The current state of the documents or binders.
        user_action_name (str): The name__v field value of the user action. This can be found using the 
                            Retrieve User Actions on Multiple Documents or Binders endpoint.
        
        Returns:
        json: The response from the API in JSON format.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/lifecycle_actions/{user_action_name}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "docIds": docIds,
            "lifecycle": lifecycle,
            "state": state
        }
        response = requests.put(url, headers=headers, data=data)
        return response.json()






    #######################################################
    # Document Lifecycle & Workflows
    ## Lifecycle Role Assignment Rules
    #######################################################


    def retrieve_lifecycle_role_assignment_rules(self, lifecycle_v=None, role_v=None, product_v=None, country_v=None, study_v=None, study_country_v=None):
        """
        Retrieve lifecycle role assignment rules (default and override) from the specified parameters. If no parameters are
        specified, it retrieves a list of all lifecycle role assignment rules from all roles in all lifecycles in your Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-lifecycle-role-assignment-rules-default-amp-override

        Parameters:
        lifecycle_v (str, optional): Name of the lifecycle to retrieve information from. Example: "general_lifecycle__c".
        role_v (str, optional): Name of the role to retrieve information from. Example: "editor__c".
        product_v (str, optional): ID/name of a specific product to see product-based override rules. Example: "0PR0011001" or "CholeCap".
        country_v (str, optional): ID/name of a specific country to see country-based override rules. Example: "0CR0022002" or "United States".
        study_v (str, optional): ID/name of a specific study to see study-based override rules (eTMF Vaults only). Example: "0ST0021J01" or "CholeCap Study".
        study_country_v (str, optional): ID/name of a specific study country to see study country-based override rules (eTMF Vaults only). Example: "0SC0001001" or "Germany".

        Returns:
        json: The response from the API in JSON format.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/configuration/role_assignment_rule"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        params = {
            "lifecycle__v": lifecycle_v,
            "role__v": role_v,
            "product__v": product_v,
            "country__v": country_v,
            "study__v": study_v,
            "study_country__v": study_country_v
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()


    def create_lifecycle_role_assignment_override_rules(self, input_file_path):
        """
        Creates lifecycle role assignment override rules in the Vault.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#create-lifecycle-role-assignment-override-rules
        
        :param input_file_path: The path to the JSON or CSV file containing the override rules data.
        :type input_file_path: str
        :return: A dictionary containing the API response.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/configuration/role_assignment_rule"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        with open(input_file_path, 'rb') as file:
            data = file.read()
        
        response = requests.post(url, headers=headers, data=data)
        
        return response.json()


    def update_lifecycle_role_assignment_rules(self, input_file_path, content_type='text/csv', accept='application/json'):
        """
        Updates lifecycle role assignment rules (default & override) in the Vault.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#update-lifecycle-role-assignment-rules-default-amp-override
        
        :param input_file_path: The path to the JSON or CSV file containing the rules data to be updated.
        :type input_file_path: str
        :param content_type: The content type of the input file, either 'application/json' or 'text/csv'. Default is 'text/csv'.
        :type content_type: str
        :param accept: The format of the response, can be 'application/json' (default), 'application/xml' or 'text/csv'.
        :type accept: str
        :return: A dictionary containing the API response.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/configuration/role_assignment_rule"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": content_type,
            "Accept": accept
        }
        
        with open(input_file_path, 'rb') as file:
            data = file.read()
        
        response = requests.put(url, headers=headers, data=data)
        
        return response.json()




    def delete_lifecycle_role_assignment_override_rules(self, lifecycle_v, role_v, object_name=None, object_name_value=None):
        """
        Deletes lifecycle role assignment override rules in the Vault.

        API Documentation: https://developer.veevavault.com/api/23.2/#delete-lifecycle-role-assignment-override-rules

        :param lifecycle_v: The name of the lifecycle from which to delete override rules.
        :type lifecycle_v: str
        :param role_v: The name of the role from which to delete override rules.
        :type role_v: str
        :param object_name: Optional: The name of the object by ID to specify the override to delete.
        :type object_name: str, optional
        :param object_name_value: Optional: The name value of the object to specify the override to delete.
        :type object_name_value: str, optional
        :return: A dictionary containing the API response.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/configuration/role_assignment_rule"
        params = {
            "lifecycle__v": lifecycle_v,
            "role__v": role_v
        }
        if object_name:
            params[object_name] = object_name_value
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.delete(url, headers=headers, params=params)
        
        return response.json()






    #######################################################
    # Document Lifecycle & Workflows
    ## Document Workflows
    #######################################################



    def retrieve_all_document_workflows(self, loc=None):
        """
        Retrieves all available document workflows that the authenticated user has permissions to view or initiate 
        and that can be initiated through the API.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-all-document-workflows

        :param loc: Optional: When localized (translated) strings are available, retrieve them by setting loc to true.
        :type loc: bool, optional
        :return: A dictionary containing the API response with details of available workflows.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/actions"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        params = {}
        if loc is not None:
            params['loc'] = loc
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def retrieve_document_workflow_details(self, workflow_name, loc=None):
        """
        Retrieves the details for a specific document workflow.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-document-workflow-details

        :param workflow_name: The name of the document workflow to retrieve details for.
        :type workflow_name: str
        :param loc: Optional: When localized (translated) strings are available, retrieve them by setting loc to true.
        :type loc: bool, optional
        :return: A dictionary containing the API response with details of the specified document workflow.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/actions/{workflow_name}"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        params = {}
        if loc is not None:
            params['loc'] = loc

        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def initiate_document_workflow(self, workflow_name, contents_sys, description_sys):
        """
        Initiates a document workflow on a set of documents.

        API Documentation: https://developer.veevavault.com/api/23.2/#initiate-document-workflow

        :param workflow_name: The name of the document workflow to initiate.
        :type workflow_name: str
        :param contents_sys: A comma-separated list of document id field values (maximum 100 documents).
        :type contents_sys: str
        :param description_sys: Description of the workflow (maximum 128 characters).
        :type description_sys: str
        :return: A dictionary containing the API response which includes details of the initiated workflow or error messages.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/actions/{workflow_name}"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        data = {
            "contents__sys": contents_sys,
            "description__sys": description_sys
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        return response.json()




    #######################################################
    # Object Lifecycle & Workflows
    #######################################################

    #######################################################
    # Object Lifecycle & Workflows
    ## Retrieve Object Record User Actions
    #######################################################


    def retrieve_object_record_user_actions(self, object_name, object_record_id, loc=None):
        """
        Retrieve all available user actions that can be initiated on a specific object record.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-record-user-actions

        :param object_name: The name of the object (name__v field value).
        :type object_name: str
        :param object_record_id: The id of the object record.
        :type object_record_id: str
        :param loc: Optional parameter to retrieve localized (translated) strings for the label, default is None.
        :type loc: bool, optional
        :return: A dictionary containing the API response which includes a list of available user actions or error messages.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/actions"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        params = {}
        if loc is not None:
            params["loc"] = loc

        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def retrieve_object_user_action_details(self, object_name, object_record_id, action_name):
        """
        Retrieves the details for a specific user action.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-object-user-action-details

        :param object_name: The object name__v field value.
        :type object_name: str
        :param object_record_id: The object record id value from which to retrieve user action details.
        :type object_record_id: str
        :param action_name: Either the name of the Objectaction or Objectlifecyclestateuseraction to initiate. This is obtained from the Retrieve User Actions request.
        :type action_name: str
        :return: A dictionary containing the API response which includes metadata for the specified object action or error messages.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/actions/{action_name}"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()


    def initiate_object_action_single_record(self, object_name, object_record_id, action_name, body_params):
        """
        Initiates an action on a specific object record.

        API Documentation: https://developer.veevavault.com/api/23.2/#initiate-object-action-on-a-single-record

        :param object_name: The object name__v field value.
        :type object_name: str
        :param object_record_id: The object record id field value from which to retrieve user actions.
        :type object_record_id: str
        :param action_name: The name of the Objectaction or Objectlifecyclestateuseraction to initiate.
        :type action_name: str
        :param body_params: A dictionary containing name-value pairs of any parameters required to initiate the action.
        :type body_params: dict
        :return: A dictionary containing the API response which includes the status of the action initiation or error messages.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/actions/{action_name}"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        response = requests.post(url, headers=headers, data=body_params)
        
        return response.json()


    def initiate_object_action_multiple_records(self, object_name, action_name, ids_list, body_params=None):
        """
        Initiates an object user action on multiple records, with a maximum of 500 records per batch.

        API Documentation: https://developer.veevavault.com/api/23.2/#initiate-object-action-on-multiple-records

        :param object_name: The object name__v field value.
        :type object_name: str
        :param action_name: Either the name of the Objectaction or Objectlifecyclestateuseraction to initiate.
        :type action_name: str
        :param ids_list: A list of object record IDs on which to initiate the action.
        :type ids_list: list of str
        :param body_params: (Optional) A dictionary containing name-value pairs of any other parameters required to initiate the action.
        :type body_params: dict, optional
        :return: A dictionary containing the API response which includes the status of the action initiation or error messages for each record ID.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/actions/{action_name}"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        body_params = body_params or {}
        body_params['ids'] = ', '.join(ids_list)
        
        response = requests.post(url, headers=headers, data=body_params)
        
        return response.json()




    #######################################################
    # Object Lifecycle & Workflows
    ## Multi-Record Workflows
    #######################################################

    def retrieve_all_multi_record_workflows(self):
        """
        Retrieves all available multi-record workflows which the authenticated user has permissions to view or initiate and can be initiated through the API.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-all-multi-record-workflows

        :return: A dictionary containing the API response which includes details of all available multi-record workflows.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/actions"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_multi_record_workflow_details(self, workflow_name):
        """
        Retrieves the fields required to initiate a specific multi-record workflow. It provides details about the necessary controls and configurations required for initiating the workflow.

        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-multi-record-workflow-details

        :param workflow_name: The name of the multi-record workflow to retrieve details for.
        :type workflow_name: str
        :return: A dictionary containing the API response which includes details of the specified multi-record workflow.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/actions/{workflow_name}"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()



    def initiate_multi_record_workflow(self, workflow_name, contents_sys, description_sys, additional_parameters=None):
        """
        Initiate a multi-record workflow on a set of records. This API call initiates the specified workflow with the necessary parameters.

        API Documentation: https://developer.veevavault.com/api/23.2/#initiate-multi-record-workflow

        :param workflow_name: The name of the workflow to initiate.
        :type workflow_name: str
        :param contents_sys: A comma-separated list of records in the format Object:{objectname}.{record_ID}.
        :type contents_sys: str
        :param description_sys: Description of the workflow, maximum of 128 characters.
        :type description_sys: str
        :param additional_parameters: Additional parameters as required by the Admin to start the workflow, if any.
        :type additional_parameters: dict, optional
        :return: A dictionary containing the API response which includes details like record_id and workflow_id of the initiated workflow.
        :rtype: dict
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/objectworkflows/actions/{workflow_name}"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        
        body = {
            "contents__sys": contents_sys,
            "description__sys": description_sys
        }
        
        if additional_parameters:
            body.update(additional_parameters)
        
        response = requests.post(url, headers=headers, data=body)
        
        return response.json()




    #######################################################
    # Users
    #######################################################


    def retrieve_user_metadata(self):
        """
        Retrieves user metadata from the Veeva Vault API.
        
        API documentation URL: https://developer.veevavault.com/api/23.2/#retrieve-user-metadata
        
        Returns:
            pd.DataFrame: A DataFrame containing the retrieved user metadata.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/users"
        r = requests.get(url, headers={"Authorization": f"{self.sessionId}"}).json()['properties']
        return pd.DataFrame(r)



    def retrieve_all_users(self, vaults=None, exclude_vault_membership=None, exclude_app_licensing=None, limit=None, start=None, sort=None):
        """
        This method retrieves user records at the domain level. Beginning in v18.1, Admins create and manage users with 
        user__sys object records. We strongly recommend using the Retrieve Object Record Collection endpoint to retrieve 
        user__sys records. More information can be found at: https://developer.veevavault.com/api/23.2/#retrieve-all-users
        
        Parameters:
        vaults (str): Optional parameter to specify the vaults to retrieve users from. It accepts values like 'all', '-1', 
                    or a comma-separated list of Vault IDs e.g., '3003,4004,5005'.
        exclude_vault_membership (bool): Optional parameter to include or exclude vault_membership fields in the response.
        exclude_app_licensing (bool): Optional parameter to include or exclude app_licensing fields in the response.
        limit (int): Optional parameter to specify the size of the result set in the page. Default is 200.
        start (int): Optional parameter to specify the starting record number. Default is 0.
        sort (str): Optional parameter to specify the sort order for the result set (e.g., 'id asc').
        
        Returns:
        response: A JSON response containing the user records data.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users"
        
        params = {
            "vaults": vaults,
            "exclude_vault_membership": exclude_vault_membership,
            "exclude_app_licensing": exclude_app_licensing,
            "limit": limit,
            "start": start,
            "sort": sort
        }
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()


    def retrieve_user(self, user_id, exclude_vault_membership=None, exclude_app_licensing=None):
        """
        This method retrieves information for one user at the domain level. Beginning in v18.1, Admins create and manage 
        users with user__sys object records. It is strongly recommended to use the Retrieve Object Record endpoint to 
        retrieve a user__sys record. More details can be found at: https://developer.veevavault.com/api/23.2/#retrieve-user

        Parameters:
        user_id (int): The ID of the user to be retrieved.
        exclude_vault_membership (bool): Optional parameter to include or exclude vault_membership fields in the response. 
                                        Including these fields may decrease performance.
        exclude_app_licensing (bool): Optional parameter to include or exclude app_licensing fields in the response. 
                                    Including these fields may decrease performance.

        Returns:
        response: A JSON response containing the information of the specified user.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users/{user_id}"
        
        params = {
            "exclude_vault_membership": exclude_vault_membership,
            "exclude_app_licensing": exclude_app_licensing
        }
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()

    def create_single_user(self, user_details, domain=None, file_path=None):
        """
        This method creates a single user in the Veeva Vault. Admins create and manage users with user__sys object records 
        from version v18.1. It is strongly recommended to use the Create Object Records endpoint to create new users, 
        unless creating cross-domain users or adding users to a domain without assigning Vault membership.
        Detailed documentation about this endpoint can be found at: https://developer.veevavault.com/api/23.2/#create-single-user
        
        Parameters:
        user_details (dict): A dictionary containing the details of the user to be created. It must include the following keys:
                            - user_name__v (required): The user's Vault username (login credential).
                            - user_first_name__v (required): The user's first name.
                            - user_last_name__v (required): The user's last name.
                            - user_email__v (required): The user's email address.
                            - user_timezone__v (required): The user's time zone.
                            - user_locale__v (required): The user's locale.
                            - security_policy_id__v (required): The user's security policy ID.
                            - user_language__v (required): The user's preferred language.
                            It can optionally include:
                            - security_profile__v: The user's security profile. Default is 'document_user__v' if omitted.
                            - license_type__v: The user's license type. Default is 'full__v' if omitted.
        domain (bool): When set to true, the user will not be assigned to a Vault.
        file_path (str): The file path to upload a profile picture (JPG, PNG, or GIF, less than 10MB).
        
        Returns:
        response: A JSON response indicating the status of the user creation.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users"

        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "multipart/form-data",
            "Accept": "application/json"
        }

        data = user_details
        if domain is not None:
            data["domain"] = domain

        files = {}
        if file_path:
            files['file'] = open(file_path, 'rb')

        response = requests.post(url, headers=headers, data=data, files=files)
        return response.json()


    def create_multiple_users(self, user_data, file_path=None, operation=None, idParam=None):
        """
        Creates multiple users in the vault. You can also add multiple existing users as cross-domain users.
        API documentation: https://developer.veevavault.com/api/23.2/#create-multiple-users
        
        Args:
        user_data (list of dict): List containing dictionaries where each dictionary contains details for a user.
        file_path (str, optional): Path to the CSV file containing user data. The values in the file must be UTF-8 encoded and follow RFC 4180 format.
        operation (str, optional): Operation type for upsert functionality. It can be "upsert".
        idParam (str, optional): Parameter for upsert functionality. It can be either "id" or "user_name__v".
        
        Returns:
        dict: Response from the API.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users"
        
        if file_path:
            with open(file_path, 'r') as f:
                data = f.read()
        else:
            data = user_data

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        params = {}
        if operation:
            params["operation"] = operation
        if idParam:
            params["idParam"] = idParam
        
        response = requests.post(url, headers=headers, json=data, params=params)
        
        return response.json()


    def update_single_user(self, user_id, payload):
        """
        Updates the information of a single user in the vault. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#update-single-user
        
        Args:
            user_id (str): The ID of the user to be updated.
            payload (dict): A dictionary containing the fields and values to be updated.
            
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users/{user_id}"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.put(url, headers=headers, data=payload)
        
        return response.json()


    def update_my_user(self, payload):
        """
        Updates the information of the currently authenticated user in the vault. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#update-my-user
        
        Args:
            payload (dict): A dictionary containing the fields and values to be updated.
            
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users/me"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.put(url, headers=headers, data=payload)
        
        return response.json()



    def update_multiple_users(self, file_path, content_type="text/csv", accept="text/csv"):
        """
        Updates the information of multiple users in the vault. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#update-multiple-users
        
        Args:
            file_path (str): The path to the input file (CSV or JSON) containing the user data to be updated.
            content_type (str, optional): The content type of the input file. Defaults to "text/csv".
            accept (str, optional): The format in which to receive the response. Defaults to "text/csv".
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users"
        headers = {
            "Content-Type": content_type,
            "Accept": accept,
            "Authorization": f"{self.sessionId}"
        }
        
        with open(file_path, 'rb') as f:
            response = requests.put(url, headers=headers, data=f)
        
        return response.json()


    def disable_user(self, user_id, domain=False):
        """
        Disables a user in a specific vault or in all vaults in the domain. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#disable-user

        Args:
            user_id (int): The ID of the user to disable.
            domain (bool, optional): When set to True, disables the user account in all vaults in the domain. Defaults to False.

        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users/{user_id}"
        if domain:
            url += "?domain=true"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.delete(url, headers=headers)
        
        return response.json()


    def change_my_password(self, current_password, new_password):
        """
        Changes the password for the currently authenticated user. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#change-my-password
        
        Args:
            current_password (str): The current password of the authenticated user.
            new_password (str): The new password to set for the authenticated user. It must be different from the current password and meet the minimum requirements configured by the Vault Admin.
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users/me/password"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        body = {
            "password__v": current_password,
            "new_password__v": new_password
        }
        
        response = requests.post(url, headers=headers, data=body)
        
        return response.json()



    def update_vault_membership(self, user_id, vault_id, active=None, security_profile=None, license_type=None):
        """
        Updates the vault membership details of a specific user in a particular vault. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#update-vault-membership
        
        Args:
            user_id (str): The ID of the user to update.
            vault_id (str): The ID of the vault where the update will take place.
            active (bool, optional): Sets the user status to active (true) or inactive (false). Defaults to None.
            security_profile (str, optional): Assigns the user a specific security profile in the vault. Defaults to None.
            license_type (str, optional): Assigns the user a specific license type in the vault. Defaults to None.
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users/{user_id}/vault_membership/{vault_id}"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        body = {}
        if active is not None:
            body["active__v"] = str(active).lower()
        if security_profile:
            body["security_profile__v"] = security_profile
        if license_type:
            body["license_type__v"] = license_type
        
        response = requests.put(url, headers=headers, data=body)
        
        return response.json()


    def retrieve_user_permissions(self, user_id, permission_name=None):
        """
        Retrieves the permissions assigned to a specific user. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#retrieve-user-permissions

        Args:
            user_id (str): The ID of the user. Use 'me' to retrieve permissions for the currently authenticated user.
            permission_name (str, optional): The name of the permission to filter the results. Should be in the format object.{object name}.{object or field}_actions. Defaults to None.
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users/{user_id}/permissions"
        
        if permission_name:
            url += f"?filter=name__v::{permission_name}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()



    def retrieve_my_user_permissions(self, permission_name=None):
        """
        Retrieves all object and object field permissions (Read, Edit, Create, Delete) assigned to the currently authenticated user. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#retrieve-my-user-permissions

        Args:
            permission_name (str, optional): The name of the permission to filter the results. Should be in the format object.{object name}.{object or field}_actions. Defaults to None.
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/users/me/permissions"
        
        if permission_name:
            url += f"?filter=name__v::{permission_name}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()




    #######################################################
    # SCIM
    #######################################################

    #######################################################
    # SCIM
    ## Discovery Endpoints
    #######################################################


    def retrieve_scim_provider(self):
        """
        Retrieves a JSON that describes the SCIM specification features available on the currently authenticated Vault. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#retrieve-scim-provider
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/ServiceProviderConfig"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()



    def retrieve_all_scim_schema_information(self):
        """
        Retrieves information about all SCIM schema specifications supported by a Vault SCIM service provider. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#retrieve-all-scim-schema-information
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/Schemas"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()



    def retrieve_single_scim_schema_information(self, schema_id):
        """
        Retrieves information about a single SCIM schema specification supported by a Vault SCIM service provider. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#retrieve-single-scim-schema-information
        
        Args:
            schema_id (str): The ID of a specific schema. For example, urn:ietf:params:scim:schemas:extension:veevavault:2.0:User.
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/Schemas/{schema_id}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_all_scim_resource_types(self):
        """
        Retrieves the types of SCIM resources available. Each resource type defines the endpoints, the core schema URI that defines the resource, and any supported schema extensions. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#retrieve-all-scim-resource-types
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/ResourceTypes"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()



    def retrieve_single_scim_resource_type(self, type):
        """
        Retrieves a single SCIM resource type. Defines the endpoints, the core schema URI which defines this resource, and any supported schema extensions. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#retrieve-single-scim-resource-type

        Args:
            type (str): A specific resource type. You can retrieve all available types from the Retrieve All SCIM Resource Types endpoint, where the value for this parameter is the id value.

        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/ResourceTypes/{type}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()




    #######################################################
    # SCIM
    ## Users
    #######################################################


    def retrieve_all_users_with_scim(self, filter=None, attributes=None, excludedAttributes=None, sortBy=None, sortOrder=None, count=None, startIndex=None):
        """
        Retrieve all users with SCIM. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#retrieve-all-users-with-scim

        Args:
            filter (str, optional): Filter for a specific attribute value, in the format {attribute} eq "{value}".
            attributes (str, optional): Include specified attributes only in a comma separated list.
            excludedAttributes (str, optional): Exclude specific attributes from the response in a comma separated list.
            sortBy (str, optional): Specify an attribute or sub-attribute to order the response.
            sortOrder (str, optional): Specify the order in which the sortBy parameter is applied. Allowed values are "ascending" or "descending".
            count (int, optional): Specify the number of query results per page.
            startIndex (int, optional): Specify the index of the first result.

        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/Users"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        params = {
            "filter": filter,
            "attributes": attributes,
            "excludedAttributes": excludedAttributes,
            "sortBy": sortBy,
            "sortOrder": sortOrder,
            "count": count,
            "startIndex": startIndex
        }

        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def retrieve_single_user_with_scim(self, user_id, filter=None, attributes=None, excludedAttributes=None):
        """
        Retrieve a specific user with SCIM. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#retrieve-single-user-with-scim

        Args:
            user_id (str): The ID of a specific user.
            filter (str, optional): Filter for a specific attribute value, in the format {attribute} eq "{value}".
            attributes (str, optional): Include specified attributes only in a comma separated list.
            excludedAttributes (str, optional): Exclude specific attributes from the response in a comma separated list.

        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/Users/{user_id}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        params = {
            "filter": filter,
            "attributes": attributes,
            "excludedAttributes": excludedAttributes
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()



    def retrieve_current_user_with_scim(self, attributes=None, excludedAttributes=None):
        """
        Retrieve the currently authenticated user with SCIM. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#retrieve-current-user-with-scim

        Args:
            attributes (str, optional): Include specified attributes only in a comma separated list.
            excludedAttributes (str, optional): Exclude specific attributes from the response in a comma separated list.

        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/Me"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        params = {
            "attributes": attributes,
            "excludedAttributes": excludedAttributes
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def update_current_user_with_scim(self, body_data, attributes=None, excludedAttributes=None):
        """
        Update the currently authenticated user with SCIM. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#update-current-user-with-scim

        Args:
            body_data (dict): A dictionary containing the data to update.
            attributes (str, optional): Include specified attributes only in a comma separated list.
            excludedAttributes (str, optional): Exclude specific attributes from the response in a comma separated list.

        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/Me"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        params = {
            "attributes": attributes,
            "excludedAttributes": excludedAttributes
        }
        
        response = requests.put(url, headers=headers, params=params, json=body_data)
        
        return response.json()


    def create_user_with_scim(self, user_data):
        """
        Create a user with SCIM. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#create-user-with-scim

        Args:
            user_data (dict): A dictionary containing the required information to create a new user.

        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/Users"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/scim+json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.post(url, headers=headers, json=user_data)
        
        return response.json()



    def update_user_with_scim(self, user_id, user_data):
        """
        Update fields values on a single user with SCIM. You can find the API documentation here:
        https://developer.veevavault.com/api/23.2/#update-user-with-scim

        Args:
            user_id (str): The ID of the user you wish to update.
            user_data (dict): A dictionary containing the information to update for the user.

        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/Users/{user_id}"
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/scim+json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.put(url, headers=headers, json=user_data)
        
        return response.json()


    def retrieve_scim_resources(self, resource_type, filter=None, attributes=None, excludedAttributes=None, sortBy=None, sortOrder=None, count=None, startIndex=None):
        """
        Retrieve a single SCIM resource type. The function defines the endpoints, the core schema URI which defines this resource, and any supported schema extensions.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-scim-resources

        Args:
            resource_type (str): The resource type to retrieve. 
            filter (str, optional): Filter for a specific attribute value. Defaults to None.
            attributes (str, optional): Include specified attributes only. Defaults to None.
            excludedAttributes (str, optional): Exclude specific attributes from the response. Defaults to None.
            sortBy (str, optional): Specify an attribute or sub-attribute to order the response. Defaults to None.
            sortOrder (str, optional): Specify the order in which the sortBy parameter is applied. Defaults to None.
            count (int, optional): Specify the number of query results per page. Defaults to None.
            startIndex (int, optional): Specify the index of the first result. Defaults to None.

        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/{resource_type}"

        params = {
            "filter": filter,
            "attributes": attributes,
            "excludedAttributes": excludedAttributes,
            "sortBy": sortBy,
            "sortOrder": sortOrder,
            "count": count,
            "startIndex": startIndex
        }

        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def retrieve_single_scim_resource(self, resource_type, resource_id, attributes=None, excludedAttributes=None):
        """
        Retrieve a single SCIM resource from the Veeva Vault. 
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-single-scim-resource

        Args:
            resource_type (str): The type of the resource to retrieve.
            resource_id (str): The ID of the resource to retrieve.
            attributes (str, optional): Include specified attributes only in a comma-separated list. Defaults to None.
            excludedAttributes (str, optional): Exclude specific attributes from the response in a comma-separated list. Defaults to None.

        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/scim/v2/{resource_type}/{resource_id}"
        
        params = {
            "attributes": attributes,
            "excludedAttributes": excludedAttributes
        }

        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()





    #######################################################
    # Groups
    #######################################################


    def retrieve_group_metadata(self):
        """
        Retrieve metadata of groups in the Veeva Vault.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-group-metadata
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/groups"

        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_all_groups(self, include_implied=None):
        """
        Retrieve all groups except Auto Managed groups in the Veeva Vault.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-all-groups
        
        Args:
            include_implied (bool, optional): When true, the response includes the implied_members__v field.
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/groups"

        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        params = {}
        if include_implied is not None:
            params['includeImplied'] = include_implied
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def retrieve_auto_managed_groups(self, limit=1000, offset=0):
        """
        Retrieve all Auto Managed groups from the Veeva Vault.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-auto-managed-groups
        
        Args:
            limit (int, optional): The maximum number of records per page in the response. Defaults to 1000.
            offset (int, optional): The offset from the entry returned to paginate the results displayed per page. Defaults to 0.
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/groups/auto"

        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        params = {
            'limit': limit,
            'offset': offset
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def retrieve_group(self, group_id, include_implied=None):
        """
        Retrieve details of a specific group using the group id from the Veeva Vault.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-group
        
        Args:
            group_id (int): The ID of the group to retrieve.
            include_implied (bool, optional): When true, includes the implied_members__v field in the response. Defaults to None.
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/groups/{group_id}"

        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        params = {}
        if include_implied is not None:
            params['includeImplied'] = include_implied
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()


    def create_group(self, label, members=None, security_profiles=None, active=True, group_description=None, allow_delegation_among_members=False):
        """
        Create a new group in the Veeva Vault.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#create-group
        
        Args:
            label (str): The label for the new group. This is used to create the group name__v value.
            members (str, optional): A comma-separated list of user IDs to assign to the group. Defaults to None.
            security_profiles (str, optional): A comma-separated list of security profiles to assign to the group. Defaults to None.
            active (bool, optional): Set to false to create the group as inactive. Defaults to True.
            group_description (str, optional): A description of the group. Defaults to None.
            allow_delegation_among_members (bool, optional): Set to true to allow members to delegate access to other members of the same group. Defaults to False.
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/groups"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        data = {
            "label__v": label,
            "active__v": active,
            "allow_delegation_among_members__v": allow_delegation_among_members
        }

        if members:
            data["members__v"] = members
        if security_profiles:
            data["security_profiles__v"] = security_profiles
        if group_description:
            data["group_description__v"] = group_description

        response = requests.post(url, headers=headers, data=data)
        
        return response.json()



    def update_group(self, group_id, label=None, members=None, security_profiles=None, active=None, group_description=None, allow_delegation_among_members=None):
        """
        Update group field values or add/remove members and security profiles in the Veeva Vault.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#update-group
        
        Args:
            group_id (str): The ID of the group to be updated.
            label (str, optional): The new label for the group. Defaults to None.
            members (str, optional): A comma-separated list of user IDs or a command to add/remove users (e.g., "add (userID1, userID2)" or "delete (userID1, userID2)"). Defaults to None.
            security_profiles (str, optional): A comma-separated list of security profiles. Defaults to None.
            active (bool, optional): Set to false to make the group inactive. Defaults to None.
            group_description (str, optional): The new description of the group. Defaults to None.
            allow_delegation_among_members (bool, optional): Set to true to allow members to delegate access only to other members of the same group. Defaults to None.
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/groups/{group_id}"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        data = {}
        
        if label is not None:
            data["label__v"] = label
        if members is not None:
            data["members__v"] = members
        if security_profiles is not None:
            data["security_profiles__v"] = security_profiles
        if active is not None:
            data["active__v"] = active
        if group_description is not None:
            data["group_description__v"] = group_description
        if allow_delegation_among_members is not None:
            data["allow_delegation_among_members__v"] = allow_delegation_among_members

        response = requests.put(url, headers=headers, data=data)
        
        return response.json()


    def delete_group(self, group_id):
        """
        Delete a user-defined group in the Veeva Vault. Note that system-managed groups cannot be deleted.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#delete-group
        
        Args:
            group_id (str): The ID of the group to be deleted.
        
        Returns:
            dict: A dictionary containing the response data.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/groups/{group_id}"

        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.delete(url, headers=headers)
        
        return response.json()



    #######################################################
    # Picklists
    #######################################################


    def retrieve_all_picklists(self):
        """
        Retrieve all picklists available in the Veeva Vault. This method provides metadata about each picklist including its name, label, kind, and where it is used.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-all-picklists
        
        Returns:
            dict: A dictionary containing the response data including details about each picklist.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/picklists"

        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_picklist_values(self, picklist_name):
        """
        Retrieve all the values configured for a specified picklist in Veeva Vault.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-picklist-values

        Args:
            picklist_name (str): The name of the picklist (e.g., "license_type__v", "product_family__c", "region__c").

        Returns:
            dict: A dictionary containing the response data with details about each picklist value.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/picklists/{picklist_name}"

        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)

        return response.json()



    def create_picklist_values(self, picklist_name, values_dict):
        """
        Create new values in a specified picklist in Veeva Vault.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#create-picklist-values

        Args:
            picklist_name (str): The name of the picklist (e.g., "license_type__v", "product_family__c", "region__c").
            values_dict (dict): A dictionary with keys as "value_1", "value_2", etc. and values as the new picklist value labels.

        Returns:
            dict: A dictionary containing the response data with details about the created picklist values.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/picklists/{picklist_name}"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.post(url, headers=headers, data=values_dict)

        return response.json()



    def update_picklist_value_label(self, picklist_name, label_updates_dict):
        """
        Update the label of existing picklist values in Veeva Vault.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#update-picklist-value-label

        Args:
            picklist_name (str): The name of the picklist (e.g., "license_type__v", "product_family__c", "region__c").
            label_updates_dict (dict): A dictionary where keys are existing picklist value names and values are the new labels.

        Returns:
            dict: A dictionary containing the response data with details about the updated picklist values.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/picklists/{picklist_name}"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.put(url, headers=headers, data=label_updates_dict)

        return response.json()


    def update_picklist_value(self, picklist_name, picklist_value_name, new_name=None, status=None):
        """
        Update the name or status of a picklist value in Veeva Vault. Be cautious as it may affect existing documents and objects.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#update-picklist-value

        Args:
            picklist_name (str): The name of the picklist (e.g., "license_type__v", "product_family__c", "region__c").
            picklist_value_name (str): The current name of the picklist value to be updated.
            new_name (str, optional): The new name for the picklist value. Defaults to None.
            status (str, optional): The new status for the picklist value, either "active" or "inactive". Defaults to None.

        Returns:
            dict: A dictionary containing the response data with status of the update operation.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/picklists/{picklist_name}/{picklist_value_name}"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        data = {}
        if new_name:
            data['name'] = new_name
        if status:
            data['status'] = status

        response = requests.put(url, headers=headers, data=data)

        return response.json()


    def inactivate_picklist_value(self, picklist_name, picklist_value_name):
        """
        Inactivates a picklist value in Veeva Vault. It does not affect picklist values that are already in use.
        Best practice is to use the update_picklist_value method to inactivate a picklist value.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#inactivate-picklist-value

        Args:
            picklist_name (str): The name of the picklist (e.g., "license_type__v", "product_family__c", "region__c").
            picklist_value_name (str): The name of the picklist value to be inactivated.

        Returns:
            dict: A dictionary containing the response data with the status of the inactivation operation.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/picklists/{picklist_name}/{picklist_value_name}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.delete(url, headers=headers)
        
        return response.json()




    #######################################################
    # Expected Document Lists
    #######################################################



    def create_placeholder_from_edl_item(self, edl_item_ids):
        """
        Creates a placeholder from an EDL item. Learn more about working with Content Placeholders in Vault Help.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#create-a-placeholder-from-an-edl-item

        Args:
            edl_item_ids (str): A comma-separated string of EDL Item IDs on which to initiate the action.

        Returns:
            dict: A dictionary containing the response data, including job_id and URL to check the job status.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/edl_item__v/actions/createplaceholder"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        data = {
            "edlItemIds": edl_item_ids
        }

        response = requests.post(url, headers=headers, data=data)
        
        return response.json()


    def retrieve_all_root_nodes(self, edl_hierarchy_or_template):
        """
        Retrieves all root EDL nodes and node metadata. Learn more about EDL hierarchies in Vault Help.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-all-root-nodes

        Args:
            edl_hierarchy_or_template (str): Specifies whether to retrieve nodes for either edl_hierarchy__v or edl_template__v.

        Returns:
            dict: A dictionary containing the response data with details of all root nodes.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/composites/trees/{edl_hierarchy_or_template}"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_specific_root_nodes(self, edl_hierarchy_or_template, ref_ids):
        """
        Retrieves the root node ID for the given EDL record IDs.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-specific-root-nodes

        Args:
            edl_hierarchy_or_template (str): Specifies whether to retrieve nodes for either edl_hierarchy__v or edl_template__v.
            ref_ids (list): A list of dictionaries where each dictionary contains a key 'ref_id__v' and the corresponding EDL record ID as value.

        Returns:
            dict: A dictionary containing the response data with the root node ID for the specified EDL record IDs.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/composites/trees/{edl_hierarchy_or_template}/actions/listnodes"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.post(url, headers=headers, json=ref_ids)
        
        return response.json()



    def retrieve_node_children(self, edl_hierarchy_or_template, parent_node_id):
        """
        Given an EDL node ID, retrieves immediate children (not grandchildren) of that node.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-a-node-39-s-children
        
        Args:
            edl_hierarchy_or_template (str): Specifies whether to retrieve node children for either edl_hierarchy__v or edl_template__v.
            parent_node_id (str): The ID of a parent node in the hierarchy.

        Returns:
            dict: A dictionary containing the response data with the immediate children of the specified parent node ID.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/composites/trees/{edl_hierarchy_or_template}/{parent_node_id}/children"
        
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)
        
        return response.json()


    def update_node_order(self, edl_hierarchy_or_template, parent_node_id, node_id, new_order):
        """
        Given an EDL parent node, updates the order of its children.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#update-node-order
        
        Args:
            edl_hierarchy_or_template (str): Specifies whether to update node order for either edl_hierarchy__v or edl_template__v.
            parent_node_id (str): The ID of a parent node in the hierarchy.
            node_id (str): The ID of the child node to update.
            new_order (str): The new order for the node in the hierarchy, such as “1”, “2”, etc.

        Returns:
            dict: A dictionary containing the response data after updating the node order.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/composites/trees/{edl_hierarchy_or_template}/{parent_node_id}/children"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        payload = {
            "id": node_id,
            "order__v": new_order
        }

        response = requests.put(url, headers=headers, json=payload)
        
        return response.json()


    def add_edl_matched_documents(self, matched_documents):
        """
        Adds matched documents to EDL Items. You must have a security profile that grants the Application: EDL Matching: Edit Document Matches permission, and EDL Matched Document APIs must be enabled in your Vault. To enable this feature, contact Veeva Support.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#add-edl-matched-documents

        Args:
            matched_documents (list of dict): List of dictionaries where each dictionary contains the details of an EDL item-document match with keys - id, document_id, major_version_number__v (optional), minor_version_number__v (optional), lock (optional).

        Returns:
            dict: A dictionary containing the response data after adding the EDL matched documents.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/edl_matched_documents/batch/actions/add"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.post(url, headers=headers, json=matched_documents)
        
        return response.json()


    def remove_edl_matched_documents(self, matched_documents):
        """
        Removes manually matched documents from EDL Items. You must have a security profile that grants the Application: EDL Matching: Edit Document Matches permission, and EDL Matched Document APIs must be enabled in your Vault. To enable this feature, contact Veeva Support.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#remove-edl-matched-documents

        Args:
            matched_documents (list of dict): List of dictionaries where each dictionary contains the details of an EDL item-document match to remove with keys - id, document_id, major_version_number__v (optional), minor_version_number__v (optional), remove_locked (optional).

        Returns:
            dict: A dictionary containing the response data after removing the EDL matched documents.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/edl_matched_documents/batch/actions/remove"

        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.post(url, headers=headers, json=matched_documents)
        
        return response.json()



    #######################################################
    # Security Policies
    #######################################################


    def retrieve_security_policy_metadata(self):
        """
        Retrieve the metadata associated with the security policy object. 
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-security-policy-metadata
        
        Returns:
            dict: A dictionary containing the metadata associated with the security policy object.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/objects/securitypolicies"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_all_security_policies(self):
        """
        Retrieve a list of all security policies in the Vault. 
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-all-security-policies
        
        Returns:
            dict: A dictionary containing a list of all security policies in the Vault.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/securitypolicies"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()



    def retrieve_security_policy(self, security_policy_name):
        """
        Retrieve the details of a specific security policy in the Vault.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-security-policy
        
        Args:
            security_policy_name (str): The name__v field value of the security policy to retrieve. This is typically a numeric value.
            
        Returns:
            dict: A dictionary containing the details of the specified security policy.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/securitypolicies/{security_policy_name}"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()



    #######################################################
    # Configuration Migration
    #######################################################


    def export_package(self, package_name):
        """
        Export a package from the Vault. The API will initiate an export job and respond with the details of the job including a job ID which can be used to check the status of the export job.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#export-package
        
        Args:
            package_name (str): The name of the Outbound Package you would like to export.
            
        Returns:
            dict: A dictionary containing the URL to check the job status and the job ID.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/package"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"{self.sessionId}"
        }
        
        data = {
            "packageName": package_name
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        return response.json()



    def import_package(self, file_path):
        """
        Import and validate a VPK package in the Vault. The API initiates an asynchronous import job and responds with the job details including a job ID which can be used to check the status of the import job.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#import-package
        
        Args:
            file_path (str): The path to the .vpk file that you want to import.
            
        Returns:
            dict: A dictionary containing the URL to check the job status and the job ID.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/package"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        files = {
            'file': open(file_path, 'rb')
        }
        
        response = requests.put(url, headers=headers, files=files)
        
        return response.json()




    def deploy_package(self, package_id):
        """
        Deploy a package in the Vault. This method initiates a deployment job and responds with the job details including a job ID which can be used to retrieve the status and results of the request.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#deploy-package
        
        Args:
            package_id (str): The ID of the vault_package__v object record that you want to deploy.
            
        Returns:
            dict: A dictionary containing the URL to check the job status and the job ID.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobject/vault_package__v/{package_id}/actions/deploy"
        
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.post(url, headers=headers)
        
        return response.json()



    def retrieve_package_deploy_results(self, package_id):
        """
        Retrieve the results of a completed package deployment in the Vault. After Vault completes the deploy job, use this method to get detailed information about the deployment results.
        API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-package-deploy-results
        
        Args:
            package_id (str): The ID of the vault_package__v object record used for deployment.
            
        Returns:
            dict: A dictionary containing the results and details of the package deployment.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobject/vault_package__v/{package_id}/actions/deploy/results"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()



    def retrieve_outbound_package_dependencies(self, package_id):
        """
        Retrieve the dependencies of an outbound package in the Vault. This API method allows you to identify all outstanding component dependencies for an outbound package and gives you the ability to add these missing dependencies to the package through another API call.
        The API documentation can be found at: https://developer.veevavault.com/api/23.2/#retrieve-outbound-package-dependencies

        Args:
            package_id (str): The ID of the outbound_package__v record for which to retrieve dependencies.

        Returns:
            dict: A dictionary containing details about the package dependencies, including total number of dependencies, target vault ID, package name, package ID, description, and URL for adding missing dependencies.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/outbound_package__v/{package_id}/dependencies"
        
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()




    def vault_compare(self, vault_id, results_type="differences", details_type="simple", include_doc_binder_templates=True, include_vault_settings=True, component_types=None, generate_outbound_packages=False):
        """
        Compare the configuration of two different Vaults. The Vault where the request is made serves as the source Vault, and the target Vault for the comparison is specified in the request body. This function allows you to initiate a comparison between configurations and view the differences or complete configurations depending on the parameters specified.
        The API documentation can be found at: https://developer.veevavault.com/api/23.2/#vault-compare

        Args:
            vault_id (str): The target Vault ID for the comparison.
            results_type (str, optional): Specify 'complete' to include all configuration values or 'differences' to only see the differences between Vaults. Defaults to 'differences'.
            details_type (str, optional): Specify the level of details in the comparison. Can be 'none' for component level details only, 'simple' for simple attribute-level details, or 'complex' for all attribute-level details. Defaults to 'simple'.
            include_doc_binder_templates (bool, optional): Include or exclude Document and Binder Templates for comparison. Defaults to True.
            include_vault_settings (bool, optional): Include or exclude Vault Settings for comparison. Defaults to True.
            component_types (str, optional): A comma-separated list of component types to include or 'none' to exclude all component types. Defaults to None (includes all components).
            generate_outbound_packages (bool, optional): If True, Vault automatically generates an Outbound Package based on the differences between the source and target Vault. Defaults to False.

        Returns:
            dict: A dictionary containing the response status, URL, and job ID for the comparison report job initiated. Use the URL and job ID to track the status and retrieve the comparison report once generated.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/vault/actions/compare"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"{self.sessionId}"
        }

        data = {
            "vault_id": vault_id,
            "results_type": results_type,
            "details_type": details_type,
            "include_doc_binder_templates": include_doc_binder_templates,
            "include_vault_settings": include_vault_settings,
            "component_types": component_types,
            "generate_outbound_packages": generate_outbound_packages
        }

        response = requests.post(url, headers=headers, data=data)

        return response.json()



    def vault_configuration_report(self, include_vault_settings=True, include_inactive_components=False, include_components_modified_since=None, include_doc_binder_templates=True, suppress_empty_results=False, component_types=None, output_format="Excel_Macro_Enabled"):
        """
        Generates an Excel™ report containing configuration information for a Vault. Users need to have the Vault Configuration Report permission to use this API. The detailed API documentation can be accessed at: https://developer.veevavault.com/api/23.2/#vault-configuration-report

        Args:
            include_vault_settings (bool, optional): Determines whether to include Vault Settings in the report. Defaults to True.
            include_inactive_components (bool, optional): Decides whether to include inactive components and subcomponents in the report. Defaults to False.
            include_components_modified_since (str, optional): To include components modified since the specified date. The date should be in the format 'yyyy-mm-dd'. Defaults to None.
            include_doc_binder_templates (bool, optional): Determines whether to include document and binder templates in the report. Defaults to True.
            suppress_empty_results (bool, optional): If True, Vault will exclude tabs with only header rows from the report. Defaults to False.
            component_types (str, optional): A comma-separated list of component types to include in the report. Defaults to None, which includes all components.
            output_format (str, optional): Specifies the output format for the report, either 'XSLX' or 'XLSM'. Defaults to 'Excel_Macro_Enabled'.

        Returns:
            dict: The response dictionary containing the status of the request, the URL, and the job ID for the new Configuration Report job. You can use the URL and job ID to track the status and retrieve the report once generated.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/vault/actions/configreport"

        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"{self.sessionId}"
        }

        data = {
            "include_vault_settings": include_vault_settings,
            "include_inactive_components": include_inactive_components,
            "include_components_modified_since": include_components_modified_since,
            "include_doc_binder_templates": include_doc_binder_templates,
            "suppress_empty_results": suppress_empty_results,
            "component_types": component_types,
            "output_format": output_format
        }

        response = requests.post(url, headers=headers, data=data)

        return response.json()


    def validate_package(self, file_path):
        """
        Validates a VPK package attached to this request. The validation response includes information on dependent components, similar to the validation logs generated through the UI. This method does not import your package. For detailed information, refer to the API documentation: https://developer.veevavault.com/api/23.2/#validate-package

        Args:
            file_path (str): The path to the VPK file to be validated.

        Returns:
            dict: The response dictionary containing the status of the validation and details of the package validation response.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/package/actions/validate"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(url, headers=headers, files=files)

        return response.json()



    def validate_inbound_package(self, package_id):
        """
        Validates an imported VPK package before deploying it to your Vault. The validation response includes information on dependent components and whether they exist in the package or in your Vault. You can add missing dependencies to the package in the source Vault before re-importing and deploying it to your target Vault. For more details, refer to the API documentation: https://developer.veevavault.com/api/23.2/#validate-inbound-package

        Args:
            package_id (str): The id field value of the vault_package__v object record to validate.

        Returns:
            dict: The response dictionary containing the status of the validation and details of the package validation response.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/vobject/vault_package__v/{package_id}/actions/validate"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.post(url, headers=headers)
        
        return response.json()



    #######################################################
    # Sandbox Vaults
    #######################################################

    def retrieve_sandboxes(self):
        """
        Retrieve information about the sandbox Vaults for the authenticated Vault.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-sandboxes
        
        Usage:
            vv_instance = Vv()
            sandboxes_info = vv_instance.retrieve_sandboxes()

        Returns:
            dict: A dictionary containing the details of the sandboxes.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def retrieve_sandbox_details_by_id(self, vault_id):
        """
        Retrieve information about the sandbox for the given Vault ID.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-sandbox-details-by-id
        
        Usage:
            vv_instance = Vv()
            sandbox_details = vv_instance.retrieve_sandbox_details_by_id(vault_id='56219')

        Args:
            vault_id (str): The Vault ID of the sandbox.

        Returns:
            dict: A dictionary containing the details of the sandbox specified by the Vault ID.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/{vault_id}"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def recheck_sandbox_usage_limit(self):
        """
        Recalculate the usage values of the sandbox Vaults for the authenticated Vault. This action can be initiated up to three times in a 24-hour period.
        API Documentation: https://developer.veevavault.com/api/23.2/#recheck-sandbox-usage-limit
        
        Usage:
            vv_instance = Vv()
            response = vv_instance.recheck_sandbox_usage_limit()

        Returns:
            dict: A dictionary containing the response status of the action.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/actions/recheckusage"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def change_sandbox_size(self, sandbox_details):
        """
        Change the size of a sandbox Vault for the authenticated Vault. You can initiate this action if there are sufficient allowances and the current sandbox meets the data and user limits of the requested size.
        API Documentation: https://developer.veevavault.com/api/23.2/#change-sandbox-size
        
        Usage:
            vv_instance = Vv()
            response = vv_instance.change_sandbox_size(sandbox_details=[{"name": "SandboxA", "size": "Full"}])

        Args:
            sandbox_details (list of dict): A list of dictionaries containing details of the sandboxes to change the size. Each dictionary should have "name" and "size" keys.

        Returns:
            dict: A dictionary containing the response status of the action.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/batch/changesize"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers, json=sandbox_details)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def set_sandbox_entitlements(self, name, size, allowance, grant, temporary_allowance=None):
        """
        Set new sandbox entitlements, including granting and revoking allowances, for the given sandbox name.
        API Documentation: https://developer.veevavault.com/api/23.2/#set-sandbox-entitlements
        
        Usage:
            vv_instance = Vv()
            response = vv_instance.set_sandbox_entitlements(name="Sandbox0", size="Large", allowance=1, grant=True, temporary_allowance=None)

        Args:
            name (str): The name of the sandbox Vault.
            size (str): The size of the sandbox: Small, Large, or Full.
            allowance (int): The number of entitlements to grant or revoke.
            grant (bool): True grants allowances and false revokes them.
            temporary_allowance (int, optional): The number of temporary sandbox allowances to grant or revoke.

        Returns:
            dict: A dictionary containing the response status and the updated entitlement details.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/entitlements/set"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "name": name,
            "size": size,
            "allowance": allowance,
            "grant": grant,
            "temporary_allowance": temporary_allowance
        }
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def create_or_refresh_sandbox(self, size, domain, name, source=None, source_snapshot=None, type=None, add_requester=None, release=None):
        """
        Create a new sandbox or refresh an existing sandbox for the currently authenticated Vault.
        API Documentation: https://developer.veevavault.com/api/23.2/#create-or-refresh-sandbox
        
        Usage:
            vv_instance = Vv()
            response = vv_instance.create_or_refresh_sandbox(size="Small", domain="veepharm.com", name="Sandbox", source=None, source_snapshot=None, type=None, add_requester=None, release=None)
        
        Args:
            size (str): The size of the sandbox: Small, Large, or Full.
            domain (str): The domain to use for the new sandbox.
            name (str): The name of the sandbox Vault.
            source (str, optional): The source to refresh the sandbox from: vault or snapshot.
            source_snapshot (str, optional): The api_name of the snapshot to create the sandbox from, if the source is a snapshot.
            type (str, optional): The type of sandbox, such as config.
            add_requester (bool, optional): Adds the currently authenticated user as a Vault Owner in the new sandbox, defaults to True.
            release (str, optional): The type of release: general, limited, or prerelease, defaults to the release level of the source Vault.

        Returns:
            dict: A dictionary containing the response status and the job ID and URL to check the status of the sandbox creation request.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "size": size,
            "domain": domain,
            "name": name,
            "source": source,
            "source_snapshot": source_snapshot,
            "type": type,
            "add_requester": add_requester,
            "release": release
        }
        
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def refresh_sandbox_from_snapshot(self, vault_id, source_snapshot):
        """
        Refresh a sandbox Vault in the currently authenticated Vault from an existing snapshot.
        API Documentation: https://developer.veevavault.com/api/23.2/#refresh-sandbox-from-snapshot
        
        Usage:
            vv_instance = Vv()
            response = vv_instance.refresh_sandbox_from_snapshot(vault_id=1001055, source_snapshot="Sandbox1 Snapshot")
        
        Args:
            vault_id (int): The Vault ID of the sandbox to be refreshed.
            source_snapshot (str): The api_name of the snapshot to refresh the sandbox from.

        Returns:
            dict: A dictionary containing the response status and the job ID and URL to check the status of the sandbox refresh request.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/{vault_id}/actions/refresh"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "source_snapshot": source_snapshot
        }
        
        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def delete_sandbox(self, sandbox_name):
        """
        Delete a sandbox Vault. How often you can delete a Vault depends on its size.
        API Documentation: https://developer.veevavault.com/api/23.2/#delete-sandbox
        
        Usage:
            vv_instance = Vv()
            response = vv_instance.delete_sandbox(sandbox_name="My Configuration Sandbox")

        Args:
            sandbox_name (str): The name of the sandbox Vault to delete. This is the name which appears on the My Vaults page.

        Returns:
            dict: A dictionary containing the response status and a message about the deletion process.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/{sandbox_name}"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason





    #######################################################
    # Sandbox Vaults
    ## Sandbox Snapshots
    #######################################################

    def create_sandbox_snapshot(self, source_sandbox, snapshot_name, description=None, include_data=False):
        """
        Create a new sandbox snapshot for the indicated sandbox Vault.
        API Documentation: https://developer.veevavault.com/api/23.2/#create-sandbox-snapshot

        Usage:
            vv_instance = Vv()
            response = vv_instance.create_sandbox_snapshot(source_sandbox="Sandbox1", snapshot_name="Snapshot1", description="First snapshot of a sandbox.", include_data=False)

        Args:
            source_sandbox (str): The name of the sandbox Vault to take a snapshot of.
            snapshot_name (str): The name of the new snapshot.
            description (str, optional): The description of the new snapshot. Defaults to None.
            include_data (bool, optional): Set to true to include data as part of the snapshot. Set to false to include only configuration. Defaults to False.

        Returns:
            dict: A dictionary containing the job ID and URL to retrieve the current status of the snapshot creation request.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/snapshot"
        headers = {
            "Authorization": self.sessionId,
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "source_sandbox": source_sandbox,
            "name": snapshot_name,
            "description": description,
            "include_data": str(include_data).lower()
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def retrieve_sandbox_snapshots(self):
        """
        Retrieve information about sandbox snapshots managed by the authenticated Vault.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-sandbox-snapshots

        Usage:
            vv_instance = Vv()
            response = vv_instance.retrieve_sandbox_snapshots()

        Returns:
            dict: A dictionary containing the details of the sandbox snapshots managed by the authenticated Vault.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/snapshot"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def delete_sandbox_snapshot(self, api_name):
        """
        Delete a sandbox snapshot managed by the authenticated Vault. Deleted snapshots cannot be recovered.
        API Documentation: https://developer.veevavault.com/api/23.2/#delete-sandbox-snapshot

        Parameters:
            api_name (str): The API name of the snapshot to delete.

        Usage:
            vv_instance = Vv()
            response = vv_instance.delete_sandbox_snapshot(api_name="sandbox_a_snapshot__c")

        Returns:
            dict: A dictionary containing the response status of the delete request.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/snapshot/{api_name}"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.delete(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason



    def update_sandbox_snapshot(self, api_name):
        """
        Recreate a sandbox snapshot for the same source sandbox Vault. This request replaces the existing snapshot with the newly created one.
        API Documentation: https://developer.veevavault.com/api/23.2/#update-sandbox-snapshot

        Parameters:
            api_name (str): The API name of the snapshot to update.

        Usage:
            vv_instance = Vv()
            response = vv_instance.update_sandbox_snapshot(api_name="veepharm_snapshot__c")

        Returns:
            dict: A dictionary containing the response status and job details of the update request.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/snapshot/{api_name}/actions/update"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def upgrade_sandbox_snapshot(self, api_name):
        """
        Upgrade a sandbox snapshot to match the release version of the source sandbox Vault. The request to upgrade a snapshot is only valid if the upgrade_status is "Upgrade Available" or "Upgrade Required".
        API Documentation: https://developer.veevavault.com/api/23.2/#upgrade-sandbox-snapshot

        Parameters:
            api_name (str): The API name of the snapshot obtained from the Retrieve Sandbox Snapshots request.

        Usage:
            vv_instance = Vv()
            response = vv_instance.upgrade_sandbox_snapshot(api_name="veepharm_snapshot__c")

        Returns:
            dict: A dictionary containing the response status and job details of the upgrade request.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/snapshot/{api_name}/actions/upgrade"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }

        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def build_production_vault(self, source):
        """
        Given a pre-production Vault, this method allows you to build a production Vault. This is analogous to the Build action in the Vault UI. It is possible to build or rebuild the source Vault for a given pre-production Vault no more than three times in a 24-hour period.
        API Documentation: https://developer.veevavault.com/api/23.2/#build-production-vault
        
        Parameters:
            source (str): The name of the source Vault to build. This can be the current pre-production Vault or a sandbox Vault. Sandboxes must be active and match the release type (General or Limited) of the pre-production Vault.
        
        Usage:
            vv_instance = Vv()
            response = vv_instance.build_production_vault(source="UAT")
        
        Returns:
            dict: A dictionary containing the response status and job details of the build request.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/actions/buildproduction"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "source": source
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def promote_to_production(self, name):
        """
        Given a built pre-production Vault, this method allows you to promote it to a production Vault. This action is analogous to the Promote action in the Vault UI. Note that you must build your pre-production Vault before you can promote it to production.
        API Documentation: https://developer.veevavault.com/api/23.2/#promote-to-production
        
        Parameters:
            name (str): The name of the pre-production Vault to promote.
        
        Usage:
            vv_instance = Vv()
            response = vv_instance.promote_to_production(name="VeePharm")
        
        Returns:
            dict: A dictionary containing the response status of the promotion request.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/sandbox/actions/promoteproduction"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            "name": name
        }

        response = requests.post(url, headers=headers, data=data)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason






    #######################################################
    # Logs
    #######################################################


    def retrieve_audit_types(self):
        """
        This method retrieves all available audit types that the user has permission to access.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-audit-types
        
        Usage:
            vv_instance = Vv()
            response = vv_instance.retrieve_audit_types()
        
        Returns:
            dict: A dictionary containing the response status and a list of available audit types.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/audittrail"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def retrieve_audit_metadata(self, audit_trail_type):
        """
        This method retrieves all fields and their metadata for a specified audit trail or log type.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-audit-metadata
        
        Args:
            audit_trail_type (str): The name of the specified audit type (document_audit_trail, object_audit_trail, etc).
        
        Usage:
            vv_instance = Vv()
            response = vv_instance.retrieve_audit_metadata(audit_trail_type='document_audit_trail')
        
        Returns:
            dict: A dictionary containing the response status and the metadata for the specified audit trail type.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/metadata/audittrail/{audit_trail_type}"
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def retrieve_audit_details(self, audit_trail_type, start_date=None, end_date=None, all_dates=None, format_result=None, limit=None, offset=None, objects=None, events=None):
        """
        This method retrieves all audit details for a specific audit type. This request supports optional parameters to narrow the results to a specified date and time within the past 30 days.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-audit-details

        Args:
            audit_trail_type (str): The name of the specified audit type. Use the Retrieve Audit Types API to retrieve types available in your Vault.
            start_date (str, optional): The start date in YYYY-MM-DDTHH:MM:SSZ format to retrieve audit information.
            end_date (str, optional): The end date in YYYY-MM-DDTHH:MM:SSZ format to retrieve audit information.
            all_dates (bool, optional): Set to true to request audit information for all dates.
            format_result (str, optional): To request a downloadable CSV file of your audit details, use 'csv'.
            limit (int, optional): Specifies the maximum number of histories per page in the response.
            offset (int, optional): Specifies the amount of offset from the entry returned.
            objects (str, optional): A comma-separated list of one or more object names to retrieve their audit details.
            events (str, optional): A comma-separated list of one or more audit events to retrieve their audit details.

        Usage:
            vv_instance = Vv()
            response = vv_instance.retrieve_audit_details(audit_trail_type='login_audit_trail', start_date='2023-08-01T00:00:00Z', end_date='2023-08-31T00:00:00Z')

        Returns:
            dict: A dictionary containing the response details and data for the specified audit trail type.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/audittrail/{audit_trail_type}"
        
        headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "all_dates": all_dates,
            "format_result": format_result,
            "limit": limit,
            "offset": offset,
            "objects": objects,
            "events": events
        }
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        else:
            return response.status_code, response.reason


    def retrieve_complete_audit_history(self, doc_id, start_date=None, end_date=None, format_result=None, limit=None, offset=None, events=None):
        """
        Retrieve complete audit history for a single document.
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-complete-audit-history-for-a-single-document

        Args:
        doc_id (str): The document ID for which to retrieve audit history.
        start_date (str): Specify a start date to retrieve audit history in YYYY-MM-DDTHH:MM:SSZ format. Defaults to the Vault’s creation date if omitted.
        end_date (str): Specify an end date to retrieve audit history in YYYY-MM-DDTHH:MM:SSZ format. Defaults to today’s date if omitted.
        format_result (str): To request a CSV file of the audit history, use 'csv'. Ignores start_date and end_date if used.
        limit (int): Paginate the results by specifying the maximum number of histories per page in the response. Can be any value between 1 and 1000. Defaults to 200 if omitted.
        offset (int): Paginate the results displayed per page by specifying the offset from the entry returned. Defaults to 0 if omitted.
        events (str): Provide a comma-separated list of one or more audit events to retrieve their audit history. Defaults to all audit events if omitted.

        Returns:
        response (dict): A dictionary containing the response data from the API call.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/documents/{doc_id}/audittrail"
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'format_result': format_result,
            'limit': limit,
            'offset': offset,
            'events': events
        }
        headers = {
            'Authorization': self.sessionId,
            'Accept': 'application/json'
        }
        response = requests.get(url, headers=headers, params=params).json()
        return response.json()


    def retrieve_audit_history_single_object_record(self, object_name, object_record_id, start_date=None, end_date=None, format_result=None, limit=None, offset=None, events=None):
        """
        Retrieve complete audit history for a single object record.
        
        API Documentation: https://developer.veevavault.com/api/23.2/#retrieve-complete-audit-history-for-a-single-object-record
        
        Parameters:
        object_name (str): The name__v of the object for which to retrieve audit history.
        object_record_id (str): The object record ID for which to retrieve audit history.
        start_date (str, optional): Specify a start date to retrieve audit history in YYYY-MM-DDTHH:MM:SSZ format. Defaults to Vault’s creation date if omitted.
        end_date (str, optional): Specify an end date to retrieve audit history in YYYY-MM-DDTHH:MM:SSZ format. Defaults to today’s date if omitted.
        format_result (str, optional): To request a CSV file of your audit history, use 'csv'. Defaults to None.
        limit (int, optional): Paginate the results by specifying the maximum number of histories per page in the response, between 1 and 1000. Defaults to 200 if omitted.
        offset (int, optional): Paginate the results displayed per page by specifying the amount of offset from the entry returned. Defaults to 0 if omitted.
        events (str, optional): Provide a comma-separated list of one or more audit events to retrieve their audit history. Defaults to all audit events if omitted.
        
        Returns:
        dict: The response data containing the audit history details.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/audittrail"
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "format_result": format_result,
            "limit": limit,
            "offset": offset,
            "events": events
        }
        headers = {
            "Accept": "application/json",
            "Authorization": self.sessionId
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()


    def retrieve_email_notification_histories(self, start_date=None, end_date=None, all_dates=None, format_result=None, limit=200, offset=0):
        """
        Retrieves details about the email notifications sent by Vault. Details include the notification date, recipient, subject, and delivery status. 
        Learn more at: https://developer.veevavault.com/api/23.2/#retrieve-email-notification-histories

        Args:
        start_date (str): Specify a start date to retrieve notification history in YYYY-MM-DD or YYYY-MM-DDTHH:mm:ssZ format. Defaults to None.
        end_date (str): Specify an end date to retrieve notification history in YYYY-MM-DD or YYYY-MM-DDTHH:mm:ssZ format. Defaults to None.
        all_dates (bool): Set to true to request notification history for all dates. Defaults to None.
        format_result (str): To request a downloadable CSV file, set this parameter to 'csv'. Defaults to None.
        limit (int): Specify the maximum number of histories per page in the response, between 1 and 1000. Defaults to 200.
        offset (int): Specify the amount of offset from the entry returned. Defaults to 0.

        Returns:
        dict: The response from the API call.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/notifications/histories"
        
        params = {
            'start_date': start_date,
            'end_date': end_date,
            'all_dates': all_dates,
            'format_result': format_result,
            'limit': limit,
            'offset': offset
        }
        
        response = requests.get(url, headers=self.APIheaders, params=params)
        return response.json()


    def download_daily_api_usage(self, date, log_format='csv'):
        """
        Retrieve the API Usage Log for a single day, up to 30 days in the past. The log contains information such as user name, user ID, remaining burst limit, and the endpoint called. 
        API documentation: https://developer.veevavault.com/api/23.2/#download-daily-api-usage

        :param date: The day to retrieve the API Usage log in 'YYYY-MM-DD' format. Date cannot be more than 30 days in the past.
        :param log_format: Optional parameter to specify the format to download. Possible values are 'csv' or 'logfile'. If omitted, defaults to 'csv'.
        
        :return: The response containing the log as a .ZIP file.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/logs/api_usage"
        params = {
            "date": date,
            "log_format": log_format
        }
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers, params=params)
        with open('response.zip', 'wb') as file:
            file.write(response.content)
        
        return response.json()


    def download_sdk_runtime_log(self, date, log_format='csv'):
        """
        Retrieve the Runtime Log for a single day, up to 30 days in the past. Users with the Admin: Logs: Vault Java SDK Logs permission can access these logs.
        API documentation: https://developer.veevavault.com/api/23.2/#download-sdk-runtime-log

        :param date: The day to retrieve the runtime log in 'YYYY-MM-DD' format. Date cannot be more than 30 days in the past.
        :param log_format: Optional parameter to specify the format to download. Possible values are 'csv' or 'logfile'. If omitted, defaults to 'csv'.
        
        :return: The response containing the log as a .ZIP file.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/logs/code/runtime"
        params = {
            "date": date,
            "log_format": log_format
        }
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }
        
        response = requests.get(url, headers=headers, params=params)
        with open(f'{date}-SdkLog.zip', 'wb') as file:
            file.write(response.content)
        
        return response.json()




    #######################################################
    # File Staging
    #######################################################


    def list_items_at_path(self, item, recursive=False, limit=1000, format_result=None):
        """
        Return a list of files and folders for the specified path. Paths are different for Admin users (Vault Owners and System Admins) and non-Admin users. 
        API documentation: https://developer.veevavault.com/api/23.2/#list-items-at-a-path

        :param item: The absolute path to a file or folder. This path is specific to the authenticated user. Admin users can access the root directory. All other users can only access their own user directory.
        :param recursive: If true, the response will contain the contents of all subfolders. If not specified, the default value is false.
        :param limit: The maximum number of items per page in the response. This can be any value between 1 and 1000. If omitted, the default value is 1000.
        :param format_result: If set to csv, the response includes a job_id. Use the Job ID value to retrieve the status and results of the request.

        :return: The response containing the list of items at the specified path.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/items/{item}"
        params = {
            "recursive": recursive,
            "limit": limit,
            "format_result": format_result
        }
        headers = {
            "Accept": "application/json",
            "Authorization": f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers, params=params)
        return response.json()


    def download_item_content(self, item, byte_range=None):
        """
        Retrieve the content of a specified file from the file staging server. Use the Range header to create resumable downloads for large files, or to continue downloading a file if your session is interrupted.
        API documentation: https://developer.veevavault.com/api/23.2/#download-item-content

        :param item: The absolute path to a file. This path is specific to the authenticated user. Admin users can access the root directory. All other users can only access their own user directory.
        :param byte_range: Optional: Specifies a partial range of bytes to include in the download.

        :return: The content of the specified file.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/items/content/{item}"
        headers = {
            "Authorization": f"{self.sessionId}"
        }
        if byte_range:
            headers["Range"] = f"bytes={byte_range}"

        response = requests.get(url, headers=headers)
        return response.content

    def create_folder_or_file(self, kind, path, overwrite=None, file_content=None):
        """
        Upload files or folders up to 50MB to the File Staging Server. You can only create one file or folder per request.
        API documentation: https://developer.veevavault.com/api/23.2/#create-folder-or-file
        
        :param kind: The kind of item to create. This can be either file or folder.
        :param path: The absolute path, including file or folder name, to place the item in the file staging server. This path is specific to the authenticated user. Admin users can access the root directory. All other users can only access their own user directory.
        :param overwrite: Optional: If set to true, Vault will overwrite any existing files with the same name at the specified destination. For folders, this is always false.
        :param file_content: To upload a file, use the multi-part attachment with the file component. The maximum allowed file size is 50MB.
        
        :return: Response from the API as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/items"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json",
            "Content-Type": "multipart/form-data"
        }
        data = {
            "kind": kind,
            "path": path
        }
        if overwrite is not None:
            data["overwrite"] = overwrite
        if file_content:
            data["file"] = file_content

        response = requests.post(url, headers=headers, data=data)
        return response.json()


    def update_folder_or_file(self, item, parent=None, name=None):
        """
        Move or rename a folder or file on the file staging server. You can move and rename an item in the same request.
        API documentation: https://developer.veevavault.com/api/23.2/#update-folder-or-file
        
        :param item: The absolute path to a file or folder. This path is specific to the authenticated user. Admin users can access the root directory. All other users can only access their own user directory.
        :param parent: Conditional: When moving a file or folder, specifies the absolute path to the parent directory in which to place the file.
        :param name: Conditional: When renaming a file or folder, specifies the new name.
        
        :return: Response from the API as a dictionary containing job ID and URL to check the job status.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/items/{item}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {}
        if parent:
            data["parent"] = parent
        if name:
            data["name"] = name

        response = requests.put(url, headers=headers, data=data)
        return response.json()



    def delete_file_or_folder(self, item, recursive=False):
        """
        Delete an individual file or folder from the file staging server.
        API documentation: https://developer.veevavault.com/api/23.2/#delete-file-or-folder
        
        :param item: The absolute path to the file or folder to delete. This path is specific to the authenticated user. Admin users can access the root directory. All other users can only access their own user directory.
        :param recursive: Applicable to deleting folders only. If true, the request will delete the contents of a folder and all subfolders. The default is false.
        
        :return: Response from the API as a dictionary containing job ID and URL to check the job status.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/items/{item}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        params = {
            "recursive": recursive
        }
        
        response = requests.delete(url, headers=headers, params=params)
        return response.json()



    #######################################################
    # File Staging
    ## Resumable Upload Sessions
    #######################################################

    def create_resumable_upload_session(self, path, size, overwrite=False):
        """
        Initiate a multipart upload session and return an upload session ID.
        API documentation: https://developer.veevavault.com/api/23.2/#create-resumable-upload-session
        
        :param path: The absolute path, including file name, to place the file in the staging server. This path is specific to the authenticated user. Admin users can access the root directory. All other users can only access their own user directory.
        :param size: The size of the file in bytes. The maximum file size is 500GB.
        :param overwrite: If set to true, Vault will overwrite any existing files with the same name at the specified destination. Default is False.
        
        :return: Response from the API as a dictionary containing details about the created upload session.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/upload"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {
            'path': path,
            'size': size,
            'overwrite': overwrite
        }
        
        response = requests.post(url, headers=headers, data=data)
        return response.json()


    def upload_to_session(self, upload_session_id, file_part, part_number, content_length, content_md5=None):
        """
        The session owner can upload parts of a file to an active upload session.
        API documentation: https://developer.veevavault.com/api/23.2/#upload-to-a-session
        
        :param upload_session_id: The upload session ID.
        :param file_part: The file part to be uploaded as binary data.
        :param part_number: The part number, which uniquely identifies a file part and defines its position within the file as a whole.
        :param content_length: The size of the file part in bytes. Parts must be at least 5MB in size, except for the last part uploaded in a session.
        :param content_md5: Optional: The MD5 checksum of the file part being uploaded.
        
        :return: Response from the API as a dictionary containing details about the uploaded file part.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/upload/{upload_session_id}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json",
            "Content-Type": "application/octet-stream",
            "Content-Length": str(content_length),
            "X-VaultAPI-FilePartNumber": str(part_number)
        }
        if content_md5:
            headers["Content-MD5"] = content_md5
        
        response = requests.put(url, headers=headers, data=file_part)
        return response.json()



    def commit_upload_session(self, upload_session_id):
        """
        Mark an upload session as complete and assemble all previously uploaded parts to create a file.
        API documentation: https://developer.veevavault.com/api/23.2/#commit-upload-session
        
        :param upload_session_id: The upload session ID.
        
        :return: Response from the API as a dictionary containing job_id for the commit.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/upload/{upload_session_id}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, headers=headers)
        return response.json()


    def list_upload_sessions(self):
        """
        Return a list of active upload sessions.
        API documentation: https://developer.veevavault.com/api/23.2/#list-upload-sessions
        
        :return: Response from the API as a dictionary containing details of all active upload sessions.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/upload"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()



    def get_upload_session_details(self, upload_session_id):
        """
        Retrieve the details of an active upload session. Admin users can get details for all sessions, while non-Admin users can only get details for sessions if they are the owner.
        API documentation: https://developer.veevavault.com/api/23.2/#get-upload-session-details
        
        :param upload_session_id: The ID of the upload session to retrieve details for.
        :return: Response from the API as a dictionary containing the details of the specified upload session.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/upload/{upload_session_id}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        return response.json()


    def list_file_parts_uploaded_to_session(self, upload_session_id, limit=1000):
        """
        Return a list of parts uploaded in a session. You must be an Admin user or the session owner.
        API documentation: https://developer.veevavault.com/api/23.2/#list-file-parts-uploaded-to-session
        
        :param upload_session_id: The ID of the upload session to retrieve the uploaded file parts for.
        :param limit: Optional parameter to specify the maximum number of items per page in the response, default is 1000.
        :return: Response from the API as a dictionary containing the list of uploaded file parts and pagination details.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/upload/{upload_session_id}/parts"
        params = {"limit": limit}
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers, params=params)
        return response.json()


    def abort_upload_session(self, upload_session_id):
        """
        Abort an active upload session and purge all uploaded file parts. Admin users can see and abort all upload sessions, while non-Admin users can only see and abort sessions where they are the owner.
        API documentation: https://developer.veevavault.com/api/23.2/#abort-upload-session
        
        :param upload_session_id: The ID of the upload session to be aborted.
        :return: Response from the API as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/upload/{upload_session_id}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.delete(url, headers=headers)
        return response.json()




    #######################################################
    # Vault Loader
    #######################################################

    #######################################################
    # Vault Loader
    ## Multi-File Extract
    #######################################################


    def extract_data_files(self, data_objects, sendNotification=False):
        """
        Create a Loader job to extract one or more data files.
        API documentation: https://developer.veevavault.com/api/23.2/#extract-data-files
        
        :param data_objects: List of dictionaries representing the data objects to extract.
        :param sendNotification: Whether to send a Vault notification when the job completes. Defaults to False.
        :return: Response from the API as a dictionary.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/loader/extract"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        params = {
            "sendNotification": sendNotification
        }
        
        response = requests.post(url, headers=headers, params=params, json=data_objects)
        return response.json()


    def retrieve_loader_extract_results(self, job_id, task_id):
        """
        Retrieve the results of a specified job task after submitting a request to extract object types from your Vault.
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-loader-extract-results

        :param job_id: The ID value of the requested extract job.
        :param task_id: The ID value of the requested extract task.
        :return: Response from the API as a string (CSV format).
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/loader/{job_id}/tasks/{task_id}/results"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "text/csv"
        }
        
        response = requests.get(url, headers=headers)
        return response.text


    def retrieve_loader_extract_renditions_results(self, job_id, task_id):
        """
        Retrieve the results of a specified job task that includes renditions requested with documents from your Vault.
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-loader-extract-renditions-results

        :param job_id: The ID value of the requested extract job.
        :param task_id: The ID value of the requested extract task.
        :return: Response from the API as a string (CSV format).
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/loader/{job_id}/tasks/{task_id}/results/renditions"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "text/csv"
        }
        
        response = requests.get(url, headers=headers)
        return response.text







    #######################################################
    # Vault Loader
    ## Multi-File Load
    #######################################################

    def load_data_objects(self, data_objects, send_notification=False):
        """
        Create a loader job and load a set of data files in the Vault.
        API documentation: https://developer.veevavault.com/api/23.2/#load-data-objects

        :param data_objects: A list of dictionaries representing data objects to load. 
        :param send_notification: Boolean indicating whether to send a Vault notification when the job completes.
        :return: Response from the API in JSON format.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/loader/load"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        params = {
            "sendNotification": send_notification
        }
        response = requests.post(url, headers=headers, json=data_objects, params=params)
        return response.json()


    def retrieve_load_success_log_results(self, job_id, task_id):
        """
        Retrieve success logs of the loader results from the Vault.
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-load-success-log-results

        :param job_id: The ID value of the requested extract job.
        :param task_id: The ID value of the requested extract task.
        :return: CSV file that includes the success log of the loader results.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/loader/{job_id}/tasks/{task_id}/successlog"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "text/csv"
        }
        response = requests.get(url, headers=headers)
        return response.content


    def retrieve_load_failure_log_results(self, job_id, task_id):
        """
        Retrieve failure logs of the loader results from the Vault.
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-load-failure-log-results

        :param job_id: The ID value of the requested extract job.
        :param task_id: The ID value of the requested extract task.
        :return: CSV file that includes the failure log of the loader results.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/loader/{job_id}/tasks/{task_id}/failurelog"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "text/csv"
        }
        response = requests.get(url, headers=headers)
        return response.content




    #######################################################
    # Jobs
    #######################################################


    def retrieve_job_status(self, job_id):
        """
        Retrieve the status of a job previously requested through the API from the Vault.
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-job-status

        :param job_id: The ID of the job, returned from the original job request.
        :return: JSON object containing details about the job status.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/jobs/{job_id}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        return response.json()


    def retrieve_job_tasks(self, job_id):
        """
        Retrieve the tasks associated with an SDK job in the Vault.
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-job-tasks

        :param job_id: The ID of the job, returned from the original job request.
        :return: JSON object containing details about the job tasks.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/jobs/{job_id}/tasks"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def retrieve_job_histories(self, start_date=None, end_date=None, status=None, limit=None, offset=None):
        """
        Retrieve a history of all completed jobs in the authenticated Vault. 
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-job-histories

        :param start_date: Sets the date to start retrieving completed jobs, in the format YYYY-MM-DDTHH:MM:SSZ. Optional.
        :param end_date: Sets the date to end retrieving completed jobs, in the format YYYY-MM-DDTHH:MM:SSZ. Optional.
        :param status: Filter to only retrieve jobs in a certain status. Optional.
        :param limit: Paginate the results by specifying the maximum number of histories per page in the response. Optional.
        :param offset: Paginate the results displayed per page by specifying the amount of offset from the first job history returned. Optional.
        :return: JSON object containing details about the job histories.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/jobs/histories"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
            "limit": limit,
            "offset": offset
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()


    def retrieve_job_monitors(self, start_date=None, end_date=None, status=None, limit=None, offset=None):
        """
        Retrieve monitors for jobs which have not yet completed in the authenticated Vault. 
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-job-monitors

        :param start_date: Sets the date to start retrieving uncompleted jobs, based on the date and time the job instance was created. Optional.
        :param end_date: Sets the date to end retrieving uncompleted jobs, based on the date and time the job instance was created. Optional.
        :param status: Filter to only retrieve jobs in a certain status. Optional.
        :param limit: Paginate the results by specifying the maximum number of jobs per page in the response. Optional.
        :param offset: Paginate the results displayed per page by specifying the amount of offset from the first job instance returned. Optional.
        :return: JSON object containing details about the job monitors.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/jobs/monitors"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "status": status,
            "limit": limit,
            "offset": offset
        }
        response = requests.get(url, headers=headers, params=params)
        return response.json()



    def start_job(self, job_id):
        """
        Moves up a scheduled job instance to start immediately. Each time a user calls this API, Vault cancels the next scheduled instance of the specified job. 
        API documentation: https://developer.veevavault.com/api/23.2/#start-job

        :param job_id: The ID of the scheduled job instance to start.
        :return: JSON object containing the response details.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/jobs/start_now/{job_id}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.post(url, headers=headers)
        return response.json()



    #######################################################
    # Managing Vault Java SDK
    #######################################################


    def retrieve_single_source_code_file(self, class_name):
        """
        Retrieve a single source code file from the currently authenticated Vault.
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-single-source-code-file
        
        :param class_name: The fully qualified class name of your file.
        :return: The source code file content.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/code/{class_name}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        return response.text


    def enable_or_disable_vault_extension(self, class_name, action):
        """
        Enable or disable a deployed Vault extension in the currently authenticated Vault. 
        Only available on entry-point classes, such as triggers and actions.
        API documentation: https://developer.veevavault.com/api/23.2/#enable-or-disable-vault-extension

        :param class_name: The fully qualified class name of your file.
        :param action: The action to be performed - either 'enable' or 'disable'.
        :return: API response.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/code/{class_name}/{action}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json",
            "Content-Type": "multipart/form-data"
        }
        response = requests.put(url, headers=headers)
        return response.json()


    def add_or_replace_single_source_code_file(self, file_path):
        """
        Add or replace a single .java file in the currently authenticated Vault. If the given file does not already exist in the Vault, it is added. If the file already exists in the Vault, the file is updated. It is not recommended to use this endpoint to deploy code as it may introduce code that breaks existing deployed code. For best practices, use the VPK Deploy method.
        API documentation: https://developer.veevavault.com/api/23.2/#add-or-replace-single-source-code-file

        :param file_path: The path to the .java file you wish to add or replace.
        :return: API response.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/code"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json",
            "Content-Type": "multipart/form-data"
        }
        with open(file_path, 'rb') as file:
            response = requests.put(url, headers=headers, files={'file': file})
        return response.json()


    def delete_single_source_code_file(self, class_name):
        """
        Delete a single source code file from the currently authenticated Vault. This endpoint is not recommended for use as it may delete code that breaks existing deployed code. For best practices, use the VPK Deploy method. Note that you cannot delete a code component currently in use.
        API documentation: https://developer.veevavault.com/api/23.2/#delete-single-source-code-file

        :param class_name: The fully qualified class name of the file to be deleted.
        :return: API response.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/code/{class_name}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.delete(url, headers=headers)
        return response.json()


    def validate_imported_package(self, package_id):
        """
        Validate a previously imported VPK package with Vault Java SDK code. Note that this endpoint does not validate component dependencies for Configuration Migration packages.
        API documentation: https://developer.veevavault.com/api/23.2/#validate-imported-package

        :param package_id: The ID of the package to validate, which can be found in the API response of a package import or in the URL of the package in the Vault UI.
        :return: API response.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/vobject/vault_package__v/{package_id}/actions/validate"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.post(url, headers=headers)
        return response.json()


    def retrieve_signing_certificate(self, cert_id):
        """
        Allows you to retrieve a signing certificate included in a Spark message header to verify that the received message came from Vault.
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-signing-certificate

        :param cert_id: The cert_id is provided in each Spark message in the X-VaultAPISignature-CertificateId header.
        :return: The public key certificate (.pem) file used for message verification.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/certificate/{cert_id}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        return response.text


    def retrieve_all_queues(self):
        """
        Retrieve all queues in a Vault.
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-all-queues
        
        :return: A list of all available queues and their operational statuses.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/queues"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        return response.json()



    def retrieve_queue_status(self, queue_name):
        """
        Retrieve the status of a specific queue.
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-queue-status
        
        :param queue_name: The name of a specific queue. For example, queue__c.
        :return: The status of the specified queue including delivery status, number of messages in the queue, and details of the last message delivered.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/queues/{queue_name}"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.get(url, headers=headers)
        return response.json()


    def disable_delivery(self, queue_name):
        """
        Disable the delivery of messages in an outbound Spark messaging queue or an SDK job queue.
        API documentation: https://developer.veevavault.com/api/23.2/#disable-delivery
        
        :param queue_name: The name of a specific queue.
        :return: Response status of the request.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/queues/{queue_name}/actions/disable_delivery"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.put(url, headers=headers)
        return response.json()


    def enable_delivery(self, queue_name):
        """
        Enable the delivery of messages in an outbound Spark messaging queue or an SDK job queue.
        API documentation: https://developer.veevavault.com/api/23.2/#enable-delivery
        
        :param queue_name: The name of a specific queue.
        :return: Response status of the request.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/queues/{queue_name}/actions/enable_delivery"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.put(url, headers=headers)
        return response.json()

    def reset_queue(self, queue_name):
        """
        Delete all messages in a specific queue. This action is final and cannot be undone.
        API documentation: https://developer.veevavault.com/api/23.2/#reset-queue
        
        :param queue_name: The name of a specific queue.
        :return: Response status and message of the request.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/queues/{queue_name}/actions/reset"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        response = requests.put(url, headers=headers)
        return response.json()






    #######################################################
    # Clinical Operations
    #######################################################

    def create_edls(self, study_id, file_content, content_type='text/csv', accept='text/csv', apply_where_edl_items_exist=None):
        """
        Create a new Expected Document List.
        API documentation: https://developer.veevavault.com/api/23.2/#create-edls
        
        :param study_id: The ID of the study.
        :param file_content: The content of the file to be uploaded in text/csv format.
        :param content_type: The content type of the request, defaults to 'text/csv'.
        :param accept: The format in which to receive the response, defaults to 'text/csv'.
        :param apply_where_edl_items_exist: Optional parameter to apply the Create EDL job to existing EDLs.
        :return: Response status and job details of the request.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/study__v/{study_id}/actions/etmfcreateedl"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": content_type,
            "Accept": accept
        }
        params = {
            "applyWhereEdlItemsExist": apply_where_edl_items_exist
        }
        response = requests.post(url, headers=headers, data=file_content, params=params)
        return response.json()


    def recalculate_milestone_document_field(self, file_content):
        """
        Recalculate the milestone__v field on a specified set of documents.
        API documentation: https://developer.veevavault.com/api/23.2/#recalculate-milestone-document-field
        
        :param file_content: The content of the CSV file to be uploaded, which contains document id values in an id column.
        :return: Response status and message of the request.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/recalculatemilestones/batch"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }
        response = requests.post(url, headers=headers, data=file_content)
        return response.json()


    def apply_edl_template_to_milestone(self, milestone_id, edl_id):
        """
        Apply an EDL template to a Milestone object record.
        API documentation: https://developer.veevavault.com/api/23.2/#apply-edl-template-to-a-milestone

        :param milestone_id: The ID of the milestone.
        :param edl_id: The ID of the EDL template to apply to this milestone.
        :return: Response status and job details of the request.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/milestone__v/{milestone_id}/actions/etmfcreateedl"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        data = {
            "edl_id": edl_id
        }
        response = requests.post(url, headers=headers, data=data)
        return response.json()


    def create_milestones_from_template(self, object_name, object_record_id):
        """
        Use this request to initiate the Create Milestones from Template user action on a study, study country, or site.
        API documentation: https://developer.veevavault.com/api/23.2/#create-milestones-from-template

        :param object_name: The object name__v field value. This endpoint only works with the study__v, study_country__v, or site__v objects.
        :param object_record_id: The object record ID field value.
        :return: Response status and job details of the request.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/{object_name}/{object_record_id}/actions/createmilestones"
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }
        response = requests.post(url, headers=headers)
        return response.json()



    def execute_milestone_story_events(self, object_name, csv_file_path, id_param=None):
        """
        Use this request to create Milestones based on specific Story Events for multiple studies, study countries, or sites.
        API documentation: https://developer.veevavault.com/api/23.2/#execute-milestone-story-events

        :param object_name: The object name__v field value. This endpoint only works with the study__v, study_country__v, or site__v objects.
        :param csv_file_path: Path to the CSV input file containing details to create milestones.
        :param id_param: (Optional) Unique field name to identify objects in the CSV input, if not using id.
        :return: Response details containing job IDs or errors.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/clinical/milestone/{object_name}/actions/applytemplate"
        if id_param:
            url += f"?idParam={id_param}"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }

        with open(csv_file_path, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
        
        return response.json()



    def veeva_site_connect_distribute_to_sites(self, distribution_id):
        """
        This API allows sponsors and CROs to send Safety reports and letters to Sites. 
        API documentation: https://developer.veevavault.com/api/23.2/#veeva-site-connect-distribute-to-sites

        :param distribution_id: The record ID of the Safety Distribution record to send. Must be in a Ready or Distributed state.
        :return: Response details containing job ID and message.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/clinical/safety_distributions/{distribution_id}/actions/send"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.post(url, headers=headers)
        
        return response.json()



    def populate_site_fee_definitions(self, target_study, source_study=None, source_template=None):
        """
        Given an existing study with Site Fee Definitions or an eligible Site Fee Template, 
        automatically generate Site Fee Definitions for a new target study. 
        This endpoint is only available in CTMS Vaults with the Vault Payments add-on.
        API documentation: https://developer.veevavault.com/api/23.2/#populate-site-fee-definitions

        :param target_study: The new study to populate with Site Fee Definitions.
        :param source_study: (Optional) To copy the Site Fee Definitions from studies, include an array with the study IDs.
        :param source_template: (Optional) To copy the Site Fee Definitions from Site Fee Templates, include an array with the template IDs.
        :return: Response details containing status and other information.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/clinical/payments/populate-site-fee-definitions"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        data = {
            "target_study": target_study,
        }
        if source_study:
            data["source_study"] = source_study
        if source_template:
            data["source_template"] = source_template

        response = requests.post(url, headers=headers, json=data)
        
        return response.json()




    #######################################################
    # PromoMats
    #######################################################

    def create_document_update_job(self):
        """
        Vault owners can update documents with a Global Content Type of 'Not Specified' to a mapped value. 
        Learn more about Configuring PromoMats Standard Metrics in Vault Help.
        API documentation: https://developer.veevavault.com/api/23.2/#standard-metrics-create-document-update-job

        :return: Response details containing jobInstanceId and any errors encountered.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/standardMetrics/createDocumentUpdateJob"

        headers = {
            "Authorization": f"{self.sessionId}"
        }

        response = requests.post(url, headers=headers)
        
        return response.json()



    #######################################################
    # QualityDocs
    #######################################################

    def document_role_check_for_document_change_control(self, object_record_id, application_role):
        """
        Check if any document added to a Document Change Control (DCC) record has one or more users in a specified 
        Application Role. This API only checks documents added to the standard Documents to be Released and Documents 
        to be Made Obsolete sections.
        API documentation: https://developer.veevavault.com/api/23.2/#document-role-check-for-document-change-control

        :param object_record_id: The ID field value of the document_change_control__v object record.
        :param application_role: The name of the application_role__v.
        :return: Response details including the Boolean check_result field.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/document_change_control__v/{object_record_id}/actions/documentrolecheck"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        data = {
            "application_role": application_role
        }

        response = requests.post(url, headers=headers, data=data)
        
        return response.json()



    #######################################################
    # QMS
    #######################################################


    def update_quality_team_members(self, object_name, csv_file_path):
        """
        Manage Quality Team members on existing records. This endpoint does not support initial Quality Team record 
        migrations or the creation of new Quality Teams on existing process records. Vault performs updates to Quality 
        Team assignments asynchronously on behalf of the user.
        API documentation: https://developer.veevavault.com/api/23.2/#update-quality-team-members

        :param object_name: The object name__v field value for the team-enabled object. 
                            For example, risk_event__v, investigation__qdm, quality_event__qdm.
        :param csv_file_path: The path to the CSV file containing the necessary parameters.
        :return: Response details including the job_id for the action.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/quality/qms/teams/vobjects/{object_name}/actions/manageassignments"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "text/csv"
        }

        with open(csv_file_path, 'rb') as f:
            response = requests.post(url, headers=headers, data=f)
        
        return response.json()





    #######################################################
    # RIM Submissions Archive
    #######################################################

    def import_submission(self, submission_id, file_path):
        """
        Import a submission into your Vault. Before executing this request, ensure you have the necessary permissions, 
        created the required object records in your Vault, and uploaded a valid submission import file or folder to your 
        file staging server following the proper structure.
        
        API documentation: https://developer.veevavault.com/api/23.2/#import-submission

        :param submission_id: The id field value of the submission__v object record.
        :param file_path: The path to the submission folder or ZIP file relative to the file staging server root 
                        or to the path to your user file staging folder.
        :return: Response details including the job_id and the URL to check the current status of the import request.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/submission__v/{submission_id}/actions/import"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

        data = {
            "file": file_path
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        return response.json()


    def retrieve_submission_import_results(self, submission_id, job_id):
        """
        Retrieve the results of a completed submission import job. Before executing this request, ensure 
        you have the necessary permissions and that the submission import job is completed (no longer active).

        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-submission-import-results

        :param submission_id: The id field value of the submission__v object record.
        :param job_id: The jobId field value returned from the Import Submission request.
        :return: Response details including the id, major_version_number__v, and minor_version_number__v of the created submission binder.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/submission__v/{submission_id}/actions/import/{job_id}/results"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()


    def retrieve_submission_metadata_mapping(self, submission_id):
        """
        Retrieve the metadata mapping values of an eCTD submission package. Before executing this request, 
        make sure you have the necessary permissions.

        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-submission-metadata-mapping

        :param submission_id: The id field value of the submission__v object record.
        :return: Response details including metadata mapping records and relevant details such as name__v, 
                external_id__v, xml_id and possible mappings like clinical_site__v, clinical_study__v, etc.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/submission__v/{submission_id}/actions/ectdmapping"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.get(url, headers=headers)

        return response.json()



    def update_submission_metadata_mapping(self, submission_id, mapping_values):
        """
        Update the mapping values of a submission. Note that XML identifiers are read-only and cannot be updated via the API. 

        API documentation: https://developer.veevavault.com/api/23.2/#update-submission-metadata-mapping

        :param submission_id: The id field value of the submission__v object record.
        :param mapping_values: A list of dictionaries containing mapping values to be updated.
        :return: Response details including success status and details of updated mapping values.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/submission__v/{submission_id}/actions/ectdmapping"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        response = requests.put(url, headers=headers, json=mapping_values)

        return response.json()



    def remove_submission(self, submission_id):
        """
        Delete a previously imported submission from your Vault. By removing a submission, you delete any sections created in the archive binder as part of the submission import. This action also removes any documents in the submission from the archive binder but does not delete the documents from Vault.

        API documentation: https://developer.veevavault.com/api/23.2/#remove-submission

        :param submission_id: The id field value of the submission__v object record.
        :return: Response details including job ID and URL to check the job status.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/submission__v/{submission_id}/actions/import"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        response = requests.delete(url, headers=headers)

        return response.json()



    def cancel_submission(self, submission_id):
        """
        Cancel an ongoing submission import or removal process. Depending on the current archive status of the submission, this action will have different outcomes as described in the API documentation. To proceed with a new import, the submission must be removed first if it was in the import or removal process.

        API documentation: https://developer.veevavault.com/api/23.2/#cancel-submission

        :param submission_id: The id field value of the submission__v object record.
        :return: Response details including the status of the request.
        """
        self.LatestAPIversion = 'v23.2'
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/vobjects/submission__v/{submission_id}/actions/import"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        params = {
            "cancel": "true"
        }

        response = requests.post(url, headers=headers, params=params)
        
        return response.json()



    def export_submission(self, binder_id, submission_id, major_version=None, minor_version=None):
        """
        Export a submission, allowing to either export the most recent version or a specific version of a Submissions Archive binder. The function supports two types of requests based on whether the major_version and minor_version are provided or not.

        API documentation: https://developer.veevavault.com/api/23.2/#export-submission

        :param binder_id: The id field value of the binder.
        :param submission_id: The id field value of the submission__v object record.
        :param major_version: (Optional) The major_version_number__v field value of the binder.
        :param minor_version: (Optional) The minor_version_number__v field value of the binder.
        :return: Response details including the URL to check the status of the export job and the job_id.
        """
        self.LatestAPIversion = 'v23.2'
        
        if major_version is not None and minor_version is not None:
            url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/versions/{major_version}/{minor_version}/actions/export"
        else:
            url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/actions/export"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }

        params = {
            "submission": submission_id
        }

        response = requests.post(url, headers=headers, params=params)
        
        return response.json()


    def export_partial_submission(self, binder_id, submission_id, major_version, minor_version, file_path):
        """
        Exports specific sections and documents from a submissions binder in Vault. Depending on the major_version and minor_version parameters, it can either export from the latest version or a specific version of the submissions binder.

        API documentation: https://developer.veevavault.com/api/23.2/#export-partial-submission

        :param binder_id: The id field value of the binder.
        :param submission_id: The id field value of the submission__v object record.
        :param major_version: The major_version_number__v field value of the binder.
        :param minor_version: The minor_version_number__v field value of the binder.
        :param file_path: The path to the CSV or JSON file containing the id values of the binder sections and/or documents to be exported.
        :return: Response details including the URL to check the status of the export job and the job_id.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/objects/binders/{binder_id}/versions/{major_version}/{minor_version}/actions/export"

        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "text/csv",
            "Accept": "application/json"
        }

        params = {
            "submission": submission_id
        }

        with open(file_path, 'rb') as f:
            response = requests.post(url, headers=headers, params=params, data=f)
        
        return response.json()


    def download_exported_submission_files(self, job_id):
        """
        Downloads the files of a successfully completed submission export job from the file staging server. The files are packaged in a ZIP file on the file staging server.

        API documentation: https://developer.veevavault.com/api/23.2/#download-exported-submission-files-via-file-staging-server

        :param job_id: The job ID of the successfully completed submission export job.
        :return: A message indicating the status of the download operation.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/services/file_staging/jobs/{job_id}/files"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        response = requests.get(url, headers=headers)
        
        return response.json()

    def copy_into_content_plan(self, source_id, target_id, order, copy_documents):
        """
        Copies a content plan section or item to reuse existing content and prevent duplicate work. This operation can be used to copy a clinical study or quality section and its matched documents for a similar submission to a different application.

        API documentation: https://developer.veevavault.com/api/23.2/#copy-into-content-plan

        :param source_id: The ID of the content plan or content plan item to copy.
        :param target_id: The ID of the parent content plan where the source content plan will be copied under. The target content plan cannot be inactive.
        :param order: An integer indicating the position in the target content plan where the source content plan will be copied. A value of 1 indicates the first position in the target content plan.
        :param copy_documents: A boolean value indicating whether matched documents are included in the copy. If false, matched documents are not included in the copy. This parameter cannot be omitted.
        :return: A JSON response containing the job ID of the asynchronous copy operation or the record ID of the newly copied content plan item.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/rim/content_plans/actions/copyinto"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        body = {
            "source_id": source_id,
            "target_id": target_id,
            "order": order,
            "copy_documents": copy_documents
        }
        
        response = requests.post(url, headers=headers, json=body)
        
        return response.json()



    #######################################################
    # Safety
    #######################################################

    #######################################################
    # Safety
    ## Intake
    #######################################################



    def intake_inbox_item(self, file_path, origin_organization, format, organization, transmission_profile=None):
        """
        Imports an Inbox Item from an E2B (R2) or E2B (R3) file containing one or more Individual Case Safety Reports (ICSRs).

        API documentation: https://developer.veevavault.com/api/23.2/#intake-inbox-item

        :param file_path: The file path of the E2B file to be imported.
        :param origin_organization: (Optional) The Vault API Name for the organization sending the E2B file. If not provided, the Origin Organization is left blank.
        :param format: The format of the file being imported, which must match the Vault API Name of the Inbound Transmission Format picklist value. It should be an E2B format.
        :param organization: (Optional) To specify which organization to send the Case to, enter the Vault API Name for the Organization record. If not provided, the Organization is set to vault_customer__v. Note that the Organization record type must be Sponsor.
        :param transmission_profile: (Optional) The Vault API Name of the Transmission Profile to be used for E2B Intake. This parameter is necessary for Narrative Template Override and Inbox Item Auto-Promotion. If not provided, Vault uses parameters on the general_api_profile__v.
        
        :return: A JSON response containing the URL to retrieve the current status of the import request and the intake ID of the E2B import.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/safety/intake/inbox-item"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "multipart/form-data"
        }
        
        data = {
            'file': ('file', open(file_path, 'rb')),
            'origin-organization': origin_organization,
            'format': format,
            'organization': organization
        }
        
        if transmission_profile:
            data['transmission-profile'] = transmission_profile
        
        response = requests.post(url, headers=headers, files=data)
        
        return response.json()


    def intake_imported_case(self, file_path, format, organization, origin_organization=None):
        """
        Imports an Imported Case from an E2B (R2) or E2B (R3) file containing one or more Individual Case Safety Reports (ICSRs).
        
        API documentation: https://developer.veevavault.com/api/23.2/#intake-imported-case

        :param file_path: The file path of the E2B file to be imported.
        :param format: The format of the file being imported, which must match the Vault API Name of the Inbound Transmission Format picklist value. Must be an E2B format or other__v.
        :param organization: (Optional) To specify which organization to send the Case to, enter the Vault API Name for the Organization record. If not provided, the Organization is set to vault_customer__v.
        :param origin_organization: (Optional) The Vault API Name for the organization sending the E2B file. If not provided, the Origin Organization is left blank.
        
        :return: A JSON response containing the URL to retrieve the current status of the import request and the intake ID of the E2B import.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/safety/intake/imported-case"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Content-Type": "multipart/form-data"
        }
        
        data = {
            'file': ('file', open(file_path, 'rb')),
            'format': format,
            'organization': organization
        }
        
        if origin_organization:
            data['origin-organization'] = origin_organization
        
        response = requests.post(url, headers=headers, files=data)
        
        return response.json()




    def retrieve_intake_status(self, inbound_id):
        """
        Retrieve the status of an intake API call using the inbound transmission ID for the ICSR intake job.
        
        API documentation: https://developer.veevavault.com/api/23.2/#retrieve-intake-status

        :param inbound_id: The Inbound Transmission ID for the ICSR intake job.
        
        :return: A JSON response containing details about the status of the intake job including processing status, ACK retrieval URL, inbound transmission and document IDs, number of cases and their statuses.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/safety/intake/status"
        
        headers = {
            "Authorization": f"{self.sessionId}",
            "Accept": "application/json"
        }
        
        params = {
            'inbound_id': inbound_id
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        return response.json()



    def retrieve_ack(self, inbound_id):
        """
        Retrieve the E2B acknowledgement message (ACK) after sending an intake call.
        API Documentation URL: https://developer.veevavault.com/api/23.2/#retrieve-ack
        
        Args:
            inbound_id (str): The Inbound Transmission ID for the ICSR intake job.
            
        Returns:
            str: The response containing the ACK XML or a failure message.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/safety/intake/ack"
        params = {'inbound_id': inbound_id}
        headers = {
            'Authorization': f"{self.sessionId}",
            'Accept': 'application/json'
        }
        
        response = requests.get(url, headers=headers, params=params)
        
        if response.status_code == 200:
            return response.text
        else:
            return response.json()






    #######################################################
    # Safety
    ## Intake JSON
    #######################################################

    def intake_json(self, api_name, intake_json, intake_form=None):
        """
        Use this endpoint to send JSON to Vault Safety, which will be imported to a single Inbox Item.
        API Documentation URL: https://developer.veevavault.com/api/23.2/#intake-json
        
        Args:
            api_name (str): The Vault API Name for the Organization record.
            intake_json (str): The filepath for the JSON intake file, or the raw JSON text.
            intake_form (str, optional): The filepath for a source intake document.
            
        Returns:
            dict: The response containing job details or a failure message.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/safety/ai/intake?API_Name={api_name}"
        
        headers = {
            'Authorization': f"{self.sessionId}",
            'Content-Type': 'application/json' if intake_form is None else 'multipart/form-data'
        }
        
        data = {
            'intake_json': intake_json,
            'intake_form': intake_form
        }
        
        response = requests.post(url, headers=headers, data=data)
        
        return response.json()


    #######################################################
    # Safety
    ## Import Narrative
    #######################################################

    def import_narrative(self, case_id, narrative_type, narrative_language, narrative_text, link_translation_to_primary=False):
        """
        Use this endpoint to import narrative text into a Case narrative.
        API Documentation URL: https://developer.veevavault.com/api/23.2/#import-narrative

        Args:
            case_id (str): Destination Case or Adverse Event Report ID.
            narrative_type (str): Type of narrative - 'primary' or 'translation'.
            narrative_language (str): Three-letter ISO 639-2 language code.
            narrative_text (str): Narrative text to be imported, limited to 100000 characters.
            link_translation_to_primary (bool): Set to true to add the localized narrative document as a supporting document to the global (English) narrative document. Defaults to False.

        Returns:
            dict: The response containing status of the request.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/safety/import-narrative"

        headers = {
            'Authorization': f"{self.sessionId}",
            'caseId': case_id,
            'narrativeType': narrative_type,
            'narrativeLanguage': narrative_language,
            'Content-Type': 'text/plain',
            'link_translation_to_primary': str(link_translation_to_primary).lower()
        }

        response = requests.post(url, headers=headers, data=narrative_text)

        return response.json()


    def bulk_import_narrative(self, narratives_file_path, integrity_check=False, migration_mode=False, archive_document=None):
        """
        Use this endpoint to bulk import case narratives into Vault Safety.
        API Documentation URL: https://developer.veevavault.com/api/23.2/#bulk-import-narrative

        Args:
            narratives_file_path (str): The file path of the CSV containing the narratives to be imported.
            integrity_check (bool): Optional: Set to true to perform additional integrity checks on the CSV file. Defaults to false.
            migration_mode (bool): Optional: Set to true to perform additional verifications on the localizedCaseId. Defaults to false.
            archive_document (bool): Optional: Set to true to send the imported narrative documents directly to the document archive, or false to create the imported documents as active narratives. Defaults to None.

        Returns:
            dict: The response containing the status of the request and details of the import operation.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/safety/import-narrative/batch/"

        headers = {
            'Content-Type': 'multipart/form-data',
            'Accept': 'text/csv',
            'Authorization': f"{self.sessionId}",
            'X-VaultAPI-IntegrityCheck': str(integrity_check).lower(),
            'X-VaultAPI-MigrationMode': str(migration_mode).lower()
        }

        if archive_document is not None:
            headers['X-VaultAPI-ArchiveDocument'] = str(archive_document).lower()

        with open(narratives_file_path, 'rb') as f:
            files = {'narratives': f}
            response = requests.post(url, headers=headers, files=files)

        return response.json()


    def retrieve_bulk_import_status(self, import_id):
        """
        Use this endpoint to retrieve the status of a bulk narrative import.
        API Documentation URL: https://developer.veevavault.com/api/23.2/#retrieve-bulk-import-status

        Args:
            import_id (str): The import_id of the bulk narrative import job, retrieved from the job request response details.

        Returns:
            dict: The response containing the status and details of the bulk narrative import job.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/safety/import-narrative/batch/{import_id}"

        headers = {
            'Authorization': f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)

        return response.json()



    #######################################################
    # SiteVault
    #######################################################

    def retrieve_documents_and_signatories(self, participant_id):
        """
        Retrieve the valid blank ICFs and signatories for a participant.
        API Documentation URL: https://developer.veevavault.com/api/23.2/#retrieve-documents-and-signatories

        Args:
            participant_id (str): The SiteVault ID of the participant. Use the /query REST interface to query the Participant (subject__v) object for the participant ID.

        Returns:
            list: The response listing the valid blank ICFs and signatories for the participant.
        """
        self.LatestAPIversion = 'v23.2'

        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/sitevault/econsent/participant/{participant_id}"

        headers = {
            'Authorization': f"{self.sessionId}"
        }

        response = requests.get(url, headers=headers)

        return response.json()

    def send_documents_to_signatories(self, documents_version_id, signatory_id, signatory_role, subject_id):
        """
        Send documents to signatories for signature.
        API Documentation URL: https://developer.veevavault.com/api/23.2/#send-documents-to-signatories

        Args:
            documents_version_id (str): The ID of the blank ICF.
            signatory_id (str): The ID of the signatory.
            signatory_role (str): The role of the signatory.
            subject_id (str): The ID of the participant.

        Returns:
            dict: The response listing the participant, the blank ICF, any signatories, and a job ID.
        """
        self.LatestAPIversion = 'v23.2'
        
        url = f"{self.vaultURL}/api/{self.LatestAPIversion}/app/sitevault/econsent/send"
        
        headers = {
            'Authorization': f"{self.sessionId}",
            'Content-Type': 'application/json'
        }
        
        payload = {
            "documents.version_id__v": documents_version_id,
            "signatory__v.id": signatory_id,
            "signatory__v.role__v": signatory_role,
            "subject__v.id": subject_id
        }
        
        response = requests.post(url, headers=headers, json=payload)
        
        return response.json()


    #######################################################
    ## Custom Functions
    #######################################################
    
    
    def call_url(self, url, method='GET', data=None, headers=None, params=None):
        
        default_headers = {
            "Authorization": self.sessionId,
            "Accept": "application/json"
        }
        
        headers = default_headers if headers is None else headers
        url = self.vaultURL + url
        
        if method == 'GET':
            response = requests.get(url, headers=headers, params=params)
        elif method == 'POST':
            response = requests.post(url, headers=headers, data=data)
        elif method == 'PUT':
            response = requests.put(url, headers=headers, data=data)
        elif method == 'DELETE':
            response = requests.delete(url, headers=headers)
        else:
            raise Exception(f"Invalid method: {method}")
        
        return response.json()
    

    async def retrieve_and_download_config_report(self):
        """
        Kicks off a config report job, monitors its status, and downloads the report file once the job is successful.

        Args:
            self: The Veeva Vault client instance.

        Returns:
            None
        """
        # Step 1: Kick off the config report job
        result = self.vault_configuration_report()
        job_id = result.get('job_id')
        
        if not job_id:
            print("Failed to initiate the job.")
            return

        # Step 2: Check the job status every 10 seconds
        while True:
            time.sleep(10)
            status_result = self.retrieve_job_status(str(job_id))
            job_status = status_result.get('data', {}).get('status')
            
            if job_status == 'SUCCESS':
                print("Job completed successfully.")
                break
            else:
                print("Job still executing... Checking again in 10 seconds.")

        # Step 3: Download the file if the job was successful
        artifact_url = status_result.get('data', {}).get('links', [])[1].get('href')
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Authorization": f"{self.sessionId}"
        }

        vaultId = self.vaultId
        iso_datetime = datetime.now().isoformat(timespec='seconds').replace(':', '-')
        response = requests.get(artifact_url, headers=headers)
        if response.status_code == 200:
            with open(f'{iso_datetime}_vault_{vaultId}_config_report.zip', 'wb') as file:
                file.write(response.content)
            print("File downloaded successfully")
        else:
            print(f"Failed to download the file. HTTP Status Code: {response.status_code}")
