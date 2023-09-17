import logging
logging.basicConfig(level=logging.INFO)
from gitlabx.abstract import AbstractGitLab

# Represents a software Project
class Project(AbstractGitLab):

	def __init__(self,personal_access_token, gitlab_url = None):
		super(Project,self).__init__(personal_access_token=personal_access_token,gitlab_url=gitlab_url)
	
	def get_all_function(self, today=False, **kwargs): 
		
		result = []
		projects = []
		
		try:
			
			function = kwargs["function"]

			logging.info("Start function: get_projects")
			result = self.gl.projects.list(owned=True, iterator=True, simple=True)
			for project in result:
				projects.append(project.asdict())
				if function is not None:
					function (data=project.asdict(), topic=kwargs["topic"], extra_data=kwargs["extra_data"])
				
		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 

		logging.info("Retrieve All Projects")
		return projects	

	def get_all(self, today=False): 
		
		result = []
		projects = []

		try:
			logging.info("Start function: get_projects")
			result = self.gl.projects.list(owned=True, iterator=True, simple=True)
			for project in result:
				projects.append(project.asdict())
				
		except Exception as e: 
			logging.error("OS error: {0}".format(e))
			logging.error(e.__dict__) 

		logging.info("Retrieve All Projects")
		
		return projects	

