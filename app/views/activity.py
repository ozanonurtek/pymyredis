from app.views.base import BaseModelView
from flask_appbuilder import action

from flask_appbuilder.models.sqla.interface import SQLAInterface
from app.models import Activity


class ActivityView(BaseModelView):
    datamodel = SQLAInterface(Activity)
    list_columns = ['created_by', 'created_on', 'message']
    search_columns = ['created_by', 'created_on', 'message']
    base_permissions = ['can_list']
