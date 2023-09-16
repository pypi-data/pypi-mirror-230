"""
Classes and functions for mocking Amazon S3 buckets.

This module assumes the moto package is installed. Do not import it into environments where moto will
not be available, for example, in any code that needs to run outside automated testing.
"""
import configparser
from configparser import ConfigParser
from contextlib import contextmanager, AbstractContextManager, ExitStack
from typing import Optional, Tuple, Callable, AsyncGenerator, Union, Mapping

from aiohttp import web
from heaobject.registry import Property
from heaobject.folder import AWSS3Folder
from heaobject.data import AWSS3FileObject

from heaserver.service.db.aws import S3, S3Manager, create_client
from heaserver.service.db.mongo import Mongo

from heaobject.keychain import Credentials, CredentialTypeVar, AWSCredentials
from heaobject.volume import AWSFileSystem, Volume, FileSystem, DEFAULT_FILE_SYSTEM
from heaobject.root import DesktopObjectDict, DesktopObject
from heaobject.account import AWSAccount
from heaobject.bucket import AWSBucket
from heaobject.awss3key import decode_key
from aiohttp.web import Request

import boto3
from moto import mock_s3, mock_organizations, mock_sts
from heaserver.service.db.mongo import MongoManager
from .util import freeze_time

from heaserver.service.testcase.collection import query_fixtures, query_content

from heaserver.service.testcase.mockmongo import MockMongo, MockMongoManager

from io import BytesIO
import logging

class MockS3WithMongo(S3, Mongo):

    async def generate_cloud_credentials(self, request: Request, oidc_client: str, arn: str) -> Optional[AWSCredentials]:
        cred_dict_list = [cred_dict for cred_dict in self.get_desktop_objects_by_collection('credentials')]
        cred = None
        if cred_dict_list and len(cred_dict_list) > 1:
            cred_dict = cred_dict_list[1]
            cred = AWSCredentials()
            cred.from_dict(cred_dict)
        elif cred_dict_list and len(cred_dict_list) == 1:
            cred_dict = cred_dict_list[0]
            cred = AWSCredentials()
            cred.from_dict(cred_dict)

        return cred if cred else None


