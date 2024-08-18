import enum


class RedisDeploymentType(enum.Enum):
    STANDALONE = "Standalone"
    SENTINEL = "Sentinel"
    MASTER_SLAVE = "Master-Slave"
    CLUSTER = "Cluster"


class TeamRedisPermission(enum.Enum):
    READ = "READ"
    READ_WRITE = "READ_WRITE"
    CLUSTER_ADMIN = "CLUSTER_ADMIN"
