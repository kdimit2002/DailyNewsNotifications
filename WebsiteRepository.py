from redis.retry import Retry
from redis.exceptions import (TimeoutError, ConnectionError)
from redis.backoff import ExponentialBackoff
import redis
from WebsiteModel import Website, MainWebsite


redis_pool = redis.ConnectionPool(host='localhost', port=6379, retry=Retry(ExponentialBackoff(cap=10, base=1), 25), max_connections=20,
                                 retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError], health_check_interval=1, decode_responses=True)

redis_client = redis.Redis(connection_pool=redis_pool)



# TODO: Must save both internal and main websites
def save(json_object: dict, website: Website):
    new_id = redis_client.incr("website:id")
    website.id = new_id
    json_object["id"] = new_id
    key = f"website:{new_id}" 
    redis_client.json().set(key,'$',json_object)
    redis_client.set(f"website:url:{hash(website.url)}", new_id)
    return new_id



def exists_by_url(url: str) -> bool:
    key = f"website:url:{hash(url)}"
    return redis_client.exists(key) == 1

def get_by_url(url: str) -> MainWebsite | None:
    website_id = redis_client.get(f"website:url:{url}")

    if website_id is None:
        return None

    key = f"website:{int(website_id)}"
    data = redis_client.json().get(key)

    if data is None:
        return None

    return MainWebsite.from_json(data)

def update(website_id: int, json_object: dict) -> bool:
    key = f"website:{website_id}"

    if not redis_client.exists(key):
        return False

    # keep id consistent
    json_object["id"] = website_id

    redis_client.json().set(key, "$", json_object)
    return True


def delete(website_id: int) -> bool:
    key = f"website:{website_id}"
    return redis_client.delete(key) == 1