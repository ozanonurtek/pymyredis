import redis
from redis.sentinel import Sentinel
from redis.cluster import RedisCluster
from app.enums import RedisDeploymentType
from app.models import RedisConnection
from app import db
import json
from typing import Any, List, Dict, Union, Set, Tuple
import shlex


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

    # String operations
    def set(self, connection_id: int, key: str, value: str, ex: int = None, px: int = None, nx: bool = False,
            xx: bool = False) -> bool:
        conn = self.get_connection(connection_id)
        return conn.set(key, value, ex=ex, px=px, nx=nx, xx=xx)

    def get(self, connection_id: int, key: str) -> str:
        conn = self.get_connection(connection_id)
        return conn.get(key)

    def mset(self, connection_id: int, mapping: Dict[str, str]) -> bool:
        conn = self.get_connection(connection_id)
        return conn.mset(mapping)

    def mget(self, connection_id: int, keys: List[str]) -> List[str]:
        conn = self.get_connection(connection_id)
        return conn.mget(keys)

    # List operations
    def lpush(self, connection_id: int, name: str, *values: Any) -> int:
        conn = self.get_connection(connection_id)
        return conn.lpush(name, *values)

    def rpush(self, connection_id: int, name: str, *values: Any) -> int:
        conn = self.get_connection(connection_id)
        return conn.rpush(name, *values)

    def lpop(self, connection_id: int, name: str) -> str:
        conn = self.get_connection(connection_id)
        return conn.lpop(name)

    def rpop(self, connection_id: int, name: str) -> str:
        conn = self.get_connection(connection_id)
        return conn.rpop(name)

    def lrange(self, connection_id: int, name: str, start: int, end: int) -> List[str]:
        conn = self.get_connection(connection_id)
        return conn.lrange(name, start, end)

    # Set operations
    def sadd(self, connection_id: int, name: str, *values: Any) -> int:
        conn = self.get_connection(connection_id)
        return conn.sadd(name, *values)

    def srem(self, connection_id: int, name: str, *values: Any) -> int:
        conn = self.get_connection(connection_id)
        return conn.srem(name, *values)

    def smembers(self, connection_id: int, name: str) -> Set[str]:
        conn = self.get_connection(connection_id)
        return conn.smembers(name)

    # Hash operations
    def hset(self, connection_id: int, name: str, key: str, value: str) -> int:
        conn = self.get_connection(connection_id)
        return conn.hset(name, key, value)

    def hget(self, connection_id: int, name: str, key: str) -> str:
        conn = self.get_connection(connection_id)
        return conn.hget(name, key)

    def hmset(self, connection_id: int, name: str, mapping: Dict[str, str]) -> bool:
        conn = self.get_connection(connection_id)
        return conn.hmset(name, mapping)

    def hgetall(self, connection_id: int, name: str) -> Dict[str, str]:
        conn = self.get_connection(connection_id)
        return conn.hgetall(name)

    # Sorted Set operations
    def zadd(self, connection_id: int, name: str, mapping: Dict[str, float]) -> int:
        conn = self.get_connection(connection_id)
        return conn.zadd(name, mapping)

    def zrange(self, connection_id: int, name: str, start: int, end: int, desc: bool = False,
               withscores: bool = False) -> List[Union[str, Tuple[str, float]]]:
        conn = self.get_connection(connection_id)
        return conn.zrange(name, start, end, desc=desc, withscores=withscores)

    # Key operations
    def delete(self, connection_id: int, *names: str) -> int:
        conn = self.get_connection(connection_id)
        return conn.delete(*names)

    def exists(self, connection_id: int, *names: str) -> int:
        conn = self.get_connection(connection_id)
        return conn.exists(*names)

    def expire(self, connection_id: int, name: str, time: int) -> bool:
        conn = self.get_connection(connection_id)
        return conn.expire(name, time)

    # Pub/Sub operations
    def publish(self, connection_id: int, channel: str, message: str) -> int:
        conn = self.get_connection(connection_id)
        return conn.publish(channel, message)

    def subscribe(self, connection_id: int, *channels: str):
        conn = self.get_connection(connection_id)
        pubsub = conn.pubsub()
        pubsub.subscribe(*channels)
        return pubsub

    # JSON operations (assuming redis-json module is installed)
    def json_set(self, connection_id: int, name: str, path: str, obj: Any) -> bool:
        conn = self.get_connection(connection_id)
        return conn.execute_command('JSON.SET', name, path, json.dumps(obj))

    def json_get(self, connection_id: int, name: str, path: str = '.') -> Any:
        conn = self.get_connection(connection_id)
        result = conn.execute_command('JSON.GET', name, path)
        return json.loads(result) if result else None

    # Generic command execution (for commands not covered by specific methods)
    def execute_command(self, connection_id: int, command: str, *args: Any) -> Any:
        conn = self.get_connection(connection_id)
        return conn.execute_command(command, *args)