class MockS3WithMockMongo(S3, MockMongo):
    """
    Overrides the S3 class' methods use moto instead of actual AWS. It also stores volume and filesystem desktop
    objects in an in-memory data structure and mocks AWS microservices' attempts to access the file system and volumes
    microservices while requesting a boto3/moto client. Moto is documented at https://github.com/spulec/moto.
    """

    def __init__(self, config: Optional[ConfigParser], mongo: MockMongo = None, **kwargs):
        super().__init__(config=config, mongo=mongo, **kwargs)
        section = super().get_config_section()
        if config and section in config:
            database_section = config[section]
            self.__region_name: Optional[str] = database_section.get('RegionName', None)
            self.__aws_access_key_id: Optional[str] = database_section.get('AWSAccessKeyId', None)
            self.__aws_secret_access_key: Optional[str] = database_section.get('AWSSecretAccessKey', None)
            self.__expiration: Optional[str] = database_section.get('Expiration', None)
            self.__session_token: Optional[str] = database_section.get('SessionToken', None)
        else:
            self.__region_name = None
            self.__aws_access_key_id = None
            self.__aws_secret_access_key = None
            self.__expiration = None
            self.__session_token = None

    async def get_file_system_and_credentials_from_volume(self, request: Request, volume_id: Optional[str]) -> Tuple[
        AWSFileSystem, Optional[CredentialTypeVar]]:

        if self.__aws_secret_access_key is not None or self.__aws_access_key_id is not None:
            creds = AWSCredentials()
            creds.where = self.__region_name
            creds.account = self.__aws_access_key_id
            creds.password = self.__aws_secret_access_key
            creds.expiration = self.__expiration
        else:
            creds = self._get_credential_by_volume(volume_id=volume_id)
        return AWSFileSystem(), creds

    async def get_volumes(self, request: Request, file_system_type_or_type_name: Union[str, type[FileSystem]]) -> \
        AsyncGenerator[Volume, None]:
        for volume_dict in self.get_desktop_objects_by_collection('volumes'):
            if issubclass(file_system_type_or_type_name, DesktopObject):
                file_system_type_name_ = file_system_type_or_type_name.get_type_name()
            else:
                file_system_type_name_ = str(file_system_type_or_type_name)
            if volume_dict.get('file_system_type', AWSFileSystem.get_type_name()) == file_system_type_name_:
                volume = Volume()
                volume.from_dict(volume_dict)
                yield volume

    async def get_account(self, request: Request, volume_id: str) -> AWSAccount | None:
        account_id = '123456789012'
        a = AWSAccount()
        a.id = account_id
        a.display_name = account_id
        a.name = account_id

        return a


    async def get_property(self, app: web.Application, name: str) -> Optional[Property]:
        prop_dict_list = [prop_dict for prop_dict in self.get_desktop_objects_by_collection('properties')
                          if prop_dict.get('name', None) == name]
        prop = None
        if prop_dict_list and len(prop_dict_list) > 0:
            prop_dict = prop_dict_list[0]
            prop = Property()
            prop.from_dict(prop_dict)
        return prop if prop else None

    async def update_credentials(self, request: Request, credentials: AWSCredentials) -> None:
        pass

    def _get_credential_by_volume(self, volume_id: str) -> Optional[AWSCredentials]:
        volume_dict = self.get_desktop_object_by_collection_and_id('volumes', volume_id)
        if volume_dict is None:
            raise ValueError(f'No volume found with id {volume_id}')
        volume = Volume()
        volume.from_dict(volume_dict)
        if volume.credential_id is None:
            creds = None
        else:
            credentials_dict = self.get_desktop_object_by_collection_and_id('credentials', volume.credential_id)
            if credentials_dict is None:
                raise ValueError(f'No credentials with id {volume.credential_id}')
            creds = AWSCredentials()
            creds.from_dict(credentials_dict)
        return creds


