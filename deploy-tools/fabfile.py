from fabric.contrib.files import append, exists, sed
from fabric.api import env, local, run, settings

import random

REPO_URL = 'https://github.com/samduthie/tdd-with-django.git'
JNOTEBOOK_REPO_URL = 'https://github.com/samduthie/jnotebooks.git'

def provision():
    #_create_user()
    with settings(prompts={'Do you want to continue? [Y/n]': 'Y'}):
	    run('sudo apt-get update')
	    run('sudo apt-get install nginx git python3 python3-pip')
	    run('sudo pip3 install virtualenv')
    print("provision completed...")
   
    if _query("deploy server? "):
        print("deployment started...")
        deploy()
        print("deployment finished...")
   
    if _query("install jupyter notebooks? "):
        print("installing notebooks...")
        setup_jupyter()

    print("provision finished")

def deploy():
	site_folder = '/home/%s/sites/%s' % (env.user, env.host)
	source_folder = site_folder + '/source'
	_create_directory_structure_if_necessary(site_folder)
	_get_latest_source(source_folder)
	_update_settings(source_folder, env.host)
	_update_virtualenv(source_folder)
	_update_static_files(source_folder)
	_update_database(site_folder, source_folder)

def setup_config():
	site_folder = '/home/%s/sites/%s' % (env.user, env.host)
	source_folder = site_folder + '/source'
	_setup_site_config(source_folder, site_folder)


def setup_jupyter():
	_setup_jupyter()

def _create_user():
	#method not called from anywhere
	#must be switched into from root
    if not (exists('/home/%s' % env.user)):
        run('useradd -m -s /bin/bash %s' % env.user)
        run('usermod -a -G sudo %s' % env.user)
        run('passwd %s' % env.user)
        run('sudo su %s' % env.user)

def _create_directory_structure_if_necessary(site_folder):
	for subfolder in('database', 'static', 'virtualenv', 'source'):
		run('#mkdir -p %s/%s' % (site_folder, subfolder))

def _get_latest_source(source_folder):
	if exists(source_folder + '/.git'):
		run('cd %s && git fetch' % (source_folder,))
	else:
		run('git clone %s %s' % (REPO_URL, source_folder))
	current_commit = local("git log -n 1 --format=%H", capture=True)
	run('cd %s && git reset %s --hard' % (source_folder, current_commit))

def _update_settings(source_folder, site_name):
	settings_path = source_folder + '/superlists/settings.py'
	sed(settings_path, "DEBUG = True", "DEBUG = False")
	sed(settings_path, 
		'ALLOWED_HOSTS = .+$',
		'ALLOWED_HOSTS = ["%s"]' % (site_name,)
	)
	secret_key_file = source_folder + '/superlists/secret_key.py'
	if not exists(secret_key_file):
		chars = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
		key = ''.join(random.SystemRandom().choice(chars) for _ in range(50))
		append(secret_key_file, "SECRET_KEY = '%s'" % (key,))
	append(settings_path, '\nfrom .secret_key import SECRET_KEY')

def _update_virtualenv(source_folder)	:
	virtualenv_folder = source_folder + '/../virtualenv'
	if not exists(virtualenv_folder + '/bin/pip'):
		run('virtualenv --python=python3 %s' % (virtualenv_folder,))
	run('%s/bin/pip install -r %s/requirements.txt' % (
		virtualenv_folder, source_folder
	))

def _update_static_files(source_folder):
	run('cd %s && ../virtualenv/bin/python3 manage.py collectstatic --noinput' % (
		source_folder,
	))

def _update_database(site_folder, source_folder):
	database_folder = source_folder + '/../database'
	database_file = 'db.sqlite3'
	if not (database_file):
		run('#mkdir -p %s/%s' % (site_folder, 'database'))
		run('#mv  %s %s' % (database_file, database_folder))
		
def _query(query):
    answer = raw_input(query)
    if answer is 'y' or answer is 'yes':
        return True
    if answer is 'n' or answer is 'no':
        return False
    print("Please only answer (y)es or (n)o")
    _query(query)

def _setup_site_config(source_folder, site_folder):
	run ('cd %s' % source_folder)
	
	run("sudo cp deploy-tools/gunicorn-upstart.template.conf \
		/etc/init/gunicorn-superlists.conf")	

	run("sudo cp deploy-tools/nginx.template.conf \
		/etc/nginx/sites-available/superlists")

	run("sudo ln -s /etc/nginx/sites-available/superlists-staging \
		 /etc/nginx/sites-enabled/superlists-staging")

	run("../virtualenv/bin/gunicorn --bind unix:/tmp/superlists.socket superlists.wsgi:application")

	run("sudo service nginx reload")

def _create_user_config():
	#todo - grab configs from git
	pass

def _setup_jupyter():
	if env.user == 'root':
		folder = '%s' % env.user
	else:
		folder = 'home/%s' % env.user

	'''todo
	create alias
	django shell

	'''
	#Sets up j notebook environment
	#pulls j notebooks from repo
	#Downloading Miniconda 64Bits for Linux
	if not (exists('/%s/miniconda3' % (folder))):
		with settings(prompts={'Do you want to continue [Y/n]? ': 'Y'}):
			run("wget https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh")
			#Changing file permission for execution
			run("chmod a+x Miniconda3-latest-Linux-x86_64.sh")
			#Installing Miniconda
			run("./Miniconda3-latest-Linux-x86_64.sh")
			run("source ~/.bashrc")
	else:
		print("conda already installed")

	if not (exists ('/%s/miniconda3/envs/py3' % (folder))):
		run("./miniconda3/bin/conda create -n py3 python=3 ipython")
	else:
		print("py3 profile already set up")
	# Activating created environment
	run("source /%s/miniconda3/bin/activate py3" % (folder))

	with settings(prompts={' Proceed ([y]/n)?' : 'y'}):
		run("/%s/miniconda3/bin/conda install jupyter" % (folder))
		# Installing the packages
		run("/%s/miniconda3/bin/conda install numpy" % (folder))
		run("/%s/miniconda3/bin/conda install pandas" % (folder))
		run("/%s/miniconda3/bin/conda install matplotlib" % (folder))

	if not (exists('/%s/jnotebooks' % env.user)):
		run("git clone %s jnotebooks" % JNOTEBOOK_REPO_URL)
		run("/%s/miniconda3/bin/jupyter notebook --generate-config" % env.user)
		
	if _query("Start Jupyter Notebooks? "):
		run("/%s/miniconda3/bin/conda/jupyter notebook --ip=0.0.0.0 --port=8080 --no-browser --allow-root &" % env.user)
