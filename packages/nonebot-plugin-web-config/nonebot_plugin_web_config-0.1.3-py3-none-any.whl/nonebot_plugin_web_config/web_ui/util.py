import json

from ..web_config import get_instances
from ..web_config.util import decode_json


def generate_menu(instances: dict):
    menu = []
    for module, configs in instances.items():
        each_menu = {"name": module, 'submenu': []}
        for config_name, instance in configs.items():
            each_menu['submenu'].append({"name": config_name, "link": f"{module}/{config_name}"})
        menu.append(each_menu)
    return menu


def generate_content_box(path, instances):
    data = {}
    if path and path != 'favicon.ico':
        paths = path.split("/")
        instance = instances[paths[0]][paths[1]]
        raw_data = instance.dict()
        schemas = instance.schema()['properties']
        if getattr(instance, "__type__") == 'list-dict':
            data = {'list-dict': raw_data['data_dict']}
        else:
            data = {"dict": {}}
            for key, value in raw_data.items():
                if key in schemas.keys() and 'description' in schemas[key] and schemas[key]['description']:
                    data["dict"][key] = {"des": schemas[key]['description'], "value": raw_data[key]}
                else:
                    data["dict"][key] = {"des": "", "value": raw_data[key]}
        return data
    else:
        return {}


def generate_index(path):
    instances = get_instances()
    return generate_menu(instances), generate_content_box(path, instances)


async def process_data(path, request):
    instances = get_instances()
    if path:
        paths = path.split("/")
        instance = instances[paths[0]][paths[1]]
        arg = paths[2]
        data = await request.json()
        data = decode_json(data)
        if arg == "save-dict":
            for key, value in data.items():
                setattr(instance, key, value)
            instance.save()
        elif arg == "delete":
            key, value = tuple(data.items())[0]
            if key in instance.data_dict.keys():
                del instance.data_dict[key]
                instance.save()
        elif arg == "add":
            instance.data_dict.update(data)
            instance.save()
        elif arg == "edit":
            new_dict = {}
            for key, value in instance.data_dict.items():
                if key == data["origin_key"]:
                    new_dict[data["new_key"]] = data["new_value"]
                else:
                    new_dict[key] = value
            instance.data_dict = new_dict
            instance.save()
