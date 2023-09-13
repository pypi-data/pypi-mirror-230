import cpe
import copy
import json
import functools


class CustomEncoder(json.JSONEncoder):
    """A C{json.JSONEncoder} subclass to encode documents that have fields of
    type C{bson.objectid.ObjectId}, C{datetime.datetime}
    """

    def default(self, obj):
        return str(obj)


def cpe_normalize_str(parsed, enc=CustomEncoder()):

    GARBAGE = ("<UNDEFINED>", "<ANY>", "<EMPTY>", "<NA>")
    TOO_AMBIGUOUS = ("version", "edition", "update", "part", "sw_edition", "hw_edition")

    cleaned = json.loads(enc.encode(parsed))
    copied = copy.deepcopy(cleaned)
    for k in copied:
        if cleaned[k] and cleaned[k] not in GARBAGE:
            continue
        del cleaned[k]

    for subkey in ("app", "os", "hw"):
        if subkey not in cleaned:
            continue
        for t in TOO_AMBIGUOUS:
            if t in cleaned[subkey][0]:
                del cleaned[subkey][0][t]

        copied = copy.deepcopy(cleaned)
        for k in copied[subkey][0]:
            if (
                "version" not in k
                and cleaned[subkey][0][k]
                and cleaned[subkey][0][k] not in GARBAGE
            ):
                continue
            del cleaned[subkey][0][k]

    return cleaned


@functools.lru_cache(maxsize=None)
def cpe_normalize_json(line):
    line = line.strip()
    parsed = cpe.CPE(line)
    cleaned = cpe_normalize_str(parsed)
    return json.dumps(cleaned)


def normalize(s):
    try:
        parsed = cpe.CPE(s)
        return cpe_normalize_str(parsed)
    except Exception:
        return None
