
from gfl.io.http.server_app import app


@app.route("/job/publish")
def job_publish():
    pass


@app.route("/job/id_list")
def job_id_list():
    pass


@app.route("/job/{id}")
def get_job(id):
    pass


@app.route("/dataset/publish")
def dataset_publish():
    pass


@app.route("/dataset/id_list")
def dataset_id_list():
    pass


@app.route("/dataset/{id}")
def get_dataset():
    pass


@app.route("/params/upload")
def params_upload():
    pass


@app.route("/params/aggregate/download")
def params_aggregate_download():
    pass


@app.route("/validation/upload")
def validation_upload():
    pass
