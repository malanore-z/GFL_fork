from flask import Flask, request, jsonify


app = Flask(__name__)


@app.route("/job/send", methods=["POST"])
def send_job():
    print(request.form["job_id"])
    print(request.form["ipfs_hash"])
    print(request.form["file"])
    return jsonify({"code": 0})

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8552, debug=True)
