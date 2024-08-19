import pytest
from unittest.mock import Mock
from app.redis_manager import RedisCommandRouter, RedisManager


@pytest.fixture
def redis_manager_mock():
    return Mock(spec=RedisManager)


@pytest.fixture
def command_router(redis_manager_mock):
    return RedisCommandRouter(redis_manager_mock)


def test_route_command_set(command_router, redis_manager_mock):
    command_router.route_command(1, 'SET mykey {"name": "John", "age": 30}')
    redis_manager_mock.set.assert_called_once_with(1, 'mykey', '{"name": "John", "age": 30}')


def test_route_command_get(command_router, redis_manager_mock):
    command_router.route_command(1, 'GET mykey')
    redis_manager_mock.get.assert_called_once_with(1, 'mykey')


def test_route_command_mset(command_router, redis_manager_mock):
    command_router.route_command(1, 'MSET key1 value1 key2 {"name": "John"}')
    redis_manager_mock.mset.assert_called_once_with(1, {'key1': 'value1', 'key2': '{"name": "John"}'})


def test_route_command_mget(command_router, redis_manager_mock):
    command_router.route_command(1, 'MGET key1 key2 key3')
    redis_manager_mock.mget.assert_called_once_with(1, ['key1', 'key2', 'key3'])


def test_route_command_lpush(command_router, redis_manager_mock):
    command_router.route_command(1, 'LPUSH mylist value1 {"name": "John"} value3')
    redis_manager_mock.lpush.assert_called_once_with(1, 'mylist', 'value1', '{"name": "John"}', 'value3')


def test_route_command_rpush(command_router, redis_manager_mock):
    command_router.route_command(1, 'RPUSH mylist value1 {"name": "John"} value3')
    redis_manager_mock.rpush.assert_called_once_with(1, 'mylist', 'value1', '{"name": "John"}', 'value3')


def test_route_command_lpop(command_router, redis_manager_mock):
    command_router.route_command(1, 'LPOP mylist')
    redis_manager_mock.lpop.assert_called_once_with(1, 'mylist')


def test_route_command_rpop(command_router, redis_manager_mock):
    command_router.route_command(1, 'RPOP mylist')
    redis_manager_mock.rpop.assert_called_once_with(1, 'mylist')


def test_route_command_lrange(command_router, redis_manager_mock):
    command_router.route_command(1, 'LRANGE mylist 0 -1')
    redis_manager_mock.lrange.assert_called_once_with(1, 'mylist', 0, -1)


def test_route_command_sadd(command_router, redis_manager_mock):
    command_router.route_command(1, 'SADD myset value1 {"name": "John"} value3')
    redis_manager_mock.sadd.assert_called_once_with(1, 'myset', 'value1', '{"name": "John"}', 'value3')


def test_route_command_srem(command_router, redis_manager_mock):
    command_router.route_command(1, 'SREM myset value1 value2')
    redis_manager_mock.srem.assert_called_once_with(1, 'myset', 'value1', 'value2')


def test_route_command_smembers(command_router, redis_manager_mock):
    command_router.route_command(1, 'SMEMBERS myset')
    redis_manager_mock.smembers.assert_called_once_with(1, 'myset')


def test_route_command_hset(command_router, redis_manager_mock):
    command_router.route_command(1, 'HSET myhash field {"name": "John"}')
    redis_manager_mock.hset.assert_called_once_with(1, 'myhash', 'field', '{"name": "John"}')


def test_route_command_hget(command_router, redis_manager_mock):
    command_router.route_command(1, 'HGET myhash field')
    redis_manager_mock.hget.assert_called_once_with(1, 'myhash', 'field')


def test_route_command_hmset(command_router, redis_manager_mock):
    command_router.route_command(1, 'HMSET myhash field1 value1 field2 {"name": "John"}')
    redis_manager_mock.hmset.assert_called_once_with(1, 'myhash', {'field1': 'value1', 'field2': '{"name": "John"}'})


