# Copyright 2014 Symantec Corporation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import shlex
import string

from magnetodb import policy
from magnetodb.api.openstack.v1 import utils
from magnetodb.common import setup_global_env
from magnetodb.openstack.common.log import logging


LOG = logging.getLogger(__name__)


def enforce_policy(rule):
    def decorator(f):
        def wrapper(self, *args, **kwargs):
            context = args[0].context
            project_id = kwargs.get('project_id')
            utils.check_project_id(context, project_id)
            policy.enforce(context, rule, {})
            LOG.debug('RBAC: Authorization granted')
            return f(self, *args, **kwargs)
        return wrapper
    return decorator


def with_global_env(default_program=None):
    def decorator(f):
        def wrapped(global_conf, **local_conf):
            options = dict(global_conf.items() + local_conf.items())
            oslo_config_args = options.get("oslo_config_args")
            program = options.get("program", default_program)
            s = string.Template(oslo_config_args)
            oslo_config_args = shlex.split(s.substitute(**options))
            setup_global_env(program, oslo_config_args)
            return f(global_conf, **local_conf)
        return wrapped
    return decorator
