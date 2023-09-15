# -*- coding: utf-8 -*-

from apistar.exceptions import ErrorResponse
from arkindex import ArkindexClient

from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential


def is_500_error(exception: Exception):
    return isinstance(exception, ErrorResponse) and 500 <= exception.status_code


class ArkindexAPIClient(ArkindexClient):
    @retry(
        reraise=True,
        retry=retry_if_exception(is_500_error),
        stop=stop_after_attempt(5),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    def request(self, operation_id, *args, **kwargs):
        return super().request(operation_id, *args, **kwargs)
