# -*- coding: UTF-8 -*-
# Copyright 2022-2023 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import asyncio
import os
import threading
from channels.layers import get_channel_layer
from django.core.management import BaseCommand, call_command
from django.conf import settings
from lino.modlib.linod.utils import LINOD


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--force',
                            help="Force starts the runworker process even if a log_socket_file exists."
                                 " Use only in production server.",
                            action="store_true",
                            default=False
                            )
        parser.add_argument("--skip-system-tasks",
                            help="Skips the system tasks coroutine",
                            action="store_true",
                            default=False)

    def handle(self, *args, **options):

        def start_worker():
            try:
                asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            call_command('runworker', LINOD)

        log_sock_file = settings.SITE.site_dir / 'log_sock'

        if log_sock_file.exists() and not options.get('force'):
            raise Exception(
                f"log socket already exists: {log_sock_file}\n"
                "It's probable that a worker process is already running. "
                "Try: 'ps awx | grep lino_runworker' OR 'sudo supervisorctl status | grep worker'\n"
                "Or the last instance of the worker process did not finish properly. "
                "In that case remove the 'log_sock' file and run this command again.")

        try:
            os.remove(str(settings.SITE.site_dir / "worker_sock"))
        except FileNotFoundError:
            pass

        try:
            os.remove(log_sock_file)
        except FileNotFoundError:
            pass

        worker_thread = threading.Thread(target=start_worker)
        worker_thread.start()

        async def initiate_linod():
            layer = get_channel_layer()
            await layer.send(LINOD, {'type': 'log.server'})
            await asyncio.sleep(1)
            if not options.get("skip_system_tasks"):
                await layer.send(LINOD, {'type': 'run.system.tasks'})

        loop = asyncio.get_event_loop()
        loop.run_until_complete(initiate_linod())

        try:
            worker_thread.join()
        except KeyboardInterrupt:
            worker_thread.join(0)
