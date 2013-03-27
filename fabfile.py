from __future__ import with_statement
from fabric.api import *
from fabric.contrib.console import confirm
from fabric.contrib.files import exists

import boto
from boto.s3.key import Key
from boto import ec2

from datetime import datetime
import sys, pprint, time, ConfigParser
from ConfigParser import SafeConfigParser

parser = SafeConfigParser()
parser.read('configure.ini')

ec2keypairname = parser.get('aws', 'ec2keypairname')
localkeypath = parser.get('aws', 'localkeypath')

precise_12_04_2 = 'ami-de0d9eb7'

aws_access_key_id = parser.get('aws', 'aws_access_key_id')
aws_secret_access_key =parser.get('aws', 'aws_secret_access_key')
volid = 'vol-9415bbe4'

def last():

	from ConfigParser import SafeConfigParser

	parser = SafeConfigParser()
	parser.read('lastLaunch.ini')
	env.user = parser.get('lastLaunch', 'username')
	env.host_string = parser.get('lastLaunch', 'host_string')
	env.key_filename = [parser.get('lastLaunch', 'keypath')]
	env.last_instance = parser.get('lastLaunch', 'instance')


def printssh():
	print 'ssh -i ~/.ssh/ec2-keypair ubuntu@%s' % (env.host_string)
	local('echo "ssh -i ~/.ssh/ec2-keypair ubuntu@%s" | pbcopy ' % (env.host_string))

def printhttp():
	print 'http://%s' % (env.host_string)	
	local('echo "http://%s" | pbcopy ' % (env.host_string))
	

def terminate():
	#terminate_instances
	with settings(warn_only = True):
		print 'killing last instance'
		conn = ec2.EC2Connection(aws_access_key_id, aws_secret_access_key)
		conn.terminate_instances(env.last_instance)
		time.sleep(1)

def test():
	run('uname -a')
	run('lsb_release -a')	

def createXL():
	'''creates an m3.xlarge - 15 GiB memory, 13ECU (4x3.25)'''
	_create('m3.xlarge')

def createL():
	'''creates an m1.large - 7.5 GiB memory, 4ECU (2x2)'''
	_create('m1.large')

def createCustom():
	'''usage: fab --set ec2=m2.xlarge createCustom '''
	_create(env.ec2)

def createS():
	'''creates an m1.small - 1.7 GiB memory, 1ECU (1x1)'''
	_create('m1.small')

def createXXL():
	'''creates an m2.2xlarge - 34.2 GiB of memory, 13ECU (4x3.25)'''
	_create('m2.2xlarge')

def _create(size):
	'''Creates a new large instance on ec2'''	
	with settings(warn_only = True):
		conn = ec2.EC2Connection(aws_access_key_id, aws_secret_access_key)
		
		time.sleep(1)
		reservation = conn.run_instances(precise_12_04_2, instance_type=size, placement='us-east-1d', key_name='ec2-keypair')
		time.sleep(1)
		instance = reservation.instances[0]
		time.sleep(1)

		print 'Starting instance %s' %(instance)
		while not instance.update() == 'running':
			time.sleep(1)

		instance.add_tag('Name', 'ipython-deploy')		

		time.sleep(1)	
		
		print 'Instance started: %s' % instance.__dict__['id']
		print 'Private DNS: %s' % instance.__dict__['private_dns_name']
		print 'Private IP: %s' % instance.__dict__['private_ip_address']
		print 'Public DNS: %s' % instance.__dict__['public_dns_name']
		

		# write temporary settings in case something goes wrong mid-configuration
		import ConfigParser
		import sys
		
		parser = ConfigParser.SafeConfigParser()
		parser.add_section('lastLaunch')
		parser.set('lastLaunch', 'host_string', str(instance.__dict__['public_dns_name']))
		parser.set('lastLaunch', 'keypath', localkeypath)
		parser.set('lastLaunch', 'username', 'ubuntu')
		parser.set('lastLaunch', 'instance', instance.__dict__['id'])
		parser.write(open('lastLaunch.ini', 'w'))

		env.user = 'ubuntu'
		env.host_string = instance.__dict__['public_dns_name']
		env.key_filename = [localkeypath]

		# enableNeuroDebian()
		# base()
		# provision()
		# externals()
		# notebook()
		# pmip()


		print 'Instance has been launched successfully'
		print 'To access, open a browser to http://%s' % (instance.__dict__['public_dns_name'])
		print 'ssh -i ~/.ssh/ec2-keypair ubuntu@%s' % (instance.__dict__['public_dns_name'])


def install():

	with settings(warn_only=True):

		_enableNeuroDebian()
		_base()
		_provision()
		_externals()

		pass



def mountstatus():


	with settings(warn_only=True):

		v_to_mount = ''
		conn = ec2.EC2Connection(aws_access_key_id, aws_secret_access_key)
		vol = conn.get_all_volumes()
		for v in vol:
			if v.id == volid:
				v_to_mount = v

		if v_to_mount.attachment_state() == None:
			print 'Volume not attached'
		else: 
			print 'Volume attached with status: %s' % v_to_mount.attachment_state()


