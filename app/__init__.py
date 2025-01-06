from flask import Flask
from flask_appbuilder import AppBuilder, SQLA

import os
appbuilder = None
db = None



def create_app():
    app = Flask(__name__)
    config_path = os.getenv('FLASK_CONFIG', 'config')
    app.config.from_object(config_path)
    global db
    db = SQLA(app)
    create_views(app)
    return app


def create_views(app):
    global appbuilder

    from app.security import PyMyRedisSecurityManager
    from app.index_view import PyMyRedisIndexView

    appbuilder = AppBuilder(app, db.session, security_manager_class=PyMyRedisSecurityManager,
                            indexview=PyMyRedisIndexView)

    from app.views.redis_connection import RedisConnectionView
    from app.views.redis_detail import RedisDetailView
    from app.views.team import TeamView
    from app.views.team_redis_role import TeamRedisRoleView
    from app.views.activity import ActivityView

    appbuilder.add_view(RedisConnectionView, "Connections", icon="fa-database")
    appbuilder.add_view(TeamView, "Teams", icon="fa-users")
    appbuilder.add_view(TeamRedisRoleView, "TeamRedisRole", icon="fa-vcard")
    appbuilder.add_view(ActivityView, 'ActivityFeed', icon="fa-file-text-o")
    appbuilder.add_view_no_menu(RedisDetailView)
