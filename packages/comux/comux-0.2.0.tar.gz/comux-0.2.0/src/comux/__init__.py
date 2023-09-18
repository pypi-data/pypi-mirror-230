# Here is the package

from kafka.consumer.fetcher import ConsumerRecord
from time import time, sleep
from typing import List, Dict, Callable, Any, Tuple, Iterable
import threading
from queue import Queue
import numpy as np
from collections import deque


try:
  from .consumer import Consumer
  from .structures import LimitedQueue
  from .db import retrieve_cam_ids
  from .ctx import Decoder
  from .producer import Producer
  from .logger import LOG_LEVELS
except ImportError as e:
  from consumer import Consumer
  from structures import LimitedQueue
  from db import retrieve_cam_ids
  from ctx import Decoder
  from producer import Producer
  from logger import LOG_LEVELS

# The consumer is not thread safe and should not be shared across threads.
# The consumer will transparently handle the failure of servers in the Kafka cluster.


class Comux:
  client_name: str
  maxlen: int
  cam_ids: List[str]
  bootstrap_servers: List[str]
  consumers: Dict[str, Consumer] = dict()
  decoders: Dict[str, Decoder] = dict()
  producer: Producer
  threads: Dict[str, threading.Thread] = dict()
  buffers: Dict[str, LimitedQueue] = dict()  # Dict[str, Dict[int, np.ndarray]]

  def __init__(self, client_name: str, db_url: str, db_database: str, db_collections: Dict[str, str],
               maxlen: int = 20, consume_schema: str = "raw_:cam_id", produce_schema: str = "stream_:cam_id", log_level: str = "ANY") -> None:
    """Class to manage cameras and their consumer. It doesn't connect consumers to the server or
       start consuming.
    Args:
        cam_ids (List[str]): list of camera ids being used also in topic names instead of `:cam_id`.
        consume_schema (str): a string consist of `:cam_id`.
        produce_schema (str): a string consist of `:cam_id`.
    """
    self.client_name = client_name
    self.maxlen = maxlen
    self.cam_ids = retrieve_cam_ids(
      client_name=client_name, url=db_url, database=db_database, collections=db_collections)

    if consume_schema.find(":cam_id") < 0 or produce_schema.find(":cam_id") < 0:
      raise ValueError(
        "consume_schema and produce_schema must contain `:cam_id`")
    self.consume_schema = consume_schema
    self.produce_schema = produce_schema
    self.log_level = LOG_LEVELS[log_level]
    return

  def setup_producer(self, bootstrap_servers: List[str], strict_on_fail: bool = True, over_write: bool = False, **kwargs: Any):
    self.producer = Producer(
      bootstrap_servers, strict_on_fail, over_write, self.log_level, **kwargs)
    return self.producer

  def _decoder(self, cam_id: str, rate: int = 10, W: int = 1920, H: int = 1080, de_codec: str = "h264", pix_fmt: str = "yuv420p"):
    self.decoders.update(
      {cam_id: Decoder(cam_id, self.maxlen, rate, W, H, de_codec, pix_fmt, self.log_level)})
    return cam_id

  def connect_consumer(self, cam_id: str, bootstrap_servers: List[str], replace: bool = True, max_offset_diff: int = 20, strict_on_fail: bool = True, over_write: bool = False, **kwargs):
    """creates a consumer and connect it to server
    Args:
        cam_id (str): camera id used as a topic
        bootstrap_servers (List[str]): Kafka bootstrap servers to connect for cameras (stream broker).
        replace (bool): replaces the old consumers with new one in case of duplication, otherwise throughs an error
        max_offset_diff (int, optional): Maximum allowed offset to fall behind, when reached consumer
          automatically moves to the end. Defaults to 5.
        strict_on_fail (bool, optional): if set to True, consumers are allowed to raise Exceptions in case of
          failuire. Defaults to True.
        over_write (bool, optional): over write default Kafka config.
        **kwargs: key value configs passed to kafka consumer

    Raises:
        NameError: if consumer exists and `overwrite` argument is False.

    Returns:
        bool | Consumer: returns the consumer. False if not succeeded.
    """
    if cam_id in self.consumers.keys():
      if not replace:
        raise NameError(
          "A consumer for camera id {} already exists, surpass this with replace=True".format(cam_id))
      else:
        if not self.kill(cam_id):
          return False
        if self.log_level >= LOG_LEVELS["DEBUG"]:
          print("❗consumer", cam_id, "is being replaced", sep=" ")
    consumer = Consumer(self.get_topic_from_cam_id(cam_id, "consume"), bootstrap_servers, max_offset_diff,
                        strict_on_fail, over_write, self.log_level, **kwargs)
    self.consumers.update({cam_id: consumer})
    self.buffers.update({cam_id: LimitedQueue(maxlen=self.maxlen)})
    return consumer

  def listen(self, cam_id: str):
    """start data flow of [consumer => decoder => buffer] on video stream of camera cam_id
       data being stored in buffer is a tuple including cam_id, index, array.

    Args:
        cam_id (str): camera id being streamed

    Returns:
        threading.Thread | bool: returns the thread itself. False if not succeeded.
    """
    # try:
    consumer = self.consumers[cam_id]
    decoder = self.decoders[cam_id]
    for msg in consumer:
      chunk: bytes = msg.value
      array = decoder.decode(chunk)
      self.buffers[cam_id].append((cam_id, decoder.index, array))
    # except Exception as e:
    #   if self.log_level >= LOG_LEVELS["ERROR"]:
    #     print("Error", e)
    #   return False

  def read(self, cam_id: str, timeout: float = 10):
    return self.buffers[cam_id].pop(timeout)
    # try:
    # except Exception as e:
    #   print(e)
    #   return (cam_id, None, None)

    # consumer = self.consumers[cam_id]
    # decoder = self.decoders[cam_id]
    # msg = self.__consume(consumer, timeout)
    # if msg == None:
    #   return cam_id, None, None
    # chunk = msg.value
    # return cam_id, *self.__decode(decoder, chunk)

  def send(self, cam_id, indx, headers: Dict[str, str | dict | list | bytes] | None = None):
    decoder = self.decoders[cam_id]
    send_chunk = decoder.get(indx)
    if headers is not None:
      for key, val in enumerate(headers):
        headers.update({key: self.encode_header(val)})
    # send via producer
    return self.producer.produce(self.get_topic_from_cam_id(
      cam_id, "produce"), send_chunk, b'', headers, 0)

  def kill(self, cam_id: str):
    """kills a consumer and its thread. pops them out of pools.

    Args:
        cam_id (str): camera id of that consumer and thread

    Returns:
        bool: True if succeed else False. None if camera id doesn't exist.
    """
    try:
      if cam_id in self.consumers.keys():
        consumer = self.consumers[cam_id]
        thread = self.threads[cam_id]
        consumer.close()
        sleep(0.1)  # wait for the thread to die
        if not thread.is_alive(): return True
        return False
      else: return None
    except Exception as e:
      if self.log_level >= LOG_LEVELS["ERROR"]:
        print("Error", e)
      return False
