# package-comux

## Usage

Well, in case you don't have the gutts to read the whole document or the code itself, you can copy these few lines of code and you're good to go. But remember that playing without the script gets you killed! someday.
```python
# Write the pid of your process to be used by `terminate.py`
open("pid", "w").write(str(os.getpid()))
# Create an instance (it is better to be one instance per process)
cameras = Comux(cam_ids, consume_schema, produce_schema, "ERROR")
# Make consumers connect (wait for it)
cameras.setup_consumers(consumer_bootstrap_servers, overwrite=True, end=True,
                        max_offset_diff=20, strict_on_fail=True, over_write=False, **{})
# Make controller connect (wait for it)
cameras.setup_controller(config_topic, control_bootstrap_servers, acts)
# construct a decoder for each camera
cameras.setup_decoders(rate=10, W=1920, H=1080,
                        de_codec="h264", pix_fmt="yuv420p")
# Make producer connect (wait for it)
cameras.setup_producer(
  producer_bootstrap_servers, strict_on_fail=True, over_write=False, **{})
# Start consuming on the background (multi-thread)
cameras.start()
# Get your messages (likely in a endless while True)
    # timeout is the amount of time waiting for a msg
    # if None, it will block till msg or msgs (a batch) comes along
    # if > 0, it will block for timeout seconds then returns None
while True:
  batch: List[Tuple[str, int | np.ndarray]] = cameras.get_batch(timeout=10)
  # a batch is list of array objects that holds an object for each camera
    # array object: tuple containing cam_id, index_of_frame, np.ndarray
    # loop over each object in batch to feed models
  for cam_id, index, array in batch:
    model = choose_mode_based_on(cam_id)
    # in case of unsuccessful decoding you get a None for array
    if array is None:
      continue
    # feed
    results = model.predict(array)
    # form your headers from results to be sent
    headers: dict = prepare(resulst)
    cameras.send(cam_id, index, headers)

```

## Notes
* main identifier on the Comux side is `cam_id` while on the Consumer side is `topic`. To convert these two to each other
  I've exposed two methods in Comux class named `get_topic_from_cam_id`, `get_cam_id_from_topic`.
  When you wish to update either of `comux.consumers` or `comux.thread` you must set key to the related `cam_id`.


## TODO
* output messages schema: it could be manual (by getting a fallback), or optionally pick one schema.
* in Control.act, how can I filter the incoming messages?
* __LOGGER__. very very important to save logs somewhere.


## Comux
```python
"""
Class to manage cameras and their consumer. It doesn't connect consumers to the server or
  start consuming.

Args:
    cam_ids (List[str]): list of camera ids being used also in topic names instead of `:cam_id`.
    bootstrap_servers (List[str]): Kafka bootstrap servers to connect for cameras (stream broker).
    control_topic (str): name of config and control topic.
    control_bootstrap_servers (List[str]): Kafka bootstrap servers to connect for config (config broker).
    acts (Dict[str, Callable]): keys are action names (key of kafka message) and the function is like
      (comux: Comux, kafka_message.value: Any) -> Any
    end (bool, optional): if set to True, consumers start from the end. Defaults to True.
    max_offset_diff (int, optional): Maximum allowed offset to fall behind, when reached consumer
      automatically moves to the end. Defaults to 20.
    strict_on_fail (bool, optional): if set to True, consumers are allowed to raise Exceptions in case of
      failuire. Defaults to True.
    over_write (bool, optional): if set to True, existing consumers are replaced with new ones in case of
      trying to create a consumer that already exists. Defaults to False.
"""
```
* Sets global properties:
  * consumers
  * threads
* Sets instance properties:
  * cam_ids
  * bootstrap_servers
  * end
  * max_offset_diff
  * strict_on_fail
  * over_write
  * consumer_options (kwargs)
* Creates the Control instance: self.control(control_topic, control_bootstrap_servers, acts, self)
  * acts are passed from Comux.
  * self is the comux instance which is passed to the control instance to be managed.

### Methods

`connect(cam_id, overwrite)`: creates a consumer for given cam_id, updates comux.consumers dict, connects it to kafka server.

`connect_all()`: creates all consumers and connects them to kafka server.

`listen(consumer)`: creates a thread with consumer running on it and push messages to the queue, updates comux.threads dict.

`start()`: creates all threads and starts consuming from all camera topics.

`get(cam_id)`: get one frame msg of camera cam_id.

`get_batch(frame: bool = False, timeout: float = None)`: gets a batch of messages (one msg of every running consumer) and compacts them into a list.

`kill(cam_id)`: kills a consumer and its thread. pops them out of pools.

## Control
```python
"""Class that uses signals coming from config topic and controls comux instance.

Args:
    topic (str): config topic
    bootstrap_servers (List[str]): kafka config broker ip
    acts (Dict[str, Callable]): keys are action names (key of kafka message) and the function is like
      (comux: Comux, kafka_message.value: Any) -> Any
    comux (_type_): comux instance to be controled
"""
```
* Sets instance properties
  * self.topic = topic
  * self.acts = acts
  * self.comux = comux
