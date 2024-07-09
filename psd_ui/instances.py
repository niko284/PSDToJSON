# These functions are used to define the values of properties we'll need
# for the actual Roblox instances. Any special processing cases can be added here

import re
import json
import numbers

CLASS_NAMES = {
	"psdimage": "Frame",
	"group": "Frame",
	"type": "TextLabel",
}

FLAG_CLASS_NAMES = {
	"TEXT_": "TextLabel",
	"TEXTBUTTON_": "TextButton",
	"FRAME_": "Frame",
}

FLAG_FUNCTIONS = {
	"TEXT_": "TextLabel",
	"FRAME_": "Frame",
}

def GetClassName(layer):
	for key in FLAG_CLASS_NAMES:
		if layer.name[:len(key)] == key:
			return FLAG_CLASS_NAMES.get(key)
	return CLASS_NAMES.get(layer.kind, "ImageLabel")

def GetClassFunc(layer):

	for key in FLAG_FUNCTIONS:
		if layer.name[:len(key)] == key:
			return FLAG_FUNCTIONS.get(key)
	return CLASS_NAMES.get(layer.kind, "ImageLabel")

# Non-flagged instances

def Frame(layer):
	offset = layer.offset

	layerName = layer.name

	for flag in FLAG_CLASS_NAMES:
		layerName = layerName.replace(flag, "")

	# if PARENT_ flag, also remove it

	hasParentFlag = "PARENT_" in layerName
	if hasParentFlag:
		layerName = layerName.replace("PARENT_", "")

	isCancelButton = layerName == "CancelButton"
	if isCancelButton:
		print("Found cancel button")
		

	if layer.parent:

		if isCancelButton:
			print("Found parnet layer for cancel button")

		layerParent = layer.parent

		if not hasParentFlag:
			for child in layer.parent:
				if "PARENT_" in child.name:
					layerParent = child
					break
		else:
			layerParent = layerParent.parent
			

		x1, y1 = offset[0], offset[1]
		x2, y2 = layerParent.offset[0], layerParent.offset[1]
		offset = (x1 - x2, y1 - y2)

	# handle strokes
	#if hasattr(layer, "stroke") and layer.stroke != None:
		# if layer.stroke.enabled == True:
			# instance["Stroke"] = layer.stroke # This is set later, but for now we use as a flag that the instance has a stroke


	instance = {
		"Name": layerName,
		"Size": layer.size,
		"Position": offset,
		"BackgroundTransparency": 1,
	}
		
	
	return instance

def Stroke(layer):
	strokeTransparency = layer.stroke.opacity
	lineJoinType = layer.stroke.line_join_type
	clrDict = layer.stroke.content[b"Clr "]

	rd = str(clrDict[b"Rd  "])
	grn = str(clrDict[b"Grn "])
	bl = str(clrDict[b"Bl  "])

	colors = [rd, grn, bl]

	#uppercase the first letter of the line join type to match Roblox's enum
	lineJoinType = lineJoinType[0].upper() + lineJoinType[1:]
	

	if clrDict is not None:
		strokeColor = ", ".join(map(str, colors))
	else:
		strokeColor = "0, 0, 0" # default to black

	return {
		"Color": strokeColor,
		"Transparency": str(1 - (strokeTransparency / 100)),
		"LineJoinMode": lineJoinType,
		"Thickness": str(layer.stroke.line_width),
	}

def ImageLabel(layer):
	instance = Frame(layer)
	instance["Image"] = True # This is set later, but for now we use as a flag that the instance has an image
	instance["BackgroundTransparency"] = 1
	return instance

def TextLabel(layer):

	style = layer.engine_dict['StyleRun']['RunArray'][0]["StyleSheet"]["StyleSheetData"]
	
	textJustification = layer.engine_dict['ParagraphRun']['RunArray'][0]['ParagraphSheet']['Properties']['Justification']
	# 0 = left, 1 = right, 2 = center

	fontset = layer.resource_dict['FontSet']

	font = fontset[style['Font']]
	fontNameUnparsed = font['Name']

	# Remove the font weight from the font name (i.e Montserrat-Bold -> Montserrat)
	fontName = fontNameUnparsed.value.split("-")[0]
	fontWeight = fontNameUnparsed.value.split("-")[1]

	textXAlignment = "Left" # Default to left
	match textJustification:
		case 0:
			textXAlignment = "Left"
		case 1:
			textXAlignment = "Right"
		case 2:
			textXAlignment = "Center"


	fillColor = style["FillColor"]["Values"]
	strokeColor = style["StrokeColor"]["Values"]

	instance = Frame(layer)
	instance["Text"] = layer.text
	instance["TextXAlignment"] = textXAlignment
	instance["Font"] = fontName
	instance["BackgroundTransparency"] = 1
	instance["Weight"] = fontWeight
	instance["TextSize"] = int(style["FontSize"])
	instance["TextColor3"] = ", ".join(map(str, [fillColor[1], fillColor[2], fillColor[3]]))
	instance["TextStrokeColor3"] = ", ".join(map(str, [strokeColor[1], strokeColor[2], strokeColor[3]]))
	instance["TextTransparency"] = 1 - (layer.opacity / 255)

	return instance


# Flagged instances

def RasterizedTextLabel(layer):
	instance = Frame(layer)
	instance["Name"] = layer.name[5:]
	instance["Text"] = "TextLabel"
	return instance