from flask import redirect, url_for
from flask_appbuilder import IndexView, expose
from flask_login import current_user


class PyMyRedisIndexView(IndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect("/login")
        return super().index()
