
import gfl.io.aspect as aspect


@aspect.Aspect(aspect.load_job, position="before")
def publish_job(client, job_id, file_ipfs, file_obj, **kwargs):
    pass


@aspect.Aspect(aspect.add_client, position="before")
def register_server_job(client, job_id, **kwargs):
    pass


@aspect.Aspect(aspect.load_params, position="before")
def upload_params(client, job_id, step, file_ipfs, file_obj, **kwargs):
    pass


@aspect.Aspect(aspect.send_validation_result, position="before")
def upload_validation_result(client, job_id, step, result, **kwargs):
    pass


@aspect.Aspect(aspect.add_client, position="before")
def fetch_jobid_list(client, **kwargs):
    pass


@aspect.Aspect(aspect.add_client, position="before")
def fetch_job(client, job_id, **kwargs):
    pass
