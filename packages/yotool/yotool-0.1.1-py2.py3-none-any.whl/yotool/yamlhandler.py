import yaml

def overwrite(origin, config):
    for key, value in origin.items():
        if isinstance(value, dict):
            overwrite(origin[key], config[key])
        else:
            config[key] = value
    return config


def get_yaml_data(file_path):
    with open(file_path, encoding='utf-8') as fo:
        return yaml.safe_load(fo.read())


class BaseYamlHandler:
    def __init__(self, file_path=None):
        if file_path:
            self.__config = self.load(file_path)

    def __call__(self, *args, **kwargs):
        return self.__config

    def load(self, file_path):
        origin = get_yaml_data(file_path)
        config = get_yaml_data(origin['inherit']) if origin['inherit'] else {}
        for key, value in origin.items():
            if key not in 'inherit':
                if isinstance(value, dict):
                    overwrite(origin[key], config[key])
                else:
                    config[key] = value
        self.__config = config
        return config


# Test
if __name__ == '__main__':
    handler = BaseYamlHandler()
    print(handler.load('test.yaml'))

    print(handler()['model'])