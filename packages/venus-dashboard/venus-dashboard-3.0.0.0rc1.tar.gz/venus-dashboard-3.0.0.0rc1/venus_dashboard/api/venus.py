# Copyright 2021 Inspur
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

from horizon.utils.memoized import memoized
from keystoneauth1.identity.generic.token import Token
from keystoneauth1.session import Session
from openstack_dashboard.api import base
from venusclient.v1 import client

LOG = logging.getLogger(__name__)


@memoized
def venusclient(request):
    endpoint = base.url_for(request, 'identity')
    token_id = request.user.token.id
    tenant_name = request.user.tenant_name
    project_domain_id = request.user.token.project.get('domain_id', 'Default')
    auth = Token(auth_url=endpoint,
                 token=token_id,
                 project_name=tenant_name,
                 project_domain_id=project_domain_id)
    session = Session(auth=auth, timeout=600)
    return client.Client(session=session)


def log_storage_days(request):
    return venusclient(request).config.get_days()


def logs(request, start_time, end_time, page_size, page_num, module_name,
         host_name, program_name, level):
    return venusclient(request).search.get_log(start_time=start_time,
                                               end_time=end_time,
                                               page_size=page_size,
                                               page_num=page_num,
                                               module_name=module_name,
                                               host_name=host_name,
                                               program_name=program_name,
                                               level=level)


def analysis(request, start_time, module_name, host_name,
             end_time, program_name, group_name, level):
    return venusclient(request).analyse.analyse_log(start_time=start_time,
                                                    end_time=end_time,
                                                    module_name=module_name,
                                                    host_name=host_name,
                                                    program_name=program_name,
                                                    level=level)
