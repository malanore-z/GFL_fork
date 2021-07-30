job_id = "2598c8089fbd30ce9a812bc46b187bcc"


if __name__ == "__main__":
    # save_client(job_id, ClientEntity(address="address-01", dataset="dataset-01", pub_key="pub-key-01"))
    # save_params(job_id, ParamsEntity(step=1, is_global=1, node_address="address-01", params="params-01", params_check="params-check-01"))
    print(get_client(job_id, "address-01"))
    print(get_params(job_id, 1, "address-01"))
