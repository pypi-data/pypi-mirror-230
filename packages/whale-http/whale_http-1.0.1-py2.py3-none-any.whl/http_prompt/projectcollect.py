import shutil
from pathlib import Path
from typing import Dict, List

import yaml
from pydantic import BaseModel

from http_prompt.utils import writeprojecttofile


class ProjectLocation(BaseModel):
    name: str
    path: str


class ProjectCollect:
    pinfos: List[ProjectLocation]
    collectfile: Path

    def __init__(self) -> None:
        self.pinfos = []

    @classmethod
    def create(cls, data: List[Dict[str, str]]):
        pc_instance = cls.__new__(cls)
        pc_instance.pinfos = []
        for item in data:
            pinfo = ProjectLocation.model_validate(item)
            pc_instance.pinfos.append(pinfo)

        return pc_instance

    @classmethod
    def load_from_file(cls, filename: Path):
        pc_instance = cls.__new__(cls)
        pc_instance.pinfos = []
        pc_instance.collectfile = filename

        with open(filename, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        for item in data:
            pinfo = ProjectLocation.model_validate(item)
            pc_instance.pinfos.append(pinfo)

        return pc_instance

    def load_data(self, data: List[Dict[str, str]]):
        for item in data:
            pinfo = ProjectLocation.model_validate(item)
            self.pinfos.append(pinfo)

    @property
    def project_names(self) -> List[str]:
        pnames: List[str] = [item.name for item in self.pinfos]
        return pnames

    @property
    def project_paths(self) -> List[str]:
        ppaths: List[str] = [item.path for item in self.pinfos]
        return ppaths

    @property
    def project_dict(self) -> Dict[str, str]:
        # pdict: Dict[str, str] = {}
        pdict: Dict[str, str] = dict(zip(self.project_names, self.project_paths))
        return pdict

    def get_path(self, projectname: str) -> str:
        projectpath: str = ""
        for item in self.pinfos:
            if projectname == item.name:
                projectpath = item.path

        return projectpath

    def _writetofile(self):
        with open(self.collectfile, mode="w", encoding="utf-8") as f:
            for item in self.pinfos:
                writeprojecttofile(f, item.name, item.path)

    def delete_project(self, projectname: str):
        for item in self.pinfos:
            if projectname == item.name:
                # todo 是否删除文件，有误删风险
                # shutil.rmtree(self.get_path(projectname), ignore_errors=True)
                self.pinfos.remove(item)
                self._writetofile()
