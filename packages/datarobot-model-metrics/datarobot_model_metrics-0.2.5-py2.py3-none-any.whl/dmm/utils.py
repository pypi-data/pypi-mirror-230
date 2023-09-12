from datetime import datetime, timedelta

from datarobot import Client
from datarobot.utils.waiters import wait_for_async_resolution
from requests import Response


def wait_for_result_raw(client: Client, response: Response) -> bytes:
    assert response.status_code in (200, 201, 202, 204), response.content

    if response.status_code == 200 or response.status_code == 204:
        data = response.content

    elif response.status_code == 201:
        status_url = response.headers["Location"]
        resp = client.get(status_url)
        if resp.status_code != 200:
            raise Exception(f"Couldn't fetch export data response={resp.content}")
        data = resp.content

    elif response.status_code == 202:
        status_url = response.headers["Location"]
        result = wait_for_async_resolution(client, status_url)
        resp = client.get(result)
        if resp.status_code != 200:
            raise Exception(f"Couldn't fetch export data response={resp.content}")
        data = resp.content
    return data


def wait_for_result_from_status_url(client: Client, status_url: str) -> bytes:
    result = wait_for_async_resolution(client, status_url)
    resp = client.get(result)
    if resp.status_code != 200:
        raise Exception(f"Couldn't fetch export data response={resp.content}")
    data = resp.content
    return data


def hour_rounder_up(datetime_to_round: datetime) -> datetime:
    datetime_to_round = datetime_to_round + timedelta(hours=1)
    return datetime_to_round.replace(second=0, microsecond=0, minute=0)


def hour_rounder_down(datetime_to_round: datetime) -> datetime:
    return datetime_to_round.replace(microsecond=0, second=0, minute=0)
