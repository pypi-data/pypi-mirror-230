from typing import Dict


def id_map(iter): return set(map(lambda el: el["_id"], iter))
def proper_map(iter, proper): return set(map(lambda el: el[proper], iter))


def retrieve_cam_ids(client_name: str, url: str, database: str, collections: Dict[str, str]):
  category = client_name
  from pymongo import MongoClient

  client = MongoClient(url)
  db = client[database]
  col = db[collections["Model"]]

  model_id = id_map(col.find({"category": category}))
  if len(model_id) > 1:
    raise Exception("Not uniqe category name!")
  else:
    model_id = list(model_id)[0]

  running_schedule_ids = proper_map(
    db[collections["Running_Schedule"]].find(), "schedule_id")

  model_camera_ids = proper_map(
    db[collections["Schedule"]].find({"$or": [{"_id": running_schedule_id} for running_schedule_id in running_schedule_ids]}), "model_camera_id")

  cam_ids = proper_map(
    db[collections["Model_Camera"]].find({"$or": [{"_id": model_camera_id, "model_id": model_id} for model_camera_id in model_camera_ids]}), "camera_id")

  return [str(cam_id) for cam_id in cam_ids]