###############  Decorators  ####################################

  def __async_cam_deco(self, func, *args, **kwargs):
    res = []
    threads: List[threading.Thread] = []
    for cam_id in self.cam_ids:
      def f(cam_id, *args, **kwargs): return res.append(func(cam_id, *args, **kwargs))
      thread = threading.Thread(target=f, args=(cam_id, *args), kwargs=kwargs)
      threads.append(thread)
      thread.start()
    [thread.join() for thread in threads]
    del threads
    del f
    return res

  def __cam_deco(self, func, *args, **kwargs):
    res = []
    for cam_id in self.cam_ids:
      res.append(func(cam_id, *args, **kwargs))
    return res

  def __forever_cam_deco(self, func, *args, **kwargs):
    for cam_id in self.cam_ids:
      thread = threading.Thread(
        target=func, args=(cam_id, *args), kwargs=kwargs)
      self.threads.update({cam_id: thread})
      thread.start()
    return True

  def __custom_deco(self, iter: List[str], func, *args, **kwargs):
    res = []
    for item in iter:
      res.append(func(item, *args, **kwargs))
    return res

  def __forever_custom_deco(self, iter: List[str], func, *args, **kwargs):
    for item in iter:
      thread = threading.Thread(
        target=func, args=(item, *args), kwargs=kwargs)
      self.threads.update({item: thread})
      thread.start()
    return True
