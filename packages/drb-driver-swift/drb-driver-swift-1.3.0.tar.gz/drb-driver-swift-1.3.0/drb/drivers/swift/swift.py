from typing import Optional, Any, List, Dict, Tuple
from pathlib import Path
from abc import ABC
from requests.auth import HTTPBasicAuth
from swiftclient.utils import generate_temp_url
from deprecated import deprecated
from drb.core import DrbNode, ParsedPath, DrbFactory
from drb.drivers.http import DrbHttpNode
from drb.exceptions.core import DrbException
from drb.nodes.abstract_node import AbstractNode
import io
import os
import requests
import secrets
import swiftclient


class SwiftAuth:
    """
    This class give us all the requirement to connect to a swift service.

    Parameters:
        authurl: authentication URL (default: None)
        user: user name to authenticate as (default: None)
        key: key/password to authenticate with (default: None)
        retries: Number of times to retry the request before failing
                 (default: 5)
        preauthurl: storage URL (if you have already authenticated)
                    (default: None)
        preauthtoken: authentication token (if you have already
                      authenticated) note authurl/user/key/tenant_name
                      are not required when specifying preauthtoken
                      (default: None)
        snet: use SERVICENET internal network default is False (default: False)
        starting_backoff: initial delay between retries
                          (seconds) (default: 1)
        max_backoff: maximum delay between retries
        (seconds) (default: 64)
        auth_version: OpenStack auth version (default: 1)
        tenant_name: The tenant/account name, required when connecting
                     to an auth 2.0 system (default: None).
        os_options: The OpenStack options which can have tenant_id,
                    auth_token, service_type, endpoint_type,
                    tenant_name, object_storage_url, region_name,
                    service_username, service_project_name,
                    service_key (default: None).
        insecure: Allow to access servers without checking SSL certs.
                  The server's certificate will not be verified
                  (default: False).
        cert: Client certificate file to connect on SSL server
              requiring SSL client certificate (default: None).
        cert_key: Client certificate private key file (default: None).
        ssl_compression: Whether to enable compression at the SSL layer.
                         If set to 'False' and the pyOpenSSL library is
                         present an attempt to disable SSL compression
                         will be made. This may provide a performance
                         increase for https upload/download operations
                         (default: True).
        retry_on_ratelimit: by default, a ratelimited connection will
                            raise an exception to the caller. Setting
                            this parameter to True will cause a retry
                            after a backoff (default: False).
        timeout: The connect timeout for the HTTP connection (default: None).
        session: A keystoneauth session object (default: None).
        force_auth_retry: reset auth info even if client got unexpected
                          error except 401 Unauthorized (default: False).
    """

    def __init__(self, authurl=None, user=None,
                 key=None, preauthurl=None,
                 preauthtoken=None,
                 os_options: Dict = None,
                 auth_version="1",
                 **kwargs):
        if authurl is not None:
            self.authurl = authurl.replace('+swift', '') \
                if '+swift' in authurl else authurl
        else:
            self.authurl = None
        self.user = user
        self.key = key
        self.preauthurl = preauthurl
        self.preauthtoken = preauthtoken
        self.os_options = os_options
        self.auth_version = auth_version
        self.retries = kwargs.get('retries', 5)
        self.snet = kwargs.get('snet', False)
        self.starting_backoff = kwargs.get('starting_backoff', 1)
        self.max_backoff = kwargs.get('max_backoff', 64)
        self.tenant_name = kwargs.get('tenant_name', None)
        self.cacert = kwargs.get('cacert', None)
        self.insecure = kwargs.get('insecure', False)
        self.cert = kwargs.get('cert', None)
        self.cert_key = kwargs.get('cert_key', None)
        self.ssl_compression = kwargs.get('ssl_compression', True)
        self.retry_on_ratelimit = kwargs.get('retry_on_ratelimit', False)
        self.timeout = kwargs.get('timeout', None)
        self.session = kwargs.get('session', None)
        self.force_auth_retry = kwargs.get('force_auth_retry', False)


class SwiftConnection:
    """
    This class use the singleton pattern to provide too
    much connection to the swift server.

    Parameters:
        auth: An Auth object to provide all the information required
              to establish the connection with the server.
    """
    swift = None

    def __new__(cls,
                auth: SwiftAuth):
        if cls.swift is None:
            cls.swift = swiftclient.client.Connection(
                auth.authurl, auth.user,
                auth.key, auth.retries,
                auth.preauthurl,
                auth.preauthtoken, auth.snet,
                auth.starting_backoff,
                auth.max_backoff, auth.tenant_name,
                auth.os_options,
                auth.auth_version, auth.cacert,
                auth.insecure, auth.cert,
                auth.cert_key,
                auth.ssl_compression,
                auth.retry_on_ratelimit,
                auth.timeout, auth.session,
                auth.force_auth_retry)
        return cls.swift


class Download(io.BytesIO):

    def __init__(self, response: swiftclient.client._RetryBody):
        self._resp = response
        self._buff = bytearray(0)
        super().__init__(self._buff)

    def read(self, *args, **kwargs):
        if isinstance(self._resp, bytes):
            return self._resp
        if not (len(args) > 0 and isinstance(
                args[0], int) and args[0] > 0):
            for chunk in self._resp:
                self._buff.extend(chunk)

            return self._buff
        for chunk in self._resp:
            self._buff.extend(chunk)
            if len(self._buff) >= args[0]:
                return self._buff

    def close(self) -> None:
        super().close()
        self._resp.close()

    def seekable(self) -> bool:
        return False


