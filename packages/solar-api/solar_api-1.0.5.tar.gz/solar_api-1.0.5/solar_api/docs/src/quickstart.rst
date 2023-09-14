Quickstart
==========
Instantiate the API wrapper using the following code:

.. code-block:: python

    from tonic_api.api import TonicApi

    # Do not include trailing backslash in TONIC_URL
    tonic = TonicApi(TONIC_URL, API_KEY)


To get synthetic data from models in your workspace, you must specify
a workspace and a model, as the below example shows:

.. code-block:: python

    workspace = tonic.get_workspace(WORKSPACE_ID)

    training_job = workspace.get_most_recent_training_job_by_model_id(MODEL_ID)
    training_job.tail_training_status()

    model = training_job.get_trained_model_by_model_id(MODEL_ID)
    sample = model.sample(100)
