from flask_appbuilder import ModelView, BaseView, expose, has_access
from app.models import Activity


class CustomBaseView(BaseView):
    def save_activity_log(self, log_message):
        activity = Activity()
        activity.message = log_message
        self.appbuilder.session.add(activity)
        self.appbuilder.session.commit()


class BaseModelView(ModelView):
    add_exclude_columns = ['created_by', 'changed_by', 'created_on', 'changed_on']
    edit_exclude_columns = ['created_by', 'changed_by', 'created_on', 'changed_on']
    show_exclude_columns = ['created_by', 'changed_by', 'created_on', 'changed_on']

    def save_activity_log(self, log_message):
        activity = Activity()
        activity.message = log_message
        self.appbuilder.session.add(activity)
        self.appbuilder.session.commit()

    def post_update(self, item):
        self.save_activity_log(item.updated_activity)
        super().post_update(item)

    def post_add(self, item):
        self.save_activity_log(item.created_activity)
        super().post_add(item)

    def post_delete(self, item):
        self.save_activity_log(item.deleted_activity)
        super().post_delete(item)

    @expose('/show/<pk>', methods=['GET'])
    @has_access
    def show(self, pk):
        item = self.datamodel.get(pk)
        if item:
            self.save_activity_log(item.show_activity)
        return super().show(pk)

    @expose('/list/', methods=['GET'])
    @has_access
    def list(self):
        log_message = f'{self.datamodel.model_name} has been listed.'
        self.save_activity_log(log_message)
        return super().list()
