"""Client for Kameleoon"""
import asyncio
import json
import threading
import time
from typing import cast, Callable, Coroutine, Optional, Tuple, Union, Any, List, Dict
import warnings
from dateutil import parser

from kameleoon.client_configuration import KameleoonClientConfiguration
from kameleoon.configuration.feature_flag import FeatureFlag
from kameleoon.configuration.rule import Rule
from kameleoon.configuration.settings import Settings
from kameleoon.configuration.variation import Variation
from kameleoon.configuration.variation_by_exposition import VariationByExposition
from kameleoon.helpers.logger import Logger
from kameleoon.hybrid.hybrid_manager_impl import HybridManagerImpl
from kameleoon.storage.cache_factory_impl import CacheFactoryImpl

from kameleoon.network.post_body_line import PostBodyLine
from kameleoon.network.activity_event import ActivityEvent
from kameleoon.network.experiment_event import ExperimentEvent
from kameleoon.network.net_provider_impl import NetProviderImpl
from kameleoon.network.net_provider import Response
from kameleoon.network.network_manager_factory import NetworkManagerFactory
from kameleoon.network.network_manager_factory_impl import NetworkManagerFactoryImpl
from kameleoon.network.services.configuration_service import ConfigurationService
from kameleoon.network.services.data_service import DataService

from kameleoon.data import Conversion, CustomData, Data, UserAgent
from kameleoon.defaults import (
    DEFAULT_CONFIGURATION_PATH,
    DEFAULT_TIMEOUT_MILLISECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    DEFAULT_VISITOR_DATA_MAXIMUM_SIZE,
    DEFAULT_CONFIGURATION_UPDATE_INTERVAL,
    USER_AGENT_MAX_COUNT,
)
from kameleoon.helpers.multi_threading import (
    ThreadEventLoop,
    run_in_thread,
    invoke_coro,
    get_loop,
    has_running_event_loop,
)
from kameleoon.helpers.repeat_timer import RepeatTimer
from kameleoon.real_time.real_time_configuration_service import (
    RealTimeConfigurationService,
)
from kameleoon.storage.varation_storage import VariationStorage
from kameleoon.targeting.conditions.sdk_language_condition import SdkLanguageCondition
from kameleoon.sdk_version import SdkVersion

from kameleoon.exceptions import (
    ExperimentConfigurationNotFound,
    NotTargeted,
    NotAllocated,
    SiteCodeDisabled,
    VariationConfigurationNotFound,
    FeatureConfigurationNotFound,
    FeatureVariableNotFound,
)
from kameleoon.helpers.functions import (
    check_visitor_code,
    obtain_hash_double,
    obtain_hash_double_rule,
    get_size,
    read_kameleoon_cookie_value,
)
from kameleoon.helpers.config import config
from kameleoon.targeting.conditions.targeting_condition import TargetingConditionType
from kameleoon.targeting.models import Segment

__all__ = [
    "KameleoonClient",
]

REFERENCE = 0
X_PAGINATION_PAGE_COUNT = "X-Pagination-Page-Count"
SEGMENT = "targetingSegment"
KAMELEOON_TRACK_EXPERIMENT_THREAD = "KameleoonTrackExperimentThread"
KAMELEOON_TRACK_DATA_THREAD = "KameleoonTrackDataThread"
STATUS_ACTIVE = "ACTIVE"
FEATURE_STATUS_DEACTIVATED = "DEACTIVATED"
HYBRID_MANAGER_CACHE_TIMEOUT_SECONDS = 5.0


