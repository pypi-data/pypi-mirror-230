from autonomous import log
from autonomous.tasks import AutoTasks
from tasks import mocktask, longmocktask, parametermocktask, errormocktask
import time
from celery.result import AsyncResult
import pytest


def test_create_task(app):
    at = AutoTasks()
    assert at._connection
    assert at.queue
    task_id = at.task(mocktask)
    time.sleep(2)
    assert at.get_task(task_id)
    assert at.get_status(task_id)
    assert at.get_result(task_id)
    assert at.get_all()


def test_param_task(app):
    at = AutoTasks()
    assert at.connection
    assert at.queue
    task_id = at.task(parametermocktask, 1, 2, "hello", key="value")
    time.sleep(2)
    assert at.get_task(task_id)
    assert at.get_status(task_id)
    assert at.get_result(task_id) == 3
    assert at.get_all()


def test_error_task(app):
    at = AutoTasks()
    task_id = at.task(errormocktask)
    time.sleep(2)
    assert at.get_status(task_id) == "FAILURE"
    try:
        response = at.get_result(task_id)
    except Exception as e:
        log(e)
    else:
        pytest.fail(f"Exception not raised: {response}")


def test_base_long_task(app):
    at = AutoTasks()
    assert at.connection
    assert at.queue
    task_id = at.task(longmocktask)
    time.sleep(2)
    assert at.get_task(task_id)
    assert at.get_status(task_id)
    assert at.get_result(task_id) == "success"
    assert at.get_all()
