import psutil


class Metrics(object):
    @classmethod
    def dict(cls):
        return {
            "memory": cls.memory_info(),
            "worker": cls.worker_info(),
            "tasks": cls.task_info(),
        }

    @classmethod
    def memory_info(cls):
        memory_info = psutil.Process().memory_info()
        return dict(rss=memory_info.rss, vms=memory_info.vms, data=memory_info.data)

    @classmethod
    def worker_info(cls):
        return {
            "number_of_worker": 0
        }

    @classmethod
    def task_info(cls):
        return {
            "scheduled": 0,
            "retry": 0,
            "error": 0,
            "done": 0,
        }


def metrics() -> dict:
    memory_info = psutil.Process().memory_info()
    return {
        "memory": dict(rss=memory_info.rss, vms=memory_info.vms, data=memory_info.data)
    }
