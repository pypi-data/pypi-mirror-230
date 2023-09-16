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

PATH_PERFIX = "/servicesNS/nobody/system/data/indexes/"
COUNT_OFFSET = "?count=-1&offset=0"
DISABLE = "/disable"
ENABLE = "/enable"
SYSTEM_MESSAGE = "/servicesNS/nobody/system/messages"
RESTART = "/services/server/control/restart"
ROLL_HOT_BUCKETS = "/roll-hot-buckets"


class Indexes(Manager, Collection):
    """
    This class represents the Indexes endpoint in REST which is a collection of
    L{Index}es.
    """

    def __init__(self, connector):
        """
        Indexes' constructor.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        Manager.__init__(self, connector)
        Collection.__init__(self)

    def __new__(cls, connector):
        """
        The function called when creating a new Indexes object.
        An internal map stores mappings from connector type to corresponding
        Indexes subclass, making sure that the appropriate Indexes class is
        evoked.

        @param connector: The connector through which Splunk is reached.
        @type connector: Connector
        """
        mappings = _CONNECTOR_TO_WRAPPER_MAPPINGS
        return create_wrapper_from_connector_mapping(cls, connector, mappings)

    @abstractmethod
    def create_index(self, index_name):
        """
        Create an index.

        @param index_name: The name of the new index.
        @type index_name: String
        """
        pass

    @abstractmethod
    def __getitem__(self, index_name):
        """
        Retrieve an index.

        @param index_name: Index name.
        @type index_name: L{String}
        """
        pass


class IndexNotFound(RuntimeError):
    def __init__(self, index_name):
        self.index_name = index_name
        super().__init__(self._error_message)

    @property
    def _error_message(self):
        f = "Could not find index with name {name}"
        return f.format(name=self.index_name)


class OperationError(Exception):
    """Raised for a failed operation, such as a time out."""

    pass


from splunksplwrapper.connector.rest import RESTConnector

# We need to do this at the bottom to avoid import errors
from splunksplwrapper.connector.sdk import SDKConnector
from splunksplwrapper.manager.indexes.rest import RESTIndexesWrapper
from splunksplwrapper.manager.indexes.sdk import SDKIndexesWrapper

_CONNECTOR_TO_WRAPPER_MAPPINGS = {
    SDKConnector: SDKIndexesWrapper,
    RESTConnector: RESTIndexesWrapper,
}
