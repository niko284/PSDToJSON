from instances import Stroke as StrokeInstance
import json

class Stroke:
    def __init__(self, layer):
        self.classname = "UIStroke"
        self.instance = StrokeInstance(layer)
        self.layer = layer
    def ToDict(self):
        return {
            "Instance": self.instance,
            "ClassName": self.classname,
            "Children": []
        }
    def ToJSON(self):
        return json.dumps(self.ToDict(), indent=None)