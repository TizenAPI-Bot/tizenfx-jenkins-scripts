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

"""Jenkins script to release TizenFX"""

import os
import re
import sys
import glob
from datetime import datetime, timezone, timedelta

import global_configuration as conf
from common.project import Project, ProjectError, ProjectNotFoundException
from common.shell import ShellError, sh


def main():
    env = BuildEnvironment(os.environ)

    if env.github_branch_name not in conf.BRANCH_API_LEVEL_MAP.keys():
        print('{} branch is not a managed branch.\n'
              .format(env.github_branch_name))
        return

    # 1. Build Project
    proj = Project(env)
    proj.build(with_analysis=False, dummy=True, pack=True)

    # 2. Push to MyGet
    proj.push_nuget_packages(env.myget_apikey, conf.MYGET_PUSH_FEED)

    # 3. Sync to Tizen Git Repository
    category = conf.BRANCH_API_LEVEL_MAP[env.github_branch_name]
    version = '{}.{}'.format(
        conf.VERSION_PREFIX_MAP[category], proj.commit_count + 10000)
    gerrit_branch = conf.GERRIT_BRANCH_MAP[category]

    sshopt = 'ssh -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
    sh('''
        git config --local user.name "TizenAPI-Bot"
        git config --local user.email "tizenapi@samsung.com"
        git config core.sshCommand '{sshopt}'
    '''.format(sshopt=sshopt), cwd=proj.workspace)

    sh('''
        git remote add gerrit {gerrit_url}
        git fetch gerrit {gerrit_branch}
        git checkout -t gerrit/{gerrit_branch}
        git merge --no-edit -s recursive -X theirs origin/{github_branch}
        ./packaging/makespec.sh -r {version} -n {version} -i {version}
        git add packaging/
    '''.format(version=version, sshopt=sshopt,
               gerrit_url=conf.GERRIT_GIT_URL, gerrit_branch=gerrit_branch,
               github_branch=env.github_branch_name), cwd=proj.workspace)

    modified = sh('git diff --cached --numstat | wc -l',
                  cwd=proj.workspace, return_stdout=True, print_stdout=False)
    if int(modified.strip()) > 0:
        dt = datetime.utcnow() + timedelta(hours=9)
        submit_tag = 'submit/{}/{:%Y%m%d.%H%M%S}'.format(gerrit_branch, dt)
        sh('''
            git commit -m "Release {version}"
            git tag -m "Release {version}" {submit_tag}
            git push -f gerrit {gerrit_branch}
            git push --tags gerrit {gerrit_branch}
        '''.format(version=version, submit_tag=submit_tag,
                   gerrit_branch=gerrit_branch), cwd=proj.workspace)
    else:
        print("No changes to publish. Skip publishing to Tizen git repo.")


class NotValidEnvironmentException(Exception):
    """Raised when there are no requried environment variables."""
    pass


class BuildEnvironment:

    def __init__(self, env):
        try:
            self.github_branch_name = env['GITHUB_BRANCH_NAME']
            self.workspace = env['WORKSPACE']
            self.myget_apikey = env['MYGET_APIKEY']
        except KeyError:
            raise NotValidEnvironmentException()


if __name__ == "__main__":
    try:
        main()
    except NotValidEnvironmentException:
        sys.stderr.write(
            "Error: No required environment variables to run checkers.\n")
        sys.exit(1)
    except ProjectNotFoundException:
        sys.stderr.write("Error: No such found project to build.\n")
        sys.exit(1)
    except ProjectError as err:
        sys.stderr.write("Error: " + err.message + '\n')
        sys.exit(1)
    except ShellError as err:
        sys.stderr.write("Error: " + err.message + '\n')
        sys.exit(1)
