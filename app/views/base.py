from flask_appbuilder import ModelView


class BaseModelView(ModelView):
    add_exclude_columns = ['created_by', 'changed_by', 'created_on', 'changed_on']
    edit_exclude_columns = ['created_by', 'changed_by', 'created_on', 'changed_on']
    show_exclude_columns = ['created_by', 'changed_by', 'created_on', 'changed_on']
