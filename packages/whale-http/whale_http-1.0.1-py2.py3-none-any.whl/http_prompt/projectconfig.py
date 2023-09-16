from pathlib import Path

import yaml
from pydantic import BaseModel

from .constants import PROJECT_CONFIG


class ProjectConfig(BaseModel):
    host: str


def get_project_conf(project_path) -> ProjectConfig:
    file = Path(project_path).joinpath(PROJECT_CONFIG)
    config_data = []
    with open(file, "r", encoding="utf-8") as f:
        config_data = yaml.safe_load(f)

    return ProjectConfig.model_validate(config_data)


# def saveconfig(name, value):
#     config = load_config()
#     config[name] = value
#     with open(get_configfile(), "w") as configfile:
#         yaml.dump(config, configfile)

# def saveconfig_item(name, value):
#     config = load_config()
#     # item = {'name': name, QRPROJECTDIR: value}
#     # print(item)
#     exists = False
#     for item in config[QC.QRPROJECTS]:
#         if item[QC.QRPROJNAME] == name:
#             item[QC.QRPROJECTDIR] = value
#             exists = True
#             break

#     if not exists:
#         config[QC.QRPROJECTS].append({QC.QRPROJNAME: name, QC.QRPROJECTDIR: value})

#     with open(get_configfile(), "w") as configfile:
#         yaml.dump(config, configfile)

# def default_data_directory():
#     if sys.platform == "win32":
#         base_dir = os.getenv("LOCALAPPDATA") or Path.home().joinpath("/AppData/Local")
#     else:
#         base_dir = os.getenv("XDG_DATA_HOME") or Path.home().joinpath(".local/share")

#     app_dir = Path(base_dir).joinpath(APPLICATIONNAME)
#     if not app_dir.exists():
#         app_dir.mkdir()

#     return app_dir

# def get_data_directory(project_name):
#     data_dir = ""
#     if project_name:
#         config_data = load_config()
#         print(config_data)
#         for config in config_data[QC.QRPROJECTS]:
#             if project_name == config[QC.QRPROJNAME]:
#                 data_dir = config[QC.QRPROJECTDIR]
#                 break
#     return data_dir or str(default_data_directory().joinpath(project_name))

# def init_data_diretory(project_name, dir):
#     datadir = Path(dir).joinpath(project_name)
#     if not datadir.exists():
#         datadir.mkdir()
#     saveconfig_item(project_name, str(datadir))
