import threading, os, unittest
import zetane
from .test_base import BaseTestCase, SCRIPT_DIR, ZETANE_DIR
import pyarrow as pa

class TestMonitor(BaseTestCase):
  def tearDown(self) -> None:
    print("teardown..")
    cache_dir = os.path.join(ZETANE_DIR, ".zcache")
    for file in os.listdir(cache_dir):
      print(file)
      if file.endswith(".arrow") or file.endswith(".parquet"):
        file_path = os.path.join(cache_dir, file)
        os.remove(file_path)
        print(f"Deleted {file_path}")
    super().tearDown()

  def test_log_data(self):
    schema = pa.schema([pa.field('text', pa.string())])

    @zetane.session(schema=schema)
    def process():
      zetane.log(text=["Event 1"])
      zetane.log(text=["Event 2"])
      key = list(zetane.monitor_proxy.session_data.keys())[0]
      self.assertEqual(zetane.monitor_proxy.session_data[key], ["Event 1", "Event 2"])

    process()

  def test_multithread(self):
    schema = pa.schema([pa.field('text', pa.string())])
    @zetane.session(schema=schema)
    def process():
      thread = threading.Thread(target=log_thread)
      thread.start()
      zetane.log(text=["Main Thread"])
      thread.join()

      key = list(zetane.monitor_proxy.session_data.keys())[0]
      # note misleadingly named method that used to be called "assertItemsEqual",
      # which is what this actually does
      self.assertCountEqual(zetane.monitor_proxy.session_data[key], ["Main Thread", "Child Thread"])

    def log_thread():
      zetane.monitor_proxy.log(text=["Child Thread"])

    process()


if __name__ == '__main__':
  unittest.main()
