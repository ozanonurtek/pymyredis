from app.views.base import BaseModelView
from flask_appbuilder import action

from flask_appbuilder.models.sqla.interface import SQLAInterface
from app.models import TeamRedisRole


class TeamRedisRoleView(BaseModelView):
    datamodel = SQLAInterface(TeamRedisRole)
    list_columns = ['team', 'connection', 'permission']
    # list_columns = ['name', 'description', 'redis_roles']
    # add_columns = ['name', 'description', 'users', 'redis_roles']
    # edit_columns = ['name', 'description', 'users', 'redis_roles']
    # show_columns = ['name', 'description', 'users', 'redis_roles']
