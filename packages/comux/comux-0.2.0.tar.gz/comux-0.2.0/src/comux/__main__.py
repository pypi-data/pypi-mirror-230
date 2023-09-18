# py __main__.py --timeout=1 --num=5000

from sys import argv as __argv
import sys
from re import match
from json import decoder as __decoder
import os
from os import path
from typing import List, Any, Dict, Tuple
from numpy import ndarray
import time


try:
  from . import Comux
except ImportError:
  Comux = __import__("__init__").Comux

from actions import ActionCenter

acts = {
  "create": ActionCenter.create(lambda el: el["_id"], lambda ret: ("✔" if ret["success"] else "✘") + " action create -> " + ret["msg"]),
  "delete": ActionCenter.delete(lambda el: el["_id"], lambda ret: ("✔" if ret["success"] else "✘") + " action delete -> " + ret["msg"]),
}


def main(client_name, db_url, db_database, db_collections, consume_schema: str, produce_schema: str, consumer_bootstrap_servers, producer_bootstrap_servers, control_bootstrap_servers, config_topic, acts, timeout, num, is_batch):
  mode = "batch" if is_batch else "single"
  open("pid", "w").write(str(os.getpid()))
  cameras = Comux(client_name, db_url, db_database,
                  db_collections, consume_schema, produce_schema, "ERROR")

  # if you don't want to run on all cameras
  # cam_ids = cameras.cam_ids
  # selected_cam_ids = cam_ids[some_range]
  # cameras.cam_ids = selected_cam_ids

  cameras.setup_consumers(consumer_bootstrap_servers, replace=True,
                          max_offset_diff=20, strict_on_fail=True, over_write=False, **{})

  cameras.setup_controller(config_topic, control_bootstrap_servers, acts)

  cameras.setup_decoders(rate=10, W=1920, H=1080,
                         de_codec="h264", pix_fmt="yuv420p")

  cameras.setup_producer(producer_bootstrap_servers,
                         strict_on_fail=True, over_write=False, **{})

  cameras.start()

  # ==========  Y O U R   L O G I C  ==========
  # batch mode
  if mode == "batch":
    for i in range(num):
      arrays = cameras.get_batch(timeout=timeout)
      for cam_id, indx, arr in arrays:
        arr: ndarray | None
        if arr is not None:
          print(i, cam_id, "index={}".format(indx), "array={}".format(
            arr.shape if isinstance(arr, ndarray) else None), sep=" ")
          cameras.send(cam_id, indx, None)
  # single mode
  else:
    cam_id = cameras.cam_ids[0]
    for i in range(num):
      _, index, array = cameras.read(cam_id)
      if array is None: continue
      print("#", index, " array shape: ", array.shape, sep="")

def h():
  print("Help mode:")
  print("    python3 -m comux bootstrap_servers cam_ids")
  print("    ENV args:")
  print("         cam_ids: list of camera ids. example ['cam_id1']")
  print("         consume_schema: string containing `:cam_id`")
  print("         produce_schema: string containing `:cam_id`")
  print(
    "         consumer_bootstrap_servers: list of broker adresses. example ['localhost:9092']")
  print(
    "         producer_bootstrap_servers: list of broker adresses. example ['localhost:9092']")
  print(
    "         control_bootstrap_servers: list of broker adresses. example ['localhost:9092']")
  print("         config_topic: topic of config signals. example conf")

  print("    Options:")
  print("         --timeout=?: wait till msg arrives (sec). default None.")
  print("         --cam_id=?: if not batch mode, the cam_id to get msg from")
  print("         --num=?: number of messages readable. default 1")
  print("         --batch: enables the batch mode on all cameras")
  print(
    "Example: py __main__.py ['192.168.10.20:9092'] ['cam_id1'] --timeout=1 --batch")


def parse(name: str, type: str = "str"):
  value = os.getenv(name)
  if value is None:
    raise ValueError("{} is required in env file.".format(name.upper()))
  match type:
    case "str":
      return value
    case "list":
      return [el.strip() for el in value.split(",")]


def env():
  import dotenv
  return dotenv.load_dotenv(
    None if (len(__argv) < 2 or __argv[1].startswith("-")) else
    __argv[1] if path.isabs(__argv[1]) else
    path.join(path.abspath("."), __argv[1])
  )


def get_args():
  os.environ.setdefault("client_name", input("client_name: "))
  os.environ.setdefault("db_url", input("db_url: "))
  os.environ.setdefault("db_database", input("db_database: "))
  os.environ.setdefault("consume_schema", input("consume_schema: "))
  os.environ.setdefault("produce_schema", input("produce_schema: "))
  os.environ.setdefault("consumer_bootstrap_servers",
                        input("consumer_bootstrap_servers: "))
  os.environ.setdefault("producer_bootstrap_servers",
                        input("producer_bootstrap_servers: "))
  os.environ.setdefault("control_bootstrap_servers",
                        input("control_bootstrap_servers: "))
  os.environ.setdefault("config_topic", input("config_topic: "))
  os.environ.setdefault("COLLECTION_Model", input("COLLECTION_Model: "))
  os.environ.setdefault("COLLECTION_Running_Schedule", input(
    "COLLECTION_Running_Schedule: "))
  os.environ.setdefault("COLLECTION_Schedule", input("COLLECTION_Schedule: "))
  os.environ.setdefault("COLLECTION_Model_Camera",
                        input("COLLECTION_Model_Camera: "))
  return True


def arg_parse(obj: str = None, flag: str = None):
  if flag:
    return True if flag in __argv else False
  vals = [obj["func"](el) for el in __argv if bool(match(obj["regex"], el))]
  val = vals[0] if len(vals) > 0 else obj["default"]
  return val


if __name__ == "__main__":
  try:
    if "--help" in __argv or "-h" in __argv:
      h()
    else:
      if not env():
        get_args()
      client_name = parse("client_name")
      db_url = parse("db_url")
      db_database = parse("db_database")
      consume_schema = parse("consume_schema")
      produce_schema = parse("produce_schema")
      consumer_bootstrap_servers = parse("consumer_bootstrap_servers", "list")
      producer_bootstrap_servers = parse("producer_bootstrap_servers", "list")
      control_bootstrap_servers = parse("control_bootstrap_servers", "list")
      config_topic = parse("config_topic")
      db_collections = {
        "Model": parse("COLLECTION_Model"),
        "Running_Schedule": parse("COLLECTION_Running_Schedule"),
        "Schedule": parse("COLLECTION_Schedule"),
        "Model_Camera": parse("COLLECTION_Model_Camera")
      }
      timeout = arg_parse({
        "func": lambda el: int(el.split("=")[1]),
        "regex": "--timeout.*",
        "default": None
      })
      num = arg_parse({
        "func": lambda el: int(el.split("=")[1]),
        "regex": "--num.*",
        "default": 1
      })
      batch = arg_parse(flag="--batch")
      main(client_name, db_url, db_database, db_collections, consume_schema, produce_schema, consumer_bootstrap_servers, producer_bootstrap_servers, control_bootstrap_servers, config_topic,
           acts, timeout, num, batch)  #

  except KeyboardInterrupt:
    print("Exited")
    sys.exit(0)
  except IndexError as e:
    print(e)
    h()
    sys.exit(0)
  except ValueError as e:
    print(e)
    sys.exit(1)
