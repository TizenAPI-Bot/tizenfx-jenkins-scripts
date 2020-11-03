#!/usr/bin/env python3
#
# Copyright (c) 2019 Samsung Electronics Co., Ltd All Rights Reserved
#
# Licensed under the Apache License, Version 2.0 (the License);
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an AS IS BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

BRANCH_API_LEVEL_MAP = {'master': 'API9', 'devel/master': 'API9',
                        'API8': 'API8',
                        'API7': 'API7',
                        'API6': 'API6',
                        'API5': 'API5',
                        'API4': 'API4'}

GERRIT_BRANCH_MAP = {'API9': '',
                     'API8': 'tizen_6.0',
                     'API7': 'tizen_5.5',
                     'API6': 'tizen_5.5_tv',
                     'API5': 'tizen_5.0',
                     'API4': 'tizen_4.0'}

VERSION_PREFIX_MAP = {'API9': '9.0.0',
                      'API8': '8.0.0',
                      'API7': '7.0.0',
                      'API6': '6.0.0',
                      'API5': '5.0.0',
                      'API4': '4.0.1'}

GERRIT_GIT_URL = ('ssh://dotnetbuild@review.tizen.org:29418/'
                  'platform/core/csapi/tizenfx')

MYGET_PUSH_FEED = 'https://tizen.myget.org/F/dotnet/api/v2/package'
