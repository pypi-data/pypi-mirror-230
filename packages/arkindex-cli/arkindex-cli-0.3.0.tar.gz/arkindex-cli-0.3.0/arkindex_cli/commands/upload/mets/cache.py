# -*- coding: utf-8 -*-
import json
import logging

logger = logging.getLogger(__name__)


class Cache(object):
    _instance = None  # singleton

    def __init__(self, path):
        assert Cache._instance is None, "Already called"

        self.path = path
        if path.exists():
            self.data = json.loads(self.path.read_text())
            logger.info(f"Loading cache from {self.path}")
        else:
            self.data = {}
            logger.info("Empty cache")

        Cache._instance = self

    def __del__(self):
        logger.info(f"Saving cache to {self.path}")
        self.path.write_text(
            json.dumps(self.data, default=str, indent=4, sort_keys=True)
        )

    @staticmethod
    def get(key):
        return Cache._instance.data.get(key)

    @staticmethod
    def set(key, value):
        Cache._instance.data[key] = value
