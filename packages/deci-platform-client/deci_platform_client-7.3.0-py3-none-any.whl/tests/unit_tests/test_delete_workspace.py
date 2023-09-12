from unittest.mock import MagicMock, patch
from uuid import uuid4

from deci_platform_client.apis.tags.platform_api import PlatformApi

from .base_test_case import BaseTestCase

get_delete_workspace_mock = patch.object(PlatformApi, "delete_workspace")


class TestDeleteWorkspace(BaseTestCase):
    @get_delete_workspace_mock
    def test_delete_workspace_string(self, delete_workspace_mock: MagicMock) -> None:
        workspace_id = str(uuid4())
        self.assertIsNone(self.client.delete_workspace(workspace_id))
        delete_workspace_mock.assert_called_once_with(path_params={"id": workspace_id})

    @get_delete_workspace_mock
    def test_delete_workspace_uuid(self, delete_workspace_mock: MagicMock) -> None:
        workspace_id = uuid4()
        self.assertIsNone(self.client.delete_workspace(workspace_id))
        delete_workspace_mock.assert_called_once_with(path_params={"id": workspace_id})
