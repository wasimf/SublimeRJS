import sublime
import math

class ModuleEdit:

	def __init__(self, content, context):
		self.content = content
		self.context = context
		#parse
		defineRegion = self.getDefineRegion()
		defineString = content[defineRegion.begin():defineRegion.end()]
		#parse modules
		modulesStart = defineString.find("[")
		if modulesStart > -1:
			modulesEnd = defineString.find("]")
			modulesTemp = defineString[(modulesStart + 1):(modulesEnd)]
			modulesTemp = modulesTemp.replace("'", '')
			modulesTemp = modulesTemp.replace('"', '')
			modulesTemp = modulesTemp.replace(' ', '')
			self.modules = modulesTemp.split(",")
			if (self.modules[0] == ""):
				self.modules = []
		else:
			self.modules = []
		#parse refrences
		refrencesStart = defineString.rfind("(")
		refrencesEnd = defineString.find(")")
		refrencesTemp = defineString[(refrencesStart + 1):refrencesEnd].split(" ")
		self.refrences = "".join(refrencesTemp).split(",")
		if (self.refrences[0] == ""):
			self.refrences = []

	def getModuleList(self):
		commentList = "\n	/*\n	*	Module list\n"
		commentList += "	*\n"

		commentList += self.renderListGroup(self.modulesCollection["autoModules"])
		commentList += self.renderListGroup(self.modulesCollection["scriptModules"])
		commentList += self.renderListGroup(self.modulesCollection["textModules"])

		commentList += "	*/"
		return commentList

	def renderListGroup(self, items):
		if len(items) == 0:
			return ""
		listBody = ""
		sortedKeys = sorted(items, reverse = False)
		numTabs = 5
		for x in range(0, len(sortedKeys)):
			div = math.floor(float(len(sortedKeys[x])) / 4)
			tabs = numTabs - div
			listBody += "	*	" + sortedKeys[x]
			for y in range(0, tabs):
				listBody += "	"
			listBody += items[sortedKeys[x]] + "\n"
		listBody += "	*" + "\n"
		return listBody

	def getDefineRegion(self):
		startIndex = self.content.find("define(")

		if self.content.find("*	Module list") is not -1:
			endIndex = self.content.find("	*/", startIndex) + 3
		else:
			endIndex = self.content.find("{", startIndex) + 1
		return sublime.Region(startIndex, endIndex)

	def addModule(self, module):
		self.modules.append(module.getImportString())
		self.refrences.append(module.getRefrenceString())

		self.updateModuleList()

	def render(self):
		output = "define("
		# modules
		if len(self.modules) > 0:
			isFirst = True
			output += "["
			for module in self.modules:
				if not isFirst:
					output += ", "
				else:
					isFirst = False
				output += "'" + module + "'"
			output += "], "
		# fundtion
		output += "function("
		# refrences
		isFirst = True
		for refrence in self.refrences:
			if not isFirst:
				output += ", "
			else:
				isFirst = False
			output += refrence
		output += ") {" + "\n" + self.getModuleList()
		return output

	def getModules(self):
		modules = []
		for importString in self.modules:
			module = self.context.getModuleByImportString(importString)
			if module is not None:
				modules.append(module)
		return modules

	def removeModule(self, module):
		self.modules.pop(self.modules.index(module.getImportString()))
		self.refrences.pop(self.refrences.index(module.getRefrenceString()))

		self.updateModuleList()

	def updateModuleList(self):
		# run throug for module list
		self.modulesCollection = {
			"autoModules": {},
			"scriptModules": {},
			"textModules": {}
		}
		for importString in self.modules:
			module = self.context.getModuleByImportString(importString)
			if module is not None:
				if module.getImportString() in self.context.settings["auto_add"]:
					self.modulesCollection["autoModules"][module.getRefrenceString()] = module.getImportString()
				elif module.type == "script":
					self.modulesCollection["scriptModules"][module.getRefrenceString()] = module.getImportString()
				elif module.type == "text":
					self.modulesCollection["textModules"][module.getRefrenceString()] = module.getImportString()
