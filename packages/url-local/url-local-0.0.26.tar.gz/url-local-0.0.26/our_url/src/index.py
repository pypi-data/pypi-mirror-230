import pymysql
import os
from dotenv.main import load_dotenv
from logger_local.MessageSeverity import MessageSeverity
from .brand_name_enum import BrandName
from .component_name_enum import ComponentName
from .entity_name_enum import EntityName
from .action_name_enum import ActionName
from .environment_name_enum import EnvironmentName
import urllib.parse

load_dotenv()

# TODO: This should be in url_circlrz.py and not index.py
class UrlCirclez:

    # static dict for domain mapping
    domain_mapping = {
        'authentication.dvlp1.circ.zone' : 'i4wp5o2381.execute-api.us-east-1.amazonaws.com',
        'authentication.play1.circ.zone' : 'nmxjjpyrv9.execute-api.us-east-1.amazonaws.com',
        'user-registration.dvlp1.circ.zone' : 'lczo7l194b.execute-api.us-east-1.amazonaws.com',
        'user-registration.play1.circ.zone' : 't3tnkh0r64.execute-api.us-east-1.amazonaws.com',
        'group.dvlp1.circ.zone' : 't91y4nxsye.execute-api.us-east-1.amazonaws.com',
        'group.play1.circ.zone' : 'fsujmjyfal.execute-api.us-east-1.amazonaws.com',
        'marketplace-goods.play1.circ.zone' : 'j8eoz0mpsj.execute-api.us-east-1.amazonaws.com',
        'logger.dvlp1.circ.zone' : 't91y4nxsye.execute-api.us-east-1.amazonaws.com',
        'logger.play1.circ.zone' : 'fsujmjyfal.execute-api.us-east-1.amazonaws.com',
        'gender-detection.play1.circ.zone' : '353sstqmj5.execute-api.us-east-1.amazonaws.com',
        'gender-detection.dvlp1.circ.zone' : '353sstqmj5.execute-api.us-east-1.amazonaws.com',
        # 'event.play1.circ.zone': 'https://p89mpsr5m1.execute-api.us-east-1.amazonaws.com/dev',
        # 'event.dvlp1.circ.zone': 'https://wbq5liyk63.execute-api.us-east-1.amazonaws.com/dvlp1/event',
        # 'websocket.dvlp1.circ.zone': 'ws://23.22.217.199:8080',
        # 'websocket.play1.circ.zone': 'ws://23.22.217.199:8080',
        'group-profile.play1.circ.zone':'https://wh1toflnza.execute-api.us-east-1.amazonaws.com/play1/api/v1/group-profile'
    }

    def _base_domain(brand_name: str, environment_name: str) -> str:
        '''
        Return the base domain based on the input environment.

        Parameters:
            brand_name (string): Actual brand name.
            env_name (string): Desired environment name

        Return:
            A string that represent the base domain of given environment name.

        '''
        if brand_name == BrandName.CIRCLEZ.value:
            if environment_name == EnvironmentName.DVLP1.value:
                return 'dvlp1.circ.zone'
            
            elif environment_name == EnvironmentName.PLAY1.value:
                return 'play1.circ.zone'
            elif environment_name == EnvironmentName.LOCAL:
                return 'localhost'
            else:
                raise ValueError('Invalid ENVIRONMENT_NAME "'+environment_name+'" in BRAND_NAME=Circlez')
        else:
            raise ValueError('Invalid BRAND_NAME "'+brand_name+'"')

        return ''
    


    @staticmethod
    def app_url(brand_name: str, environment_name: str) -> str:
        if brand_name == BrandName.CIRCLEZ.value:
            if environment_name == EnvironmentName.LOCAL.value:
                # TODO: Align it with TypeScript default and environment variable.
                return "localhost:5173"
            elif environment_name == EnvironmentName.PLAY1.value:
                return "http://circles-user-reactjs-frontend.play1.circ.zone.s3-website-us-east-1.amazonaws.com/"
            elif environment_name == EnvironmentName.DVLP1.value:
                return "https://d2f9rjvjaf75eo.cloudfront.net/"
            else:
                raise ValueError('Invalid environment name')
        return 'unknown'
    


    @staticmethod
    def endpoint_url(brand_name: str, environment_name: str, component: str, entity: str, version: int, action: str, path_parameters=None, query_parameters=None) -> str:
        '''
        Function that generate a url with the format: 
            "https://{direct_domain}/{environment_name}/api/v{version}/{entity}/{action}/{parameters}"

        Parameters:
            brand_name (string): Actual brand name.
            environment_name (string): Desired environment name.
            component (string): Desired component.
            version (integer): Version.
            action (string): Desired action.
            path_parameters (dictionary): A dictionary representing the path parameters with their values.
            query_parameters (dictionary): A dictionary representing the query parameters with their values.

        Return:
            A string that represent the desired endpoint url based on input.

        '''
        base_url = UrlCirclez._base_url_builder(component, brand_name, environment_name, version, entity, action)

        if path_parameters:
            path_params_string = '/'.join([urllib.parse.quote_plus(str(val)) for val in path_parameters.values()])
            url_with_path_params = f"{base_url}/{path_params_string}"
        else:
            url_with_path_params = base_url

        if query_parameters:
            query_params_string = '&'.join([f"{urllib.parse.quote_plus(key)}={urllib.parse.quote_plus(str(value))}" for key, value in query_parameters.items()])
            url_with_query_params = f"{url_with_path_params}?{query_params_string}"
        else:
            url_with_query_params = url_with_path_params
        
        new_url = UrlCirclez._convert_to_direct_url(url_with_query_params)
        return new_url



    def _base_url_builder(component: str, brand_name: str, environment_name: str, version: int, entity: str, action: str) -> str:
        '''
        Function that generate the basic direct url with the format:
            "https://{direct_domain}/{environment_name}/api/v{version}/{entity}/{action}"

        Parameters:
            brand_name (string): Actual brand name.
            environment_name (string): Desired environment name.
            component (string): Desired component.
            version (integer): Version.
            action (string): Desired action.

        Return:
            A string representing direct url after mapping out the the domain.
        '''
        base_domain = f"{component}.{UrlCirclez._base_domain(brand_name, environment_name)}"
        # TODO: write to the log the base_domain
        
        # TODO: add try catch to check that there is no KeyError when there is no entry called base_domain
        direct_domain = UrlCirclez.domain_mapping[base_domain]
        # base_url = f"https://{component}.{UrlCirclez._base_domain(brand_name, env_name)}/api/v{version}/{entity}/{action}"
        direct_url = f"https://{direct_domain}/{environment_name}/api/v{version}/{entity}/{action}"
        return direct_url



    def _convert_to_direct_url(direct_url: str, path_parameters=None, query_parameters=None) -> str:
        '''
        Function that conver the base url to direct url.
        
        Parameters:
            direct_url (string): The direct url after mapping the domain from the base domain.
            path_parameters (dictionary): A dictionary representing desired path parameters.
            query_parameters (dictionary): A dictionary representing desired query parameters.

        Return:
            A string representing the final url after adding all the parameters to the direct url.
        '''
        if path_parameters:
            for key, value in path_parameters.items():
                direct_url = direct_url.replace(f"{{{key}}}", value)

        path_params_string = '/'.join(urllib.parse.quote_plus(str(value)) for value in path_parameters.values()) if path_parameters else ''
        url_with_path_params = f"{direct_url}/{path_params_string}" if path_params_string else direct_url

        if query_parameters:
            query_params_string = '&'.join(f"{urllib.parse.quote_plus(str(key))}={urllib.parse.quote_plus(str(value))}" for key, value in query_parameters.items())
            url_with_query_params = f"{url_with_path_params}?{query_params_string}"
        else:
            url_with_query_params = url_with_path_params

        return url_with_query_params

