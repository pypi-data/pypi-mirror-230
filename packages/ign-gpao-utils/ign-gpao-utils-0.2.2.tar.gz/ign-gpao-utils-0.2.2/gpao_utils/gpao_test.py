from pytest import fail
from client import worker
import time
import requests


def is_all_job_done_for_project_starting_with(url: str, project_name: str, pytrace=True):
    """ This method fail if any job is found failed """
    response = worker.send_request(url + "jobs", "GET")
    all_jobs_done = True
    found_at_least_one_job = False

    if response and response.json():
        for job in response.json():
            if job["project_name"].startswith(project_name):
                found_at_least_one_job = True
                status = job["job_status"]
                if status == 'failed':
                    fail("job named '" + job["job_name"] + "' has status FAILED", pytrace)
                if status != 'done':
                    all_jobs_done = False

    if not found_at_least_one_job:
        fail("There is not any project starting with: " + project_name)
    return all_jobs_done


def pretty_time_delta(seconds):
    sign_string = '-' if seconds < 0 else ''
    seconds = abs(int(seconds))
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return '%s%dd%dh%dm%ds' % (sign_string, days, hours, minutes, seconds)
    elif hours > 0:
        return '%s%dh%dm%ds' % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return '%s%dm%ds' % (sign_string, minutes, seconds)
    else:
        return '%s%ds' % (sign_string, seconds)


def wait_running_job(url_api, project_name, delay_second=1, delay_log_second=10):
    all_jobs_done = False
    duration_second = 0

    while(not all_jobs_done):
        time.sleep(delay_second)
        duration_second = duration_second + delay_second
        if duration_second % delay_log_second == 0:
            print("wait for job to finish since " + pretty_time_delta(duration_second))

        all_jobs_done = is_all_job_done_for_project_starting_with(url_api, project_name)


def start_threads(url_api, num_thread, pattern=""):
    hosts_list = []
    response = worker.send_request(url_api + "nodes", "GET")
    if response and response.json():
        for host in response.json():
            hostname = host["host"]
            if pattern == "" or pattern in hostname:
                hosts_list.append(hostname)

    json_host = {
        "hosts": hosts_list
    }
    params = {
        "value": str(num_thread)
    }
    response = requests.post(url_api + "node/setNbActive", params=params, json= json_host)
    assert response.status_code == 200


def assert_all_jobs_are_done_in_project(project_name: str, pytrace=True):
    """Verify that all job in this project are Done. Verify this for all project starting with this name"""
    response = worker.send_request(worker.GPAO_API_URL + "jobs", "GET")
    any_job_for_this_project_name = False

    if response and response.json():
        for job in response.json():
            if job["project_name"] == project_name:
                any_job_for_this_project_name = True
                status = job["job_status"]
                if status != "done":
                    fail(
                        "job named '" + job["job_name"] + "' has status : " + status,
                        pytrace,
                    )

    if not any_job_for_this_project_name:
        fail(f"There is not any job for this project name {project_name}")


def delete_project(project_name: str):
    """Delete all projects that have this name"""
    response = worker.send_request(worker.GPAO_API_URL + "projects", "GET")
    id_list = []
    if response and response.json():
        for proj in response.json():
            if proj["project_name"] == project_name:
                id = proj["project_id"]
                id_list.append(id)
    json_ids = {
        "ids": id_list
    }
    response = requests.delete(worker.GPAO_API_URL + "projects/delete", json=json_ids)