def test_route_command_hgetall(command_router, redis_manager_mock):
    command_router.route_command(1, 'HGETALL myhash')
    redis_manager_mock.hgetall.assert_called_once_with(1, 'myhash')


def test_route_command_zadd(command_router, redis_manager_mock):
    command_router.route_command(1, 'ZADD myzset 1 member1 2 {"name": "John"}')
    redis_manager_mock.zadd.assert_called_once_with(1, 'myzset', {'member1': 1.0, '{"name": "John"}': 2.0})


def test_route_command_zrange(command_router, redis_manager_mock):
    command_router.route_command(1, 'ZRANGE myzset 0 -1 WITHSCORES')
    redis_manager_mock.zrange.assert_called_once_with(1, 'myzset', 0, -1, withscores=True)


def test_route_command_delete(command_router, redis_manager_mock):
    command_router.route_command(1, 'DEL key1 key2')
    redis_manager_mock.delete.assert_called_once_with(1, 'key1', 'key2')


def test_route_command_exists(command_router, redis_manager_mock):
    command_router.route_command(1, 'EXISTS key1 key2')
    redis_manager_mock.exists.assert_called_once_with(1, 'key1', 'key2')


def test_route_command_expire(command_router, redis_manager_mock):
    command_router.route_command(1, 'EXPIRE mykey 100')
    redis_manager_mock.expire.assert_called_once_with(1, 'mykey', 100)


def test_route_command_publish(command_router, redis_manager_mock):
    command_router.route_command(1, 'PUBLISH mychannel {"message": "Hello"}')
    redis_manager_mock.publish.assert_called_once_with(1, 'mychannel', '{"message": "Hello"}')


def test_route_command_json_set(command_router, redis_manager_mock):
    command_router.route_command(1, 'JSON.SET mykey . {"name": "John", "age": 30}')
    redis_manager_mock.json_set.assert_called_once_with(1, 'mykey', '.', {"name": "John", "age": 30})


def test_route_command_json_get(command_router, redis_manager_mock):
    command_router.route_command(1, 'JSON.GET mykey .name')
    redis_manager_mock.json_get.assert_called_once_with(1, 'mykey', '.name')


def test_route_command_unknown(command_router, redis_manager_mock):
    command_router.route_command(1, 'UNKNOWN_COMMAND arg1 arg2')
    redis_manager_mock.execute_command.assert_called_once_with(1, 'UNKNOWN_COMMAND', 'arg1', 'arg2')


def test_route_command_set_with_options(command_router, redis_manager_mock):
    command_router.route_command(1, 'SET mykey value EX 60 NX')
    redis_manager_mock.set.assert_called_once_with(1, 'mykey', 'value', EX='60', NX=True)


def test_route_command_set_with_px_xx_options(command_router, redis_manager_mock):
    command_router.route_command(1, 'SET mykey value PX 1000 XX')
    redis_manager_mock.set.assert_called_once_with(1, 'mykey', 'value', PX='1000', XX=True)


def test_route_command_zrange_with_options(command_router, redis_manager_mock):
    command_router.route_command(1, 'ZRANGE myzset 0 -1 WITHSCORES REV')
    redis_manager_mock.zrange.assert_called_once_with(1, 'myzset', 0, -1, withscores=True)


def test_route_command_invalid_json(command_router, redis_manager_mock):
    result = command_router.route_command(1, 'SET mykey {invalid_json}')
    redis_manager_mock.set.assert_called_once_with(1, 'mykey', '{invalid_json}')


def test_route_command_missing_args(command_router):
    result = command_router.route_command(1, 'SET')
    assert "Error: SET command requires at least key and value arguments" in result


def test_route_command_too_many_args(command_router):
    result = command_router.route_command(1, 'GET key1 key2')
    assert "Error: GET command requires exactly one argument (key)" in result


def test_parse_json_arg(command_router):
    assert command_router._parse_json_arg('{"name": "John"}') == {"name": "John"}
    assert command_router._parse_json_arg('not_json') == 'not_json'


if __name__ == '__main__':
    pytest.main()
