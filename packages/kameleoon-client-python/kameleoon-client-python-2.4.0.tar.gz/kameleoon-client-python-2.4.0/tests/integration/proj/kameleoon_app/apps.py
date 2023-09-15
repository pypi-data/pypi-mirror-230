import sys
import os
from django.apps import AppConfig

ROOT_DIR = os.path.join(
    os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    )
)
sys.path.append(ROOT_DIR)

from tests_defaults import SITE_CODE
from kameleoon import KameleoonClient

from tests.test_network_manager_factory import TestNetworkManagerFactory


class KameleoonConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "kameleoon_app"

    def ready(self):
        configuration_path = os.path.join(ROOT_DIR, "tests", "resources", "config.yml")
        KameleoonClient._network_manager_factory = TestNetworkManagerFactory()
        self.kameleoon_client = KameleoonClient(
            SITE_CODE, configuration_path=configuration_path
        )
