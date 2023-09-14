from flask_api import status
from flask_restful import Resource, reqparse, abort, wraps
from .executer import ExecuterCaller
from .common import intersect

def _check_roles(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        from . import configure

        if not getattr(func, 'permitted_roles', False):
            
            return func(*args, **kwargs)

        permitted_roles = getattr(func, 'permitted_roles')

        roles = intersect(permitted_roles, configure['AGENT_ROLES'])

        if roles:
            return func(*args, **kwargs)

        abort(406) #Not Acceptable

    return wrapper

class Resource(Resource):
    method_decorators = [_check_roles]   # applies to all inherited resources

class Command(Resource):

    parser = reqparse.RequestParser()
    parser.add_argument('command_code', type=str)
    parser.add_argument('initial_param', type=dict)
    parser.add_argument('executer', type=str)
    #parser.add_argument('items', type=list, location='json')

    def post(self):

        data = Command.parser.parse_args()

        rtn, message = ExecuterCaller.instance().execute_command(data)

        if rtn:
            status_code = status.HTTP_200_OK            
        else:
            status_code = status.HTTP_400_BAD_REQUEST

        return dict(message=message['message']), status_code