import sys
import av
from time import time
from collections import deque
from typing import List, Any, Dict
try:
  from ..logger import LOG_LEVELS
except:
  from logger import LOG_LEVELS
try:
  from ..structures import LimitedDict
except:
  from structures import LimitedDict


av.logging.set_level(av.logging.PANIC)


class Decoder:
  index: int
  sizes: list
  diffs: list
  stamp: float
  W: int
  H: int
  rate: int
  pix_fmt: str
  de_codec: str
  _started: bool
  __buff: LimitedDict  # deque[Dict[int, bytes]]

  def __init__(self, id: str, maxlen:int=20, rate: int = 10, W: int = 1920, H: int = 1080, de_codec="h264", pix_fmt="yuv420p", log_level: str = "ERROR") -> None:
    # vars
    self.index = -1
    self.sizes = []
    self.diffs = []
    self._packet_pool = []
    self.stamp: float = 0  # Not started yet
    self._started = False
    self.__buff = LimitedDict(maxlen=maxlen)
    # inputs
    self.maxlen = maxlen
    self.id = id
    self.W = W
    self.H = H
    self.rate = rate
    self.pix_fmt = pix_fmt
    self.de_codec = de_codec
    self.__log_level = log_level
    # handlers
    self.__de_ctx = self.__create_ctx(de_codec, "r", self.rate)
    return

  def __append(self, chunk: bytes):
    if self.index >= max(self.maxlen, 65535):
      self.index = -1
    self.index += 1
    in_chunk_size = len(chunk)
    self.__buff.update({self.index: chunk})
    self.sizes.append(in_chunk_size)
    return True

  def _add_diff(self, diff):
    self.diffs.append(diff)
    return int(diff * 1000)

  def __create_ctx(self, codec, mode, rate):
    ctx = av.codec.context.CodecContext.create(codec, mode)  # type: ignore
    if self.W != None:
      ctx.width = self.W
    if self.H != None:
      ctx.height = self.H
    if self.pix_fmt != None:
      ctx.pix_fmt = self.pix_fmt
    # ctx.time_base = self.time_base
    if mode == "w":
      ctx.rate = rate
      # flags options -> QSCALE,4MV,OUTPUT_CORRUPT,QPEL,DROPCHANGED,PASS1,PASS2,LOOP_FILTER,PSNR,TRUNCATED,INTERLACED_DCT,
      #                  LOW_DELAY,GLOBAL_HEADER,BITEXACT,INTERLACED_ME,Interlaced motion estimation,CLOSED_GOP
      ctx.flags |= 'LOW_DELAY'
      ctx.flags |= 'GLOBAL_HEADER'
      # flags2 options -> FAST,NO_OUTPUT,LOCAL_HEADER,CHUNKS,IGNORE_CROP,SHOW_ALL,EXPORT_MVS,SKIP_MANUAL,RO_FLUSH_NOOP
      ctx.flags2 |= 'FAST'
      # options -> ffmpeg encoder options
      ctx.options = {
          **ctx.options,
          "delay": "10",
          "bufsize": str(65536 * 8)  # Set ratecontrol buffer size (in bits).
      }
    return ctx

  def __check(self, packet):
    if isinstance(packet, list):
      return "flushed"  # Not parsed
    if packet is None:
      return None  # Not parsed / buffered
    if packet.is_corrupt:
      return False  # None-frame
    return True

  def __parse(self, chunk):
    packets = self.__de_ctx.parse(chunk)
    match len(packets):
      case 0:  # Buffered packet -> likely one packet will be buffered
        return None
      case 1:  # Normal behavior
        return packets[0]
      case _:  # Flush to decoder
        return packets

  def __decode(self, packet):
    try:
      frames = self.__de_ctx.decode(packet)
      # frames = self.__de_ctx.decode(self._packet_pool[-1])
      if not frames:
        return None
      return frames[0]
    except Exception as e:
      print(e)
      # consequences of `non-existing PPS 0 referenced`
      # self.__unappend()
      if self.__log_level >= LOG_LEVELS["ERROR"]:
        print("Couldn't decode frame...")
      return False

  def __to_array(self, frame):
    return frame.to_ndarray(format="bgr24")

  def decode(self, chunk: bytes):
    self.stamp = time()
    self.__append(chunk)

    packet = self.__parse(chunk)
    match self.__check(packet):
      # flushed decoder / almost never occures
      case "flushed": return enumerate(self.flush())
      # buffered
      case None: return (print("Buffered in parser") if self.__log_level >= LOG_LEVELS["ANY"] else None)
      # corrupted
      case False: return (print("! corrupted packet") if self.__log_level >= LOG_LEVELS["ANY"] else None)
      # self._packet_pool.append(packet)  # parsed
      case True: pass

    if self.__log_level >= LOG_LEVELS["ANY"]:
      print("IN -> dts:", packet.dts, "| size:", packet.size, "| pack pts:",
            packet.pts, "| keyframe:", packet.is_keyframe)  # type: ignore
    frame = self.__decode(packet)
    if not frame:
      if self.__log_level >= LOG_LEVELS["ANY"]:
        print("Buffered in decoder:",
              (packet.pts if packet.pts is not None else 0) / 90000, "sec", sep=" ")
      return None  # buffered / likely one packet
    array = self.__to_array(frame)
    self._started = True
    self._add_diff(time() - self.stamp)
    return array

  def get(self, indx: int):
    return self.__buff.pop(indx)

  def _get_avg_size(self):
    if len(self.sizes) == 0:
      return 0
    return round((sum(self.in_sizes) / len(self.in_sizes)) / 1024, 2)

  def _get_avg_delay(self):
    return 0 if not len(self.diffs) else int((sum(self.diffs) / len(self.diffs)) * 1000)


if __name__ == "__main__":
  try:  # Auto exception handlers
    pass
  except:
    # re-run
    sys.exit(0)

# logs
# print("==============================Results========================================")
# print("IN -> Avg size:", self._get_avg_size("in"),
#       "KB | consumed offset:", self.consumed_offset)
# print("OUT -> Avg size:", self._get_avg_size("out"),
#       "KB | produced offset:", self.produced_offset)
# print("DELAY -> Avg:", self._get_avg_delay(), "ms",
#       "(consider there is no sending)" if not SEND else "")
# print("================================END==========================================")

# headers

  # def _extract_header(self, headers, header):
  #   return headers[[el[0] for el in headers].index(header)][1]
# pts = int.from_bytes(self._extract_header(message.headers, 'pts'))
# time_stamp = int.from_bytes(
#   self._extract_header(message.headers, 'time_stamp'))
# is_keyframe = bool.from_bytes(
#   self._extract_header(message.headers, 'is_keyframe'))
