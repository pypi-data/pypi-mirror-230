import os
import shutil
import time
from unittest import TestCase

from openmodule.config import override_settings, settings
from openmodule.models.base import OpenModuleModel
from openmodule.utils.databox import upload
from openmodule_test.rpc import MockRPCClient


@override_settings(DATABOX_UPLOAD_DIR="/tmp/upload")
class DataboxTest(TestCase):
    def setUp(self):
        super().setUp()
        try:
            shutil.rmtree(settings.DATABOX_UPLOAD_DIR)
        except Exception:
            pass
        os.makedirs(settings.DATABOX_UPLOAD_DIR)
        self.rpc_client = MockRPCClient(immediate_callbacks={("databox", "trigger_upload"): self.trigger_upload})
        self.trigger_called = 0

    def trigger_upload(self, request: OpenModuleModel, _) -> OpenModuleModel:
        self.trigger_called += 1
        return OpenModuleModel()

    def wait_for_trigger(self) -> bool:
        for i in range(10):
            if self.trigger_called > 0:
                return True
            time.sleep(0.1)
        return False

    def test_upload(self):
        with open("/tmp/asdf.txt", "w") as f:
            f.write("asdf")
        upload("/tmp/asdf.txt", "/enforcement/test/asdf.txt", rpc_client=self.rpc_client)
        self.assertTrue(self.wait_for_trigger())
        self.assertIn("enforcement", os.listdir(settings.DATABOX_UPLOAD_DIR))
        self.assertIn("test", os.listdir(os.path.join(settings.DATABOX_UPLOAD_DIR, "enforcement")))
        self.assertIn("asdf.txt", os.listdir(os.path.join(settings.DATABOX_UPLOAD_DIR, "enforcement/test")))

    def test_upload_dst_is_dir(self):
        with open("/tmp/asdf.txt", "w") as f:
            f.write("asdf")
        upload("/tmp/asdf.txt", "/enforcement/test/", rpc_client=self.rpc_client)
        self.assertTrue(self.wait_for_trigger())
        self.assertIn("enforcement", os.listdir(settings.DATABOX_UPLOAD_DIR))
        self.assertIn("test", os.listdir(os.path.join(settings.DATABOX_UPLOAD_DIR, "enforcement")))
        self.assertIn("asdf.txt", os.listdir(os.path.join(settings.DATABOX_UPLOAD_DIR, "enforcement/test")))

    def test_upload_directory(self):
        if os.path.exists("/tmp/asdf"):
            shutil.rmtree("/tmp/asdf")
        os.makedirs("/tmp/asdf")
        with open("/tmp/asdf/asdf.txt", "w") as f:
            f.write("asdf")
        with self.assertRaises(AssertionError) as e:
            upload("/tmp/asdf", "/enforcement/test/asdf", rpc_client=self.rpc_client)
        self.assertIn("src must be a file and no directory", str(e.exception))
