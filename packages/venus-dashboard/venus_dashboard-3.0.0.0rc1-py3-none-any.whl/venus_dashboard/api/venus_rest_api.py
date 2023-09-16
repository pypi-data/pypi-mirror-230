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

from django.views import generic
import logging
from openstack_dashboard.api.rest import urls
from openstack_dashboard.api.rest import utils as rest_utils
from venus_dashboard.api import venus

LOG = logging.getLogger(__name__)


@urls.register
class LogStorageDays(generic.View):
    url_regex = r'venus/log_storage_days$'

    @rest_utils.ajax()
    def get(self, request):
        return venus.log_storage_days(request)


@urls.register
class Logs(generic.View):
    url_regex = r'venus/search/logs$'

    @rest_utils.ajax()
    def get(self, request):
        start_time = request.GET.get('start_time', 0)
        end_time = request.GET.get('end_time', 0)
        page_size = request.GET.get('page_size', 20)
        page_num = request.GET.get('page_num', 1)
        module_name = request.GET.get('module_name', '')
        host_name = request.GET.get('host_name', '')
        program_name = request.GET.get('program_name', '')
        level = request.GET.get('level', '')
        return venus.logs(request, start_time, end_time, page_size, page_num,
                          module_name, host_name, program_name, level)


@urls.register
class Analysis(generic.View):
    url_regex = r'venus/v1/search/analyse/logs$'

    @rest_utils.ajax()
    def get(self, request):
        start_time = request.GET.get('start_time', 0)
        end_time = request.GET.get('end_time', 0)
        module_name = request.GET.get('module_name', '')
        host_name = request.GET.get('host_name', '')
        program_name = request.GET.get('program_name', '')
        group_name = request.GET.get('group_name', '')
        level = request.GET.get('level', '')
        return venus.analysis(request, start_time, module_name, host_name,
                              end_time, program_name, group_name, level)
