from frame import Frame 
import requests
import psd_tools
from psd_tools import PSDImage
from upload import TarmacSync

FILE_FORMAT = "img_{0}.png"
PARENT_FLAG = "PARENT_"

def RecursiveFrame(frame, psd, imgFrames):
	for layer in psd:
		if not layer.is_visible():
			continue

		if PARENT_FLAG in layer.name:
			print("Skipping %s" % layer.name)
			continue # skip layers with PARENT_ flag, they are used to describe parent layers

		isParentLayer = layer.kind == "group" or layer.kind == "artboard" # parent layers are groups or artboards (they contain children layers)
		# for parent layers, our frame might be described by a child named "ParentBackground", find it

		parentLayer = None
		if isParentLayer:
			for child in layer:
				if PARENT_FLAG in child.name:
					parentLayer = child
					print("Got parent layer %s for %s" % (parentLayer.name, layer.name))
					break


		layerFrame = Frame(parentLayer if parentLayer is not None else layer)

		frame.AddChild(layerFrame)

		# if the layer is an image, add it to the list of images
		if layerFrame.instance.get("Image"):
			imgFrames.append(layerFrame)

		if isParentLayer:
			RecursiveFrame(layerFrame, layer, imgFrames)

def main(filename, outputPath, contentPath, cookie):
	psd = PSDImage.open(filename)
	top = Frame(psd)

	imgFrames = []
	RecursiveFrame(top, psd, imgFrames)

	for i in range(len(imgFrames)):
		name = FILE_FORMAT.format(i + 1)
		imgPath = outputPath.as_posix() + "/" + name
		imgFrames[i].layer.composite().save(imgPath)

		if contentPath:
			subPath = "/".join(contentPath.parts[-2:])
			imgFrames[i].instance["Image"] = "rbxasset://" + subPath + "/" + name
			imgFrames[i].layer.composite().save(contentPath.as_posix() + "/" + name)
	
	if cookie:
		assetids = TarmacSync(outputPath, cookie)
		for i in range(len(imgFrames)):
			imgFrames[i].instance["Image"] = assetids[i]

	json = open(outputPath.as_posix() + "/output.json", "w")
	json.write(top.ToJSON())
	json.close()