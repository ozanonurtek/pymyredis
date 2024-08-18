# from flask import g
# from app.models import TeamRedisRole, TeamRedisPermission, ExtendUser, Team, user_team
# from app import db
#
#
# def get_user_id():
#     return g.user.id
#
#
# def is_fab_admin():
#     user = g.user
#     return user.roles and any(role.name == 'Admin' for role in user.roles)
#
#
# def get_user_teams():
#     return db.session.query(Team).join(user_team, Team.id == user_team.c.team_id).filter(user_team.c.user_id == get_user_id()).all()
#
#
# def get_allowed_connection_ids(session):
#     data = db.session.query(TeamRedisRole.connection_id).distinct(). \
#         join(Team, Team.id == TeamRedisRole.team_id). \
#         join(user_team, user_team.c.team_id == Team.id). \
#         filter(user_team.c.user_id == get_user_id())
#     return [row[0] for row in data]  # Return a list of IDs
#
#
# def get_user_redis_roles(redis_connection_id):
#     teams = get_user_teams()
#     ids = [team.id for team in teams]
#     permissions = db.session.query(TeamRedisRole).filter(
#         TeamRedisRole.team_id.in_(ids),
#         TeamRedisRole.connection_id == redis_connection_id
#     ).all()
#     return [p.permission for p in permissions]
#
#
# def can_read(redis_connection_id):
#     if is_fab_admin():
#         return True
#
#     permissions = get_user_redis_roles(redis_connection_id)
#     for permission in permissions:
#         if permission == TeamRedisPermission.READ:
#             return True
#
#     return False
#
#
# def can_write(redis_connection_id):
#     if is_fab_admin():
#         return True
#     permissions = get_user_redis_roles(redis_connection_id)
#     for permission in permissions:
#         if permission == TeamRedisPermission.READ_WRITE:
#             return True
#
#     return False
#
#
# def can_cluster_admin(redis_connection_id):
#     if is_fab_admin():
#         return True
#     permissions = get_user_redis_roles(redis_connection_id)
#     for permission in permissions:
#         if permission == TeamRedisPermission.CLUSTER_ADMIN:
#             return True
#
#     return False
