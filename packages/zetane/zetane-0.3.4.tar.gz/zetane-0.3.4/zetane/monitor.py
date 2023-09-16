import zipfile, io, json, os
import numpy as np
import random
from threading import Lock
import functools
import datetime
from pathlib import Path
import linecache
import pyarrow as pa
import pyarrow.dataset as ds

THIS_DIR = Path(__file__).absolute().parent

class Session:
    def __init__(self, id, schema=None):
        self.id = id
        self.name = id.split("-")[2]
        self.timestamp = id.split("-")[1]
        self.schema = None
        self.value_dict = dict()

        if schema:
            self.schema = schema
            cache_path = os.path.join(".zcache", f"{self.id}.arrow")
            os.makedirs(".zcache", exist_ok=True)
            self.sink = pa.OSFile(cache_path, 'wb')
            self.writer = pa.ipc.new_file(self.sink, self.schema)

    # object destructor since we are being risky with our file handles
    def __del__(self):
        self.close_session()

    def close_session(self):
        self.writer.close()
        self.sink.close()

    def append(self, **kwargs):
        arrays = list()
        for arg, value in kwargs.items():
            try:
                field = self.schema.field(arg)
                array = pa.array(value, type=field.type)
            except pa.ArrowInvalid as e:
                field_name = field.name
                raise ValueError(f"Failed to convert field {field_name} to {field.type}")
            arrays.append(array)

        batch = pa.record_batch(arrays, self.schema)
        print("Writing ", batch)
        self.writer.write(batch)

class Monitor():
    def __init__(self, connection, compression=zipfile.ZIP_DEFLATED):
        self.connection = connection
        self.memory = None
        self.compression = compression
        self._reset()

        self.session_data = {}
        self._session_locks = {}
        self._active_session_key = None

    def __enter__(self):
        return self

    def close(self):
        self.memory.close()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def _reset(self):
        self.names = set()
        self.header = {"inputs": [], "outputs": []}
        if self.memory is not None:
            self.memory.close()
        self.memory = io.BytesIO(b'')

    def _add_array(self, is_input, name, numpy_array, named_array):
        if not isinstance(numpy_array, np.ndarray):
            raise Exception("Expected a numpy array. Got: " + type(numpy_array))

        instance = {"name": name,
                    "shape": numpy_array.shape,
                    "type": numpy_array.dtype.str,
                    "named": False}

        if named_array is not None:
            if not isinstance(named_array, np.ndarray):
                raise Exception("Expected a numpy array. Got: " + type(named_array))
            if named_array.dtype.str[1] != "U":
                raise Exception("Expected np._object. Got: " + named_array.dtype)
            if len(numpy_array.shape) != named_array.size:
                if len(numpy_array.shape) != len(named_array.shape):
                    raise Exception("Invalid named array")
                for i in range(len(numpy_array.shape)):
                    if numpy_array.shape[i] % named_array.shape[i] != 0:
                        raise Exception("Invalid named array")
            instance["named"] = True

        if name not in self.names:
            if is_input:
                self.header["inputs"].append(instance)
            else:
                self.header["outputs"].append(instance)
            self.names.add(name)
        else:
            raise Exception("The array \'" + name + "\' already exists")


        with zipfile.ZipFile(self.memory, 'a', self.compression) as file:
            file.writestr(name, numpy_array.tobytes())
            if named_array is not None:
                file.writestr(name + "_named", named_array.tobytes())

    def generate_key(self):
        return f"session-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}-{self.gen_words()}"

    def gen_words(self):
        filename = 'utils/eff-short.txt'
        filepath = THIS_DIR / filename
        line_count = len(linecache.getlines(str(filepath)))
        word_count = 4
        words = list()

        for i in range(word_count):
            rand = random.randint(0, line_count)
            word = linecache.getline(str(filepath), rand)
            words.append(word.rstrip())

        return "-".join(words)

    def get_session_lock(self, key):
        if key not in self._session_locks:
            self._session_locks[key] = Lock()
        return self._session_locks[key]

    def get_current_session_key(self):
        if self._active_session_key is not None:
            return self._active_session_key
        else:
            return self.open_session()

    def open_session(self, schema=None):
        key = self.generate_key()
        self._active_session_key = key
        self.session_data[key] = Session(key, schema)
        return key

    def close_session(self, key):
        print(f"Closing session {key}")
        del self.session_data[key]
        self._active_session_key = None

    def session(self, schema=None):
        def wrap(func):
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                key = self.open_session(schema)
                try:
                    return func(*args, **kwargs)
                finally:
                    self.close_session(key)
            return wrapper
        return wrap

    def log(self, *args, **kwargs):
        key = self.get_current_session_key()
        if key is None:
            raise Exception("Not in session")

        lock = self.get_session_lock(key)
        with lock:
            self.session_data[key].append(*args, **kwargs)

    def add_input(self, name, numpy_array, named_array=None):
        self.connection.auth_check()
        self._add_array(True, name, numpy_array, named_array)

    def add_output(self, name, numpy_array, named_array=None):
        self.connection.auth_check()
        self._add_array(False, name, numpy_array, named_array)

    def send(self, name, org=None, project=None):
        self.connection.auth_check()
        with zipfile.ZipFile(self.memory, 'a', self.compression) as file:
            file.writestr("header.json", json.dumps(self.header))

        self.connection.config(project=project, org=org)

        if name[-4:] != ".zip":
            zip_name = name + ".zip"
        else:
            zip_name = name

        body = {"filename": zip_name, "file_size": self.memory.getbuffer().nbytes, "metadata": json.dumps("")}
        newObj = {
            'upload_status': {'status': "Pending"},
            'dataset_type': 'classification',
        }

        body = {**body, **newObj}
        post_url = self.connection.api_url_builder(self.connection.org, self.connection.project, "tensor")
        res = self.connection.req_handle(post_url, "post", body)

        dataset_id = res.json()["id"]
        res = self.connection.multipart_upload("tensors", dataset_id, self.memory)
        res = self.connection.confirm_upload("tensors", dataset_id)

        print("Completed")
        return res
