import re
import requests
import subprocess

TARMAC_TOML = '''name = "{0}"

[[inputs]]
glob = "{1}/*.png"
codegen = true
codegen-path = "{1}/assetids.lua"
codegen-base-path = "{1}"'''

def VerifyUsername(cookie):
	try:
		response = requests.get("https://www.roblox.com/game/GetCurrentUser.ashx", cookies={".ROBLOSECURITY": cookie})
		response = requests.get("https://api.roblox.com/users/" + response.text)
		username = response.json().get("Username")
		valid = input("The username associated with this cookie is " + username + ". Is this correct? (y/n) : ")
		return valid == "y"
	except:
		print("Something was wrong with the cookie provided. Ensure it's a valid account cookie.")
		return False

def TarmacSync(outputPath, cookie):
	parentPath = outputPath.parent
	subPath = "/".join(outputPath.parts[-1:])

	f = open(parentPath.as_posix() + "/tarmac.toml", "w")
	f.write(TARMAC_TOML.format(parentPath.stem, subPath))
	f.close()

	f = open(outputPath.as_posix() + "/assetids.lua", "r")
	matches = re.findall(r'\S+_(\d+) = "(rbxassetid://\d+)"', f.read())

	arr = []
	for match in matches:
		index = int(match[0]) - 1
		arr.insert(index, match[1])

	return arr
