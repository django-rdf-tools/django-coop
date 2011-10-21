# -*- coding: utf-8 -*-
from fabric.api import env,local,run,sudo,cd,hide,show,settings,prefix,prompt,require
from fabric.contrib.console import confirm
from fabric.colors import red, green,yellow
from fabric.decorators import task
from fabric.contrib.files import append,contains,exists,sed,upload_template
from fabtools import icanhaz
import fabtools

#Paramètres Vagrant
env.vm_path = "/Users/dom/VM/devcoop"


#Paramètres par défaut
env.domain = "dev.django.coop"
env.projet = "devcoop"
# Paramètres PostGreSQL
env.pg_pass = '123456'


@task
def _vagrant():
    '''A utiliser en premier pour une VM locale'''
    # change from the default user to 'vagrant'
    env.user = 'vagrant'
    # connect to the port-forwarded ssh
    env.hosts = ['127.0.0.1:2222']
    # use vagrant ssh key
    #with cd(env.vm_path):
    result = local('vagrant ssh_config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]
    
    #icanhaz.deb.packages(['dkms'])#mise à jour guest additions


@task
def _alias():
    '''load local SSH alias/keys'''
    def _annotate_hosts_with_ssh_config_info():
        from os.path import expanduser
        from paramiko.config import SSHConfig
        def hostinfo(host, config):
            hive = config.lookup(host)
            if 'hostname' in hive:
                host = hive['hostname']
            if 'user' in hive:
                host = '%s@%s' % (hive['user'], host)
            if 'port' in hive:
                host = '%s:%s' % (host, hive['port'])
            return host
        try:
            config_file = file(expanduser('~/.ssh/config'))
        except IOError:
            pass
        else:
            config = SSHConfig()
            config.parse(config_file)
            keys = [config.lookup(host).get('identityfile', None)
                for host in env.hosts]
            env.key_filename = [expanduser(key) for key in keys if key is not None]
            env.hosts = [hostinfo(host, config) for host in env.hosts]
    _annotate_hosts_with_ssh_config_info()


def config():
    prompt('Nom de domaine:',default=env.domain,key='domain')
    prompt('Nom du projet django:',default=env.projet,key='projet')
    prompt('Config : (1)Apache seul ou (2)Apache+Nginx :',key='websrv',validate=int,default=1)


@task
def gandi():
    '''Ajoute le dépôt Gandi dans les dépôts APT autorisés'''
    with hide('running', 'stdout', 'stderr'):
        run('wget http://mirrors.gandi.net/gandi/pubkey')
        sudo('apt-key add pubkey')
        print(green('Gandi mirror added'))


def lang():
    '''Règlage des locale de l'OS'''
    with hide('running', 'stdout', 'stderr'):
        lang = run("echo $LANG")
        if(lang != 'fr_FR.UTF-8'):
            sudo('locale-gen fr_FR.UTF-8')
            sudo('/usr/sbin/update-locale LANG=fr_FR.UTF-8')
            print(green('Locale updated'))


def postgresql_setup():
    '''PostgreSQL 8.4 installation & configuration'''
    #'postgresql','binutils','gdal-bin','libproj-dev','postgis',  
    icanhaz.deb.packages(['libpq-dev'])
    icanhaz.deb.packages(['postgresql-8.4','postgresql-client-8.4', 'postgis','postgresql-8.4-postgis'])
    icanhaz.deb.packages(['postgresql-server-dev-8.4','python-psycopg2'])
    
    # création d'un utilisateur postgre avec le meme nom d'utilisateur
    icanhaz.postgres.user(env.user, env.pg_pass)
    
    #creation du template postgis
    with settings( show('user'), hide('warnings', 'running', 'stdout', 'stderr'),warn_only=True ):
        if not 'template_postgis' in run('echo|psql -l'):
            sudo('su postgres; POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib/postgis-1.5')
            sudo('su postgres; createdb -E UTF8 template_postgis')
            sudo('su postgres; createlang -d template_postgis plpgsql # Adding PLPGSQL language support.')
            sudo('su postgres; psql -d postgres -c "UPDATE pg_database SET datistemplate=\'true\' WHERE datname=\'template_postgis\';"')
            sudo('su postgres; psql -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql')
            sudo('su postgres; psql -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql')
            sudo('su postgres; psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"')
            sudo('su postgres; psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"')
            sudo('su postgres; psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"')

    
    icanhaz.postgres.server()
    with cd('/etc/postgresql/8.4/main/'):
        change = False
        #accès par mot de passe en local
        if not contains('pg_hba.conf','local   all         all                               password',use_sudo=True): 
            sudo("sed -i 's/local   all         all                               ident/local   all         all                               password/g' pg_hba.conf",user='postgres')
            change = True
        #rajouter une ligne pour qu'on accède de l'extérieur 
        if not contains('pg_hba.conf','host    all         all         0.0.0.0/0               md5'):
            append('pg_hba.conf','host    all         all         0.0.0.0/0               md5',use_sudo=True)
            change = True
        # le serveur écoute sur toutes les interfaces    
        if not contains('postgresql.conf','listen_addresses = \'\\*\'',use_sudo=True):
            sudo('echo "listen_addresses = \'*\'"|cat - postgresql.conf > /tmp/out && mv /tmp/out postgresql.conf')
            change = True
        if change : sudo('/etc/init.d/postgresql restart')
    
    
    #icanhaz.postgres.database(env.projet, env.user, 'template_postgis')
    


def environnement():
    icanhaz.python.package('virtualenv',use_sudo=True)
    icanhaz.python.package('virtualenvwrapper',use_sudo=True)
    #icanhaz.python.package('virtualenvwrapper.django',use_sudo=True)
    with settings( show('user'), hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True ):
        if not 'www-data' in run('echo | groups %s' % (env.user)):
            sudo('usermod -a -G www-data %s' % (env.user))
            print(green('User %s added to the www-data group' % (env.user)))
        if not exists('projects/'):
            run('mkdir projects .python-eggs .virtualenvs')
            sudo('chown %s:www-data .python-eggs' % (env.user))
            sudo('chgrp -R www-data projects/')
            sudo('chmod -R 2750 projects/')
            print(green('Dossier projects créé'))   
        append('.bash_profile','export WORKON_HOME=$HOME/.virtualenvs')
        append('.bash_profile','export PROJECT_HOME=$HOME/projects')
        append('.bash_profile','source /usr/local/bin/virtualenvwrapper.sh')
        


def apache_nginx():
    '''Apache + mod_wsgi pour Django avec Nginx en proxy'''
    icanhaz.deb.packages(['apache2','libapache2-mod-wsgi'])
    with cd('/etc/apache2/'):
        with settings( show('user'), hide('warnings', 'running', 'stdout', 'stderr'),warn_only=True ):
            if not contains('ports.conf','127.0.0.1',use_sudo=True):
                sed('ports.conf','NameVirtualHost \\*:80','NameVirtualHost 127.0.0.1:80',use_sudo=True)
                sed('ports.conf','Listen 80','Listen 127.0.0.1:80',use_sudo=True)
                print(green('/etc/apache2/ports.conf updated'))
    with cd('/etc/apache2/'):
        with settings( show('user'), hide('warnings', 'running', 'stdout', 'stderr'),warn_only=True ):
            if not contains('apache2.conf','ServerName localhost',use_sudo=True):    
                sudo("echo 'ServerName localhost'|cat - apache2.conf > /tmp/out && mv /tmp/out apache2.conf")
                sudo("sed -i 's/KeepAlive On/KeepAlive Off/g' apache2.conf")    
                print(green('/etc/apache2/apache2.conf updated'))
    #sudo("apache2ctl graceful") #plante de toute façon sans virtualhosts
    icanhaz.deb.packages(['nginx'])
    with cd('/etc/nginx/'):
        with settings( show('user'), hide('warnings', 'running', 'stdout', 'stderr'), warn_only=True ):
            if not contains('nginx.conf','worker_processes 2;',use_sudo=True): 
                sudo("sed -i 's/worker_processes 4;/worker_processes 2;/g' nginx.conf")
                print(green('/etc/nginx/nginx.conf updated'))
    #to be continued...


def apache():
    '''Config générale Apache + mod_wsgi sans media proxy'''
    icanhaz.deb.packages(['apache2','libapache2-mod-wsgi'])
    #virer le site par défaut
    with cd('/etc/apache2/sites-enabled/'):
        if exists('000-default'):
            sudo('rm 000-default')


def django_project():
    '''Créer un projet django dans son virtualenv'''
    require('virtualenv',provided_by='mkvirtualenv')
    if not exists('projects/%s/' % (env.projet)):
        print(yellow('le projet %s n’existe pas encore' % (env.projet)))
        if confirm('Créer un projet django nommé "%s" ?' % (env.projet),default=False):
            with prefix('workon %s' % (env.virtualenv)):
                with cd('projects/'):
                    run('django-admin.py startproject %s' % (env.projet))           


def mkvirtualenv():
    '''Création du virtualenv'''
    if not exists('/home/%(user)s/.virtualenvs/%(projet)s' % env ):
        #if confirm('Créer un virtualenv nommé "%s" ?' % (env.projet),default=False):
        with settings(show('debug')):
            run('mkvirtualenv %(projet)s' % env)
    env.virtualenv = env.projet                


def apache_vhost():
    if(env.websrv == 1):
        vhost_context = {
            'user' : env.user,
            'domain' : env.domain,
            'projet' : env.projet
        }
        upload_template('fab_templates/vhost.txt','/etc/apache2/sites-available/%(domain)s' % env, context=vhost_context, use_sudo=True)
        with cd('/etc/apache2/'):
            with settings(warn_only=True):
                sudo('rm sites-enabled/%(domain)s' % env)
            sudo('ln -s `pwd`/sites-available/%(domain)s sites-enabled/%(domain)s' % env)
    elif(env.websrv == 2):
        print(red('Pas encore écrit !!!')) #TODO
    sudo('apachectl restart')
        


def django_wsgi():
    #cdsitepackages ;pwd  --> path du virutalenv
    with prefix('workon %(projet)s' % env):
        sp_path = run('cdsitepackages ; pwd')
    wsgi_context = {
            'site-packages' : sp_path,
            'user' : env.user,
            'projet' : env.projet
        }
    upload_template('fab_templates/wsgi.txt','%(projet)s.wsgi' % env, context=wsgi_context, use_sudo=True)



def dependencies():
    '''Installe les modules pythons nécessaires au projet'''
    with cd('projects/%(projet)s' % env):
        if exists('requirements.txt'):
            with prefix('workon %(projet)s' % env):
                run('pip install -r requirements.txt')
                sudo('apachectl graceful')

@task
def test():
        print('ok')
@task
def setup():
    '''Installation serveur'''
    config()
    #if gandi
    lang()
    #tout ça est commun à tous les serveurs Django (+geodjango)
    icanhaz.deb.packages(['git-core','mercurial','gcc','curl','build-essential'])
    icanhaz.deb.packages(['python-imaging','python-setuptools','memcached','python-memcache'])
    postgresql_setup()
    
    if(env.websrv == 1):
        apache()
    elif(env.websrv == 2):
        apache_nginx()
    
    if not fabtools.python.is_pip_installed():
        fabtools.python.install_pip()    
    
    environnement() #projects folder + install virtualenv tools
    mkvirtualenv()
    django_project() #si besoin de créer le projet
    django_wsgi() # juste le script
    dependencies() #si fichier requirements
    apache_vhost()
    
    #synchro db
    
    #git commands


    

