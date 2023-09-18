import requests
import os
import json


def create(
    name, first, second, address="localhost:80", sorry_words=["я не могу", "извините"]
):
    """Create SBS"""
    if not "name" in first or not "name" in second:
        print("Please, provide model names.")
        return

    if not "data" in first or not "data" in second:
        print("Please, provide paths to the files with data.")
        return

    if not os.path.isfile(first["data"]):
        print(f"{first['data']} does not exist")
        return

    if not os.path.isfile(first["data"]):
        print(f"{second['data']} does not exist")
        return

    if not name:
        print("Please, provide SBS name.")
        return

    with open(first["data"], "r", encoding="utf-8") as file1:
        content1 = json.load(file1)

    with open(second["data"], "r", encoding="utf-8") as file2:
        content2 = json.load(file2)

    err = validate(content1, content2)
    if err:
        print(err)
        return

    extra_data = {
        "sorry_1": get_sorry(content1, sorry_words),
        "sorry_2": get_sorry(content2, sorry_words),
        "avg_len_1": avg_len(content1),
        "avg_len_2": avg_len(content2),
    }

    with open(first["data"], "rb") as file_1:
        with open(second["data"], "rb") as file_2:
            response = requests.post(
                f"http://{address}/sbs/create",
                data={
                    "name": name,
                    "model_1": first["name"],
                    "model_2": second["name"],
                    "filename_1": os.path.basename(first["data"]),
                    "filename_2": os.path.basename(second["data"]),
                    "extra_data": json.dumps(extra_data),
                },
                files={first["data"]: file_1, second["data"]: file_2},
            )

    res = json.loads(response.content.decode("utf-8"))

    return res


def avg_len(content):
    """Calculate avg lenght"""
    return round(sum(len(x[1]) for x in content) / len(content))


def info(sbs_guid, address="localhost:80"):
    """Get SBS status"""
    response = requests.get(f"http://{address}/sbs/info/{sbs_guid}")

    res = json.loads(response.content.decode("utf-8"))

    return res


def validate(content1, content2):
    """Validate content"""

    len1, len2 = len(content1), len(content2)

    if len1 != len2:
        return f"Provided files contain different amount of items: {len1} and {len2}."

    return ""


def get_sorry(content, sorry_words):
    """Calculate censored answers"""
    c = 0
    for x in content:
        for sorry in sorry_words:
            if sorry.lower() in x[1].lower():
                c += 1
    return c
