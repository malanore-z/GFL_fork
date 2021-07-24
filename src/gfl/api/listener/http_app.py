__all__ = [
    "HttpListener"
]

from flask import Flask, request

from gfl.conf import GflConf


app = Flask(__name__)
app.logger.disabled = True


@app.route("/test", methods=["GET", "POST"])
def app_test():
    if request.method == "GET":
        return {
            "method": "GET",
            "args": dict(request.args)
        }
    else:
        return {
            "method": "POST",
            "data": dict(request.form)
        }


class HttpListener(object):

    @classmethod
    def start(cls) -> None:
        bind_ip = GflConf.get_property("api.http.bind_ip")
        port = int(GflConf.get_property("api.http.port"))
        app.run(host=bind_ip, port=port)


if __name__ == "__main__":
    HttpListener.start()
