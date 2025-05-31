from .models import Task

from datetime import datetime,timedelta

def cron_task():
    # print("cron task")
    in_progress_tasks = Task.objects.filter(status="in_progress")
    now = datetime.now()
    timeout_period_transcription = now - timedelta(days=30)
    timeout_period_verification = now - timedelta(days=7)

    for task in in_progress_tasks:

        if task.started.timestamp() < timeout_period_transcription.timestamp() and task.type=="transcription":# and task.id >= 113 :
            task.status = "timeout"
            task.ended=datetime.now()
            task.save()
            task.document.status = "to_transcribe"
            task.document.save()

        elif task.started.timestamp() < timeout_period_verification.timestamp() and task.type=="verification":# and task.id >= 113 :
            task.status = "timeout"
            task.ended=datetime.now()
            task.save()
            task.document.status = "to_verify"
            task.document.save()