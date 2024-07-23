import json
import random
import time
from collections import OrderedDict, defaultdict
from typing import Any, Callable, Dict, List

import pybase64


#res = ""

class OrderedMap:
    def __init__(self):
        self.map = OrderedDict()

    def add(self, key: str, value: Any):
        self.map[key] = value

    def to_json(self):
        return json.dumps(self.map)

    def __str__(self):
        return self.to_json()


TurnTokenList = List[List[Any]]
FloatMap = Dict[float, Any]
StringMap = Dict[str, Any]
FuncType = Callable[..., Any]

start_time = time.time()


def get_turnstile_token(dx: str, p: str) -> str:
    decoded_bytes = pybase64.b64decode(dx)
    #print(decoded_bytes.decode())
    return process_turnstile_token(decoded_bytes.decode(), p)


def process_turnstile_token(dx: str, p: str) -> str:
    result = []
    p_length = len(p)
    if p_length != 0:
        for i, r in enumerate(dx):
            result.append(chr(ord(r) ^ ord(p[i % p_length])))
    else:
        result = list(dx)
    return ''.join(result)


def is_slice(input_val: Any) -> bool:
    return isinstance(input_val, (list, tuple))


def is_float(input_val: Any) -> bool:
    return isinstance(input_val, float)


def is_string(input_val: Any) -> bool:
    return isinstance(input_val, str)


def to_str(input_val: Any) -> str:
    if input_val is None:
        return "undefined"
    elif is_float(input_val):
        return f"{input_val:.16g}"
    elif is_string(input_val):
        special_cases = {
            "window.Math": "[object Math]",
            "window.Reflect": "[object Reflect]",
            "window.performance": "[object Performance]",
            "window.localStorage": "[object Storage]",
            "window.Object": "function Object() { [native code] }",
            "window.Reflect.set": "function set() { [native code] }",
            "window.performance.now": "function () { [native code] }",
            "window.Object.create": "function create() { [native code] }",
            "window.Object.keys": "function keys() { [native code] }",
            "window.Math.random": "function random() { [native code] }"
        }
        return special_cases.get(input_val, input_val)
    elif isinstance(input_val, list) and all(isinstance(item, str) for item in input_val):
        return ','.join(input_val)
    else:
        print(f"Type of input is: {type(input_val)}")
        return str(input_val)


def get_func_map() -> FloatMap:
    process_map: FloatMap = defaultdict(lambda: None)

    def func_1(e: float, t: float):
        e_str = to_str(process_map[e])
        t_str = to_str(process_map[t])
        if e_str is not None and t_str is not None:
            res = process_turnstile_token(e_str, t_str)
            process_map[e] = res
        else:
            print(f"Warning: Unable to process func_1 for e={e}, t={t}")

    def func_2(e: float, t: Any):
        process_map[e] = t

    def func_5(e: float, t: float):
        n = process_map[e]
        tres = process_map[t]
        if n is None:
            process_map[e] = tres
        elif is_slice(n):
            nt = n + [tres] if tres is not None else n
            process_map[e] = nt
        else:
            if is_string(n) or is_string(tres):
                res = to_str(n) + to_str(tres)
            elif is_float(n) and is_float(tres):
                res = n + tres
            else:
                res = "NaN"
            process_map[e] = res

    def func_6(e: float, t: float, n: float):
        tv = process_map[t]
        nv = process_map[n]
        if is_string(tv) and is_string(nv):
            res = f"{tv}.{nv}"
            if res == "window.document.location":
                process_map[e] = "https://chatgpt.com/"
            else:
                process_map[e] = res
        else:
            print("func type 6 error")

    def func_24(e: float, t: float, n: float):
        tv = process_map[t]
        nv = process_map[n]
        if is_string(tv) and is_string(nv):
            process_map[e] = f"{tv}.{nv}"
        else:
            print("func type 24 error")

    def func_7(e: float, *args):
        n = [process_map[arg] for arg in args]
        ev = process_map[e]
        if isinstance(ev, str):
            if ev == "window.Reflect.set":
                obj = n[0]
                key_str = str(n[1])
                val = n[2]
                obj.add(key_str, val)
        elif callable(ev):
            ev(*n)

    def func_17(e: float, t: float, *args):
        i = [process_map[arg] for arg in args]
        tv = process_map[t]
        res = None
        if isinstance(tv, str):
            if tv == "window.performance.now":
                current_time = time.time_ns()
                elapsed_ns = current_time - int(start_time * 1e9)
                res = (elapsed_ns + random.random()) / 1e6
            elif tv == "window.Object.create":
                res = OrderedMap()
            elif tv == "window.Object.keys":
                if isinstance(i[0], str) and i[0] == "window.localStorage":
                    res = ["STATSIG_LOCAL_STORAGE_INTERNAL_STORE_V4", "STATSIG_LOCAL_STORAGE_STABLE_ID",
                           "client-correlated-secret", "oai/apps/capExpiresAt", "oai-did",
                           "STATSIG_LOCAL_STORAGE_LOGGING_REQUEST", "UiState.isNavigationCollapsed.1"]
            elif tv == "window.Math.random":
                res = random.random()
        elif callable(tv):
            res = tv(*i)
        process_map[e] = res

    def func_8(e: float, t: float):
        process_map[e] = process_map[t]

    def func_14(e: float, t: float):
        tv = process_map[t]
        if is_string(tv):
            try:
                token_list = json.loads(tv)
                process_map[e] = token_list
            except json.JSONDecodeError:
                print(f"Warning: Unable to parse JSON for key {t}")
                process_map[e] = None
        else:
            print(f"Warning: Value for key {t} is not a string")
            process_map[e] = None

    def func_15(e: float, t: float):
        tv = process_map[t]
        process_map[e] = json.dumps(tv)

    def func_18(e: float):
        ev = process_map[e]
        e_str = to_str(ev)
        decoded = pybase64.b64decode(e_str).decode()
        process_map[e] = decoded

    def func_19(e: float):
        ev = process_map[e]
        e_str = to_str(ev)
        encoded = pybase64.b64encode(e_str.encode()).decode()
        process_map[e] = encoded

    def func_20(e: float, t: float, n: float, *args):
        o = [process_map[arg] for arg in args]
        ev = process_map[e]
        tv = process_map[t]
        if ev == tv:
            nv = process_map[n]
            if callable(nv):
                nv(*o)
            else:
                print("func type 20 error")

    def func_21(*args):
        pass

    def func_23(e: float, t: float, *args):
        i = list(args)
        ev = process_map[e]
        tv = process_map[t]
        if ev is not None and callable(tv):
            tv(*i)

    process_map.update({
        1: func_1, 2: func_2, 5: func_5, 6: func_6, 24: func_24, 7: func_7,
        17: func_17, 8: func_8, 10: "window", 14: func_14, 15: func_15,
        18: func_18, 19: func_19, 20: func_20, 21: func_21, 23: func_23
    })

    return process_map