###############  Map Decos  ######################################

  def setup_consumers(self, bootstrap_servers: List[str], replace: bool = True, max_offset_diff: int = 20, strict_on_fail: bool = True, over_write: bool = False, **kwargs):
    self.consumer_bootstrap_servers = bootstrap_servers
    return self.__cam_deco(self.connect_consumer, bootstrap_servers=bootstrap_servers, replace=replace, max_offset_diff=max_offset_diff, strict_on_fail=strict_on_fail, over_write=over_write, **kwargs)

  def start(self):
    return self.__forever_cam_deco(self.listen)

  def setup_decoders(self, rate: int = 10, W: int = 1920, H: int = 1080, de_codec: str = "h264", pix_fmt: str = "yuv420p"):
    return self.__cam_deco(self._decoder, rate=rate, W=W, H=H, de_codec=de_codec, pix_fmt=pix_fmt)

  def get_batch(self, timeout: float = None):
    return self.__cam_deco(self.read, timeout=timeout)  # TODO: async

  # indexes: List[int], headers: List[Dict[str, str | dict | list]]
  def send_batch(self, arrays: List[Tuple[str | int | str | dict | list]]):
    raise NotImplementedError  # TODO
###############    Utils    ######################################

  def get_topic_from_cam_id(self, cam_id: str, mode: str) -> str:
    match mode:
      case "consume":
        return self.consume_schema.replace(":cam_id", cam_id)
      case "produce":
        return self.produce_schema.replace(":cam_id", cam_id)

  def get_cam_id_from_topic(self, topic: str, mode: str):
    match mode:
      case "consume":
        schema_list = self.consume_schema.split(":cam_id")
      case "produce":
        schema_list = self.produce_schema.split(":cam_id")
    for r in schema_list:
      topic = topic.replace(r, "")
    return topic

  def encode_header(self, header: str | dict | list | bytes):
    if isinstance(header, bytes):
      return header
    raise NotImplementedError(
      "At this moment, we can't encode headers other than bytesType!")

###############    Control actions    ############################
  def create(self, cam_id: str, replace: bool = True, max_offset_diff: int = 5, strict_on_fail: bool = True, over_write: bool = False, **kwargs: Any):
    self.connect_consumer(cam_id, self.consumer_bootstrap_servers, replace,max_offset_diff,strict_on_fail,over_write,**kwargs)
    self._decoder(cam_id)
    thread = threading.Thread(target=self.listen, args=([cam_id]), kwargs={})
    self.threads.update({cam_id: thread})
    thread.start()
    sleep(0.1)
    ret = True if thread.is_alive() else False
    msg = "{} started".format(cam_id) if ret else "not successful"
    return {"success": ret, "msg": msg}

  def delete(self, cam_id: str):
    ret = self.kill(cam_id)
    if ret:
      # don't pop them immidietly to check if everything is good
      self.consumers.pop(cam_id)
      self.threads.pop(cam_id)
      self.decoders.pop(cam_id)
      self.buffers.pop(cam_id)
    msg = "{} killed".format(cam_id) if ret else "not successful" if ret == False else "{} doesn't exist".format(cam_id)
    return {"success": ret, "msg": msg}

  def update(self, cam_id: str):
    raise NotImplementedError("update {}!".format(cam_id))
