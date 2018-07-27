import os
import time
import uuid
import tempfile
import subprocess
from subprocess import CalledProcessError

from a_frame.utils.action_providers.action_base import ActionBase

class AnsibleAction(ActionBase):
	"""
		Runs an ansible playbook on a generated inventory file with vars from input form
	"""

	# for inventory file
	tmp_path = ''
	filename = ''
	extra_vars = {}		# evals false while empty

	def set_endpoint(self, endpoint, host_vars):
		"""
			Builds the inventory file for the specified endpoint, including the variables provided from the input form

			:param host_vars: contains the variables from the input_form to be added to inventory
		"""
		print("endpoint type: " + type(endpoint).__name__)
		print("host vars: " + str(host_vars))
		# Only save vars that are adjusted
		for key in host_vars:
			if not (host_vars[key][0] == "{" and host_vars[key][1] == "{" and host_vars[key][-1] == "}" and host_vars[key][-2] == "}"):
				self.extra_vars[key] = host_vars[key]
		print("extra vars: " + str(self.extra_vars))

		if type(endpoint).__name__ == "unicode":
			self.filename = endpoint
			return

		contents = ''
		contents += "[" + endpoint['name'].replace(' ','') + "]\n"
		contents += endpoint['ip'] + " ansible_connection=ssh ansible_ssh_user=" + endpoint['username'] + " ansible_ssh_pass=" + endpoint['password'] + "\n\n"
		print(contents)

		self.tmp_path, self.filename = tempfile.mkstemp()
		with os.fdopen(self.tmp_path, 'w') as tmp:
			tmp.write(contents)

		return

	def execute_template(self, template):
		"""
			Builds Ansible command to execute, writes it to a tmp file, and then executes it.
			Requires SSHPass, logs into servers via SSH rather than keys by default. (Can use any auth means if you add a custom inventory endpoint)
			Certainly vulnerable to command injection on local machine.

			:param template: path to the playbook to be ran
			:return: String results from the output of the script
		"""

		command = ''
		command += "ansible-playbook "
		command += template
		command += " -i "
		command += str(self.filename)
		if self.extra_vars:
			command += " --extra-vars ' "
			for key in self.extra_vars:
				# if user is leaving vars alone don't include them in command
				if not (self.extra_vars[key][0] == "{" and self.extra_vars[key][1] == "{" and self.extra_vars[key][-1] == "}" and self.extra_vars[key][-2] == "}"):
					command += key + "=" + self.extra_vars[key] + " "
			command += "'"
		print("built command: %s" % command)

		path = "/tmp/" + str(uuid.uuid4())
		f = open(path, "w+")
		f.write(command)
		f.flush()
		time.sleep(.5)
		filename = f.name
		os.chmod(filename, 0700)
		f.close()
		env = os.environ.copy()

		try:
			output = subprocess.check_output(filename, shell=True, env=env)
			print output
			if self.tmp_path != '':
				os.remove(self.filename)
			self.extra_vars = {}
			return output
		except CalledProcessError as cpe:
			o = "Error calling local script"
			o += subprocess.check_output('cat %s' % filename, shell=True, env=env)
			o += "\n-----------------------------\n"
			o += str(cpe)
			o += "\n-----------------------------\n"
			print o
			if self.tmp_path != '':
				os.remove(self.filename)
			self.extra_vars = {}
			return o

