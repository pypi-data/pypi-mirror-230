# This file is part of the helm-sign Python package
#    https://gitlab.com/MatthiasLohr/helm-sign
#
# Copyright 2020 Matthias Lohr <mail@mlohr.com>
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import hashlib
import os
import tarfile
from typing import Any

import yaml


class HelmChart(object):
    def __init__(self, filename: str) -> None:
        self._filename = filename

    def checksum(self, hash_alg: str = "sha256") -> str:
        h = hashlib.new(hash_alg)
        with open(self.filename, "rb") as f:
            h.update(f.read())
        return h.hexdigest()

    def get_chart_meta(self) -> Any:
        with tarfile.open(self.filename) as archive:
            chart_name = os.path.commonprefix(archive.getnames())
            chart_yaml_fp = archive.extractfile(os.path.join(chart_name, "Chart.yaml"))
            if chart_yaml_fp is not None:
                meta = yaml.load(chart_yaml_fp, Loader=yaml.SafeLoader)
            else:
                raise RuntimeError("Cannot find Chart.yaml")
        return meta

    @property
    def filename(self) -> str:
        return self._filename
