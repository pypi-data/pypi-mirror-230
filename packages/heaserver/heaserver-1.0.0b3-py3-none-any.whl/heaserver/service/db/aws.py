import configparser
from abc import ABC
from contextlib import contextmanager
from functools import partial
from aiohttp.web import Request
from botocore.client import BaseClient
import jwt
import boto3
from aiohttp import hdrs, web
from aiohttp.web_request import Request
from botocore.exceptions import ClientError
from mypy_boto3_s3 import S3Client, S3ServiceResource
from mypy_boto3_sts import STSClient

from heaserver.service.appproperty import HEA_DB
from heaserver.service.db.database import DatabaseContextManager

from heaserver.service.db.mongo import Mongo

from ..oidcclaimhdrs import SUB

from heaobject.account import AWSAccount
from heaobject.keychain import AWSCredentials, Credentials, CredentialTypeVar
from heaobject.registry import Property
from heaobject.root import DesktopObjectDict
from heaobject.volume import AWSFileSystem, FileSystemTypeVar
from heaobject.user import NONE_USER
from ..heaobjectsupport import type_to_resource_url
from heaserver.service import client
from yarl import URL
from . import database
from .database import Database, MicroserviceDatabaseManager
from ..testcase.collection import query_fixtures, query_content
from heaobject.awss3key import decode_key
from typing import Optional, Any, Tuple, List
from configparser import ConfigParser
import asyncio
from typing import cast, overload, Literal
from threading import Lock
import logging

_boto3_client_lock = Lock()
_boto3_resource_lock = Lock()

class AWS(Database, ABC):
    """
    Connectivity to Amazon Web Services (AWS) for HEA microservices. Subclasses must call this constructor.
    """
    pass


