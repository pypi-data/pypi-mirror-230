#
# Copyright (C) 2021 The Delta Lake Project Authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import logging
import os
from deltastore.profile import DeltaSharingProfile
from deltastore.protocols import Table
from deltastore.restclient import DeltaSharingRestClient


logging.basicConfig(
    format="%(asctime)s:%(levelname)s:%(message)s",
    datefmt="%Y/%m/%d %I:%M:%S %p",
    level=os.getenv("LOGLEVEL", "INFO").upper(),
)


class DeltaSharingReader:
    def __init__(self, profile):
        self.client = DeltaSharingRestClient(
            DeltaSharingProfile.read_from_file(profile)
        )

    def fetch_files(self, share, schema, table, predicates=None, version=None):
        response = self.client.list_files_in_table(
            table=Table(name=table, share=share, schema=schema),
            jsonPredicateHints=predicates,
            limitHint=None,
            version=version,
        )
        files = []
        for file in response.add_files:
            files.append(file.url)
        return files


def connect(profile):
    return DeltaSharingReader(profile)
