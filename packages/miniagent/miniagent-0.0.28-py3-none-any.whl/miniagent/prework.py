from .executer import ExecuterCaller
from .common import intersect, ExitType
import os

class Prework:

    def __init__(self,
                 caller: ExecuterCaller, 
                 preworks: list,
                 agent_roles: list) -> None:

        self.caller = caller
        
        for prework in preworks:

            if prework.get('agent_roles') \
                and not intersect(agent_roles, prework.get('agent_roles')):
                continue
            if not prework.get('executer'):
                continue

            self._do_prework(prework)

    def _do_prework(self, prework: dict):
        
        from . import app, zipkin
        rtn = 0

        with app.app_context():

            if zipkin:

                zipkin.create_span('prework')
                zipkin.update_tags(param=prework)

            rtn, results = self.caller.execute_command(prework)

            if zipkin:
                zipkin.update_tags(
                    param  = prework,
                    result = results,
                )

        if rtn == ExitType.NORMAL_EXIT.value:
            os._exit(0)
        elif rtn == ExitType.ABNORMAL_EXIT.value:
            os._exit(1)