class S3(AWS):
    """
    Connectivity to AWS Simple Storage Service (S3) for HEA microservices.
    """
    OIDC_CLIENT = "OIDC_CLIENT"
    # this is the buffer we give to refresh credentials in minutes on our end before they expire on aws
    EXPIRATION_LIMIT = 540
    MAX_DURATION_SECONDS = 43200

    async def update_credentials(self, request: Request, credentials: AWSCredentials) -> None:
        """
        This is a wrapper function to be extended by tests
        It obtains credential's url from the registry and that makes PUT

        :param request:
        :param credentials:
        :returns: None if it succeeds otherwise it will raise ValueError or HTTPError
        """
        resource_url = await type_to_resource_url(request, Credentials)
        if not resource_url:
            raise ValueError(f'No service for type {Credentials.get_type_name()}')
        if credentials.id is None:
            raise ValueError(f'credentials must have a non-None id attribute')
        await client.put(app=request.app, url=URL(resource_url) / credentials.id, data=credentials,
                         headers=request.headers)

    async def get_property(self, app: web.Application, name: str) -> Optional[Property]:
        """
        This is a wrapper function to be extended by tests
        Gets the Property with the given name from the HEA registry service.

        :param app: the aiohttp app.
        :param name: the property's name.
        :return: a Property instance or None (if not found).
        """
        return await client.get_property(app=app, name=name)

    async def generate_cloud_credentials(self, request: Request, oidc_client: str, arn: str) -> Optional[
        AWSCredentials]:
        return await generate_cloud_credentials(request=request, oidc_client=oidc_client, arn=arn)

    async def get_file_system_and_credentials_from_volume(self, request: Request, volume_id) -> Tuple[AWSFileSystem, Optional[AWSCredentials]]:
        return await database.get_file_system_and_credentials_from_volume(request, volume_id, AWSFileSystem, AWSCredentials)

    @overload
    async def get_client(self, request: Request, service_name: Literal['s3'], volume_id: str) -> S3Client:
        ...

    @overload
    async def get_client(self, request: Request, service_name: Literal['sts'], volume_id: str) -> STSClient:
        ...

    async def get_client(self, request: Request, service_name: str, volume_id: str) -> S3Client | STSClient:
        """
        Gets an AWS service client.  If the volume has no credentials, it uses the boto3 library to try and find them.
        This method is not designed to be overridden.

        :param request: the HTTP request (required).
        :param service_name: AWS service name (required).
        :param volume_id: the id string of a volume (required).
        :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
        was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
        application-level property.
        :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
        the volume's credentials were not found, or a necessary service is not registered.

        TODO: need a separate exception thrown for when a service is not registered (so that the server can respond with a 500 error).
        TODO: need to lock around client creation because it's not threadsafe, manifested by sporadic KeyError: 'endpoint_resolver'.
        """
        logger = logging.getLogger(__name__)
        if volume_id is not None:
            _, credentials = \
                await self.get_file_system_and_credentials_from_volume(request, volume_id)
            logger.info("credentials retrieved from database checking if expired: %s", credentials.to_dict()
                        if credentials else None)
            loop = asyncio.get_running_loop()
            if not credentials:  # delegate to boto3 to find the credentials
                return await loop.run_in_executor(None, create_client, service_name)

            oidc_client = await self.get_property(app=request.app, name=S3.OIDC_CLIENT)
            if oidc_client:  # generating temp creds from aws
                return await self.__get_temporary_credentials(request=request,
                                                            credentials=credentials,
                                                            aws_source=boto3.client,
                                                            service_name=service_name, oidc_client_prop=oidc_client)
            # for permanent credentials
            return await loop.run_in_executor(None, partial(create_client, service_name,
                                                            region_name=credentials.where,
                                                            aws_access_key_id=credentials.account,
                                                            aws_secret_access_key=credentials.password))
        else:
            raise ValueError('volume_id is required')

    async def get_resource(self, request: Request, service_name: str, volume_id: str) -> S3ServiceResource:
        """
        Gets an AWS resource. If the volume has no credentials, it uses the boto3 library to try and find them. This
        method is not designed to be overridden.

        :param request: the HTTP request (required).
        :param service_name: AWS service name (required).
        :param volume_id: the id string of a volume (required).
        :return: a Mongo client for the file system specified by the volume's file_system_name attribute. If no volume_id
        was provided, the return value will be the "default" Mongo client for the microservice found in the HEA_DB
        application-level property.
        :raise ValueError: if there is no volume with the provided volume id, the volume's file system does not exist,
        the volume's credentials were not found, or a necessary service is not registered.

        TODO: need to lock around resource creation because it's not threadsafe, manifested by sporadic KeyError: 'endpoint_resolver'.
        """
        logger = logging.getLogger(__name__)
        if volume_id is not None:
            _, credentials = \
                await self.get_file_system_and_credentials_from_volume(request, volume_id)
            logger.info(
                "credentials retrieved from database checking if expired: %s", credentials.to_dict() if credentials else None)
            loop = asyncio.get_running_loop()
            if not credentials:  # delegate to boto3 to find the credentials
                return await loop.run_in_executor(None, create_resource, service_name)

            oidc_client = await self.get_property(app=request.app, name=S3.OIDC_CLIENT)
            if oidc_client:  # generating temp creds from aws
                return await self.__get_temporary_credentials(request=request,
                                                            credentials=credentials,
                                                            aws_source=boto3.resource,
                                                            service_name=service_name, oidc_client_prop=oidc_client)

            # for permanent credentials
            return await loop.run_in_executor(None, partial(create_resource, service_name,
                                                            region_name=credentials.where,
                                                            aws_access_key_id=credentials.account,
                                                            aws_secret_access_key=credentials.password))

        else:
            raise ValueError('volume_id is required')

    async def get_account(self, request: Request, volume_id: str) -> AWSAccount | None:
        """
        Gets the current user's AWS account dict associated with the provided volume_id.

        :param request: the HTTP request object (required).
        :param volume_id: the volume id (required).
        :return: the AWS account dict, or None if not found.
        """

        sts_client = await self.get_client(request, 'sts', volume_id)
        return await S3._get_account(sts_client, request.headers.get(SUB, NONE_USER))

    @staticmethod
    async def _get_account(sts_client, owner: str) -> AWSAccount:
        aws_object_dict = {}
        account = AWSAccount()

        loop = asyncio.get_running_loop()
        identity_future = loop.run_in_executor(None, sts_client.get_caller_identity)
        # user_future = loop.run_in_executor(None, iam_client.get_user)
        await asyncio.wait([identity_future])  # , user_future])
        aws_object_dict['account_id'] = identity_future.result().get('Account')
        # aws_object_dict['alias'] = next(iam_client.list_account_aliases()['AccountAliases'], None)  # Only exists for IAM accounts.
        # user = user_future.result()['User']
        # aws_object_dict['account_name'] = user.get('UserName')  # Only exists for IAM accounts.

        account.id = aws_object_dict['account_id']
        account.name = aws_object_dict['account_id']
        account.display_name = aws_object_dict['account_id']
        account.owner = owner
        # account.created = user['CreateDate']
        # FIXME this info coming from Alternate Contact(below) gets 'permission denied' with IAMUser even with admin level access
        # not sure if only root account user can access. This is useful info need to investigate different strategy
        # alt_contact_resp = account_client.get_alternate_contact(AccountId=account.id, AlternateContactType='BILLING' )
        # alt_contact =  alt_contact_resp.get("AlternateContact ", None)
        # if alt_contact:
        # account.full_name = alt_contact.get("Name", None)

        return account

    async def __get_temporary_credentials(self, request: web.Request, credentials: AWSCredentials,
                                        aws_source: Any,
                                        service_name: str, oidc_client_prop: Property) -> Any:
        """
            Gets temporary credentials and returns the authorized client. In order to do that it
            gets the previous credential's role_arn and then assumes it.

            :param request: the aiohttp request
            :param credentials: the aws credentials last saved
            :param aws_source: must be either boto3.client or boto3.resource.
            :param service_name: The type of client to return
            :param oidc_client_prop: The property for the open id connect client
            :return: the boto3 client provided with credentials
            :raise ValueError if no previously saved credentials it raises ValueError
        """
        logger = logging.getLogger(__name__)
        assert credentials.role_arn is not None, 'credentials must have a non-None role_arn attribute'
        oidc_client = oidc_client_prop.value
        loop = asyncio.get_running_loop()

        if credentials.has_expired(S3.EXPIRATION_LIMIT):
            logger.info("credentials need to be refreshed")
            cloud_creds = await self.generate_cloud_credentials(request=request, oidc_client=oidc_client,
                                                                arn=credentials.role_arn)
            if not cloud_creds:
                raise ValueError(f'Could not generate cloud credentials with {oidc_client} '
                                 f'and these params {credentials.role_arn}')
            logger.info("credentials successfully obtained from cloud:  %s" % cloud_creds.to_dict())
            credentials.account = cloud_creds.account
            credentials.password = cloud_creds.password
            credentials.session_token = cloud_creds.session_token
            credentials.expiration = cloud_creds.expiration
            await self.update_credentials(request=request, credentials=credentials)
            logger.info("credentials updated in the database")
        return await loop.run_in_executor(None, partial(create_client if aws_source == boto3.client else create_resource,
                                                        service_name,
                                                        region_name=credentials.where,
                                                        aws_access_key_id=credentials.account,
                                                        aws_secret_access_key=credentials.password,
                                                        aws_session_token=credentials.session_token))


