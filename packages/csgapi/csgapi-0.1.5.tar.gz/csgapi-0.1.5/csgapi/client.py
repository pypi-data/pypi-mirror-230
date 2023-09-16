
# TODO: in this file we are going to follow the client.py to create obejcts to represent the
# csg server connection. cli.py is an addition for custom features for gitlab, optional for us

# -*- coding: utf-8 -*-
#
# Copyright (C) 2013-2017 Gauvain Pocentek <gauvain@pocentek.net>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Wrapper for the GitLab API."""
import json

from .utils import handle_client_exception
from contextlib import nullcontext
from typing import Any, Optional

import requests
import requests.utils


REDIRECT_MSG = (
    "python-gitlab detected a {status_code} ({reason!r}) redirection. You must update "
    "your GitLab URL to the correct URL to avoid issues. The redirection was from: "
    "{source!r} to {target!r}"
)

DEFAULT_BASE_UTL = "https://csgenome.org/api/"  # can change in the future
CONTENT_TYPE = "application/json"


class CSGenome(object):
    """Represents a GitLab server connection.

    Args:
        url: The URL of the GitLab server (defaults to https://gitlab.com).
        private_token: The user private token
        oauth_token: An oauth token
        job_token: A CI job token
        ssl_verify: Whether SSL certificates should be validated. If
            the value is a string, it is the path to a CA file used for
            certificate validation.
        timeout: Timeout to use for requests to the GitLab server.
        http_username: Username for HTTP authentication
        http_password: Password for HTTP authentication
        api_version: Gitlab API version to use (support for 4 only)
        pagination: Can be set to 'keyset' to use keyset pagination
        order_by: Set order_by globally
        user_agent: A custom user agent to use for making HTTP requests.
        retry_transient_errors: Whether to retry after 500, 502, 503, or
            504 responses. Defaults to False.
    """

    def __init__(self, url=None, auth_token=None, email=None, password=None, new_password=None, per_page=50):
        # http_username: Optional[str] = None, # NOTE: depends on the future of auth
        # http_password: Optional[str] = None, # NOTE: same as above
        # api_version: str = "4", # NOTE: not in the near future lol
        # pagination: Optional[str] = None, # NOTE: with the current api implementation, we can only support num per page. this would be good to have tho
        # order_by: Optional[str] = None, # NOTE: also nice to have, don't know how useful it will be
        # -------------- params ---------------

        # self._url = f"{self._base_url}/api/v{api_version}" # NOTE: I don't think we have these, or will have them
        self._url = self._get_base_url(url)
        #: Timeout to use for requests to gitlab server
        # self.timeout = timeout # NOTE: might introduce in the future
        self.headers = {'email': email, 'password': password, "Content-type": CONTENT_TYPE}
        self.data = {'email': email, 'password': password, 'new_password': new_password}
        self.email = email
        self.password = password
        self.new_password = new_password
        self.cookies = {'token': auth_token}
        self.auth_token = auth_token  # NOTE: not sure if it will be used in the future
        self.session = requests.Session()
        self.per_page = per_page
        self._set_auth_info()

        # ------------ Objects ------------
        # NOTE: We must delay import of gitlab.v4.objects until now or
        # otherwise it will cause circular import errors
        # import gitlab.v4.objects
        # import .objects.country as country_object
        # import .objects.codename as codename_object
        from .objects import codename, country, file_system, \
            firmware, floating_point_unit, interconnect_family, manufacturer, microarchitectures, \
            operating_system, other_software, pointer, system_state
        from .objects import country, genera, green500, isas, ontology_type, \
            processor_hierarchy, processors, spec1995, spec2000, spec2006, spec2017, \
            top500, top500_ranks, processor_configuration, has_processor, memory_configuration, \
            has_memory, accelerator_configuration, has_accelerator, interconnect_configuration, \
            has_interconnect, operating_system_configuration, has_operating_system, system_configuration
        from .objects import country, application, architecture,\
            continent, region, segment, system_family, system_manufacturer, systems, interconnect, \
            benchmarks, used_to_run, graphics_cards, coprocessors
        from .objects import contributor, contribution, contribution_category, race, has_race, has_ethnicity, \
            ethnicity, has_education, organization, has_organization, degree_type, source

        self.used_to_run = used_to_run.UsedToRunManager(self)
        self.benchmarks = benchmarks.BenchmarksManager(self)
        self.codenames = codename.CodenameManager(self)
        self.file_system = file_system.FileSystemManager(self)
        self.firmware = firmware.FirmwareManager(self)
        self.floating_point_unit = floating_point_unit.FloatingPointUnitManager(self)
        self.interconnect = interconnect.InterconnectManager(self)
        self.interconnect_family = interconnect_family.InterconnectFamilyManager(self)
        self.manufacturers = manufacturer.ManufacturerManager(self)
        self.microarchitectures = microarchitectures.MicroarchitecturesManager(self)
        self.operating_system = operating_system.OperatingSystemManager(self)
        self.other_software = other_software.OtherSoftwareManager(self)
        self.pointer = pointer.PointerManager(self)
        self.system_state = system_state.SystemStateManager(self)
        self.genera = genera.GeneraManager(self)
        self.green500 = green500.Green500Manager(self)
        self.isas = isas.IsasManager(self)
        self.ontology_type = ontology_type.OntologyTypeManager(self)
        self.processor_hierarchy = processor_hierarchy.ProcessorHierarchyManager(self)
        self.processors = processors.ProcessorsManager(self)
        self.processor_configuration = processor_configuration.ProcessorConfigurationManager(self)
        self.has_processor = has_processor.HasProcessorManager(self)
        self.memory_configuration = memory_configuration.MemoryConfigurationManager(self)
        self.has_memory = has_memory.HasMemoryManager(self)
        self.accelerator_configuration = accelerator_configuration.AcceleratorConfigurationManager(self)
        self.has_accelerator = has_accelerator.HasAcceleratorManager(self)
        self.interconnect_configuration = interconnect_configuration.InterconnectConfigurationManager(self)
        self.has_interconnect = has_interconnect.HasInterconnectManager(self)
        self.operating_system_configuration = operating_system_configuration.OperatingSystemConfigurationManager(self)
        self.has_operating_system = has_operating_system.HasOperatingSystemManager(self)
        self.system_configuration = system_configuration.SystemConfigurationManager(self)
        self.spec1995 = spec1995.Spec1995Manager(self)
        self.spec2000 = spec2000.Spec2000Manager(self)
        self.spec2006 = spec2006.Spec2006Manager(self)
        self.spec2017 = spec2017.Spec2017Manager(self)
        self.top500 = top500.Top500Manager(self)
        self.top500_ranks = top500_ranks.Top500RanksManager(self)

        #self._objects = objects

        self.country = country.CountryManager(self)
        self.application = application.ApplicationManager(self)
        self.architecture = architecture.ArchitectureManager(self)
        self.continent = continent.ContinentManager(self)
        self.region = region.RegionManager(self)
        self.segment = segment.SegmentManager(self)
        self.system_family = system_family.SystemFamilyManager(self)
        self.system_manufacturer = system_manufacturer.SystemManufacturerManager(self)
        self.systems = systems.SystemsManager(self)
        self.graphics_cards = graphics_cards.GraphicsCardManager(self)
        self.coprocessors = coprocessors.CoprocessorManager(self)

        from .objects import contributor, contribution, contribution_category, race, has_race, \
            has_ethnicity, ethnicity, has_education, organization, has_organization, degree_type, contribution_name, \
            resource, from_country, has_contribution_name, contributor_source

        # hidden figures
        self.contributor = contributor.ContributorManager(self)
        self.contribution = contribution.ContributionManager(self)
        self.contribution_category = contribution_category.ContributionCategoryManager(self)
        self.race = race.RaceManager(self)
        self.has_race = has_race.HasRaceManager(self)
        self.has_contribution_name = has_contribution_name.HasContributionNameManager(self)
        self.has_ethnicity = has_ethnicity.HasEthnicityManager(self)
        self.ethnicity = ethnicity.EthnicityManager(self)
        self.has_education = has_education.HasEducationManager(self)
        self.organization = organization.OrganizationManager(self)
        self.has_organization = has_organization.HasOrganizationManager(self)
        self.degree_type = degree_type.DegreeTypeManager(self)
        self.contribution_name = contribution_name.ContributionNameManager(self)
        self.from_country = from_country.FromCountryManager(self)
        self.resource= resource.ResourceManager(self)
        self.source = source.SourceManager(self)
        self.contributor_source = contributor_source.ContributorSourceManager(self)

    def __enter__(self):
        return self

    def __exit__(self, *args: Any):
        self.session.close()

    @property
    def api_url(self) -> str:
        # NOTE: we don't have one that needs to be computed
        """The computed API base URL."""
        return self._url

    # TODO: adapt this to auth check for ppl using the python client
    def auth(self) -> None:
        """Performs an authentication using private token.

        The `user` attribute will hold a `gitlab.objects.CurrentUser` object on
        success.
        """
        # self.user = self._objects.CurrentUserManager(self).get()
        pass

    # NOTE: very slick, should reuse if we have more than one in the future

    def _set_auth_info(self):
        if (self.email and not self.password) or \
                (not self.email and self.password):
            raise ValueError("Both or none of email and password should be present")

        if not self.new_password:  # not changing password, should be header
            self.session.headers.update(self.headers)

    def enable_debug(self) -> None:
        import logging
        from http.client import HTTPConnection  # noqa

        HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    def get_per_page(self):
        return self.per_page

    # def _get_session_opts(self) -> Dict[str, Any]:
    #     return {
    #         "headers": self.headers.copy(),
    #         "auth": self._http_auth,
    #         # "timeout": self.timeout,
    #         # "verify": self.ssl_verify,
    #         #TODO: add the other ones
    #     }

    def _get_base_url(self, url: Optional[str] = None) -> str:
        """Return the base URL with the trailing slash stripped.
        If the URL is a Falsy value, return the default URL.
        Returns:
            The base URL
        """
        return url or DEFAULT_BASE_UTL

    def _build_url(self, path: str) -> str:
        """Returns the full url from path.

        If path is already a url, return it unchanged. If it's a path, append
        it to the stored url.

        Returns:
            The full URL
        """
        if path.startswith("http://") or path.startswith("https://"):
            return path
        else:
            return f"{self._url}{path}"


