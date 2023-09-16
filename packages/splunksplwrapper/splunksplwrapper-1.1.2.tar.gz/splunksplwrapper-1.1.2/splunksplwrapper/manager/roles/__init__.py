#
# Copyright 2023 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from abc import abstractmethod

from splunksplwrapper.manager import Manager
from splunksplwrapper.misc.collection import Collection
from splunksplwrapper.misc.manager_utils import create_wrapper_from_connector_mapping


class Roles(Manager, Collection):
    """
    This class represents the Roles endpoint in REST which is a collection of
    L{Role}es.
    """

    def __init__(self, connector):
        """
        Roles' constructor.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        Manager.__init__(self, connector)
        Collection.__init__(self)

    def __new__(cls, connector):
        """
        The function called when creating a new Roles object.
        An internal map stores mappings from connector type to corresponding
        Roles subclass, making sure that the appropriate Roles class is
        evoked.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        mappings = _CONNECTOR_TO_WRAPPER_MAPPINGS
        return create_wrapper_from_connector_mapping(cls, connector, mappings)

    @abstractmethod
    def create_role(self, role_name, parent_role_name):
        """
        Create a role.

        @param role_name: The name of the new role.
        @type role_name: String
        @param parent_role_name: The name of the role's parent.
        @type parent_role_name: String
        """
        pass

    @abstractmethod
    def delete_role(self, role_name):
        """
        Delete a role.

        @param role_name: The name of the role to be deleted.
        @type role_name: String
        """
        pass

    @abstractmethod
    def update_role(self, role_name, **kwargs):
        """
        Update a role.

        @param role_name: The name of the role to be updated.
        @type role_name: String
        @param kwargs: The new arguments for role to be updated.
        @type kwargs: kwargs
        """
        pass

    @abstractmethod
    def __getitem__(self, role_name):
        """
        Retrieve an role.

        @param role_name: Role name.
        @type role_name: L{Role}
        """
        pass


class RoleNotFound(RuntimeError):
    def __init__(self, role_name):
        self.role_name = role_name
        super().__init__(self._error_message)

    @property
    def _error_message(self):
        f = "Could not find role with name {name}"
        return f.format(name=self.role_name)


# We need to do this at the bottom to avoid import errors
from splunksplwrapper.connector.sdk import SDKConnector
from splunksplwrapper.manager.roles.sdk import SDKRolesWrapper

_CONNECTOR_TO_WRAPPER_MAPPINGS = {SDKConnector: SDKRolesWrapper}
