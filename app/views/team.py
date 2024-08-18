from app.views.base import BaseModelView
from flask_appbuilder import action

from flask_appbuilder.models.sqla.interface import SQLAInterface
from app.models import Team


class TeamView(BaseModelView):
    datamodel = SQLAInterface(Team)

    list_columns = ['name', 'description', 'users']
    add_columns = ['name', 'description', 'users']
    edit_columns = ['name', 'description', 'users']
    show_columns = ['name', 'description', 'users']
