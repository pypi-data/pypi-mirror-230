import logging
import time
from typing import List, Optional

import redis

from truera.authn.usercontext import RequestContext


class PersistentKVStoreClient:

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[str] = None,
        password: Optional[str] = None,
        cluster_mode: bool = True
    ):
        if host is not None and port is not None:
            if cluster_mode:
                self._redis_client = redis.cluster.RedisCluster(
                    host=host, port=port, password=password, ssl=True
                )
            else:
                self._redis_client = redis.Redis(
                    host=host, port=port, password=password, ssl=True
                )
        else:
            raise ValueError("Missing config to connect to Redis.")
        self._logger = logging.getLogger(__name__)

    def get(
        self,
        key: str,
        request_context: RequestContext,
        ttl_in_seconds: Optional[int] = None
    ) -> Optional[str]:
        """
        Returns the value associated with the key.

        Args:
            key: The key we want to retrieve the value for.
            request_context: Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.
            ttl_in_seconds: TTL for key in seconds. If set, we will reset the key ttl to make the more recently accessed keys available. Defaults to None.

        Returns:
            str: The value associated with the key.
        """
        self._redis_client.psync
        redis_key = self._get_redis_key(key, request_context)
        self._logger.debug(f"Getting key {redis_key}")
        val = self._retry_on_error(self._redis_client.get, redis_key)
        if val is None:
            return None
        if ttl_in_seconds:
            self._retry_on_error(
                self._redis_client.expire, redis_key, ttl_in_seconds
            )
        return val.decode("utf-8")

    def keys(self, prefix: str, request_context: RequestContext) -> list:
        """
        Returns keys matching a prefix.
        This is inefficient and slow as it will go through the entire set of keys and will match with each. We should avoid using it other than for debugging.

        Args:
            prefix: Prefix by which we want to return the keys. If prefix is `""`, it will return all keys.
            request_context: Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.

        Returns:
            list: List of keys matching this prefix.
        """
        tenant_id = request_context.get_user_context().get_tenant_id()
        # throw if tenant_id is None or empty
        if not tenant_id or len(tenant_id) == 0:
            raise ValueError("Tenant ID cannot be empty")
        redis_key = f"{tenant_id}/{prefix}*"
        self._logger.debug(f"Getting keys {redis_key}")
        return self._retry_on_error(self._redis_client.keys, redis_key)

    def set(
        self,
        key: str,
        value: str,
        request_context: RequestContext,
        ttl_in_seconds: Optional[int] = None
    ) -> bool:
        """
        Sets the value for the key. 
        Keys can be partitions with / for internal representation of hierarchy- Redis itself does not have any optimizations for keys.

        Args:
            key: Key we want to add to the store.
            value: Value associated with the key.
            request_context:  Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.
            ttl_in_seconds: TTL for key in seconds. If set, we will set the key ttl to value passed. Defaults to None.

        Returns:
            bool: Whether the set operation was performed or not
        """
        redis_key = self._get_redis_key(key, request_context)
        self._logger.debug(f"Setting key {redis_key} to {value}")
        return self._retry_on_error(
            self._redis_client.set, redis_key, value, ex=ttl_in_seconds
        )

    def delete(self, keys: List[str], request_context: RequestContext) -> int:
        """
        Deletes given keys from the store.

        Args:
            key: Keys we want to delete from the store.
            request_context: Request context provides the tenant id to properly construct the Redis key as `tenant_id/key`.

        Returns:
            int: Number of keys deleted.
        """
        redis_keys = [self._get_redis_key(key, request_context) for key in keys]
        self._logger.debug(f"Deleting keys of length {len(redis_keys)}")
        return self._retry_on_error(self._redis_client.delete, *redis_keys)

    def _get_redis_key(self, key, request_context: RequestContext) -> str:
        tenant_id = request_context.get_user_context().get_tenant_id()
        # throw if tenant_id is None or empty
        if not tenant_id or len(tenant_id) == 0:
            raise ValueError("Tenant ID cannot be empty")
        return f"{tenant_id}/{key}"

    def _retry_on_error(
        self, func, *args, max_retries=3, retry_delay=1, **kwargs
    ):
        for i in range(max_retries):
            try:
                return func(*args, **kwargs)
            except (
                redis.exceptions.ConnectionError, redis.exceptions.TimeoutError
            ) as e:
                if i == max_retries - 1:
                    raise e
                self._logger.error(
                    f"Retryable error connecting to redis: {e}, retrying in {retry_delay} seconds"
                )
                time.sleep(retry_delay)
                continue
            except redis.exceptions.RedisError as e:
                self._logger.error(f"Error connecting to redis: {e}")
                raise e
