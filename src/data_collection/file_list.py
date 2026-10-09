import json

from data_collection.globals import file_list, skill_tag_ids, target_dir


def process_file_list():
    """
    Use RemoteLocalizeFileList.json to get useful data lists.

    Gets skillTag files to use for skillTagPersistence later
    """

    for filename in file_list["skillTag"]:
        path = target_dir / (filename + ".json")

        with open(path, "r", encoding="utf-8-sig") as f:
            data = json.load(f)

        ids = [item["id"] for item in data["dataList"]]
        skill_tag_ids.extend(ids)


__all_ = ["process_file_list"]
