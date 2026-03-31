from redis.retry import Retry
from redis.exceptions import (TimeoutError, ConnectionError)
from redis.backoff import ExponentialBackoff
import redis
from WebsiteModel import Website, MainWebsite
from dataclasses import dataclass, field

@dataclass
class WebsiteRepository:

    redis_pool = field(init=False)

    redis_client = field(init=False)

    def __post_init__(self, redis_pool, redis_client):
        self.redis_pool = redis.ConnectionPool(host='localhost', port=6379, retry=Retry(ExponentialBackoff(cap=10, base=1), 25), max_connections=20,
                                    retry_on_error=[ConnectionError, TimeoutError, ConnectionResetError], health_check_interval=1, decode_responses=True)
        self.redis_client = redis.Redis(connection_pool=redis_pool)
        



    # Saves websites details as json
    def saveWebsiteDetails(self,json_object: dict, website: MainWebsite):

        website_id = self.redis_client.get(f"website:url:{website.url}")

        if website_id is not None:
            key = f"website:{website_id}" 
            json_object["id"] = website_id 
            website.to_json()
            self.redis_client.json().set(website_id,'$',website.to_json())
           


        new_id = self.redis_client.incr("website:id")
        website.id = new_id
        json_object["id"] = new_id
        key = f"website:{new_id}" 
        self.redis_client.json().set(key,'$',json_object)
        self.redis_client.set(f"website:url:{website.url}", new_id)

        return new_id

    # Saves main websites url we are searching to a set in redis 
    def saveWebsiteUrl(self, url: MainWebsite):
        self.redis_client.sadd("Websites", url)
        return url
    
    # Check if website's url exist in the set of urls
    def exists_by_url(self, url: str) -> bool:
        return self.redis_client.sismember("Websites", url) == 1



    def get_by_url(self, url: str) -> MainWebsite | None:
        website_id = self.redis_client.get(f"website:url:{url}")

        if website_id is None:
           raise Exception("Website details was not found")

        key = f"website:{int(website_id)}"
        data = self.redis_client.json().get(key)

        if data is None:
            return None

        return MainWebsite.to_obj(data)

    def update(self, url: str, json_object: dict) -> bool:
        website_id = self.redis_client.get(f"website:url:{url}")

        if website_id is None:
            raise Exception("Website details was not found")
    
        key = f"website:{website_id}"

        if not self.redis_client.exists(key):
            return False

        # keep id consistent
        json_object["id"] = website_id

        self.redis_client.json().set(key, "$", json_object)
        return True


    def delete(self, website_id: int) -> bool:
        key = f"website:{website_id}"
        return self.redis_client.delete(key) == 1    
    
    
    
    
    
    
    
    # def exists_by_url(self, url: str) -> bool:
    #     key = f"website:url:{(url)}"
    #     return self.redis_client.exists(key) == 1