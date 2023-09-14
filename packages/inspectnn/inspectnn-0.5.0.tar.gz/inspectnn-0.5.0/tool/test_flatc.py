import json

with open("examples/mnist_model_quant.tflite") as f:
    model_json = json.load(f)