# ------------------ REST functions -----------------------

    def http_request(self, verb, path, post_data=None, params=None):
        """Make an HTTP request to the Gitlab server.

        Args:
            verb: The HTTP method to call ('get', 'post', 'put', 'delete')
            path: Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            query_data: Data to send as query parameters
            post_data: Data to send in the body (will be converted to
                              json by default)
            raw: If True, do not convert post_data to json
            streamed: Whether the data should be streamed
            files: The files to send to the server
            timeout: The timeout, in seconds, for the request
            obey_rate_limit: Whether to obey 429 Too Many Request
                                    responses. Defaults to True.
            max_retries: Max retries after 429 or transient errors,
                               set to -1 to retry forever. Defaults to 10.
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            A requests result object.

        Raises:
            GitlabHttpError: When the return code is not 2xx
        """
        url = self._build_url(path)
        params = params or {}

        result = self.session.request(
            headers={'Authorization': f'Bearer {self.auth_token}'} if self.auth_token else None,
            method=verb,
            url=url,
            json=post_data,  # specifically used for POST
            # data=data, #NOTE: so far not sure about the diff between data and json
            params=params,  # takes a json
        )
        if verb == 'post':  # NOTE: handles location header, can remove if necessary
            added_location = result.headers.get("Location") or None
            return (added_location, result)
        return result

    def http_get(self, path, params=None):
        """Make a GET request to the Gitlab server.

        Args:
            path: Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            query_data: Data to send as query parameters
            streamed: Whether the data should be streamed
            raw: If True do not try to parse the output as json
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            A requests result object is streamed is True or the content type is
            not json.
            The parsed json data otherwise.

        Raises:
            GitlabHttpError: When the return code is not 2xx
            GitlabParsingError: If the json data could not be parsed
        """
        try:
            result = self.http_request("get", path, params=params)
            return result.json()
        except Exception:
            return handle_client_exception(400, {'message': 'Unable to parse result.'})

    def http_list(self, path, params=None):
        """Make a GET request to the Gitlab server for list-oriented queries.
        Args:
            path: Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projects')
            query_data: Data to send as query parameters
            **kwargs: Extra options to send to the server (e.g. sudo, page,
                      per_page)
        Returns:
            A list of the objects returned by the server. If `as_list` is
            False and no pagination-related arguments (`page`, `per_page`,
            `all`) are defined then a GitlabList object (generator) is returned
            instead. This object will make API calls when needed to fetch the
            next items from the server.
        Raises:
            GitlabHttpError: When the return code is not 2xx
            GitlabParsingError: If the json data could not be parsed
        """
        res = CSGList(self, path, query_data=params).json()
        return (res['errors'], True) if 'errors' in res.keys() else (list(res['data']), False)

    def http_post(self, path, post_data=None):
        """Make a POST request to the Gitlab server.

        Args:
            path: Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            query_data: Data to send as query parameters
            post_data: Data to send in the body (will be converted to
                              json by default)
            raw: If True, do not convert post_data to json
            files: The files to send to the server
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            The parsed json returned by the server if json is return, else the
            raw content

        Raises:
            GitlabHttpError: When the return code is not 2xx
            GitlabParsingError: If the json data could not be parsed
        """
        # NOTE: we assume no query param
        post_data = post_data or {}

        try:
            location, result = self.http_request("post", path, post_data=post_data)
            if location:
                res = ({"Location": location, "data": result.json()})
                return res
            return result.json()
        except Exception:
            return handle_client_exception(400, {'message': 'Unable to parse result.'})

    def http_put(self, path, put_data=None):
        """Make a PUT request to the Gitlab server.

        Args:
            path: Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            query_data: Data to send as query parameters
            post_data: Data to send in the body (will be converted to
                              json by default)
            raw: If True, do not convert post_data to json
            files: The files to send to the server
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            The parsed json returned by the server.

        Raises:
            GitlabHttpError: When the return code is not 2xx
            GitlabParsingError: If the json data could not be parsed
        """
        put_data = put_data or {}

        result = self.http_request("put", path, post_data=put_data)
        try:
            return result.json()
        except Exception:
            return handle_client_exception(400, {'message': 'Unable to parse result.'})

    def http_delete(self, path):
        """Make a DELETE request to the Gitlab server.

        Args:
            path: Path or full URL to query ('/projects' or
                        'http://whatever/v4/api/projecs')
            **kwargs: Extra options to send to the server (e.g. sudo)

        Returns:
            The requests object.

        Raises:
            GitlabHttpError: When the return code is not 2xx
        """
        return self.http_request("delete", path)

    # @gitlab.exceptions.on_http_error(gitlab.exceptions.GitlabSearchError)
    # def search(
    #     self, scope: str, search: str, **kwargs: Any
    # ) -> Union["GitlabList", List[Dict[str, Any]]]:
    #     """Search GitLab resources matching the provided string.'

    #     Args:
    #         scope: Scope of the search
    #         search: Search string
    #         **kwargs: Extra options to send to the server (e.g. sudo)

    #     Raises:
    #         GitlabAuthenticationError: If authentication is not correct
    #         GitlabSearchError: If the server failed to perform the request

    #     Returns:
    #         A list of dicts describing the resources found.
    #     """
    #     data = {"scope": scope, "search": search}
    #     return self.http_list("/search", query_data=data, **kwargs)


