from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Enum, Text
from sqlalchemy.orm import relationship
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder.security.sqla.models import User
from app.enums import TeamRedisPermission, RedisDeploymentType
from flask_login import current_user
from markupsafe import Markup
from flask import url_for
from datetime import datetime

user_team = Table('user_team', Model.metadata,
                  Column('user_id', Integer, ForeignKey('ab_user.id')),
                  Column('team_id', Integer, ForeignKey('team.id'))
                  )


class BaseModel(Model, AuditMixin):
    __abstract__ = True

    @property
    def created_activity(self):
        return f"{self.__class__.__name__} with id: {self.id} and properties {self.__repr__()} has been created."

    @property
    def updated_activity(self):
        return f"{self.__class__.__name__} with id: {self.id} and properties {self.__repr__()} has been updated."

    @property
    def deleted_activity(self):
        return f"{self.__class__.__name__} with id: {self.id} and properties {self.__repr__()} has been deleted."

    @property
    def show_activity(self):
        return f"{self.__class__.__name__} with id: {self.id} and properties {self.__repr__()} has been displayed."


class ExtendUser(User):
    __tablename__ = "ab_user"
    teams = relationship('Team', secondary=user_team, back_populates='users')

    def is_fab_admin(self):
        return self.roles and any(role.name == 'Admin' for role in self.roles)

    def get_allowed_connection_ids(self):
        ids = []
        for team in self.teams:
            for role in team.redis_roles:
                ids.append(role.connection_id)
        return ids

    def get_user_redis_roles(self, redis_connection_id):
        permissions = []
        for team in self.teams:
            for role in team.redis_roles:
                permissions.append(role.permission)
        return permissions

    def can_read(self, redis_connection_id):
        if self.is_fab_admin():
            return True

        permissions = self.get_user_redis_roles(redis_connection_id)
        for permission in permissions:
            if permission == TeamRedisPermission.READ:
                return True

        return False

    def can_write(self, redis_connection_id):
        if self.is_fab_admin():
            return True
        permissions = self.get_user_redis_roles(redis_connection_id)
        for permission in permissions:
            if permission == TeamRedisPermission.READ_WRITE:
                return True

        return False

    def can_cluster_admin(self, redis_connection_id):
        if self.is_fab_admin():
            return True
        permissions = self.get_user_redis_roles(redis_connection_id)
        for permission in permissions:
            if permission == TeamRedisPermission.CLUSTER_ADMIN:
                return True

        return False


class RedisConnection(BaseModel):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    deployment_type = Column(Enum(RedisDeploymentType), nullable=False)
    description = Column(String(256))

    # Standalone and general fields
    host = Column(String(128))
    port = Column(Integer)
    db = Column(Integer)

    # Sentinel specific fields
    sentinel_hosts = Column(String(512))  # Comma-separated list of host:port
    sentinel_master = Column(String(50))

    # Master-Slave specific fields
    master_host = Column(String(128))
    master_port = Column(Integer)
    slave_hosts = Column(String(512))  # Comma-separated list of host:port

    # Cluster specific fields
    cluster_nodes = Column(String(1024))  # Comma-separated list of host:port

    # Password field (optional, for all types)
    password = Column(String(256))
    team_roles = relationship('TeamRedisRole', back_populates='connection', cascade='all, delete-orphan')

    def details(self):
        return Markup('<a href="' + url_for('RedisDetailView.redis_detail',
                                            connection_id=self.id) + '"><button class="btn-primary btn-block">Details</button></a>')

    def info(self):
        # This is bad
        from app.redis_manager import redis_manager

        info = redis_manager.get_redis_info(self)
        return Markup(f'<span> CPU: {info["cpu_usage"]} | RAM: {info["memory_usage"]} </span>')

    def __repr__(self):
        return f"{self.name} - {self.description}"

    def execute_activity(self, command, result):
        return f"Following command: {command} has been executed on {self.__class__.__name__} with id: {self.id} and properties {self.__repr__()}. Execution result: {result}"


class Team(BaseModel):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(String(256))
    users = relationship('ExtendUser', secondary=user_team, back_populates='teams')
    redis_roles = relationship('TeamRedisRole', back_populates='team', cascade='all, delete-orphan')

    def __repr__(self):
        return self.name


class TeamRedisRole(BaseModel):
    id = Column(Integer, primary_key=True)
    team_id = Column(Integer, ForeignKey('team.id'), nullable=False)
    connection_id = Column(Integer, ForeignKey('redis_connection.id'), nullable=False)
    permission = Column(Enum(TeamRedisPermission), nullable=False)

    team = relationship('Team', back_populates='redis_roles')
    connection = relationship('RedisConnection', back_populates='team_roles')

    def __repr__(self):
        return f"{self.team.name} - {self.permission}"


class Activity(BaseModel):
    id = Column(Integer, primary_key=True)
    message = Column(Text, nullable=False)

    def __repr__(self):
        return f"{self.id}"
