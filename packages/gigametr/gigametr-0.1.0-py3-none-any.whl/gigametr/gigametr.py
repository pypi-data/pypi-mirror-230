import requests
import os
import json


def create_sbs(name, first, second, address="localhost:80"):
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

    with open(first["data"], "rb") as file_1:
        with open(second["data"], "rb") as file_2:
            response = requests.post(
                f"http://{address}/sbs/create",
                data={
                    "name": name,
                    "model_1": first["name"],
                    "model_2": second["name"],
                    "filename_1": first["data"],
                    "filename_2": second["data"],
                },
                files={first["data"]: file_1, second["data"]: file_2},
            )

    res = json.loads(response.content.decode("utf-8"))

    return res


def get_info(sbs_guid, address="localhost:80"):
    """Get SBS status"""
    response = requests.get(f"http://{address}/sbs/info/{sbs_guid}")

    res = json.loads(response.content.decode("utf-8"))

    return res
