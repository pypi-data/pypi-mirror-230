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

import unittest

from HelmSign.chart import HelmChart


class HelmChartTest(unittest.TestCase):
    def test_init(self) -> None:
        chart = HelmChart("tests/charts/hcloud-cloud-controller-manager-2.0.0.tgz")

        # test checksums
        self.assertEqual("6fed28c93d2d45378f528ec5a5d271fd744c49be5e240fdc4d1c6dd3f5119569", chart.checksum("sha256"))
