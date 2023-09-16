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
import logging
import threading
import urllib.error
import urllib.parse
import urllib.request

from splunksplwrapper.connector.base import Connector

LOGGER = logging.getLogger("rest util log")


class RestUtils(threading.Thread):
    def invoke_restAPI(
        self,
        splunk,
        appname="",
        arguments={"output_mode": "json"},
        request_type="GET",
        acl=None,
        splunk_user="",
        splunk_pwd="",
        request_url="/servicesNS/nobody/system/apps/local",
    ):
        LOGGER.info("Creating edit a saved search")
        if splunk_user == "":
            splunk_user = splunk.username
        if splunk_pwd == "":
            splunk_pwd = splunk.password

        if request_type == "POST":
            request_args = arguments

        if request_type == "UPDATE":
            request_type = "POST"
            request_url = request_url + "/" + appname
            request_args = arguments

        if request_type == "GET" or request_type == "DELETE":
            request_url = request_url + "/" + appname
            request_args = {"output_mode": "json"}
            response, content = self.make_http_request(
                splunk, request_type, request_url, request_args, splunk_user, splunk_pwd
            )

        response, content = self.make_http_request(
            splunk, request_type, request_url, request_args, splunk_user, splunk_pwd
        )

        if acl != None:
            acl_req_url = request_url + "/" + appname + "/acl"
            res, cont = self.make_http_request(
                splunk, request_type, acl_req_url, acl, splunk_user, splunk_pwd
            )

        return response, content

    def make_http_request(
        self,
        splunk,
        request_type,
        request_url,
        request_args="",
        splunk_user="",
        splunk_pwd="",
    ):
        """
        This is a REST helper that will generate a http request
        using request_type - GET/POST/...
        request_url and request_args
        """
        if splunk_user == "":
            splunk_user = splunk.username
        if splunk_pwd == "":
            splunk_pwd = splunk.password
        restconn = splunk.create_logged_in_connector(
            contype=Connector.REST, username=splunk_user, password=splunk_pwd
        )
        try:
            response, content = restconn.make_request(
                request_type, request_url, request_args
            )
            return response, content

        except urllib.error.HTTPError as err:
            print(
                "Http error code is ({}): {} : {}".format(
                    err.code, err.errno, err.strerror
                )
            )
        finally:
            restconn.logout()