def process_turnstile(dx: str, p: str) -> str:
    tokens = get_turnstile_token(dx, p)
    #print(tokens)
    res = ""
    token_list = json.loads(tokens)
    process_map = get_func_map()

    def func_3(e: str):
        nonlocal res
        res = pybase64.b64encode(e.encode()).decode()
        #print("inside :", res)
    process_map[3] = func_3
    process_map[9] = token_list
    process_map[16] = p

    #print(tokens[0])

    for token in token_list:
        try:
            e = token[0]
            t = token[1:]
            f = process_map.get(e)
            if callable(f):
                f(*t)
            else:
                print(f"Warning: No function found for key {e}")
        except Exception as exc:
            print(f"Error processing token {token}: {exc}")

    return res


if __name__ == "__main__":
    result = process_turnstile("""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
1oVFUIDUwMGBUhEGE8OBjsBRDoAS1ELFRIFUB9SBEoUVFIeBVBwFUJtVAEUBUpWHE0XAVcDU1dlSUJiDgEcUwJNEl4CTVgBGUMcAU4WXRsaDVU5AUFsA1UDVFIURVoPFwsDTxFQHkYMVU8JBE8NDFQYV
xxpGEQ/HE0XA1IDUVAURVEBFwcDPh1BaVEHTVIGGUMVD0wPVAEUBVBIDVgbFF4bSlgJOD8=""", """gAAAAACWzYwMjQsIk1vbiBKdWwgMDEgMjAyNCAwMzoyODowMyBHTVQtMDUwMCAoRWFzdGVybiBTdGFuZGFyZCBUaW1lKSIsNDI5NDcwNTE1Miw0MywiTW96aWxsYS81LjAgKFgxMTsgTGludXgg
eDg2XzY0KSBBcHBsZVdlYktpdC81MzcuMzYgKEtIVE1MLCBsaWtlIEdlY2tvKSBDaHJvbWUvMTI2LjAuMC4wIFNhZmFyaS81MzcuMzYiLCJodHRwczovL2Nkbi5vYWlzdGF0aWMuY29tL19uZXh0L3N0
YXRpYy9PbjdfOTdXdTloM1hQbk5pcy1COHUvX3NzZ01hbmlmZXN0LmpzIiwiIiwiZW4tVVMiLCJlbi1VUyxlcy1VUyxlbixlcyIsMjEsImNvb2tpZUVuYWJsZWTiiJJ0cnVlIiwiX3JlYWN0TGlzdGVu
aW5nbzc0M2xubnB2ZGciLCJfb2FpSGFuZGxlU2Vzc2lvbkV4cGlyZWQiLDI0NDU1LjYxMDk1MDc3MywiNDhkNGM2MWQtMDgwYi00NTM2LWIzYWEtYjk3M2JlMzliN2RmIl0=""")
    print(result)
