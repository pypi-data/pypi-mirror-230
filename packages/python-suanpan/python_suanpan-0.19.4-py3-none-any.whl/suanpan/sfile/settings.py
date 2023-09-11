import pickle
import pathlib
from suanpan.storage import storage
from suanpan.log import logger


class Settings(object):
    def __init__(self):
        self._data = None
        self._key = None
        self._local = None

    def __setattr__(self, key, value):
        if key in ['_data', '_key', '_local']:
            super(Settings, self).__setattr__(key, value)
        else:
            if self._data is None:
                self._load()

            self._data[key] = value
            self._save()

    def __setitem__(self, key, value):
        if self._data is None:
            self._load()

        self._data[key] = value
        self._save()

    def __getitem__(self, item):
        if self._data is None:
            self._load()

        return self._data.get(item)

    def __getattribute__(self, item):
        try:
            return super(Settings, self).__getattribute__(item)
        except AttributeError:
            if self._data is None:
                self._load()

            return self._data.get(item)

    def _load(self):
        self._key = storage.getKeyInNodeConfigsStore('settings.pickle')
        self._local = storage.getPathInTempStore('settings.pickle')
        pathlib.Path(storage.tempStore).mkdir(parents=True, exist_ok=True)

        try:
            storage.downloadFile(self._key, self._local)
            with open(self._local, 'rb') as f:
                self._data = pickle.load(f)
        except Exception as e:
            logger.debug(f'failed to load settings: {e}')
            self._data = {}

    def _save(self):
        with open(self._local, 'wb') as f:
            pickle.dump(self._data, f)
        storage.uploadFile(self._key, self._local)
