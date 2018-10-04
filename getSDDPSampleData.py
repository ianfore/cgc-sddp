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
	
#  GLOBALS
FLAGS = {'targetFound': False,               # target project exists in CGC project
        }
TARGET_PROJECT = 'gecko'                       # project we will use in CGC (Settings > Project name in GUI)

def setCGCMetadata(samp, myFile):
	sample = samp.find("Attributes/Attribute[@attribute_name='submitted sample id']").text
	gender = samp.find("Attributes/Attribute[@attribute_name='sex']").text
	affected = samp.find("Attributes/Attribute[@attribute_name='subject is affected']").text
	sample_type = samp.find("Attributes/Attribute[@attribute_name='body site']").text
	gap_consent_short_name = samp.find("Attributes/Attribute[@attribute_name='gap_consent_short_name']").text
	if affected == 'Yes':
		group = 'case'
	else:
		group = 'control'

	#singleFile = api_call(path=myFiles.href[0], flagFullPath=True) 
	# here we modify the file #1, adapt appropriately
 
	myFile.metadata = {           
		"library_id":"Lib"+sample,
		"platform": "Illumina HiSeq",
		'gender': gender,
	    "experimental_strategy":"WGS",
	    "sample_id":sample,
	    "sample_type":sample_type,
	    "primary_site":"Colorectal",
	    "gap_consent_short_name":gap_consent_short_name,
	    "case_id":sample,
	    "investigation":"GECCO",
	    "group":group
	}
	#print(metadata)
	try:
		myFile.save()
	except ResourceNotModified as e:
		print ("metadata already up to date")   


def processSample(samp, myProject, myVolume):
	sample = samp.find("Attributes/Attribute[@attribute_name='submitted sample id']").text
	print ("Sample:"+sample)
	filename = sample+'.recal.cram.crai'
	files = api.files.query(project=myProject,names=[filename])	
	print(api.remaining)
	if len(files) > 0 :
		for f in files:
			print ("already imported " + f.name)
			#setCGCMetadata(samp, f)
	else:
		# Import file to the project
		imp = api.imports.submit_import(volume=myVolume, project=myProject, location=filename)
		# Wait until the import finishes
# 		while True:
# 			import_status = imp.reload().state
# 			if import_status in (ImportExportState.COMPLETED, ImportExportState.FAILED):
# 				break
# 			time.sleep(10)
# 		# Continue with the import
# 		if imp.state == ImportExportState.COMPLETED:
# 			imported_file = imp.result
# 			setCGCMetadata(samp, imported_file)


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

		
	tree = ET.parse('gecco_biosample.xml')
	root = tree.getroot()
	for samp in root:
		processSample(samp, project, myVolume)  
  