class CSGList(object):
    """Generator representing a list of remote objects.

    The object handles the links returned by a query to the API, and will call
    the API again when needed.
    """
    # NOTE: we do not calculate page number, but only provide urls for pagination

    def __init__(self, csg: CSGenome, url: str, query_data: dict):
        self._csgenome = csg
        self._base_url = url
        self._original_query = query_data
        self._query(self._base_url, query_data)

        # Remove query_parameters from kwargs, which are saved via the `next` URL
        # self._kwargs.pop("query_parameters", None)

    def _query(self, url, params=None):
        try:
            result = self._csgenome.http_request("get", url, params=params)
            self._data = result.json()
        except Exception:
            self._data = {'errors': 'Could not connect to server. Check your connection or try again later'}
            return handle_client_exception(400, {'message': 'Unable to parse result.'})

        try:
            links = self._data['links']
            self._next_url = links["next"]
            self._fist_url = links["first"]
            self._last_url = links["last"]
            self._prev_url = links["prev"]
        except KeyError:
            pass  # TODO: return some error

    def __iter__(self):
        return self

    # def __next__(self):
    #     return self.next_page()

    def json(self):
        data = self._data.copy()
        return data

    def gen(self, object_creator):
        # default the same query data with next page
        if 'errors' in self._data:
            from csgapi.base import CSGError
            raise CSGError(self._data)

        for item in self._data['data']:
            yield object_creator(item)

        while self._next_url:
            self._original_query['page'] += 1
            new_query = self._original_query.copy()
            self._query(self._base_url, new_query)

            for item in self._data['data']:
                yield object_creator(item)