# pylint: disable=R0904
class KameleoonClient:
    """
    KameleoonClient

    Example:

    .. code-block:: python3

        from kameleoon import KameleoonClient

        SITE_CODE = 'a8st4f59bj'

        kameleoon_client = KameleoonClient(SITE_CODE)

        kameleoon_client = KameleoonClient(SITE_CODE,
                           configuration_path='/etc/kameleoon/client-python.yaml')

        kameleoon_client = KameleoonClient(SITE_CODE)

        kameleoon_client = KameleoonClient(SITE_CODE, logger=MyLogger)
    """

    initialize = False
    timer: Optional[threading.Timer] = None

    _network_manager_factory: NetworkManagerFactory = NetworkManagerFactoryImpl()

    # pylint: disable=R0913
    def __init__(
        self,
        site_code: str,
        configuration_path: str = DEFAULT_CONFIGURATION_PATH,
        configuration_object: Optional[KameleoonClientConfiguration] = None,
        logger=None,
    ):
        """
        :param site_code: Code of the website you want to run experiments on. This unique code id can
                              be found in our platform's back-office. This field is mandatory.
        :type site_code: str
        :param configuration_path: Path to the SDK configuration file.
                                   This field is optional and set to /etc/kameleoon/client-python.yaml by default.
        :type configuration_path: str
        :param configuration:   Configuration object which can be used instead of external file at configuration_path.
                                This field is optional set to None by default.
        :type configuration: KameleoonClientConfiguration
        :param logger: Optional component which provides a log method to log messages. By default see class Logger.
        """
        # pylint: disable=too-many-instance-attributes
        # Eight is reasonable in this case.
        self.site_code = site_code
        self._experiments: List[Dict[str, Any]] = []
        self._feature_flags: List[FeatureFlag] = []
        self.settings = Settings()
        self.logger = logger or Logger.shared()
        self.variation_storage = VariationStorage()
        self.real_time_configuration_service: Optional[RealTimeConfigurationService] = None
        self.update_configuration_handler: Optional[Callable[[], None]] = None
        self._setup_client_configuration(configuration_path, configuration_object)
        self.hybrid_manager = HybridManagerImpl(
            HYBRID_MANAGER_CACHE_TIMEOUT_SECONDS,
            CacheFactoryImpl(),
            self.multi_threading,
        )

        self.data: Dict[str, List[Data]] = {}
        self.user_agent_data: Dict[str, UserAgent] = {}

        self.network_manager = self._network_manager_factory.create(
            self.site_code, self.environment, DEFAULT_TIMEOUT_SECONDS, NetProviderImpl(), self.logger
        )
        self._thread_event_loop = ThreadEventLoop() if self.multi_threading else None

        self._init_fetch_configuration()

    def __del__(self):
        self._clear_timer()
        if self._thread_event_loop:
            self._thread_event_loop.run_coro(self.network_manager.net_provider.close())
            self._thread_event_loop.stop()
        else:
            invoke_coro(self.network_manager.net_provider.close())

    ###
    #   Public API methods
    ###

    def get_visitor_code(
        self,
        cookies: Union[str, Dict[str, str]],
        default_visitor_code: Optional[str] = None,
    ) -> str:
        """
        Load cookies from a string (presumably HTTP_COOKIE) or
        from a dictionary.
        See SimpleCookie() https://docs.python.org/3/library/http.cookies.html

        :param cookies: str ot dict
        :param default_visitor_code: Optional str
        :return: kameleoon_cookie_value
        :rtype: str

        Examples:

        .. code-block:: python3

            kameleoon_client = KameleoonClient(SITE_CODE)

            kameleoon_client.get_visitor_code(cookies)

            kameleoon_client.get_visitor_code(cookies, default_visitor_code)

        """
        # pylint: disable=no-self-use
        return read_kameleoon_cookie_value(cookies, default_visitor_code)

    def obtain_visitor_code(
        self,
        cookies: Union[str, Dict[str, str]],
        default_visitor_code: Optional[str] = None,
    ) -> str:
        """Depreacted function. Please use `get_visitor_code` instead."""
        warnings.warn(
            "Call to deprecated function `obtain_visitor_code`. Please use `get_visitor_code` instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.get_visitor_code(cookies, default_visitor_code)

    def trigger_experiment(self, visitor_code: str, experiment_id: int) -> Optional[int]:  # noqa: C901
        """Trigger an experiment.

        If such a visitor_code has never been associated with any variation,
        the SDK returns a randomly selected variation.
        If a user with a given visitor_code is already registered with a variation, it will detect the previously
        registered variation and return the variation_id.
        You have to make sure that proper error handling is set up in your code as shown in the example to the right to
        catch potential exceptions.

        :param visitor_code: Visitor code
        :param experiment_id: Id of the experiment you want to trigger.
        :return: variation_id:  Id of the variation

        :raises:

            ExperimentConfigurationNotFound: Raise when experiment configuration is not found
            NotAllocated: The visitor triggered the experiment, but did not activate it. Usually, this happens because
                          the user has been associated with excluded traffic
            NotTargeted: The visitor is not targeted by the experiment, as the associated targeting segment conditions
                         were not fulfilled. He should see the reference variation
            VisitorCodeNotValid: Raise when the provided visitor code is not valid
                        (empty, or longer than 255 characters)
            SiteCodeDisabled: Raise when the siteCode is not disabled, SDK doesn't work with disabled siteCodes.
                        To make SDK working please enable Site in your account.


        Examples:

        .. code-block:: python

                visitor_code = kameleoon_client.get_visitor_code(request.COOKIES)
                variation_id = 0
                try:
                    variation_id = kameleoon_client.trigger_experiment(visitor_code, 135471)
                except NotAllocated as ex:
                    variation_id = 0
                    client.logger.error(ex)
                except NotTargeted as ex:
                    variation_id = 0
                    client.logger.error(ex)
                except ExperimentConfigurationNotFound as ex:
                    variation_id = 0
                    client.logger.error(ex)

                recommended_products_number = 5

                if variation_id == 148382:
                    recommended_products_number = 10
                elif variation_id == 187791:
                    recommended_products_number = 8

                response = JsonResponse({...})
                # set a cookie
                response.set_cookie(**kameleoon_cookie)
        """
        # pylint: disable=too-many-locals,no-else-return,no-else-raise
        # pylint: disable=too-many-branches,too-many-statements,too-many-nested-blocks
        check_visitor_code(visitor_code)
        experiment = next(
            (experiment for experiment in self._experiments if experiment["id"] == experiment_id),
            None,
        )
        if not experiment:
            raise ExperimentConfigurationNotFound(experiment_id)
        self.__check_site_code_enable(experiment)
        targeted = self.__check_targeting(visitor_code, experiment)
        if targeted:
            # Disable storage (sticky allocation)
            # saved_variation_id = self.__is_valid_saved_variation(
            #     visitor_code, experiment_id, experiment["respoolTime"]
            # )
            variation_id = self.__calculate_variation_for_experiment(visitor_code, experiment)
            none_variation = variation_id is None
        else:
            variation_id = None
        self.__send_tracking_request(visitor_code, experiment_id, variation_id)
        self.__save_variation(visitor_code, experiment_id, variation_id)
        if not targeted:
            raise NotTargeted(visitor_code, experiment_id)
        if none_variation:
            raise NotAllocated(visitor_code, experiment_id)
        return variation_id

    def add_data(self, visitor_code: str, *args) -> None:
        """
        To associate various data with the current user, we can use the add_data() method.
        This method requires the visitor_code as a first parameter, and then accepts several additional parameters.
        These additional parameters represent the various Data Types allowed in Kameleoon.

        Note that the add_data() method doesn't return any value and doesn't interact with the Kameleoon back-end
        servers by itself. Instead, all declared data is saved for further sending via the flush() method described
        in the next paragraph. This reduces the number of server calls made, as data is usually grouped
        into a single server call triggered by the execution of flush()

        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: str
        :param args:
        :return: None

        Examples:

        .. code-block:: python

                from kameleoon.data import PageView

                visitor_code = kameleoon_client.get_visitor_code(request.COOKIES)
                kameleoon_client.add_data(visitor_code, CustomData("test-id", "test-value"))
                kameleoon_client.add_data(visitor_code, Browser(BrowserType.CHROME))
                kameleoon_client.add_data(visitor_code, PageView("www.test.com", "test-title"))
                kameleoon_client.add_data(visitor_code, Conversion(1, 100.0))
                kameleoon_client.add_data(visitor_code, Interest(1))
        """
        check_visitor_code(visitor_code)
        self._check_data_size(self.visitor_data_maximum_size)
        if args:
            list_data = []
            for arg in args:
                if isinstance(arg, UserAgent):
                    self._add_user_agent(visitor_code, arg)
                else:
                    list_data.append(arg)
            if visitor_code in self.data:
                if not self.data[visitor_code]:
                    self.data[visitor_code] = []
                self.data[visitor_code] += list_data
            else:
                self.data[visitor_code] = list_data
        self.logger.debug("Successfully adding data")

    def track_conversion(self, visitor_code: str, goal_id: int, revenue: float = 0.0) -> None:
        """
        To track conversion, use the track_conversion() method. This method requires visitor_code and goal_id to track
        conversion on this particular goal. In addition, this method also accepts revenue as a third optional argument
        to track revenue. The visitor_code is usually identical to the one that was used when triggering the experiment.
        The track_conversion() method doesn't return any value. This method is non-blocking as the server
        call is made asynchronously.

        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: str
        :param goal_id: ID of the goal. This field is mandatory.
        :type goal_id: int
        :param revenue: Revenue of the conversion. This field is optional.
        :type revenue: float
        :return: None
        """
        check_visitor_code(visitor_code)
        self.add_data(visitor_code, Conversion(goal_id, revenue))
        self.flush(visitor_code)

    def flush(self, visitor_code: Optional[str] = None):
        """
        Data associated with the current user via add_data() method is not immediately sent to the server.
        It is stored and accumulated until it is sent automatically by the trigger_experiment()
        or track_conversion() methods, or manually by the flush() method.
        This allows the developer to control exactly when the data is flushed to our servers. For instance,
        if you call the add_data() method a dozen times, it would be a waste of ressources to send data to the
        server after each add_data() invocation. Just call flush() once at the end.
        The flush() method doesn't return any value. This method is non-blocking as the server call
        is made asynchronously.


        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: Optional[str]

        Examples:

        .. code-block:: python

                from kameleoon.data import PageView

                visitor_code = kameleoon_client.get_visitor_code(request.COOKIES)
                kameleoon_client.add_data(visitor_code, CustomData("test-id", "test-value"))
                kameleoon_client.add_data(visitor_code, Browser(BrowserType.CHROME))
                kameleoon_client.add_data(visitor_code, PageView("www.test.com", "test-title"))
                kameleoon_client.add_data(visitor_code, Conversion(1, 100.0))
                kameleoon_client.add_data(visitor_code, Interest(1))

                kameleoon_client.flush()

        """
        if visitor_code is not None:
            check_visitor_code(visitor_code)
            self.__send_tracking_request(visitor_code)
        else:
            not_sent_data = self.__get_all_not_sent_data()
            for vis_code, data in not_sent_data.items():
                self.__send_tracking_request(vis_code, visitor_data=data)

    def get_variation_associated_data(self, variation_id: int) -> Dict[str, str]:
        """Obtain variation associated data.

        To retrieve JSON data associated with a variation, call the get_variation_associated_data method of our SDK.
        The JSON data usually represents some metadata of the variation, and can be configured on our web application
        interface or via our Automation API.

        This method takes the variationID as a parameter and will return the data as a json string.
        It will throw an exception () if the variation ID is wrong or corresponds to an experiment
        that is not yet online.

        :param variation_id: int  ID of the variation you want to obtain associated data for. This field is mandatory.
        :return: Dict  Data associated with this variationID.

        :raises: VariationNotFound

        Example:

        .. code-block:: python3

                visitor_code = kameleoon_client.get_visitor_code(request.COOKIES)

                experiment_id = 75253

                try:
                    variation_id = kameleoon_client.trigger_experiment(visitor_code, experiment_id)
                    dict_object = kameleoon_client.get_variation_associated_data(variation_id)
                    first_name = dict_object["firstName"]
                except VariationNotFound:
                    # The variation is not yet activated on Kameleoon's side,
                    ie the associated experiment is not online
                    pass
        """
        variations = list(
            filter(
                lambda variation: variation["id"] == variation_id,
                [
                    variation
                    for variations in [experiment["variations"] for experiment in self._experiments]
                    for variation in variations
                ],
            )
        )
        if not variations:
            raise VariationConfigurationNotFound(variation_id)
        variation = variations[0]
        return json.loads(variation["customJson"])

    def obtain_variation_associated_data(self, variation_id: int) -> Dict[str, str]:
        """Depreacted function. Please use `get_variation_associated_data` instead."""
        warnings.warn(
            "Call to deprecated function `obtain_variation_associated_data`. "
            "Please use `get_variation_associated_data` instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.get_variation_associated_data(variation_id)

    def is_feature_active(self, visitor_code: str, feature_key: str) -> bool:
        """
        Check if feature is active for a given visitor code

        This method takes a visitor_code and feature_key (or feature_id) as mandatory arguments to check
        if the specified feature will be active for a given user.
        If such a user has never been associated with this feature flag, the SDK returns a boolean
        value randomly (true if the user should have this feature or false if not). If a user with a given visitor_code
        is already registered with this feature flag, it will detect the previous feature flag value.
        You have to make sure that proper error handling is set up in your code as shown in the example to the right
        to catch potential exceptions.


        :param visitor_code: str Unique identifier of the user. This field is mandatory.
        :param feature_key: str Key of the feature flag you want to expose to a user. This field is mandatory.
        :return: bool Value of the feature that is active for a given visitor_code.


        :raises:
            FeatureConfigurationNotFound: Exception indicating that the requested feature ID has not been found in
                                          the internal configuration of the SDK. This is usually normal and means that
                                          the feature flag has not yet been activated on Kameleoon's side
                                          (but code implementing the feature is already deployed on the
                                          web-application's side).
            VisitorCodeNotValid: Raise when the provided visitor code is not valid
                        (empty, or longer than 255 characters)

        Examples:

        .. code-block:: python3

                visitor_code = kameleoon_client.get_visitor_code(request.COOKIES)
                feature_key = "new_checkout"
                has_new_checkout = False

                try:
                    has_new_checkout = kameleoon_client.is_feature_active(visitor_code, feature_key)
                except NotTargeted:
                    # The user did not trigger the feature, as the associated targeting segment conditions were not
                    # fulfilled. The feature should be considered inactive
                    logger.debug(...)
                except FeatureConfigurationNotFound:
                    # The user will not be counted into the experiment, but should see the reference variation
                    logger.debug(...)

                if has_new_checkout:
                    # Implement new checkout code here
        """
        (_, variation_key) = self.__get_feature_variation_key(visitor_code, feature_key)
        return variation_key != Variation.Type.OFF.value

    def obtain_feature_variable(
        self, feature_key: str, variable_key: str
    ) -> Union[bool, str, float, Dict[str, Any], None]:
        """
        Retrieve a feature variable.
        A feature variable can be changed easily via our web application.

        :param feature_key: Union[str, int] ID or Key of the feature you want to obtain to a user.
                            This field is mandatory.
        :param variable_key: str  Key of the variable. This field is mandatory.
        :return: bool or str or float or dict

        :raises: FeatureVariableNotFound: Exception indicating that the requested variable has not been found.
                                         Check that the variable's ID (or key) matches the one in your code.
                 FeatureConfigurationNotFound: Exception indicating that the requested feature ID has not been found
                                               in the internal configuration of the SDK. This is usually normal and
                                               means that the feature flag has not yet been activated on
                                               Kameleoon's side.

        Example:

        .. code-block:: python3

                feature_key = "myFeature"
                variable_key = "myVariable"
                try:
                    data = kameleoon_client.obtain_feature_variable(feature_key, variable_key)
                except FeatureConfigurationNotFound:
                    # The feature is not yet activated on Kameleoon's side
                    pass
                except FeatureVariableNotFound:
                    # Request variable not defined on Kameleoon's side
                    pass
        """
        warnings.warn(
            "Call to deprecated function `obtain_feature_variable`. " "Please use `get_feature_variable` instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        variables = self.get_feature_all_variables(feature_key, Variation.Type.OFF.value)
        if variable_key in variables:
            return variables[variable_key]
        raise FeatureVariableNotFound(variable_key)

    def get_feature_all_variables(self, feature_key: str, variation_key: str) -> Dict[str, Any]:
        """
        Retrieve all feature variables.
        A feature variables can be changed easily via our web application.

        :param feature_key: str Key of the feature you want to obtain to a user.
                            This field is mandatory.
        :return: Dictionary of feature variables
        :rtype: Dict[str, Any]

        :raises: FeatureConfigurationNotFound: Exception indicating that the requested feature Key has not been found
                                               in the internal configuration of the SDK. This is usually normal and
                                               means that the feature flag has not yet been activated on
                                               Kameleoon's side.
                 VariationConfigurationNotFound: Variation key isn't found for current feature flag.

        Example:

        .. code-block:: python3
                try:
                    data = kameleoon_client.get_feature_all_variables(feature_key)
                except FeatureConfigurationNotFound:
                    # The feature is not yet activated on Kameleoon's side
                except VariationConfigurationNotFound:
                    # The variation key is not found for current feature flag
                    pass
        """

        # pylint: disable=no-else-raise
        feature_flag = self.__find_feature_flag(feature_key)
        variation = feature_flag.get_variation(variation_key)
        if not variation:
            raise VariationConfigurationNotFound(variation_key)
        variables: Dict[str, Any] = {}
        for var in variation.variables:
            variables[var.key] = var.get_value()
        return variables

    def obtain_feature_all_variables(self, feature_key: str, variation_key: str = "off") -> Dict[str, Any]:
        """Depreacted function. Please use `get_feature_all_variables` instead."""
        warnings.warn(
            "Call to deprecated function `obtain_feature_all_variables`. "
            "Please use `get_feature_all_variables` instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.get_feature_all_variables(feature_key, variation_key)

    async def get_remote_data_async(self, key: str, timeout: Optional[float] = None) -> Optional[Any]:
        """
        The get_remote_data_async method allows you to retrieve data asynchronously (according to a key passed as
        argument) stored on a remote Kameleoon server. Usually data will be stored on our remote servers
        via the use of our Data API. This method, along with the availability of our highly scalable servers
        for this purpose, provides a convenient way to quickly store massive amounts of data that
        can be later retrieved for each of your visitors / users.

        :param key: key you want to retrieve data. This field is mandatory.
        :type key: str
        :param timeout: requests timeout in seconds (default value is 5 seconds)
        :type timeout: Optional[float]

        :return: data assosiated with this key, decoded into json
        :rtype: Optional[Any]
        """
        service: DataService = self.network_manager.get_service(DataService)
        response = await service.get_remote_data(key, timeout)
        return response.content

    def get_remote_data(self, key: str, timeout: Optional[float] = None) -> Optional[Any]:
        """
        The get_remote_data method allows you to retrieve data (according to a key passed as
        argument) stored on a remote Kameleoon server. Usually data will be stored on our remote servers
        via the use of our Data API. This method, along with the availability of our highly scalable servers
        for this purpose, provides a convenient way to quickly store massive amounts of data that
        can be later retrieved for each of your visitors / users.

        :param key: key you want to retrieve data. This field is mandatory.
        :type key: str
        :param timeout: requests timeout in seconds (default value is 5 seconds)
        :type timeout: Optional[float]

        :return: data assosiated with this key, decoded into json
        :rtype: Optional[Any]
        """
        coro = self.get_remote_data_async(key, timeout)
        return self.__make_sync_call_anyway(coro, "get_remote_data")

    def retrieve_data_from_remote_source(self, key: str, timeout: Optional[float] = None) -> Optional[Any]:
        """
        Deprecated, please use `get_remote_data`

        The retrieve_data_from_remote_source method uses for obtaining a list of experiment IDs:
        - currently available for the SDK

        :return: List of all experiments IDs
        :rtype: List[int]
        """
        warnings.warn(
            "Call to deprecated function `retrieve_data_from_remote_source`. " "Please use `get_remote_data` instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        return self.get_remote_data(key, timeout)

    async def get_remote_visitor_data_async(self, visitor_code: str, add_data=True,
                                            timeout: Optional[float] = None) -> List[Data]:
        """
        The get_remote_visitor_data_async is an asynchronous method for retrieving custom data for
        the latest visit of `visitor_code` from Kameleoon Data API and optionally adding it
        to the storage so that other methods could decide whether the current visitor is targeted or not.

        :param visitor_code: The visitor code for which you want to retrieve the assigned data. This field is mandatory.
        :type key: str
        :param add_data: A boolean indicating whether the method should automatically add retrieved data for a visitor.
        If not specified, the default value is `True`. This field is optional.
        :type add_data: bool
        :param timeout: requests timeout in seconds (default value is 5 seconds)
        :type timeout: Optional[float]

        :return: A list of data assigned to the given visitor.
        :rtype: List[Data]
        """
        service: DataService = self.network_manager.get_service(DataService)
        response = await service.get_remote_visitor_data(visitor_code, timeout)
        if response.content is None:
            return []
        data_list = self.__parse_custom_data_list(response.content)
        if add_data:
            self.add_data(visitor_code, *data_list)
        return data_list

    def get_remote_visitor_data(self, visitor_code: str, add_data=True,
                                timeout: Optional[float] = None) -> List[Data]:
        """
        The get_remote_visitor_data is a synchronous method for retrieving custom data for
        the latest visit of `visitor_code` from Kameleoon Data API and optionally adding it
        to the storage so that other methods could decide whether the current visitor is targeted or not.

        :param visitor_code: The visitor code for which you want to retrieve the assigned data. This field is mandatory.
        :type key: str
        :param add_data: A boolean indicating whether the method should automatically add retrieved data for a visitor.
        If not specified, the default value is `True`. This field is optional.
        :type add_data: bool
        :param timeout: requests timeout in seconds (default value is 5 seconds)
        :type timeout: Optional[float]

        :return: A list of data assigned to the given visitor.
        :rtype: List[Data]
        """
        coro = self.get_remote_visitor_data_async(visitor_code, add_data, timeout)
        result = self.__make_sync_call_anyway(coro, "get_remote_visitor_data")
        if result is None:
            return []
        return cast(List[Data], result)

    def __parse_custom_data_list(self, raw: Any) -> List[Data]:
        try:
            latest_record = raw.get("currentVisit")
            if latest_record is None:
                previous_visits = raw.get("previousVisits")
                if previous_visits:
                    latest_record = previous_visits[0]
                else:
                    return []
            return [
                CustomData(jcd.get("index", -1), *jcd.get("valuesCountMap", []))
                for event in latest_record.get("customDataEvents", [])
                if (jcd := event.get("data"))
            ]
        except Exception as ex:  # pylint: disable=W0703
            self.logger.error(f"Parsing of visitor data failed: {ex}")
            return []

    def get_experiment_list(self) -> List[int]:
        """
        The get_experiment_list method uses for obtaining a list of experiment IDs:
        - currently available for the SDK

        :return: List of all experiments IDs
        :rtype: List[int]
        """
        return list(map(lambda experiment: experiment["id"], self._experiments))

    def get_experiment_list_for_visitor(self, visitor_code: str, only_allocated: bool = True) -> List[int]:
        """
        The get_experiment_list method uses for obtaining a list of experiment IDs:
        - currently targeted for a visitor
        - currently targeted and allocated simultaneously for a visitor

        :param visitor_code: unique identifier of a visitor
        :type visitor_code: Optional[str]
        :param only_allocated: if `only_allocated` parameter is `true` result contains only allocated for visitor
         experiments, otherwise it contains all targeted experiments for specific `visitor_code`
        :type only_allocated: bool

        :return: List of all experiments IDs (targeted or targeted and allocated simultaneously)
                 for current visitorCode
        :rtype: List[int]
        """

        def filter_conditions(experiment: Dict[str, Any]) -> bool:
            if not self.__check_targeting(visitor_code, experiment):
                return False

            return not only_allocated or self.__calculate_variation_for_experiment(visitor_code, experiment) is not None

        return list(
            map(
                lambda experiment: experiment["id"],
                filter(
                    filter_conditions,
                    self._experiments,
                ),
            )
        )

    def obtain_experiment_list(self, visitor_code: Optional[str] = None, only_allocated: bool = True) -> List[int]:
        """Depreacted function. Please use `get_experiment_list` or `get_experiment_list_for_visitor` instead."""
        warnings.warn(
            "Call to deprecated function `obtain_experiment_list`. "
            "Please use `get_experiment_list` or `get_experiment_list_for_visitor` instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        if visitor_code is None:
            return self.get_experiment_list()
        return self.get_experiment_list_for_visitor(visitor_code, only_allocated)

    def get_feature_list(self) -> List[str]:
        """
        The get_feature_list method uses for obtaining a list of feature flag IDs:
        - currently available for the SDK

        :return: List of all feature flag IDs
        :rtype: List[int]
        """
        return list(map(lambda feature_flag: feature_flag.feature_key, self._feature_flags))

    def get_active_feature_list_for_visitor(self, visitor_code: str) -> List[str]:
        """
        The get_active_feature_list_for_visitor method uses for obtaining a list of feature flag IDs:
        - currently targeted and active simultaneously for a visitor

        :param visitor_code: unique identifier of a visitor
        :type visitor_code: Optional[str]

        :return: List of all feature flag IDs or targeted and active simultaneously
                 for current visitorCode
        :rtype: List[int]
        """

        def filter_conditions(feature_flag: FeatureFlag) -> bool:
            (variation, rule) = self.__calculate_variation_rule_for_feature(visitor_code, feature_flag)
            variation_key = self.__calculate_variation_key(variation, rule, feature_flag)
            return variation_key != Variation.Type.OFF.value

        return list(
            map(
                lambda feature_flag: feature_flag.feature_key,
                filter(
                    filter_conditions,
                    self._feature_flags,
                ),
            )
        )

    # pylint: disable=W0613
    def obtain_feature_list(
        self,
        visitor_code: Optional[str] = None,
        only_active: bool = True,
    ) -> List[str]:
        """Depreacted function. Please use `get_feature_list` or `get_active_feature_list_for_visitor` instead."""
        warnings.warn(
            "Call to deprecated function `obtain_experiment_list`. "
            "Please use `get_feature_list` or `get_active_feature_list_for_visitor` instead.",
            category=DeprecationWarning,
            stacklevel=2,
        )
        if visitor_code is None:
            return self.get_feature_list()
        return self.get_active_feature_list_for_visitor(visitor_code)

    def get_feature_variation_key(self, visitor_code: str, feature_key: str) -> str:
        """
        Returns a variation key for visitor code

        This method takes a visitor_code and feature_key as mandatory arguments and
        returns a variation assigned for a given visitor
        If such a user has never been associated with any feature flag rules, the SDK returns a default variation key
        You have to make sure that proper error handling is set up in your code as shown in the example
        to the right to catch potential exceptions.

        :param visitor_code: unique identifier of a visitor
        :type visitor_code: str
        :param feature_key: unique identifier of feature flag
        :type feature_key: str

        :return: Returns a variation key for visitor code
        :rtype: str

        :raises:
            FeatureConfigurationNotFound: Exception indicating that the requested feature ID has not been found in
                                          the internal configuration of the SDK. This is usually normal and means that
                                          the feature flag has not yet been activated on Kameleoon's side
                                          (but code implementing the feature is already deployed on the
                                          web-application's side).
            VisitorCodeNotValid: Raise when the provided visitor code is not valid
                                 (empty, or longer than 255 characters)
        """
        (_, variation_key) = self.__get_feature_variation_key(visitor_code, feature_key)
        return variation_key

    def get_feature_variable(
        self, visitor_code: str, feature_key: str, variable_key: str
    ) -> Union[bool, str, float, Dict[str, Any], List[Any], None]:
        """
        Retrieves a feature variable value from assigned for visitor variation
        A feature variable can be changed easily via our web application.

        :param visitor_code: unique identifier of a visitor
        :type visitor_code: str
        :param feature_key: unique identifier of feature flag
        :type feature_key: str
        :param variable_name: variable name you want to retrieve
        :type variable_name: str

        :return: Feature variable value from assigned for visitor variation
        :rtype: Union[bool, str, float, Dict, List]

        :raises:
            FeatureConfigurationNotFound: Exception indicating that the requested feature ID has not been found in
                                          the internal configuration of the SDK. This is usually normal and means that
                                          the feature flag has not yet been activated on Kameleoon's side
                                          (but code implementing the feature is already deployed on the
                                          web-application's side).
            FeatureVariableNotFound: Variable provided name doesn't exist in this feature
            VisitorCodeNotValid: Raise when the provided visitor code is not valid
                                 (empty, or longer than 255 characters)
        """

        (feature_flag, variation_key) = self.__get_feature_variation_key(visitor_code, feature_key)
        variation = feature_flag.get_variation(variation_key)
        variable = variation.get_variable_by_key(variable_key) if variation else None
        if variable is None:
            raise FeatureVariableNotFound(variable_key)
        return variable.get_value()

    ###
    #   Private API methods
    ###

    # Useless without storage
    # def __is_valid_saved_variation(
    #     self, visitor_code: str, experiment_id: int, respool_times: Dict[str, int]
    # ) -> Optional[int]:
    #     # get saved variation
    #     saved_variation_id = self.variation_storage.get_variation_id(
    #         visitor_code, experiment_id
    #     )
    #     if saved_variation_id is not None:
    #         # get respool time for saved variation id
    #         respool_time = respool_times.get(str(saved_variation_id))
    #         # checking variation for validity along with respoolTime
    #         return self.variation_storage.is_variation_id_valid(
    #             visitor_code, experiment_id, respool_time
    #         )
    #     return None

    def __check_targeting(self, visitor_code: str, campaign: Dict[str, Any]):
        return (
            SEGMENT not in campaign
            or campaign[SEGMENT] is None
            or campaign[SEGMENT].check_tree(lambda type: self.__get_condition_data(type, visitor_code, campaign["id"]))
        )

    def __check_targeting_id_object(self, visitor_code: str, campaign_id: int, targeting_object: Rule) -> bool:
        return (
            targeting_object.targeting_segment is None
            or targeting_object.targeting_segment.check_tree(
                lambda type: self.__get_condition_data(type, visitor_code, campaign_id)
            )
            is True
        )

    TARGETING_DATA_CONDITION_TYPES = (
        TargetingConditionType.CUSTOM_DATUM,
        TargetingConditionType.PAGE_TITLE,
        TargetingConditionType.PAGE_URL,
        TargetingConditionType.BROWSER,
        TargetingConditionType.DEVICE_TYPE,
        TargetingConditionType.CONVERSIONS,
    )

    def __get_condition_data(self, type_condition_str: str, visitor_code: str, campaign_id: int):
        condition_type = TargetingConditionType(type_condition_str)
        if condition_type in KameleoonClient.TARGETING_DATA_CONDITION_TYPES:
            return self.data.get(visitor_code) or []

        if condition_type == TargetingConditionType.TARGET_EXPERIMENT:
            return self.variation_storage.get_saved_variation_id(visitor_code)

        if condition_type == TargetingConditionType.EXCLUSIVE_EXPERIMENT:
            return (
                campaign_id,
                self.variation_storage.get_saved_variation_id(visitor_code),
            )

        if condition_type == TargetingConditionType.VISITOR_CODE:
            return visitor_code

        if condition_type == TargetingConditionType.SDK_LANGUAGE:
            return SdkLanguageCondition.SdkInfo(SdkVersion.NAME, SdkVersion.VERSION)

        return None

    def _check_data_size(self, visitor_data_maximum_size: int) -> None:
        """
        Checks the memory for exceeding the maximum size
        :param visitor_data_maximum_size: int
        :return: None
        """
        while get_size(self.data) > (visitor_data_maximum_size * (2**20)):
            keys = self.data.keys()
            if len(list(keys)) > 0:
                del self.data[list(keys)[-1]]
            new_data = self.data.copy()
            del self.data
            self.data = new_data
            del new_data
            if get_size({}) >= get_size(self.data):
                break

    # pylint: disable=no-self-use
    def _feature_flag_scheduled(self, feature_flag: Dict[str, Any], date: float) -> bool:
        """
        Checking that feature flag is scheduled then determine its status in current time
        :param feature_flag: Dict[str, Any]
        :return: bool
        """
        current_status = feature_flag["status"] == STATUS_ACTIVE
        if feature_flag["featureStatus"] == FEATURE_STATUS_DEACTIVATED or len(feature_flag["schedules"]) == 0:
            return current_status
        for schedule in feature_flag["schedules"]:
            if (schedule.get("dateStart") is None or parser.parse(schedule["dateStart"]).timestamp() < date) and (
                schedule.get("dateEnd") is None or parser.parse(schedule["dateEnd"]).timestamp() > date
            ):
                return True
        return False

    def _parse_json(self, custom_json: Dict[str, Any]):
        if custom_json["type"] == "Boolean":
            return bool(custom_json["value"])
        if custom_json["type"] == "String":
            return str(custom_json["value"])
        if custom_json["type"] == "Number":
            return float(custom_json["value"])
        if custom_json["type"] == "JSON":
            return json.loads(custom_json["value"])
        raise TypeError("Unknown type for feature variable")

    def __calculate_variation_for_experiment(self, visitor_code: str, experiment: Dict[str, Any]) -> Optional[int]:
        """Calculates the variation for a given visitor_code and experiment"""
        threshold = obtain_hash_double(visitor_code, experiment["respoolTime"], experiment["id"])
        for variation_id, value in experiment["deviations"].items():
            threshold -= value
            if threshold < 0:
                try:
                    variation = int(variation_id)
                except ValueError:
                    variation = 0
                return variation
        return None

    def _init_fetch_configuration(self) -> None:
        """
        :return:
        """
        run_in_thread(self._fetch_configuration, with_event_loop=True).join()

    def _fetch_configuration(self, time_stamp: Optional[int] = None) -> None:
        """
        Fetches configuration from CDN service.
        Should be run in a separate thead.
        :return:  None
        """
        # pylint: disable=W0703
        try:
            configuration_json = self._obtain_configuration(time_stamp)
            if configuration_json:
                self._experiments = self._fetch_experiments(configuration_json)
                self._feature_flags = FeatureFlag.from_array(configuration_json["featureFlagConfigurations"])
                self.settings = self._fetch_settings(configuration_json)
                self._call_update_handler_if_needed(time_stamp is not None)
        except Exception as ex:
            self.logger.error(ex)
        self._manage_configuration_update(self.settings.real_time_update)

    def _call_update_handler_if_needed(self, need_call: bool) -> None:
        """
        Call the handler when configuraiton was updated with new time stamp
        :param need_call: this parameters indicates if we need to call handler or not
        :type need_call: bool
        :return:  None
        """
        if need_call and self.update_configuration_handler is not None:
            self.update_configuration_handler()

    def _manage_configuration_update(self, is_real_time_update: bool):
        if is_real_time_update:
            if self.timer is not None:
                self._clear_timer()
            if self.real_time_configuration_service is None:
                url = self.network_manager.url_provider.make_real_time_url()
                self.real_time_configuration_service = RealTimeConfigurationService(
                    url,
                    lambda real_time_event: self._fetch_configuration(real_time_event.time_stamp),
                    logger=self.logger,
                )
        else:
            if self.real_time_configuration_service is not None:
                self.real_time_configuration_service.close()
                self.real_time_configuration_service = None
            self._add_fetch_configuration_timer()

    def get_engine_tracking_code(self, visitor_code: str) -> str:
        """
        The `get_engine_tracking_code` returns the JavaScript code to be inserted in your page
        to send automatically the exposure events to the analytics solution you are using.
        :param visitor_code: Unique identifier of the user. This field is mandatory.
        :type visitor_code: str
        :return: Tracking code
        :rtype: str
        """
        return self.hybrid_manager.get_engine_tracking_code(visitor_code)

    def on_update_configuration(self, handler: Callable[[], None]):
        """
        The `on_update_configuration()` method allows you to handle the event when configuration
        has updated data. It takes one input parameter: callable **handler**. The handler
        that will be called when the configuration is updated using a real-time configuration event.
        :param handler: The handler that will be called when the configuration
        is updated using a real-time configuration event.
        :type need_call: Callable[[None], None]
        :return:  None
        """
        self.update_configuration_handler = handler

    def _add_fetch_configuration_timer(self) -> None:
        """
        Add timer for updating configuration with specific interval (polling mode)
        :return: None
        """
        if self.timer is None:
            self.timer = RepeatTimer(self.actions_configuration_refresh_interval, self._fetch_configuration)
            self.timer.setDaemon(True)
            self.timer.start()

    def _clear_timer(self) -> None:
        """
        Remove timer which updates configuration with specific interval (polling mode)
        :return: None
        """
        if self.timer is not None:
            self.timer.cancel()
            self.timer = None

    def _obtain_configuration(self, time_stamp: Optional[int]) -> Optional[Dict[str, Any]]:
        """
        Obtaining configuration from CDN service.
        Should be run in a separate thead.
        :param sitecode:
        :type: str
        :return: None
        """
        self.logger.debug("Obtaining configuration")
        service: ConfigurationService = self.network_manager.get_service(ConfigurationService)
        response_coro = service.fetch_configuration(self.environment, time_stamp)
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
        response = loop.run_until_complete(response_coro)
        if response.code and (response.code // 100 == 2):
            return response.content
        return None

    # fetching segment for both types: experiments and feature_flags (campaigns)
    # pylint: disable=no-self-use
    def _complete_campaign(self, campaign) -> Dict[str, Any]:
        """
        :param campaign (experiment or feature_flag):
        :type: dict
        :return: campaign (experiment or feature_flag)
        :rtype: dict
        """
        campaign["id"] = int(campaign["id"])
        if "respoolTime" in campaign and campaign["respoolTime"] is not None:
            campaign["respoolTime"] = {
                ("origin" if respoolTime["variationId"] == "0" else respoolTime["variationId"]): respoolTime["value"]
                for respoolTime in campaign["respoolTime"]
            }
        if "variations" in campaign and campaign["variations"] is not None:
            campaign["variations"] = [
                {"id": int(variation["id"]), "customJson": variation["customJson"]}
                for variation in campaign["variations"]
            ]
        if "segment" in campaign and campaign["segment"] is not None:
            campaign["targetingSegment"] = Segment(campaign["segment"])
        return campaign

    def _complete_experiment(self, experiment) -> Dict[str, Any]:
        """
        :param experiment:
        :type: dict
        :return:  experiment
        :rtype: dict
        """
        if "deviations" in experiment and experiment["deviations"] is not None:
            experiment["deviations"] = {
                ("origin" if deviation["variationId"] == "0" else deviation["variationId"]): deviation["value"]
                for deviation in experiment["deviations"]
            }
        return self._complete_campaign(experiment)

    def _fetch_experiments(self, configuration: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Fethcing experiments from CDN response
        :param configuration: Full configuration of experiments and feature flags
        :type: Optional[Dict[str, Any]]
        :return: List of experiments
        :rtype: List[Dict[str, Any]]
        """
        experiments = configuration["experiments"] if configuration is not None else []
        if experiments:
            experiments = [self._complete_experiment(experiment) for experiment in experiments]
            self.logger.debug(f"Experiment are fetched: {experiments}")
        return experiments

    def _fetch_settings(self, configuration: Optional[Dict[str, Any]]) -> Settings:
        """
        Fethcing configuration settings from CDN response
        :param configuration: Full configuration of experiments and feature flags
        :type: Optional[Dict[str, Any]]
        :return: Settings of configuration
        :rtype: Dict[str, Any]
        """
        if configuration:
            settings = Settings(configuration.get("configuration"))
            return settings
        return self.settings

    def __make_sync_call_anyway(self, coro: Coroutine[Any, Any, Any], method_name: str) -> Optional[Any]:
        try:
            asyncio.get_running_loop()
            self.logger.warning(
                f"Called synchronous `{method_name}` method from asynchronous code. "
                f"Please use `{method_name}_async` method instead."
            )
        except RuntimeError:
            result = get_loop().run_until_complete(coro)
            return result
        if self._thread_event_loop is None:
            self._thread_event_loop = ThreadEventLoop()
            self._thread_event_loop.start()
            self.logger.warning(
                "Despite the mono-thread mode an event loop background thread has "
                f"been started because of the call of synchronous `{method_name}` method"
            )
        future = self._thread_event_loop.run_coro(coro)
        while not future.done():
            time.sleep(0.01)
        if future.cancelled():
            self.logger.error("`%s` call was cancelled", method_name)
        elif future.exception():
            self.logger.error("`%s` call failed with exception: %s", method_name, future.exception())
        else:
            return future.result()
        return None

    def __run_call(self, coro: Coroutine[Any, None, Any]):
        try:
            if self.multi_threading:
                cast(ThreadEventLoop, self._thread_event_loop).run_coro(coro)
            else:
                invoke_coro(coro)
        except Exception as ex:  # pylint: disable=W0703
            self.logger.error("Exception occurred during call run: %s", ex)

    def __is_sync_mode(self) -> bool:
        if self.multi_threading:
            return False
        return not has_running_event_loop()

    def __send_tracking_request(
        self,
        visitor_code: str,
        experiment_id: Optional[int] = None,
        variation_id: Optional[int] = None,
        visitor_data: Optional[List[Data]] = None,
    ):
        user_agent = self._get_user_agent(visitor_code)
        data = visitor_data or self.__get_visitor_not_sent_data(visitor_code)
        lines = cast(List[PostBodyLine], data)
        if (experiment_id is not None) and (variation_id is not None):
            lines.append(ExperimentEvent(experiment_id, variation_id))
        elif len(lines) == 0:
            lines.append(ActivityEvent())
        service: DataService = self.network_manager.get_service(DataService)
        coro = service.send_tracking_data(visitor_code, lines, user_agent, sync=self.__is_sync_mode())

        async def call() -> Response:
            response = await coro
            if response.success:
                for data_item in data:
                    data_item.sent = True
            return response

        self.__run_call(call())

    def __get_all_not_sent_data(self) -> Dict[str, List[Data]]:
        """Get not sent data for all visitor codes"""
        return {
            visitor_code: [d for d in data_list if not d.sent]
            for visitor_code, data_list in self.data.items()
            if data_list
        }

    def __get_visitor_not_sent_data(self, visitor_code: str) -> List[Data]:
        """
        :param visitor_code: Optional[str]
        :return: Dict[str, List[Type[Data]]]
        """
        try:
            return [d for d in self.data[visitor_code] if not d.sent]
        except (KeyError, IndexError) as ex:
            self.logger.error(ex)
            return []

    def __check_site_code_enable(self, exp_or_ff: Dict[str, Any]):
        """
        raise SiteCodeDisabled if site of Experiment or Feature Flag is disabled
        :param exp_or_ff:
        :type exp_or_ff: Dict[str, Any]
        """
        if exp_or_ff.get("siteEnabled") is not True:
            raise SiteCodeDisabled(self.site_code)

    def _setup_client_configuration(  # noqa: C901
        self,
        configuration_path: str,
        configuration_object: Optional[KameleoonClientConfiguration],
    ):
        """
        helper method to parse client configuration and setup client
        """
        config_yml = configuration_path or DEFAULT_CONFIGURATION_PATH
        self.config = config(config_yml, configuration_object)
        try:
            target_environment = self.config["target_environment"]
        except KeyError:
            target_environment = "prod"
        if target_environment == "test":
            self.tracking_base_url = "https://api-ssx.kameleoon.net/"
        else:
            self.tracking_base_url = "https://api-ssx.kameleoon.com/"
        try:
            self.environment = self.config["environment"]
        except KeyError:
            self.environment = "production"
        try:
            self.multi_threading = self.config["multi_threading"]
        except KeyError:
            self.multi_threading = False
        try:
            actions_configuration_refresh_interval = int(self.config["actions_configuration_refresh_interval"])
            self.actions_configuration_refresh_interval = actions_configuration_refresh_interval * 60
        except KeyError:
            self.actions_configuration_refresh_interval = DEFAULT_CONFIGURATION_UPDATE_INTERVAL
        try:
            self.default_timeout = self.config["default_timeout"]
        except KeyError:
            self.default_timeout = DEFAULT_TIMEOUT_MILLISECONDS
        try:
            self.visitor_data_maximum_size = int(self.config["visitor_data_maximum_size"])
        except KeyError:
            self.visitor_data_maximum_size = DEFAULT_VISITOR_DATA_MAXIMUM_SIZE

    def _add_user_agent(self, visitor_code: str, user_agent: UserAgent):
        if len(self.user_agent_data) > USER_AGENT_MAX_COUNT:
            self.user_agent_data = {}
        self.user_agent_data[visitor_code] = user_agent

    def _get_user_agent(self, visitor_code: str) -> Optional[UserAgent]:
        return self.user_agent_data.get(visitor_code)

    def __get_feature_variation_key(self, visitor_code: str, feature_key: str) -> Tuple[FeatureFlag, str]:
        """
        helper method for getting variation key for feature flag
        """
        check_visitor_code(visitor_code)
        feature_flag = self.__find_feature_flag(feature_key)
        (variation, rule) = self.__calculate_variation_rule_for_feature(visitor_code, feature_flag)
        variation_key = self.__calculate_variation_key(variation, rule, feature_flag)
        experiment_id = rule.experiment_id if rule is not None else None
        variation_id = variation.variation_id if variation else None
        self.__send_tracking_request(visitor_code, experiment_id, variation_id)
        self.__save_variation(visitor_code, experiment_id, variation_id)
        return (feature_flag, variation_key)

    def __calculate_variation_rule_for_feature(
        self, visitor_code: str, feature_flag: FeatureFlag
    ) -> Tuple[Optional[VariationByExposition], Optional[Rule]]:
        """helper method for calculate variation key for feature flag"""
        for rule in feature_flag.rules:
            # check if visitor is targeted for rule, else next rule
            if not self.__check_targeting_id_object(visitor_code, feature_flag.id_, rule):
                continue
            # uses for rule exposition
            hash_rule = obtain_hash_double_rule(visitor_code, rule.id_, rule.respool_time)
            # check main expostion for rule with hashRule
            if hash_rule <= rule.exposition:
                if rule.is_targeted_delivery and len(rule.variation_by_exposition) > 0:
                    return (rule.variation_by_exposition[0], rule)

                # uses for variation's expositions
                hash_variation = obtain_hash_double_rule(visitor_code, rule.experiment_id, rule.respool_time)
                # get variation with hash_variation
                variation = rule.get_variation(hash_variation)
                if variation:
                    return (variation, rule)
            elif rule.is_targeted_delivery:
                break
        return (None, None)

    def __calculate_variation_key(
        self,
        var_by_exp: Optional[VariationByExposition],
        rule: Optional[Rule],
        feature_flag: FeatureFlag,
    ) -> str:
        if var_by_exp:
            return var_by_exp.variation_key
        if rule and rule.is_experimentation:
            return Variation.Type.OFF.value
        return feature_flag.default_variation_key

    def __find_feature_flag(self, feature_key: str) -> FeatureFlag:
        """
        helper method for getting the feature flag v2 from the list
        """
        feature_flag = next(
            (ff for ff in self._feature_flags if ff.feature_key == feature_key),
            None,
        )
        if feature_flag is None:
            raise FeatureConfigurationNotFound(feature_key)
        return feature_flag

    def __save_variation(
        self,
        visitor_code: str,
        experiment_id: Optional[int],
        variation_id: Optional[int],
    ):
        """
        helper method for saving variations (to variation_storage and hybrid_manager)
        """
        if experiment_id is not None and variation_id is not None:
            self.variation_storage.update_variation(
                visitor_code,
                experiment_id,
                variation_id,
            )
            self.hybrid_manager.add_tracking_variation(visitor_code, experiment_id, variation_id)
