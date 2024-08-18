import redis
from redis.sentinel import Sentinel
from redis.cluster import RedisCluster
from app.enums import RedisDeploymentType
from app.models import RedisConnection
from typing import Any
from app import db


class RedisManager:
    def __init__(self):
        self.connections = {}

    def test_connection(self, connection) -> bool:
        try:
            conn = self.get_connection(connection.id)
            conn.ping()
            return True
        except redis.ConnectionError:
            return False

    def get_connection(self, connection_id):
        if connection_id not in self.connections:

            connection = db.session.query(RedisConnection).get(connection_id)
            if not connection:
                raise ValueError(f"Redis connection with id {connection_id} not found")

            if connection.deployment_type == RedisDeploymentType.STANDALONE:
                self.connections[connection_id] = redis.Redis(
                    host=connection.host,
                    port=connection.port,
                    db=connection.db,
                    password=connection.password
                )
            elif connection.deployment_type == RedisDeploymentType.SENTINEL:
                sentinel_hosts = [tuple(h.split(':')) for h in connection.sentinel_hosts.split(',')]
                sentinel = Sentinel(sentinel_hosts, password=connection.password)
                self.connections[connection_id] = sentinel.master_for(connection.sentinel_master)
            elif connection.deployment_type == RedisDeploymentType.MASTER_SLAVE:
                self.connections[connection_id] = redis.Redis(
                    host=connection.master_host,
                    port=connection.master_port,
                    password=connection.password
                )
            elif connection.deployment_type == RedisDeploymentType.CLUSTER:
                cluster_nodes = [n.split(':') for n in connection.cluster_nodes.split(',')]
                self.connections[connection_id] = RedisCluster(
                    startup_nodes=cluster_nodes,
                    password=connection.password
                )

        return self.connections[connection_id]

    def execute_command(self, connection_id: int, command: str, *args: Any) -> Any:
        conn = self.get_connection(connection_id)
        # TODO: parse command, check if json, use dumps
        return conn.execute_command(command, *args)

    def get_redis_info(self, connection):
        try:
            self.test_connection(connection)
            client = self.connections[connection.id]
            info = client.info()
            return {
                'cpu_usage': info.get('used_cpu_sys', 'N/A'),
                'memory_usage': info.get('used_memory_human', 'N/A'),
                'status': 'Connected'
            }
        except Exception as e:
            return {
                'cpu_usage': 'N/A',
                'memory_usage': 'N/A',
                'status': f'Disconnected: {str(e)}'
            }


redis_manager = RedisManager()
