import mlflow
import mlflow.pyfunc
import os
import sys
sys.path.append(os.environ['WORKSPACE'])
from ecips_utils import ecips_config


models = {
    "Barcode Model": [ecips_config.ECIPS_INFERENCE_BARCODE_MODEL_NAME, ecips_config.ECIPS_INFERENCE_BARCODE_VERSION],
    "Digit Model":  [ecips_config.ECIPS_INFERENCE_DIGIT_MODEL_NAME, ecips_config.ECIPS_INFERENCE_DIGIT_VERSION],
    "Stamp Model": [ecips_config.ECIPS_INFERENCE_STAMP_MODEL_NAME, ecips_config.ECIPS_INFERENCE_STAMP_VERSION],
    "Package Model": [ecips_config.ECIPS_INFERENCE_PACKAGE_MODEL_NAME, ecips_config.ECIPS_INFERENCE_PACKAGE_VERSION],
    "PVI Model": [ecips_config.ECIPS_INFERENCE_PVI_MODEL_NAME, ecips_config.ECIPS_INFERENCE_PVI_VERSION]
}

for name in models:
    model = mlflow.pyfunc.load_model(
        model_uri="models:/" + str(name) + "/" + str(models[name][1])
    )

    model_path = ('/var/lib/mlflow/' + mlflow.get_run(model.metadata.run_id).info._experiment_id + '/' +
                  model.metadata.run_id + '/artifacts/' + model.metadata.artifact_path + '/' +
                  model.metadata.flavors['python_function']['artifacts']['model']['path'])
    os.system("mkdir -p " + os.environ['WORKSPACE'] + "/ecips_serving/models/" + models[name][0] + "/" +
              str(models[name][1]))
    os.system("cp " + model_path + " " + os.environ['WORKSPACE'] + "/ecips_serving/models/" + models[name][0] +
              "/" + str(models[name][1]) + "/model.plan")