class RedisCommandRouter:
    def __init__(self, redis_manager):
        self.redis_manager = redis_manager
        self.command_map = {
            'SET': self._handle_set,
            'GET': self._handle_get,
            'MSET': self._handle_mset,
            'MGET': self._handle_mget,
            'LPUSH': self._handle_lpush,
            'RPUSH': self._handle_rpush,
            'LPOP': self._handle_lpop,
            'RPOP': self._handle_rpop,
            'LRANGE': self._handle_lrange,
            'SADD': self._handle_sadd,
            'SREM': self._handle_srem,
            'SMEMBERS': self._handle_smembers,
            'HSET': self._handle_hset,
            'HGET': self._handle_hget,
            'HMSET': self._handle_hmset,
            'HGETALL': self._handle_hgetall,
            'ZADD': self._handle_zadd,
            'ZRANGE': self._handle_zrange,
            'DEL': self._handle_delete,
            'EXISTS': self._handle_exists,
            'EXPIRE': self._handle_expire,
            'PUBLISH': self._handle_publish,
            'JSON.SET': self._handle_json_set,
            'JSON.GET': self._handle_json_get,
            'KEYS': self._handle_keys,
        }

    def route_command(self, connection_id: int, command_string: str) -> Any:
        try:
            parts = self._parse_command(command_string)
            if not parts:
                raise ValueError("Empty command")
            command = parts[0].upper()
            args = parts[1:]

            if command in self.command_map:
                return self.command_map[command](connection_id, *args)
            else:
                return self.redis_manager.execute_command(connection_id, command, *args)
        except Exception as e:
            return f"Error: {str(e)}"

    def _parse_command(self, command_string: str) -> List[str]:
        parts = []
        current_part = ""
        in_quotes = False
        in_braces = 0

        for char in command_string:
            if char == '"' and not in_braces:
                in_quotes = not in_quotes
                current_part += char
            elif char == '{':
                in_braces += 1
                current_part += char
            elif char == '}':
                in_braces -= 1
                current_part += char
            elif char.isspace() and not in_quotes and not in_braces:
                if current_part:
                    parts.append(current_part)
                    current_part = ""
            else:
                current_part += char

        if current_part:
            parts.append(current_part)

        return parts

    def _parse_json_arg(self, arg: str) -> Any:
        try:
            return json.loads(arg)
        except json.JSONDecodeError:
            return arg

    def _serialize(self, value: Any) -> str:
        if isinstance(value, (dict, list)):
            return json.dumps(value)
        return str(value)

    def _handle_set(self, connection_id: int, *args) -> Any:
        if len(args) < 2:
            raise ValueError("SET command requires at least key and value arguments")
        key, value = args[0], self._serialize(self._parse_json_arg(args[1]))
        options = {}
        if len(args) > 2:
            for i in range(2, len(args), 2):
                if i + 1 < len(args):
                    options[args[i].upper()] = args[i + 1]
                else:
                    options[args[i].upper()] = True
        return self.redis_manager.set(connection_id, key, value, **options)

    def _handle_get(self, connection_id: int, *args) -> Any:
        if len(args) != 1:
            raise ValueError("GET command requires exactly one argument (key)")
        return self.redis_manager.get(connection_id, args[0])

    def _handle_mset(self, connection_id: int, *args) -> Any:
        if len(args) % 2 != 0:
            raise ValueError("MSET command requires an even number of arguments")
        mapping = {args[i]: self._serialize(self._parse_json_arg(args[i + 1])) for i in range(0, len(args), 2)}
        return self.redis_manager.mset(connection_id, mapping)

    def _handle_mget(self, connection_id: int, *args) -> Any:
        return self.redis_manager.mget(connection_id, list(args))

    def _handle_lpush(self, connection_id: int, *args) -> Any:
        if len(args) < 2:
            raise ValueError("LPUSH command requires at least two arguments")
        return self.redis_manager.lpush(connection_id, args[0],
                                        *[self._serialize(self._parse_json_arg(arg)) for arg in args[1:]])

    def _handle_rpush(self, connection_id: int, *args) -> Any:
        if len(args) < 2:
            raise ValueError("RPUSH command requires at least two arguments")
        return self.redis_manager.rpush(connection_id, args[0],
                                        *[self._serialize(self._parse_json_arg(arg)) for arg in args[1:]])

    def _handle_lpop(self, connection_id: int, *args) -> Any:
        if len(args) != 1:
            raise ValueError("LPOP command requires exactly one argument")
        return self.redis_manager.lpop(connection_id, args[0])

    def _handle_rpop(self, connection_id: int, *args) -> Any:
        if len(args) != 1:
            raise ValueError("RPOP command requires exactly one argument")
        return self.redis_manager.rpop(connection_id, args[0])

    def _handle_lrange(self, connection_id: int, *args) -> Any:
        if len(args) != 3:
            raise ValueError("LRANGE command requires exactly three arguments")
        return self.redis_manager.lrange(connection_id, args[0], int(args[1]), int(args[2]))

    def _handle_sadd(self, connection_id: int, *args) -> Any:
        if len(args) < 2:
            raise ValueError("SADD command requires at least two arguments")
        return self.redis_manager.sadd(connection_id, args[0],
                                       *[self._serialize(self._parse_json_arg(arg)) for arg in args[1:]])

    def _handle_srem(self, connection_id: int, *args) -> Any:
        if len(args) < 2:
            raise ValueError("SREM command requires at least two arguments")
        return self.redis_manager.srem(connection_id, args[0],
                                       *[self._serialize(self._parse_json_arg(arg)) for arg in args[1:]])

    def _handle_smembers(self, connection_id: int, *args) -> Any:
        if len(args) != 1:
            raise ValueError("SMEMBERS command requires exactly one argument")
        return self.redis_manager.smembers(connection_id, args[0])

    def _handle_hset(self, connection_id: int, *args) -> Any:
        if len(args) != 3:
            raise ValueError("HSET command requires exactly three arguments")
        return self.redis_manager.hset(connection_id, args[0], args[1], self._serialize(self._parse_json_arg(args[2])))

    def _handle_hget(self, connection_id: int, *args) -> Any:
        if len(args) != 2:
            raise ValueError("HGET command requires exactly two arguments")
        return self.redis_manager.hget(connection_id, args[0], args[1])

    def _handle_hmset(self, connection_id: int, *args) -> Any:
        if len(args) < 3 or len(args) % 2 == 0:
            raise ValueError("HMSET command requires at least three arguments, with an odd number of arguments")
        mapping = {args[i]: self._serialize(self._parse_json_arg(args[i + 1])) for i in range(1, len(args), 2)}
        return self.redis_manager.hmset(connection_id, args[0], mapping)

    def _handle_hgetall(self, connection_id: int, *args) -> Any:
        if len(args) != 1:
            raise ValueError("HGETALL command requires exactly one argument")
        return self.redis_manager.hgetall(connection_id, args[0])

    def _handle_zadd(self, connection_id: int, *args) -> Any:
        if len(args) < 3 or len(args) % 2 == 0:
            raise ValueError("ZADD command requires at least three arguments, with an odd number of arguments")
        mapping = {self._serialize(self._parse_json_arg(args[i + 1])): float(args[i]) for i in range(1, len(args), 2)}
        return self.redis_manager.zadd(connection_id, args[0], mapping)

    def _handle_zrange(self, connection_id: int, *args) -> Any:
        if len(args) < 3:
            raise ValueError("ZRANGE command requires at least three arguments")
        name, start, stop = args[0], int(args[1]), int(args[2])
        withscores = False
        if len(args) > 3 and 'WITHSCORES' in [arg.upper() for arg in args[3:]]:
            withscores = True
        return self.redis_manager.zrange(connection_id, name, start, stop, withscores=withscores)

    def _handle_delete(self, connection_id: int, *args) -> Any:
        if not args:
            raise ValueError("DEL command requires at least one argument")
        return self.redis_manager.delete(connection_id, *args)

    def _handle_exists(self, connection_id: int, *args) -> Any:
        if not args:
            raise ValueError("EXISTS command requires at least one argument")
        return self.redis_manager.exists(connection_id, *args)

    def _handle_expire(self, connection_id: int, *args) -> Any:
        if len(args) != 2:
            raise ValueError("EXPIRE command requires exactly two arguments")
        return self.redis_manager.expire(connection_id, args[0], int(args[1]))

    def _handle_publish(self, connection_id: int, *args) -> Any:
        if len(args) != 2:
            raise ValueError("PUBLISH command requires exactly two arguments")
        return self.redis_manager.publish(connection_id, args[0], self._serialize(self._parse_json_arg(args[1])))

    def _handle_json_set(self, connection_id: int, *args) -> Any:
        if len(args) != 3:
            raise ValueError("JSON.SET command requires exactly three arguments")
        return self.redis_manager.json_set(connection_id, args[0], args[1], self._parse_json_arg(args[2]))

    def _handle_json_get(self, connection_id: int, *args) -> Any:
        if len(args) < 1 or len(args) > 2:
            raise ValueError("JSON.GET command requires one or two arguments")
        key = args[0]
        path = args[1] if len(args) == 2 else '.'
        return self.redis_manager.json_get(connection_id, key, path)

    def _handle_keys(self, connection_id: int, *args) -> Any:
        if len(args) != 1:
            raise ValueError("KEYS command requires exactly one argument (pattern)")
        return self.redis_manager.execute_command(connection_id, 'KEYS', args[0])


# Usage example
redis_manager = RedisManager()
command_router = RedisCommandRouter(redis_manager)

# Example of how to use the command router
# connection_id = 1  # Assume this is a valid connection ID
# result = command_router.route_command(connection_id, 'SET mykey {"name": "John", "age": 30}')
# print(result)
#
# result = command_router.route_command(connection_id, 'GET mykey')
# print(result)
