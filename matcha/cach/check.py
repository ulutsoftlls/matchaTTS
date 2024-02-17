from matcha.api import app
from flask_caching import Cache


# Получите объект кеша
cache = Cache(app)

# Получите все ключи в кеше
all_keys = cache.cache._client.keys('*')

# Выведите все значения для каждого ключа
for key in all_keys:
    value = cache.get(key)
    print(f"Key: {key}, Value: {value}")