* self.connect(bootstrap_servers):
* self.sub()
* self.run()

### Methods

`connect(bootstrap_servers)`: connects to kafka

`sub()`: subscribes to config topic provided

`run()`: creates a daemon thread and starts listening for config messages. `__listen()` is running on the background.</br>
`__listen()`: Mainly reads a kafka message and pass it to the act method.
```python
msg: ConsumerRecord = next(self)
print(self.act(msg.key, msg.value))
```

`act(action: str, value: Any)`: action is the key of kafka message and value is the message.value. In this method
```python
def act(self, action: str, value: Any) -> str:
  """takes action name (msg.key) and value (msg.value), finds the responsible action from
      self.acts and calls it with (self, value) as inputs.

  Args:
      action (str): the name of action need to be called.
      value (Any): the value passed to the action.

  Returns:
      str: the result of action, or "✘ No action '" + action + "' defined!" if there is no defined action.
  """
  if action in self.acts.keys():
    return self.acts[action](self.comux, value)
  else:
    return "✘ No action '" + action + "' defined!"
```

`kill()`: kill the control thread. also consuming messages will be stopped.
### Properties

`topic_last_offset`: returns the last offset of config topic. If kafka broker doesn't support it, it returns None.

`offset`: the consumed offset.

## Consumer


## Structure
```
│┌┬┐║╔╦╗
─├┼┤═╠╬╣
│└┴┘║╚╩╝

batch_array = comux.get_batch()
│
│
│
│ Comux ─ setup_control ─── comux.setup_consumers() ────────────────── comux.start()
│  │ │    setup_producer    comux.setup_decoders()                       ║
│  │ │     │                 │                                           ║
│  │ │     │                 │                                           ║
│  │ │  Control              ├ cam_id 1: Consumer1 & CodecContext1 ┐     ║
│  │ │ (Consumer)            │                                     └─────╬─────────────────────────┐
│  │ │     │                 ├ cam_id 2: Consumer2 & CodecContext2 └─────╬─────────────┐           │
│  │ │     │                 │                                           ║             │           │
│  │ │     │                 ├ ...                                       ║             │           │
│  │ │     │                 │                                     ┌─────╩─┐           │           │
│  │ │     │                 └ cam_id N: ConsumerN & CodecContextN ┘       │           │           │
│  │ │     │                                                               │           │           │
│  │ │     │                Action Signals                                 │           │           │
│  │ │ ┌───┴────╦═══════════════delete══════════════════════════════╗  ┌───┴──────┐┌───┴────┐  ┌───┴────┐
│  │ │ │Thread 1╬═══════════════create══════════════════════════════╬══╣Thread N+1││Thread 3│  │Thread 2│
│  │ │ │ Config ╬═══════════════update══════════════════════════════╣  │ camera   ││ camera │  │ camera │
│  │ │ └────────╩═══════════════??????══════════════════════════════╝  └────┬─────┘└────┬───┘  └────┬───┘
│  │ │                                                                  ┌───┴───────────┴───────────┴────┐
│  │ └───────────────────────────────────────────────────────────┐      │ consumer=>decoder=>buffer=>out │
│  │                                                             │      └────────────────────────────────┘
│  ├ MongoConnect                                                │     
│  │  │                                                          │     
│  │  ├ connect(): make the connection to specific collection    │     
│  │  ├ fetch(): get the data from collection                    │     
│  │  └ ret_cam_ids(): retrive camera ids from fetched data ─────┘                    
│  │                                                                                  
│  │                                                                                  
│  │                                                                                  
│  │                                                                                  
│  │                                                                                  
│  │                                                                                  
│  │                                                                                  
│  │                                                                                  
│  │                                                                                  
│  ├ Consumer M                                                                       
│  │     │                                                                            
│  │     ├ next ─┬───────────────── ✉ = msg.value 
│  │     │       │                  ║
│  │     │       ┴                  ║
│  │     └ check falling back       ║
│  │                                ║
│  │                                ║
│  ├ CodecContext M                 ║
│  │ │                              ║
│  │ │                              ║
│  │ │         ┌─────────────────┐  ║     ✉
│  │ ├ Buffer => original packet <══╣ ────────┐
│  │ │         └──────────────┬──┘  ║         │✉
│  │ │                              ║         │
│  │ │                              ║         │
│  │ decode                         ║         │✉
│  │     ├ Parse ═══════════════════╝         │
│  │     │   ║                                │
│  │     │   P (packet)                       │
│  │     │   ║                                │✉
│  │     ├ Check                              │
│  │     │   ║                                │
│  │     │   P (h264 encoded packet of data)  │✉
│  │     │   ║                                │
│  │     └ To Array                           │
│  │         ║                                │
└──┼────── array                              │✉
   │         │       *********************    │
   │       ┌─┴──┐    * Imagine it called *    │
   │       │ AI │    * outside here      *    │
   │       └──┬─┘    *********************    │
   │  ┌── Meta data and headers = results     │
   │  │                                       │✉
   │  │   ┌───────────────────────────────────┘
   │  │   │                                   
   └ Producer
          │
          └ send: produce the original packet along with results as headers
```
