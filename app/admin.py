from django.contrib import admin

from goal.models import Goal #goal table (goalテーブル)
from .models import Task #task table (taskテーブル)
from goal.models import TaskByAI #task_by_AI tabel (task_by_AI テーブル)
from mycalendar.models import Events

#from .models import Comic #comic table (comic テーブル)
#from .models import Panel #panel table (panle　テーブル)
admin.site.register(Goal)
admin.site.register(Task)
admin.site.register(TaskByAI)
admin.site.register(Events)

#admin.site.register(Comic)
#admin.site.register(Panel)
