
import uuid
from .settings import DJANGO_SIMPLETASK2_TASK_LOCK_NAME_TEMPLATE

class SimpleRedisLock(object):
    def __init__(self, redis_conn, app_label, model_name, task_id, timeout):
        self.worker_id = str(uuid.uuid4())
        self.redis_conn = redis_conn
        self.app_label = app_label
        self.model_name = model_name
        self.task_id = task_id
        self.lock_redis_key = DJANGO_SIMPLETASK2_TASK_LOCK_NAME_TEMPLATE.format(app_label=app_label, model_name=model_name, task_id=task_id)
        self.timeout = timeout
    
    def __enter__(self, *args, **kwargs):
        locked = self.redis_conn.set(self.lock_redis_key, self.worker_id, ex=self.timeout, nx=True)
        if locked:
            return True
        else:
            return False

    def __exit__(self, *args, **kwargs):
        script = """
if redis.call("get", KEYS[1]) == ARGV[1] then
    return redis.call("del", KEYS[1])
else
    return 0
end
""".strip()
        self.redis_conn.eval(script, 1, self.lock_redis_key, self.worker_id)
