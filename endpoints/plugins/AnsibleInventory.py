import abc
from endpoint_base import EndpointBase

class AnsibleInventory(EndpointBase):
	"""
		Endpoint provider in the form of an Ansible inventory.
		Only Ansible Actions will work on these endpoint groups.
		For use with advanced Ansible actions that involve multiple devices to run.
	"""

	inv_name = ""
        etype = "ansible"

	def get_config_options(self):
		"""
		:return: List of configuration options for per-instance configuration
		"""
		config = [
			{
				"name": "inv_path",
				"label": "Inventory Path",
				"type": "text",
				"value": "/var/tmp/some_inventory_file.ini"
			}
		]
		return config

	def load_instance_config(self, config):
		print("__ ansible load_instance_config __")
		filename = config[0]["value"]
		self.inv_name = filename
		print(self.inv_name)
		print(config)
		return

	def get_next(self):
		return self

	def get_endpoint_by_id(self, endpoint_id): # no need to find specific endpoints, there's only one
		return self
