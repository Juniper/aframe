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

    def set_endpoint(self, endpoint, host_vars):
        """
            Builds the inventory file for the specified endpoint, including the variables provided from the input form

            :param host_vars: contains the variables from the input_form to be added to inventory
        """

        contents = ''
        contents += "[" + endpoint['name'].replace(' ','') + "]\n"
        contents += endpoint['ip'] + " ansible_connection=ssh ansible_ssh_user=" + endpoint['username'] + " ansible_ssh_pass=" + endpoint['password'] + "\n\n"
        contents += "[all:vars]\n"
        for key in host_vars:
            contents += key + "='" + host_vars[key] + "'\n"

        self.tmp_path, self.filename = tempfile.mkstemp()
        with os.fdopen(self.tmp_path, 'w') as tmp:
            tmp.write(contents)

        return

    def execute_template(self, template):
        """
           Builds Ansible command to execute, writes it to a tmp file, and then executes it.
           Requires SSHPass, logs into servers via SSH rather than keys.
           Certainly vulnerable to command injection on local machine.

           :param template: path to the playbook to be ran
           :return: String results from the output of the script
        """
        command = ''
        command += "ansible-playbook "
        command += template
        command += " -i "
        command += str(self.filename)
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
            os.remove(self.filename)
            return output
        except CalledProcessError as cpe:
            o = "Error calling local script"
            o += subprocess.check_output('cat %s' % filename, shell=True, env=env)
            o += "\n-----------------------------\n"
            o += str(cpe)
            o += "\n-----------------------------\n"
            print o
            os.remove(self.filename)
            return o

