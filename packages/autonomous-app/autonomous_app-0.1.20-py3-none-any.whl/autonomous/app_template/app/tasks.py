import time
from autonomous import log
from rq.decorators import job
from autonomous.tasks import AutoTasks


@job
def mocktask():
    time.sleep(1)
    log("MockTask")
    return "success"


@job
def longmocktask():
    time.sleep(30)
    return "success"


@job
def parametermocktask(*args, **kwargs):
    log("ParameterMockTask", args, kwargs)

    return args[0] + args[1]


@job
def errormocktask():
    raise Exception("ErrorMockTask")
