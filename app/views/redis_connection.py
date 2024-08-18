from flask import redirect, url_for, flash, g
from app.views.base import BaseModelView
from flask_appbuilder import action
from flask_appbuilder.models.sqla.interface import SQLAInterface
from app.models import RedisConnection
from app.redis_manager import redis_manager
from app.filters import CanListConnectionFilter


class RedisConnectionView(BaseModelView):
    datamodel = SQLAInterface(RedisConnection)
    # list_template = 'list_redis_cards.html'
    base_permissions = ['can_list', 'can_show', 'can_add', 'can_edit', 'can_delete']
    list_columns = ['name', 'deployment_type', 'description', 'info', 'details']
    add_columns = ['name', 'deployment_type', 'description', 'host', 'port', 'db',
                   'sentinel_hosts', 'sentinel_master', 'master_host', 'master_port',
                   'slave_hosts', 'cluster_nodes', 'password']
    edit_columns = ['name', 'deployment_type', 'description', 'host', 'port', 'db',
                    'sentinel_hosts', 'sentinel_master', 'master_host', 'master_port',
                    'slave_hosts', 'cluster_nodes', 'password']
    show_columns = ['name', 'deployment_type', 'description', 'host', 'port', 'db',
                    'sentinel_hosts', 'sentinel_master', 'master_host', 'master_port',
                    'slave_hosts', 'cluster_nodes']

    base_filters = [('id', CanListConnectionFilter, ())]

    def _list(self):
        # widgets = self._list()
        query = self.datamodel.session.query(self.datamodel.obj)

        # Apply base filters
        query = self._base_filters.apply_all(query)

        # Apply any additional filters (if needed)
        # query = self.apply_additional_filters(query)  # Uncomment if you have additional filters

        # Get the items
        items = query.all()

        redis_info = []
        for item in items:
            info = redis_manager.get_redis_info(item)
            redis_info.append(info)
        return super()._list()

    # @expose('/list/')
    # @has_access
    # def list(self):
    #     widgets = self._list()
    #     query = self.datamodel.session.query(self.datamodel.obj)
    #
    #     # Apply base filters
    #     query = self._base_filters.apply_all(query)
    #
    #     # Apply any additional filters (if needed)
    #     # query = self.apply_additional_filters(query)  # Uncomment if you have additional filters
    #
    #     # Get the items
    #     items = query.all()
    #
    #     redis_info = []
    #     for item in items:
    #         info = self.get_redis_info(item)
    #         redis_info.append(info)
    #
    #     return self.render_template(
    #         self.list_template,
    #         title=self.list_title,
    #         widgets=widgets,
    #         redis_connections=zip(items, redis_info)
    #     )

    @action("test_connection", "Test Connection", "Are you sure you want to test this connection?", "fa-bolt",
            single=False)
    def test_connection(self, selected_items):

        items = selected_items
        if not isinstance(selected_items, list):
            items = list()
            items.append(selected_items)

        for item in items:
            try:
                if not g.user.can_read(item.id):
                    raise Exception("Unauthorized to read this cluster")
                redis_manager.test_connection(item)
                flash(f"Successfully connected to {item.name}", "success")
            except Exception as e:
                flash(f"Failed to connect to {item.name}: {str(e)}", "error")
            return redirect(url_for('RedisConnectionView.list'))
