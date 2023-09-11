# MIT License
#
# Copyright (c) 2018 Evgeny Medvedev, evge.medvedev@gmail.com
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
import logging

from heath_check.common.base.executors.batch_work_executor import BatchWorkExecutor
from heath_check.common.base.jobs.base_job import BaseJob
from heath_check.check_rule.telnet_rule_check import telnet_rule_check
from heath_check.model import HealthCheckService

logger = logging.getLogger(__name__)

HEALTH_CHECK_RULE_DEFAULT = {
    "telnet": telnet_rule_check
}


class MultiThreadsHeathCheckJob(BaseJob):
    def __init__(
            self,
            work_iterable: list[HealthCheckService],
            max_workers=100,
            batch_size=5,
    ):
        self.work_iterable: list[HealthCheckService] = work_iterable
        self.batch_work_executor = BatchWorkExecutor(batch_size, max_workers)
        self._dict_cache = []
        self.max_workers = max_workers
        self.result = {}
        self.health_check_rule = HEALTH_CHECK_RULE_DEFAULT

    def add_health_check_rule(self, rule_name, rule_func):
        self.health_check_rule[rule_name] = rule_func

    def _start(self):
        # self.item_exporter.open()
        pass

    def _export(self):

        self.batch_work_executor.execute(
            self.work_iterable,
            self._export_batch,
            total_items=len(self.work_iterable)
        )

    def _export_batch(self, work_data: list[HealthCheckService]):
        for health_check_service in work_data:
            rule_name = health_check_service.type
            rule_func = self.health_check_rule.get(rule_name)
            if rule_func:
                rule_func(health_check_service)

    def _end(self):
        self.batch_work_executor.shutdown()
        # self.item_exporter.close()
        pass

    def get_result(self):

        return self.work_iterable


