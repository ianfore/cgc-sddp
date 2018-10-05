""" Script to add metadata to files uploaded from sddp


        To set your CGC credentials on the API, you will need an authentication token, which you can obtain from
        https://cgc.sbgenomics.com/account/#developer. You will need to replace 'AUTH_TOKEN' with this

        for questions contact: Ian Fore
"""
#  IMPORTS
import time
import json
import xml.etree.ElementTree as ET
import sevenbridges as sbg
from sevenbridges.errors import SbgError, ResourceNotModified
from sevenbridges.http.error_handlers import rate_limit_sleeper, maintenance_sleeper
from sevenbridges.models.enums import ImportExportState
	
def setCGCMetadata(exptPkg, myFile):
	designElement = exptPkg.find("EXPERIMENT/DESIGN")
	platformElement = exptPkg.find("EXPERIMENT/PLATFORM")
	runsetElement = exptPkg.find("RUN_SET")
	platform = platformElement.find("ILLUMINA/INSTRUMENT_MODEL").text
	strategy = designElement.find("LIBRARY_DESCRIPTOR/LIBRARY_STRATEGY").text
	a1 = runsetElement.findall("RUN/RUN_ATTRIBUTES/RUN_ATTRIBUTE[TAG='assembly']")
	assembly = a1[0].find("VALUE").text
	print(assembly)
	myFile.metadata['platform'] = platform
	myFile.metadata['experimental_strategy'] = strategy
	myFile.metadata['reference_genome'] = assembly
	
	try:
		myFile.save()
	except ResourceNotModified as e:
		print ("metadata already up to date")   


def processSample(exptPkg, myProject, myVolume):
	sample = exptPkg.find("SAMPLE").get("alias")
	print ("Sample:"+sample)
	filename = sample+'.recal.cram'
	files = api.files.query(project=myProject,names=[filename])	
	print(api.remaining)
	if len(files) > 0 :
		for f in files:
			setCGCMetadata(exptPkg, f)


#%% CODE (broken into blocks below, this wilfl eventually become an iPython notebook
if __name__ == "__main__":

	config = sbg.Config(profile='cgc')
	#api = sbg.Api()

	api = sbg.Api(config=config, error_handlers=[rate_limit_sleeper, maintenance_sleeper])
	# list all projects you are part of

	try:
		project_id = 'forei/gecco'
		project = api.projects.get(id=project_id)
		print ("Found " + project.name)
	except SbgError as e:
		print (e.message)

	# List all volumes available
	myVolume = api.volumes.get('forei/sddp_phs001554')

		
	tree = ET.parse('data/geccoExperimentPackage.xml')
	root = tree.getroot()
	for exptPkg in root:
		processSample(exptPkg, project, myVolume)  
  