class SwiftNode(AbstractNode, ABC):
    """
    Common SwiftNode interface
    """

    def __init__(self, auth: SwiftAuth):
        super().__init__()
        self._auth = auth
        self._swift = None

    def get_service_url(self) -> Optional[str]:
        """
        Returns URL of the swift auth service.

        :returns: string URL representation the swift auth service
        :rtype: str
        """
        return self._auth.authurl

    def get_storage(self) -> Optional[str]:
        """
        Returns URL of the swift storage.

        :returns: string URL representation the swift storage
        :rtype: str
        """
        return self._auth.preauthurl

    def get_auth(self) -> SwiftAuth:
        """
        Return the Auth object created to access the service.

        :returns: an Auth object.
        :rtype: SwiftAuth
        """
        return self._auth

    def close(self) -> None:
        """
        Close The swift connection
        """
        if self._swift is not None:
            self._swift.close()

    def __eq__(self, other):
        return isinstance(other, SwiftNode) and \
               self._auth == other._auth

    def __hash__(self):
        return hash(self.auth)

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class SwiftObject(SwiftNode):

    def __init__(self, path: str, obj: dict,
                 auth: SwiftAuth, parent: SwiftNode):
        super().__init__(auth)
        self.add_impl(io.BytesIO, self._to_stream)
        self.name = obj.get('name')
        if path.endswith("/"):
            self._path = path + self.name
        else:
            self._path = path + "/" + self.name
        for k, v in obj.items():
            self.__imatmul__((k, v))
        self.parent = parent

    @property
    def path(self) -> ParsedPath:
        return ParsedPath(self._path)

    @property
    @deprecated(version='1.2.0')
    def children(self) -> List[DrbNode]:
        return []

    @staticmethod
    def _to_stream(node: DrbNode, **kwargs):
        if not isinstance(node, SwiftObject):
            raise TypeError(f'Invalid node type: {type(node)}')

        node._swift = SwiftConnection(node._auth)
        if kwargs.get('temp_url', False):
            storage, token = node._swift.get_auth()
            key = secrets.token_hex(nbytes=8)
            # Set secret key to enable download
            myobj = {
                'X-Account-Meta-Temp-URL-Key': key,
                'X-Auth-Token': token
            }
            requests.post(storage, headers=myobj)

            storage_url = storage.split('v1')
            total = '/v1' + storage_url[1] + '/' \
                    + node.parent.name + '/' \
                    + node.name
            url = generate_temp_url(total, 3600,
                                    key,
                                    'GET')
            http_node = DrbHttpNode(storage_url[0] + url[1:])

            return http_node.get_impl(io.BytesIO, resp_chunk_size=kwargs.get(
                'chunk_size', 12000))
        else:
            _, body = node._swift.get_object(
                container=node.parent.name,
                obj=node.name,
                resp_chunk_size=kwargs.get('chunk_size', 12000))
            return Download(body)


class SwiftContainer(SwiftNode):

    def __init__(self, obj: dict, auth: SwiftAuth, parent: SwiftNode):
        super().__init__(auth)
        self.name = obj.get('name')
        if parent.name.endswith("/"):
            self._path = parent.name + self.name
        else:
            self._path = parent.name + "/" + self.name
        for k, v in obj.items():
            self.__imatmul__((k, v))
        self._children = None
        self.parent = parent

    @property
    def path(self) -> ParsedPath:
        return ParsedPath(self._path)

    @property
    @deprecated(version='1.2.0')
    def children(self) -> List[DrbNode]:
        self._swift = SwiftConnection(self._auth)
        if self._children is None:
            _, objects = self._swift.get_container(self.name,
                                                   full_listing=True)
            self._children = [
                SwiftObject(self._path, obj, self._auth, self)
                for obj in objects
            ]
        return self._children

    # def has_child(self, name: str = None, namespace: str = None) -> bool:
    #     if namespace is None:
    #         if name is not None:
    #             return name in [x.name for x in self.children]
    #         return len(self.children) > 0
    #     return False


class SwiftService(SwiftNode):

    def __init__(self, auth: SwiftAuth):
        super().__init__(auth)
        self._children = None

    @property
    @deprecated(version='1.2.0')
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        if not self._attrs:
            self._swift = SwiftConnection(self._auth)
            for k, v in self._swift.get_capabilities().items():
                self.__imatmul__((k, v))
        return super().attributes

    @property
    def parent(self) -> Optional[DrbNode]:
        return None

    @property
    def path(self) -> ParsedPath:
        return ParsedPath(Path(os.path.sep).as_posix())

    @property
    @deprecated(version='1.2.0')
    def children(self) -> List[DrbNode]:
        self._swift = SwiftConnection(self._auth)
        if self._children is None:
            _, containers = self._swift.get_account()
            self._children = [
                SwiftContainer(container, self._auth, self)
                for container in containers]
        return self._children

    @property
    def name(self) -> str:
        if self._auth.preauthurl:
            return self._auth.preauthurl
        return self._auth.authurl

    # def has_child(self, name: str = None, namespace: str = None) -> bool:
    #     if namespace is None:
    #         if name is not None:
    #             return name in [x.name for x in self.children]
    #         return len(self.children) > 0
    #     return False


class SwiftNodeFactory(DrbFactory):
    """ authurl=None, user=None,
                 key=None, preauthurl=None,
                 preauthtoken=None,
                 os_options: Dict = None,
                 auth_version="1",
                 """

    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, SwiftNode):
            return node
        if isinstance(node, DrbHttpNode):
            if isinstance(node.auth, HTTPBasicAuth):
                auth = SwiftAuth(authurl=node.path.path,
                                 user=node.auth.username,
                                 key=node.auth.password
                                 )
            else:
                auth = SwiftAuth(authurl=node.path.path)
            return SwiftService(auth=auth)
        raise NotImplementedError("Call impl method")