class S3WithMongo(S3, Mongo):
    def __init__(self, config: Optional[ConfigParser], **kwargs):
        super().__init__(config, **kwargs)


class S3Manager(MicroserviceDatabaseManager):
    """
    Database manager for mock Amazon Web Services S3 buckets. It will not make any calls to actual S3 buckets. This
    class is not designed to be subclassed.
    """

    def get_database(self) -> S3:
        return S3(self.config)

    @classmethod
    def database_types(self) -> list[str]:
        return ['system|awss3']


class S3WithMongoManager(S3Manager):

    def get_database(self) -> S3:
        return S3WithMongo(self.config)

async def generate_cloud_credentials(request: Request, oidc_client: str, arn: str) -> Optional[
    AWSCredentials]:
    """
    :param request: the HTTP request (required).
    :param oidc_client: the name openidc client
    :param arn: The aws role arn that to be assumed
    :returns the AWSCredentials populated with the resource's content, None if no such resource exists, or another HTTP
    status code if an error occurred.
    """
    logger = logging.getLogger(__name__)
    sub = request.headers.get(SUB, None)
    if sub is None:
        raise ValueError('OIDC SUB header is required')
    if not arn:
        raise ValueError('Cannot get credentials arn which is required')
    auth: List[str] = request.headers.get(hdrs.AUTHORIZATION, '').split(' ')

    if not len(auth) == 2:
        raise ValueError("Bearer Token is required in header")
    token = jwt.decode(auth[1], options={"verify_signature": False})
    claim = token.get('resource_access', None)
    assumed_role_object = None
    try:
        if claim and arn in claim[oidc_client]['roles']:
            sts_client = boto3.client('sts')
            assumed_role_object = sts_client.assume_role_with_web_identity(
                WebIdentityToken=auth[1], RoleArn=arn,
                RoleSessionName=sub, DurationSeconds=S3.MAX_DURATION_SECONDS
            )
        else:
            raise ClientError("Permission Denied, invalid role")
    except ClientError as ce:
        logger.info(f"Permission Denied: {ce}")
        return None
    if not assumed_role_object.get('Credentials'):
        return None
    creds = AWSCredentials()
    creds.account = assumed_role_object.get('Credentials')['AccessKeyId']
    creds.password = assumed_role_object.get('Credentials')['SecretAccessKey']
    creds.session_token = assumed_role_object.get('Credentials')['SessionToken']
    creds.expiration = assumed_role_object.get('Credentials')['Expiration']

    return creds


