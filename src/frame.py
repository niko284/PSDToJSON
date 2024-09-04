import json
import instances
import stroke

INDENT = None

class Frame:
	def __init__(self, layer):
		classname = instances.GetClassName(layer)
		funcname = instances.GetClassFunc(layer)
		instance = getattr(instances, funcname)(layer)

		self.layer = layer
		self.classname = classname
		self.instance = instance
		self.children = []

		if instance.get("Stroke"):
			# create a new Frame instance for the stroke
			self.children.append(stroke.Stroke(layer))
			# remove the stroke from the instance
			del instance["Stroke"]
	
	def AddChild(self, child):
		self.children.append(child)
	
	def ToDict(self):
		return {
			"Instance": self.instance,
			"ClassName": self.classname,
			"Children": [child.ToDict() for child in self.children]
		}
	
	def ToJSON(self):
		return json.dumps(self.ToDict(), indent=INDENT)