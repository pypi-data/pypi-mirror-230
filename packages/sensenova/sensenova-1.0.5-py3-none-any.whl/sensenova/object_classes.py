from sensenova import api_resources


OBJECT_CLASSES = {
    "dataset": api_resources.Dataset,
    "model": api_resources.Model,
    "fine-tune": api_resources.FineTune,
    "serving": api_resources.Serving
}