class MockS3Manager(S3Manager):
    """
    Database manager for mocking AWS S3 buckets with moto. Mark test fixture data that is managed in S3 buckets with
    this database manager in testing environments. Furthermore, connections to boto3/moto clients normally require
    access to the registry and volume microservices. This database manager does not mock those connections, and actual
    registry and volume microservices need to be running, as is typical in integration testing environments. For unit
    testing, see MockS3ManagerWithMockMongo, which also mocks the connections to the registry and volume microservices.
    """

    @classmethod
    def get_environment_updates(cls) -> dict[str, str]:
        result = super().get_environment_updates()
        result.update({'AWS_ACCESS_KEY_ID': 'testing',
                       'AWS_SECRET_ACCESS_KEY': 'testing',
                       'AWS_SECURITY_TOKEN': 'testing',
                       'AWS_SESSION_TOKEN': 'testing',
                       'AWS_DEFAULT_REGION': 'us-east-1'
                       })
        return result

    @classmethod
    def get_context(cls) -> list[AbstractContextManager]:
        result = super().get_context()
        result.extend([mock_s3(), mock_organizations(), mock_sts(), freeze_time()])
        return result

    def get_database(self) -> S3:
        return S3(self.config)

    def insert_desktop_objects(self, desktop_objects: Optional[Mapping[str, list[DesktopObjectDict]]]):
        super().insert_desktop_objects(desktop_objects)
        logger = logging.getLogger(__name__)

        self.__organization_inserter()
        self.__awsaccount_inserter()

        for coll, objs in query_fixtures(desktop_objects, db_manager=self).items():
            logger.debug('Inserting %s collection object %s', coll, objs)
            inserters = self.get_desktop_object_inserters()
            if coll in inserters:
                inserters[coll](objs)

    def insert_content(self, content: Optional[Mapping[str, Mapping[str, bytes]]]):
        super().insert_content(content)
        if content is not None:
            client = create_client('s3')
            for key, contents in query_content(content, db_manager=self).items():
                if key == 'awss3files':
                    for id_, content_ in contents.items():
                        bucket_, actual_content = content_.split(b'|', 1)
                        bucket = bucket_.decode('utf-8')
                        with BytesIO(actual_content) as f:
                            client.upload_fileobj(Fileobj=f, Bucket=bucket, Key=decode_key(id_))
                else:
                    raise KeyError(f'Unexpected key {key}')

    @classmethod
    def get_desktop_object_inserters(cls) -> dict[str, Callable[[list[DesktopObjectDict]], None]]:
        return {'buckets': cls.__bucket_inserter,
                'awss3folders': cls.__awss3folder_inserter,
                'awss3files': cls.__awss3file_inserter}

    @classmethod
    def __organization_inserter(cls):
        cls.__create_organization()

    @classmethod
    def __awsaccount_inserter(cls):
        pass  # moto automatically creates one account to use. Creating your own accounts doesn't seem to work.


    @classmethod
    def __awss3file_inserter(cls, v):
        for awss3file_dict in v:
            awss3file = AWSS3FileObject()
            awss3file.from_dict(awss3file_dict)
            cls.__create_awss3file(awss3file)

    @classmethod
    def __awss3folder_inserter(cls, v):
        for awss3folder_dict in v:
            awss3folder = AWSS3Folder()
            awss3folder.from_dict(awss3folder_dict)
            cls.__create_awss3folder(awss3folder)

    @classmethod
    def __bucket_inserter(cls, v):
        for bucket_dict in v:
            awsbucket = AWSBucket()
            awsbucket.from_dict(bucket_dict)
            cls.__create_bucket(awsbucket)

    @staticmethod
    def __create_organization():
        client = boto3.client('organizations')
        client.create_organization(FeatureSet='ALL')

    @staticmethod
    def __create_bucket(bucket: AWSBucket):
        client = create_client('s3')
        if bucket is not None:
            if bucket.name is None:
                raise ValueError('bucket.name cannot be None')
            else:
                if bucket.region != 'us-east-1' and bucket.region:
                    client.create_bucket(Bucket=bucket.name,
                                         CreateBucketConfiguration={'LocationConstraint': bucket.region})
                else:
                    client.create_bucket(Bucket=bucket.name)
                client.put_bucket_versioning(Bucket=bucket.name,
                                             VersioningConfiguration={'MFADelete': 'Disabled', 'Status': 'Enabled'})

    @staticmethod
    def __create_awss3folder(awss3folder: AWSS3Folder):
        assert awss3folder.bucket_id is not None, 'awss3file must have a non-None bucket_id attribute'
        assert awss3folder.key is not None, 'awss3file must have a non-None key attribute'
        client = create_client('s3')
        client.put_object(Bucket=awss3folder.bucket_id, Key=awss3folder.key, StorageClass=awss3folder.storage_class.name)

    @staticmethod
    def __create_awss3file(awss3file: AWSS3FileObject):
        assert awss3file.bucket_id is not None, 'awss3file must have a non-None bucket_id attribute'
        assert awss3file.key is not None, 'awss3file must have a non-None key attribute'
        client = create_client('s3')
        client.put_object(Bucket=awss3file.bucket_id, Key=awss3file.key, StorageClass=awss3file.storage_class.name)



class MockS3WithMockMongoManager(MockS3Manager, MockMongoManager):
    """
    Database manager for mocking AWS S3 buckets with moto. Mark test fixture data that is managed in S3 buckets with
    this database manager in unit test environments. Furthermore, connections to boto3/moto clients normally require
    access to the registry and volume microservices. This database manager mocks those connections. Mark
    component, volume, and filesystem test collections with this database manager to make them available in unit
    testing environments. This class is not designed to be subclassed.
    """

    def get_database(self) -> MockS3WithMockMongo:
        return MockS3WithMockMongo(config=self.config, mongo=self.get_mongo())

    @classmethod
    def database_types(self) -> list[str]:
        return ['system|awss3', 'system|mongo']

