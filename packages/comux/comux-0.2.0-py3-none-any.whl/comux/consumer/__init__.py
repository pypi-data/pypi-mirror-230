from kafka import KafkaConsumer, TopicPartition
from kafka.errors import NoBrokersAvailable, UnsupportedVersionError
from kafka.consumer.fetcher import ConsumerRecord
import ctypes
import sys
from typing import List, Dict
import threading
from queue import Queue, Empty, Full
import os

try:
  from ..logger import LOG_LEVELS
except:
  from logger import LOG_LEVELS

class Consumer(KafkaConsumer):
  topic: str
  max_offset_diff: int
  __log_level: str
  
  def __init__(self, topic: str, bootstrap_servers: List[str], max_offset_diff: int = 20, strict_on_fail: bool = True, over_write: bool = False, log_level: str = "ERROR", **kwargs) -> None:
    self.topic = topic
    self.__log_level = log_level
    self.max_offset_diff = max_offset_diff
    try:
      kw = self.prepare_kwargs(over_write, **kwargs)
      self.connect(bootstrap_servers, kw)
      self.sub()

    except NoBrokersAvailable:
      if self.__log_level >= LOG_LEVELS["ERROR"]:
        print("✘ Couldn't connect to ", bootstrap_servers)
      if strict_on_fail:
        sys.exit(1)
    except AssertionError as e:
      if self.__log_level >= LOG_LEVELS["ERROR"]:
        print(e)
        print("✘ Provide camera_id as topic.")
      sys.exit(1)

  def sub(self) -> None:
    self.assign([TopicPartition(self.topic, 0)])
    self.poll()
    self.seek_to_end()
    return

  def __iter__(self):
    if self.__log_level >= LOG_LEVELS["DEBUG"]:
      print("✔ consumer", self.topic, "listening", sep=" ")
    self.seek_to_end()
    return super().__iter__()

  def __next__(self):
    try:
      msg = super().__next__()
      self.check_fall_behind(msg.offset)
      return msg
    except (OSError, SystemExit) as _:
      if self.__log_level >= LOG_LEVELS["DEBUG"]:
        print("✔ Consumer ", self.topic, " has stopped...")
      return

###############  DO NOT TOUCH  ####################################

  def prepare_kwargs(self, over_write: bool, **kwargs):
    defaults = {
      "request_timeout_ms": 10500,
      # 'max_poll_interval_ms': 10000,
      # "session_timeout_ms": 5000,
      "client_id": "some_id",
      "group_id": "some_id",
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

  def connect(self, bootstrap_servers, kwargs):
    kwargs.setdefault("bootstrap_servers", bootstrap_servers)
    super(Consumer, self).__init__(**kwargs)
    if self.__log_level >= LOG_LEVELS["DEBUG"]:
      print("✔ consumer", self.topic, "connected", sep=" ")

  def check_fall_behind(self, offset: int):
    if offset + self.max_offset_diff < self.topic_last_offset:
      self.seek_to_end()
    return


###############  Properties  ####################################

  @property
  def offset(self):
    return self.position(TopicPartition(self.topic, 0))

  @property
  def topic_last_offset(self) -> int | None:
    try:
      offsets = self.end_offsets([TopicPartition(self.topic, 0)])
      return list(offsets.values())[0]
    except UnsupportedVersionError:
      if self.__log_level >= LOG_LEVELS["ERROR"]:
        print("✘ Broker doesn't support getting last offset... returning None")
      return None
