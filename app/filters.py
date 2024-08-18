from flask import g
from flask_appbuilder.models.sqla.filters import BaseFilter
from app.models import TeamRedisRole, Team, user_team




class CanListConnectionFilter(BaseFilter):
    name = "CanListConnectionFilter"
    arg_name = "canlistconnection"

    def apply(self, query, value):
        if g.user.is_fab_admin():
            return query

        return query.join(TeamRedisRole). \
            join(Team, Team.id == TeamRedisRole.team_id). \
            join(user_team, user_team.c.team_id == Team.id). \
            filter(user_team.c.user_id == g.user.id)
