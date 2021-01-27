from io import BytesIO

import requests
from requests_toolbelt import MultipartEncoder


if __name__ == "__main__":
    url = "http://127.0.0.1:8552/job/send"
    m = MultipartEncoder(fields={
        "job_id": "1234566",
        "ipfs_hash": None,
        "file": BytesIO(b"zxcvb")
    })
    resp = requests.post(url, data=m, headers={
        "Content-Type": m.content_type
    })
    print(resp.text)
