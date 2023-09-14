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

import os
import unittest


class End2EndTest(unittest.TestCase):
    def test_sign_verify(self) -> None:
        result = os.system(
            "helm-sign --gnupg-home ./tests/keyring --key 3DBB996D7FB10281C942A3F4D561C90DBD736806"
            " tests/charts/hcloud-cloud-controller-manager-2.0.0.tgz"
        )
        self.assertEqual(0, result, "sign chart")

        result = os.system(
            "helm verify --keyring ./tests/keyring/BD736806.pub tests/charts/hcloud-cloud-controller-manager-2.0.0.tgz"
        )
        self.assertEqual(0, result, "verify signature")

    def test_sign_verify_with_key_password(self) -> None:
        result = os.system(
            "helm-sign --gnupg-home ./tests/keyring --key E1E4BAAC62DEC3708D2575BC62AECDC525329FAA --passphrase S3cret!"
            " tests/charts/hcloud-cloud-controller-manager-2.0.0.tgz"
        )
        self.assertEqual(0, result, "sign chart")

        result = os.system(
            "helm verify --keyring ./tests/keyring/25329FAA.pub tests/charts/hcloud-cloud-controller-manager-2.0.0.tgz"
        )
        self.assertEqual(0, result, "verify signature")
