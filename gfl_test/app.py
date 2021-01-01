from flask import Flask, jsonify


app = Flask(__name__)


@app.route("/")
def index():
    ret = {
        "code": 0,
        "path": "/index"
    }
    return jsonify(ret)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8989)
