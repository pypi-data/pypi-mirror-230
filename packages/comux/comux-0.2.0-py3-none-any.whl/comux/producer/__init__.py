from kafka import KafkaProducer
from kafka.producer.future import FutureRecordMetadata, RecordMetadata
from kafka.errors import NoBrokersAvailable, KafkaError
import ctypes
import sys
from typing import List, Dict, Any
import threading
from queue import Queue, Empty, Full
import os

try:
  from ..logger import LOG_LEVELS
except:
  from logger import LOG_LEVELS


class Producer(KafkaProducer):
  __offsets: Dict[str, int]
  __log_level: str

  def __init__(self, bootstrap_servers: List[str], strict_on_fail: bool = True, over_write: bool = False, log_level: str = "ERROR", **kwargs) -> None:
    self.__offsets = {}
    self.__log_level = log_level
    try:
      kw = self.prepare_kwargs(over_write, **kwargs)
      self.connect(bootstrap_servers, kw)
    except NoBrokersAvailable:
      if self.__log_level >= LOG_LEVELS["ERROR"]:
        print("✘ Couldn't connect to ", bootstrap_servers)
      if strict_on_fail:
        sys.exit(1)

  def produce(self, topic: Any, value: Any, key: Any | None = None, headers: Any | None = None, partition: Any | None = None) -> int | None:
    future: FutureRecordMetadata = self.send(topic, value, key, headers,
                                             partition)
    try:
      record_metadata: RecordMetadata = future.get(timeout=10)
      # Successful result returns assigned partition and offset
      self.__offsets.update({topic: record_metadata.offset})
      return record_metadata.offset
    except KafkaError:
      return None
###############  DO NOT TOUCH  ####################################

  def prepare_kwargs(self, over_write: bool, **kwargs):
    defaults = {
      "request_timeout_ms": 10500,
      "acks": "all",
      # "session_timeout_ms": 5000,
      "client_id": "some_id",
      "security_protocol": "PLAINTEXT",
      "ssl_cafile": None,
      "ssl_certfile": None,
      "ssl_keyfile": None,
      "ssl_password": None,
    }
    if not over_write:
      kwargs.update(defaults)
    if over_write:
      for key in defaults.keys():
        if key not in kwargs.keys():
          kwargs.setdefault(key, defaults[key])
    return kwargs

  def connect(self, bootstrap_servers, kwargs: dict):
    kwargs.setdefault("bootstrap_servers", bootstrap_servers)
    super(Producer, self).__init__(**kwargs)
    if self.__log_level >= LOG_LEVELS["ANY"]:
      print("✔ producer connected")
###############  Properties  ####################################

  def offset(self, topic: str):
    try:
      return self.__offsets[topic]
    except KeyError:
      return None
