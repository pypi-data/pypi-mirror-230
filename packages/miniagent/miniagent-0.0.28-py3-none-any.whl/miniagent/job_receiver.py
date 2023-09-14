from datetime import datetime, timedelta
from . import scheduler
from .executer import ExecuterCaller
from .common import intersect
import os
import logging

class ScheduledJob:

    def __init__(self, caller: ExecuterCaller, jobs: list, exit_after_jobs: bool=False) -> None:

        self.caller = caller
        for job in jobs:
            self._run_job(job)

        if exit_after_jobs:
            self._trigger_suicide_bomber()

    def _run_job(self, job: dict) -> int:

        executer = job.pop('executer')

        from . import configure
        if job.get('agents'):
            agents = job.pop('agents')
            if configure['AGENT_NAME'] not in agents:
                return 0

        if job.get('agent_roles'):
            roles = job.pop('agent_roles')
            if not intersect(configure['AGENT_ROLES'], roles):
                return 0

        param = dict(
                    executer=executer,
                    initial_param={'job_id':job['id']}
                 )

        if job.get('params'):
            params = job.pop('params')
            param['initial_param'].update(params)
        
        scheduler.add_job(
            func=self._call_execute_command,
            args=[job['id'], param],
            **job
        )

        logging.info("Job is added. job_id : "+ job['id'])

        return 1
    
    def _call_execute_command(self, id: str, message: dict):

        from . import app, zipkin
        with app.app_context():

            if zipkin:
                zipkin.create_span('scheduled_job.'+ id)
                zipkin.update_tags(param=message)

            rtn, comment = self.caller.execute_command(message)

            if zipkin:
                zipkin.update_tags(
                    param  = message,
                    result = comment,
                )

    def _trigger_suicide_bomber(self):
                
        scheduler.add_job(
            id='commit_suicide',
            func=self._commit_suicide,
            trigger='interval', 
            seconds=10
        )

        logging.info("Suicide job is started. job_id : commit_suicide")

    def _commit_suicide(self):

        p = [ j.id for j in scheduler.get_jobs() if j.id != 'commit_suicide']
        if not p:
            logging.info("Program is killed by commit_suicide job.")
            os._exit(0) # completed normally