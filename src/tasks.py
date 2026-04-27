# /tasks.py
"""
Импортируйте все таски для воркеров taskiq и запуска в терминале единой командой

`taskiq worker src.config.tkq:broker src.tsq_tasks`
"""

from src.services.mailing import send_email_task