class S3ClientContext(DatabaseContextManager[S3Client]): # Go into db package?
    """
    Provides an S3Client object.
    """

    async def connection(self) -> S3Client:
        return await cast(S3, self.request.app[HEA_DB]).get_client(self.request, 's3', self.volume_id)


@overload
def create_client(service_name: Literal['s3'],
                   region_name: str | None = None,
                   aws_access_key_id: str | None = None,
                   aws_secret_access_key: str | None = None,
                   aws_session_token: str | None = None) -> S3Client:
    ...

@overload
def create_client(service_name: Literal['sts'],
                   region_name: str | None = None,
                   aws_access_key_id: str | None = None,
                   aws_secret_access_key: str | None = None,
                   aws_session_token: str | None = None) -> STSClient:
    ...

def create_client(service_name: Literal['s3', 'sts'],
                   region_name: str | None = None,
                   aws_access_key_id: str | None = None,
                   aws_secret_access_key: str | None = None,
                   aws_session_token: str | None = None) -> S3Client | STSClient:
    """
    Thread-safe boto client creation. Once created, clients are generally
    thread-safe.
    """
    with _boto3_client_lock:
        return boto3.client(service_name,
                        region_name=region_name,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        aws_session_token=aws_session_token)

def create_resource(service_name: Literal['s3'],
                     region_name: str | None = None,
                     aws_access_key_id: str | None = None,
                     aws_secret_access_key: str | None = None,
                     aws_session_token: str | None = None) -> S3ServiceResource:
    """
    Thread-safe boto resource creation. REsources are generally NOT
    thread-safe!
    """
    with _boto3_resource_lock:
        return boto3.resource(service_name,
                        region_name=region_name,
                        aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key,
                        aws_session_token=aws_session_token)
