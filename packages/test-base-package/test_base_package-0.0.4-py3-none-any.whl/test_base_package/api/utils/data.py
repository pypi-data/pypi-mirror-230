from utils.read_data import ReadFileData

dataRow = {}


def get_conf():
    read = ReadFileData()
    data = read.load_yaml("conf.yml")
    return data


dataRow = get_conf()
