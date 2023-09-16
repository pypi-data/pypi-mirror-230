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

PATH_PERFIX = "/servicesNS/nobody/system/search/jobs/"
EVENTS = "/events"
RESULTS = "/results"
SUMMARY = "/summary"
CONTROL = "/control"
RESULTS_PREVIEW = "/results_preview"
TIMELINE = "/timeline"
SEARCHLOG = "/search.log"


class Jobs(Manager, Collection):
    """
    Jobs is the manager that handles searches.
    It does not handle pausing, resuming, etc of individual searches, it just
    spawns and lists searches.
    """

    def __init__(self, connector):
        Manager.__init__(self, connector)
        Collection.__init__(self)

    def __new__(cls, connector):
        mappings = _CONNECTOR_TO_WRAPPER_MAPPINGS
        return create_wrapper_from_connector_mapping(cls, connector, mappings)

    @abstractmethod
    def create(self, query, **kwargs):
        pass

    @abstractmethod
    def __getitem__(self, sid):
        pass


class JobNotFound(RuntimeError):
    def __init__(self, sid):
        self.sid = sid
        super().__init__(self._error_message)

    @property
    def _error_message(self):
        return f"Could not find a job with SID {self.sid}"


# We need this at the bottom to avoid cyclic imports

from splunksplwrapper.connector.rest import RESTConnector
from splunksplwrapper.connector.sdk import SDKConnector
from splunksplwrapper.manager.jobs.rest import RESTJobsWrapper
from splunksplwrapper.manager.jobs.sdk import SDKJobsWrapper

_CONNECTOR_TO_WRAPPER_MAPPINGS = {
    SDKConnector: SDKJobsWrapper,
    RESTConnector: RESTJobsWrapper,
}
