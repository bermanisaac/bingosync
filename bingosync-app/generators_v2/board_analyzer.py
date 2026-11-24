from generators_v2.bg2_ccomm_v1 import CCommV1
from generators_v2.bg2_sinkout_royale import SinkoutRoyale
import os

json_path = "generators/generator_jsons_v2"
json_323 = os.path.join(json_path, "celeste_v2_lockout.json")
json_34 = os.path.join(json_path, "celeste_v2_3_4.json")

with open(json_34, encoding="utf-8") as json_file:
    json = json_file.read()

    gen = SinkoutRoyale(json)
    gen.debug = True
    board = gen.get_card(5176883, None, 10)