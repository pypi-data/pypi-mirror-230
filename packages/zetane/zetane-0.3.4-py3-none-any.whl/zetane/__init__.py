from .protector import Protector, Connection
from .monitor import Monitor
import os

""" Settings """
default_client = None
default_connection = None
monitor_proxy = None

# called on import
api_key = os.getenv("ZETANE_API_KEY", None)
address = os.getenv("ZETANE_ADDRESS", "https://protector-api-1.zetane.com/")

def config(*args, **kwargs):
  return _proxy('config', *args, **kwargs)

def upload_dataset(*args, **kwargs):
  return _proxy('upload_dataset', *args, **kwargs)

def upload_model(*args, **kwargs):
  return _proxy('upload_model', *args, **kwargs)

def get_entries(*args, **kwargs):
  return _proxy('get_entries', *args, **kwargs)

def get_orgs_and_projects(*args, **kwargs):
  return _proxy('get_orgs_and_projects', *args, **kwargs)

def report(*args, **kwargs):
  return _proxy('report', *args, **kwargs)

def get_report_status(*args, **kwargs):
  return _proxy('get_report_status', *args, **kwargs)

def create_project(*args, **kwargs):
  return _proxy('create_project', *args, **kwargs)

def delete_project(*args, **kwargs):
  return _proxy('delete_project', *args, **kwargs)

def log(*args, **kwargs):
  return _monitor_proxy('log', *args, **kwargs)

def session(*args, **kwargs):
  return _monitor_proxy('session', *args, **kwargs)

def get_connection(*args, **kwargs):
  global default_connection

  if not default_connection:
    default_connection = _connection_factory(*args, **kwargs)

  return default_connection

def _proxy(method, *args, **kwargs):
  """Create an analytics client if one doesn't exist and send to it."""
  global default_client
  global default_connection

  if not default_connection:
    default_connection = _connection_factory(*args, **kwargs)

  if not default_client:
    default_client = Protector(default_connection)

  fn = getattr(default_client, method)
  return fn(*args, **kwargs)

def _monitor_proxy(method, *args, **kwargs):
  """Create an analytics client if one doesn't exist and send to it."""
  global monitor_proxy
  global default_connection

  if not default_connection:
    default_connection = _connection_factory(*args, **kwargs)

  if not monitor_proxy:
    monitor_proxy = Monitor(default_connection)

  fn = getattr(monitor_proxy, method)
  return fn(*args, **kwargs)

def _connection_factory(*args, **kwargs):
  if api_key is not None:
    conn = Connection(api_key, address=address)

  elif 'api_key' in kwargs:
    conn = Connection(kwargs['api_key'], kwargs.get("address", "https://protector-api-1.zetane.com"))

  elif len(args) > 0:
    conn = Connection(args[0], args[1])

  else:
      print("** Please set your api key with zetane.config(api_key=\"your_api_key\") before calling other methods. **\n")

      raise TypeError('Failed to authenticate API key, no API key provided.')

  return conn

