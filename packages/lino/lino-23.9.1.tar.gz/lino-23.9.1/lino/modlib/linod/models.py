# -*- coding: UTF-8 -*-
# Copyright 2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)
# See https://dev.lino-framework.org/plugins/linod.html

import logging
import sys
import traceback
from django.conf import settings
from django.utils.timezone import now

from lino.api import dd, rt, _

from lino.core.roles import SiteStaff
from lino.mixins import Sequenced

from lino.modlib.system.mixins import RecurrenceSet
from .choicelists import Procedures, Procedure, LogLevels

logger = logging.getLogger(__name__)


class SetupTasks(dd.Action):
    """Run this only in development environment."""
    label = _("Setup tasks")
    help_text = _("Run this action only in development environment (not designed for production environment).")
    select_rows = False

    def run_from_ui(self, ar, **kwargs):
        if not settings.SITE.is_demo_site:
            ar.error(message="Action is not allowed in production site.")
            return
        from lino.modlib.linod.tasks import Tasks
        Tasks().setup()
        ar.success(refresh_all=True)


class RunNow(dd.Action):
    label = _("Run job")
    select_rows = True

    def run_from_ui(self, ar, **kwargs):
        for rule in ar.selected_rows:
            if not isinstance(rule, rt.models.linod.JobRule):
                continue
            rule.run(ar)
        ar.set_response(refresh_all=True)


class JobRule(Sequenced, RecurrenceSet):
    class Meta:
        abstract = dd.is_abstract_model(__name__, 'JobRule')
        app_label = 'linod'
        verbose_name = _("Job rule")
        verbose_name_plural = _("Job rules")

    name = dd.CharField(max_length=50, default="", blank=True)
    procedure = Procedures.field(strict=False)
    log_level = LogLevels.field(default='debug')
    cancelled = dd.BooleanField(default=False)

    setup_tasks = SetupTasks()
    run_now = RunNow()

    def disabled_fields(self, ar):
        df = super().disabled_fields(ar)
        df.add('procedure')
        return df

    def put_message(self, msg, level, *whom):
        for who in whom:
            getattr(who, level)(msg)

    def run(self, ar, lgr=None):
        if lgr is None:
            lgr = logger
        lgr.debug(f"running rule: {self!r}")
        Job = rt.models.linod.Job
        job = Job(rule=self)
        job.full_clean()
        job.save_new_instance(ar)
        sar = self.get_default_table().request(parent=ar)
        try:
            self.procedure.run(sar)
            self.put_message(f"successfully run: {job}", 'debug', lgr, ar, sar)
        except Exception as e:
            self.put_message(f"job failed: {self!r}", 'warning', lgr, ar, sar)
            self.cancelled = True
            self.save()
            excinfo = sys.exc_info()
            err = traceback.print_exception(excinfo, excinfo[1], excinfo[2])
            self.put_message(err, 'error', lgr, ar, sar)
        levels = ['debug', 'info', 'warning', 'error', 'critical']
        job.message = "\n".join([msg for msg in
                    [sar.response.get(level + '_message', "") for level in levels[levels.index(self.log_level.name):]]
                    if msg != ""])
        job.save()
        Job.objects.exclude(
            pk__in=list(Job.objects.filter(
                rule=self
            ).order_by("-start_datetime").values_list('pk', flat=True)[:dd.plugins.linod.remove_after])
        ).filter(rule=self).delete()
        return job

    def __str__(self):
        r = f"Job rule #{self.pk} {self.procedure.value}"
        if self.cancelled:
            r += " ('cancelled')"
        return r

    def __repr__(self):
        r = f"Job rule #{self.pk} <{self.procedure!r}>"
        if self.cancelled:
            r += " ('cancelled')"
        return r


class Job(dd.Model):
    allow_cascaded_delete = ['rule']

    class Meta:
        abstract = dd.is_abstract_model(__name__, 'Job')
        app_label = 'linod'
        verbose_name = _("Job")
        verbose_name_plural = _("Jobs")
        ordering = ('-start_datetime',)

    start_datetime = dd.DateTimeField(auto_now=True, editable=False)
    rule = dd.ForeignKey('linod.JobRule', null=False, blank=False, editable=False)
    message = dd.TextField(editable=False)

    def __str__(self):
        r = f"Job #{self.pk} {self.rule}"
        return r


class Jobs(dd.Table):
    label = _("Task history")
    model = 'linod.Job'
    required_roles = dd.login_required(SiteStaff)
    column_names = "start_datetime rule message *"
    detail_layout = """
    start_datetime rule
    message
    """


class JobsByRule(Jobs):
    master_key = 'rule'
    column_names = "start_datetime message *"


class JobRules(dd.Table):
    label = _("System tasks")
    model = 'linod.JobRule'
    required_roles = dd.login_required(SiteStaff)
    column_names = "name procedure every every_unit log_level cancelled *"
    detail_layout = """
    name every every_unit procedure
    log_level cancelled
    linod.JobsByRule
    """
    insert_layout = """
    name
    every every_unit
    procedure
    """
