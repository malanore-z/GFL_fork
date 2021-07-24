from io import BytesIO
from typing import NoReturn

from requests_toolbelt import MultipartEncoder

from gfl.net.abstract import NetSend, File
from gfl.net.http.http import Http


class HttpSend(NetSend):

    @classmethod
    def send_partial_params(cls, client: str, job_id: str, step: int, params: File) -> NoReturn:
        pass

