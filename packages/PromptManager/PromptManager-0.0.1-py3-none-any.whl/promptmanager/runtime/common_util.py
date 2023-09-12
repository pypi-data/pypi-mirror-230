import json
import os


class PMCommonUtil:

    @staticmethod
    def object_to_json(obj):
        json_str = json.dumps(obj, ensure_ascii=False, default=lambda obj: obj.__dict__)
        return json_str

    @staticmethod
    def object_to_dict(obj):
        json_str = json.dumps(obj, ensure_ascii=False, default=lambda obj: obj.__dict__)
        dict = json.loads(json_str)
        return dict

    @staticmethod
    def json_to_dict(json_str):
        dict = json.loads(json_str)
        return dict

    @staticmethod
    def convert_list_to_dict(to_convert_list: list) -> dict:
        result_dict = {}
        for param in to_convert_list:
            if isinstance(param, object):
                param = PMCommonUtil.object_to_dict(param)

            key = param['name'] if 'name' in param else param['variable']
            value = param['value'] if not PMCommonUtil.is_value_none("value", param) else param['defaultValue']

            result_dict[key] = value
        return result_dict

    @staticmethod
    def convert_dict_to_list(to_convert_dict: dict) -> list[dict]:
        result_list = []

        for k, v in to_convert_dict.items():
            item = {
                "name": k,
                "variable": k,
                "type": type(v).__name__ if type(v).__name__ != 'str' else "text",
                "value": v
            }
            result_list.append(item)

        return result_list

    @staticmethod
    def is_value_none(_key, _dict: dict) -> bool:
        if _key not in _dict:
            return True
        if _dict[_key] == '' or _dict[_key] is None:
            return True
        return False

    @staticmethod
    def json_to_dict(json_str):
        dict_result = json.loads(json_str)
        return dict_result

    @staticmethod
    def object_to_dict(obj):
        json_str = json.dumps(obj, ensure_ascii=False, default=lambda obj: obj.__dict__)
        dict = json.loads(json_str)
        return dict

    @staticmethod
    def find_path(root, target, path):
        """
        root: need find json
        target: target value
        path: find target value path
        """
        if isinstance(root, dict):
            for key, value in root.items():
                if value == target:
                    yield [key]
                else:
                    for path_part in PMCommonUtil.find_path(value, target, []):
                        yield [key] + path_part
        elif isinstance(root, list):
            for index, value in enumerate(root):
                if value == target:
                    yield [index]
                else:
                    for path_part in PMCommonUtil.find_path(value, target, []):
                        yield [index] + path_part

    @staticmethod
    def find_path_by_key(root, target_key, path):
        """
        root: need find json
        target: target value
        path: find target value path
        """
        if isinstance(root, dict):
            for key, value in root.items():
                if key == target_key:
                    yield [key]
                else:
                    for path_part in PMCommonUtil.find_path_by_key(value, target_key, []):
                        yield [key] + path_part
        elif isinstance(root, list):
            for index, value in enumerate(root):
                if index == target_key:
                    yield [index]
                else:
                    for path_part in PMCommonUtil.find_path_by_key(value, target_key, []):
                        yield [index] + path_part

    @staticmethod
    def generate_ios_by_variables(variables: list) -> list:
        ios = []
        for variable in variables:
            io = {
                "name": variable['name'],
                "type": variable['type'],
                "defaultValue": variable['defaultValue'],
                "value": variable['value'] if 'value' in variable else None
            }
            ios.append(io)

        return ios

    @staticmethod
    def generate_variables_by_ios(ios: list) -> list:
        variables = []
        for io in ios:
            variable = {
                "variable": io['name'],
                "type": io['type'],
                "defaultValue": io['defaultValue'],
                "value": io['value'] if 'value' in io else None
            }
            variables.append(variable)

        return variables

    @staticmethod
    def generate_io_output_key(node, output_name: str) -> str:
        return node.id + "_" + output_name

    @staticmethod
    def generate_io_output_key_by_edge(edge) -> str:
        return edge.source_node + "_" + edge.source_output_name

    @staticmethod
    def is_json(text):
        try:
            json.loads(text)
            return True
        except ValueError:
            return False


class FileUtil:
    @staticmethod
    def write(file_path: str, content: str):
        if not os.path.exists(file_path):
            parent_path = os.path.abspath(os.path.join(file_path, os.pardir))
            if not os.path.exists(parent_path):
                os.makedirs(parent_path)

        with open(file_path, "w") as f:
            f.write(content)

    @staticmethod
    def read(file_path):
        content = None
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                content = f.read()
        return content

    @staticmethod
    def delete_file(file_path):
        if os.path.exists(file_path):
            os.remove(file_path)
