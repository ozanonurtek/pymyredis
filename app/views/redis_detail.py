from flask import g, jsonify, request, redirect, url_for, flash
from flask_appbuilder import expose, has_access
from app.models import RedisConnection
from flask import g
from app.redis_manager import redis_manager
from app.views.base import CustomBaseView


class RedisDetailView(CustomBaseView):
    route_base = "/redisdetailview"
    default_view = 'redis_detail'

    @expose('/<int:connection_id>')
    @has_access
    def redis_detail(self, connection_id):
        connection = self.appbuilder.session.query(RedisConnection).get(connection_id)

        if not connection:
            flash("Redis connection not found", "error")
            return redirect(url_for('RedisConnectionView.list'))

        self.save_activity_log(connection.show_activity)

        is_writable = g.user.can_cluster_admin(connection_id) or g.user.can_write(connection_id)
        return self.render_template(
            'redis_detail.html',
            connection=connection,
            can_write=is_writable
        )

    @expose('/<int:connection_id>/execute', methods=['POST'])
    @has_access
    def execute_command(self, connection_id):
        connection = self.appbuilder.session.query(RedisConnection).get(connection_id)
        if not connection:
            return jsonify({'error': 'Connection not found'}), 404

        command = request.json.get('command')

        can_execute = ((command.startswith("keys") or command.startswith("get")) or \
                       g.user.can_cluster_admin(connection_id)) or (
                              g.user.can_write(connection_id) and command.startswith("set"))

        if not can_execute:
            self.save_activity_log(connection.execute_activity(command, "Unauthorized"))
            return jsonify({'error': 'You do not have permission to execute this command'}), 403

        try:
            result = redis_manager.execute_command(connection.id, command)
            if isinstance(result, list):
                result = [r.decode('utf-8') if isinstance(r, bytes) else r for r in result]
            else:
                result = result.decode('utf-8') if isinstance(result, bytes) else result

            self.save_activity_log(connection.execute_activity(command, "Authorized. Executed successfuly"))
            return jsonify({'result': result})
        except Exception as e:
            err = str(e)
            self.save_activity_log(connection.execute_activity(command, f"Authorized. Failed to execute: {err}"))
            return jsonify({'error': err}), 500
