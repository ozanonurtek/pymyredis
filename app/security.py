from flask_appbuilder.security.sqla.manager import SecurityManager
from app.enums import TeamRedisPermission
from app.models import ExtendUser
import logging

log = logging.getLogger(__name__)


class PyMyRedisSecurityManager(SecurityManager):
    def __init__(self, appbuilder):
        super(PyMyRedisSecurityManager, self).__init__(appbuilder)
        self.create_custom_roles()
        self.appbuilder = appbuilder

    user_model = ExtendUser

    def create_custom_roles(self):
        read_values = ['can_list',
                       'can_show', 'can_redis_detail', 'menu_access', 'view_details', 'can_execute_command',
                       ]

        values = {
            'RedisConnectionView': read_values,
            'RedisDetailView': read_values,
            'Connections': read_values
        }
        custom_roles = {
            TeamRedisPermission.READ.value: values,
            TeamRedisPermission.READ_WRITE.value: values,
            TeamRedisPermission.CLUSTER_ADMIN.value: values,
        }

        for role_name, role_config in custom_roles.items():
            role = self.find_role(role_name)
            if not role:
                try:
                    role = self.add_role(role_name)
                except Exception as e:
                    log.error(f"Error adding role {role_name}: {str(e)}")
                    continue

            for view, permissions in role_config.items():
                for permission in permissions:
                    pvm = self.find_permission_view_menu(permission, view)
                    if not pvm:
                        self.add_permission_view_menu(permission, view)
                    pvm = self.find_permission_view_menu(permission, view)
                    if pvm and pvm not in role.permissions:
                        self.add_permission_role(role, pvm)

# def create_admin():
#     from app import appbuilder
#     sm = appbuilder.sm
#     user = sm.find_user(username="admin")
#     if not user:
#         admin_role = sm.find_role(sm.auth_role_admin)
#         redis_ui_admin_role = sm.find_role("redis-ui-admin")
#
#         user = sm.add_user(
#             username="admin",
#             first_name="Admin",
#             last_name="User",
#             email="admin@example.com",
#             role=[admin_role, redis_ui_admin_role],
#             password="password"
#         )
#         if user:
#             log.info("Admin user created")
#         else:
#             log.error("Failed to create admin user")
#     else:
#         log.info("Admin user already exists")