def attachebs():

	with settings(warn_only=True):

		v_to_mount = ''
		conn = ec2.EC2Connection(aws_access_key_id, aws_secret_access_key)
		vol = conn.get_all_volumes()
		for v in vol:
			if v.id == volid:
				v_to_mount = v

		print 'trying to attach volume %s to instance %s' % (v_to_mount, env.last_instance)

		if v_to_mount.attachment_state() == None:
			print 'volume not attached, continuing'
			result = v_to_mount.attach(env.last_instance, '/dev/xvdf')

			# if result == True:
			# 	print 'volume attached successfully, sleep for 20s then mount'
			# 	sudo('mkdir -m 000 /vol')
			# 	sudo('mount /dev/xvdf /vol')

			# else:
			# 	print 'volume not attached'

		else: 
			print v_to_mount.attachment_state()

		# 	if exists('/vol'):
		# 		print 'vol present'
		# 	else:
		# 		sudo('mkdir -m 000 /vol')
		# 		sudo('mount /dev/xvdf /vol')		


def mountebs():

	with settings(warn_only=True):

		if not exists('/vol'):
			sudo('mkdir -m 000 /vol')
			sudo('mount /dev/xvdf /vol')

		# # sudo mkfs.ext4 /dev/xvdf

def unmountebs():

	with settings(warn_only=True):

		sudo('umount /dev/xvdf')

		v_to_unmount = ''
		conn = ec2.EC2Connection(aws_access_key_id, aws_secret_access_key)
		vol = conn.get_all_volumes()
		for v in vol:
			if v.id == volid:
				v_to_unmount = v

		result = v_to_unmount.detach(force=True)
		if result == True:
			print 'volume detached successfully'
		else:
			print 'volume not attached successfully'

		print v_to_unmount.attachment_state()




def _base():
	'''[create] Basic packages for building, version control'''
	with settings(warn_only=True):
		
		# update existing tools
		run("sudo apt-get -y update", pty = True)
		run("sudo apt-get -y upgrade", pty = True)		
		
		# install build and CVS tools
		packagelist = ' '.join(['git-core', 'mercurial', 'subversion', 'unzip', 'build-essential', 'g++', 'libav-tools', 'uuid-dev', 'libfreetype6-dev','libpng12-dev'])
		
		run('sudo apt-get -y install %s' % packagelist, pty = True)

		# install python components
		packagelist = ' '.join(['python-setuptools', 'python-pip', 'python-dev', 'python-lxml', 'libxml2-dev', 'python-imaging', 'libncurses5-dev', 'cmake-curses-gui', 'imagemagick', 's3cmd'])
		run('sudo apt-get -y install %s' % packagelist, pty = True)
		
		packagelist = ['tornado', 'supervisor', 'virtualenv', 'jinja2']
		for each_package in packagelist: 
			print each_package
			run('sudo pip install %s' % each_package, pty = True)


def setupBlenderEnvironment():

	_base()

	with settings(warn_only=True):

		sudo('add-apt-repository ppa:irie/blender')
		sudo('apt-get update')
		sudo('apt-get -y install blender')

		put('id_rsa.pub','~/.ssh/id_rsa.pub')
		put('id_rsa', '~/.ssh/id_rsa')
		
		sudo('chmod 0600 .ssh/id_rsa')
		sudo('chmod 0600 .ssh/id_rsa.pub')

		put('s3cfg', '.s3cfg')
		sudo('chmod 0600 .s3cfg')

		run('s3cmd get s3://aibs/untitled.blend untitled.blend --force')



def _notebook():
	'''install python notebook'''
	with settings(warn_only=True):

		put('id_rsa.pub','~/.ssh/id_rsa.pub')
		put('id_rsa', '~/.ssh/id_rsa')
		
		sudo('chmod 0600 .ssh/id_rsa')
		sudo('chmod 0600 .ssh/id_rsa.pub')

		sudo('easy_install readline')
		sudo('apt-get install -y libfreetype6-dev libpng12-dev python-matplotlib')

		sudo('pip install -U requests')
		sudo('pip install -U beautifulsoup4')
		sudo('pip install pyzmq')
		sudo('pip install workerpool')
		# sudo('pip install -U matplotlib')

		run('ipython profile create default')
		run('ipython profile create nbserver')
		run("rm -rvf ~/.ipython/profile_nbserver")
		put('profile_nbserver.zip', '.ipython/profile_nbserver.zip')

		with cd('.ipython'):
			run('unzip profile_nbserver.zip')		
			run('rm profile_nbserver.zip')

		put('supervisord.conf.ipython')
		sudo('mv supervisord.conf.ipython /home/ubuntu/config/supervisord.conf')
		sudo('rm /etc/supervisord.conf')
		sudo('ln -s /home/ubuntu/config/supervisord.conf /etc/supervisord.conf')

		put('supervisor.start')
		sudo('supervisord')
		sudo('chmod +x supervisor.start')
		sudo('chown root:root supervisor.start')
		sudo('mv /home/ubuntu/supervisor.start /etc/init.d/supervisor')
		sudo('update-rc.d -f supervisor remove')
		sudo('update-rc.d supervisor defaults')
		sudo('supervisorctl restart all')


def connectivity():

	with settings(warn_only=True):

		_notebook()
		
		# get the most recent version, or clone to directory
		if exists('connectivity-blend'):
			with cd('connectivity-blend'):
				run('git pull --rebase')
		else:
			run('git clone git@github.com:richstoner/connectivity-blend.git')				
			run('git config --global user.name "richstoner"')
			run('git config --global user.email "stonerri@gmail.com"')
































