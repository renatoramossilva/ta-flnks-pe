"""Set up a Redis connection and initialize a handler for interacting with it.

Further info: https://github.com/renatoramossilva/bindl-lib/tree/9986de1b57542ee34dfd8bbd74615cc59948e6f8/src/bindl/redis_wrapper
"""

import bindl.redis_wrapper.connection.redis_connection as rc
import bindl.redis_wrapper.redis_handler as rh
from bindl.logger import setup_logger

LOG = setup_logger(__name__)


def get_redis_repo() -> rc.RedisConnectionHandler:
    """Connect to a Redis server.

    This function establishes a connection to a Redis server using the RedisConnectionHandler.
    It verifies the connection by sending a ping request. If the connection is successful,
    a log message is recorded indicating that Redis is connected. Otherwise, an error
    message is logged. Finally, it returns a RedisHandler instance initialized with the
    established connection.

    **Returns**
        RedisHandler: An instance of RedisHandler initialized with the Redis connection.

    **Raises**
        Exception: If the Redis connection cannot be established.
    """
    redis_conn = rc.RedisConnectionHandler(host="redis").connect()
    if redis_conn.ping():
        LOG.info("🎉 Redis is connected!")
    else:
        LOG.error("Unable to connect to Redis.")
    return rh.RedisHandler(redis_conn)
