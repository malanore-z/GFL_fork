

import gfl.io.http.server_receive
from gfl.conf import GflConf
from gfl.io.http.server_app import app


if __name__ == "__main__":
    app.run(host=GflConf.http.listen_url, port=GflConf.http.listen_port)
