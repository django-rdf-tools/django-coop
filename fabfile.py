# -*- coding: utf-8 -*-
from fabric.api import env,local,run,sudo,cd,hide,show,settings,prefix,prompt,require
from fabric.contrib.console import confirm
from fabric.colors import red, green,yellow
from fabric.decorators import task,with_settings
from fabric.contrib.files import append,contains,exists,sed,upload_template
from fabtools import icanhaz
import fabtools

#Paramètres Vagrant
env.vm_path = "/Users/dom/VM/devcoop"


#Paramètres par défaut
env.domain = "dev.django.coop"
env.projet = "devcoop"
# Paramètres PostGreSQL
env.pgpass = '123456'
# Paramètres Déploiement
env.websrv=1


def pretty_apt(pkglist):
    for pkg in (pkglist):
        icanhaz.deb.package(pkg)
        print(green(u'Paquet Debian "'+unicode(pkg)+u'" : installé.'))


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
    if not env.projet :
        prompt('Nom de domaine:',       default=env.domain, key='domain')
        prompt('Nom du projet django:', default=env.projet, key='projet')
        prompt('Passe PostgreSQL :',default=env.pgpass, key='pgpass')
        #prompt('Config : (1)Apache seul ou (2)Apache+Nginx :',key='websrv',validate=int,default=env.websrv)


@task
def gandi():
    '''Ajoute le dépôt APT Gandi'''
    with hide('running', 'stdout', 'stderr'):
        run('wget http://mirrors.gandi.net/gandi/pubkey')
        sudo('apt-key add pubkey')
        print(green('Gandi public key added.'))


@task
def postgresql_setup():
    '''PostgreSQL 8.4 + PostGIS 1.5'''
    config()
    pretty_apt(['libpq-dev','binutils','gdal-bin','libproj-dev',
    'postgresql-8.4-postgis','postgresql-server-dev-8.4','python-psycopg2'])
    fabtools.deb.upgrade()
    #'postgresql-server-dev-8.4',
    #'postgresql-8.4','postgresql-client-8.4' ?
    # création d'un utilisateur postgresql avec le meme nom d'utilisateur
    icanhaz.postgres.user(env.user, env.pgpass)
    if not fabtools.postgres.user_exists(env.user):
        sudo('''psql -c "ALTER ROLE %(user)s CREATEDB;"''' % env, user='postgres')
        sudo('''psql -c "ALTER USER %(user)s with SUPERUSER;"''' % env, user='postgres')
        print(green('Création du superuser PostGreSQL %(user)s.' % env))
    if not exists('.pgpass'):
        run('echo "*:*:*:vagrant:123456" >> .pgpass')
        sudo('chmod 0600 .pgpass')
        print(green('Création fichier .pgpass.'))
    postgis_template()
    postgresql_net_access()
    icanhaz.postgres.server()#start server



@task
def django_project():
    '''Créer un projet django dans son virtualenv'''
    config()
    if not exists('/home/%(user)s/.virtualenvs/%(projet)s' % env ):
        #if confirm('Pas de virtualenv nommé "%s", faut-il le créer ?' % (env.projet),default=False):
        run('mkvirtualenv %(projet)s' % env)
    if not exists('projects/%s/' % (env.projet)):
        print(yellow('le projet %(projet)s n’existe pas encore' % env))
        if confirm('Créer un projet django nommé "%(projet)s" ?' % env ,default=False):
            with prefix('workon %(projet)s' % env):
                with cd('projects/'):
                    run('django-admin.py startproject %s' % (env.projet))
                    print(green('Projet Django "%(projet)s" créé.' % env))
    else:
        print(green('Le projet Django "%(projet)s" existe déjà.' % env))                          
    #créer la db avec le nom du projet (idempotent)
    icanhaz.postgres.database(env.projet, env.user, 'template_postgis')
    print(green('Création d’une base de données %(projet)s.' % env))
    django_wsgi()
    apache_vhost()
    dependencies() 
    #synchro db
    #git commands   


@task
@with_settings(show('user'))
#@with_settings(hide='warnings', 'running', 'stdout', 'stderr'))
def test():    
    print('Salut!')
    
    
@task
def setup():
    '''Installation de base pour Ubuntu >= 10.10'''
    config()
    #if gandi
    lang()
    fabtools.deb.update_index() # apt-get quiet update
    fabtools.deb.upgrade()
    # paquets communs à tous les serveurs Django+geodjango
    pretty_apt(['git-core','mercurial','gcc','curl','build-essential',
        'python-imaging','python-setuptools','memcached','python-memcache'])
    
    # pip special case
    if not fabtools.python.is_pip_installed():
        fabtools.python.install_pip()    
        print(green('pip : installé.'))
    
    environnement()
    #config apache
    if(env.websrv == 1):
        apache()
    elif(env.websrv == 2):
        apache_nginx()
    


def django_wsgi():
    if not exists('/home/%(user)s/%(projet)s.wsgi'):
        with prefix('workon %(projet)s' % env):
            sp_path = run('cdsitepackages ; pwd')
            wsgi_context = {
                'site-packages' : sp_path,
                'user' : env.user,
                'projet' : env.projet
            }
        upload_template('fab_templates/wsgi.txt','%(projet)s.wsgi' % env, context=wsgi_context, use_sudo=True)
        print(green('Script %(projet)s.wsgi créé.'))


def dependencies():
    '''Installe les modules pythons nécessaires au projet'''
    with cd('projects/%(projet)s' % env):
        if exists('requirements.txt'):
            print(green('Installation des dépendances du projet.'))
            with prefix('workon %(projet)s' % env):
                run('pip install -r requirements.txt')
                sudo('apachectl restart')
        else:
            print(yellow('Aucun fichier "requirements.txt" trouvé.'))


def environnement():
    icanhaz.python.package('virtualenv',use_sudo=True)
    icanhaz.python.package('virtualenvwrapper',use_sudo=True)
    #icanhaz.python.package('virtualenvwrapper.django',use_sudo=True)
    if not 'www-data' in run('echo | groups %s' % (env.user)):
        sudo('usermod -a -G www-data %s' % (env.user))
        print(green('Utilisateur %s ajouté au grope "www-data"' % (env.user)))
    if not exists('projects/'):
        run('mkdir projects .python-eggs .virtualenvs')
        sudo('chown %s:www-data .python-eggs' % (env.user))
        sudo('chgrp -R www-data projects/')
        sudo('chmod -R 2750 projects/')
        print(green('Dossier "projects" créé.'))   
    # sur .bash_profile et pas .bashrc
    append('.bash_profile','export WORKON_HOME=$HOME/.virtualenvs')
    append('.bash_profile','export PROJECT_HOME=$HOME/projects')
    append('.bash_profile','export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python')
    append('.bash_profile','export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv')
    append('.bash_profile','source /usr/local/bin/virtualenvwrapper.sh')


def apache_nginx():
    '''Apache + mod_wsgi pour Django avec Nginx en proxy'''
    icanhaz.deb.packages(['apache2','libapache2-mod-wsgi'])
    with cd('/etc/apache2/'):
        if not contains('ports.conf','127.0.0.1',use_sudo=True):
            sed('ports.conf','NameVirtualHost \\*:80','NameVirtualHost 127.0.0.1:80',use_sudo=True)
            sed('ports.conf','Listen 80','Listen 127.0.0.1:80',use_sudo=True)
            print(green('/etc/apache2/ports.conf updated'))
    with cd('/etc/apache2/'):
        if not contains('apache2.conf','ServerName localhost',use_sudo=True):    
            sudo("echo 'ServerName localhost'|cat - apache2.conf > /tmp/out && mv /tmp/out apache2.conf")
            sudo("sed -i 's/KeepAlive On/KeepAlive Off/g' apache2.conf")    
            print(green('/etc/apache2/apache2.conf updated'))
    #sudo("apache2ctl graceful") #plante de toute façon sans virtualhosts
    pretty_apt(['nginx'])
    with cd('/etc/nginx/'):
        if not contains('nginx.conf','worker_processes 2;',use_sudo=True): 
            sudo("sed -i 's/worker_processes 4;/worker_processes 2;/g' nginx.conf")
            print(green('/etc/nginx/nginx.conf updated'))
    #to be continued...


def apache():
    '''Config générale Apache + mod_wsgi sans media proxy'''
    pretty_apt(['apache2','libapache2-mod-wsgi'])
    #virer le site par défaut
    with cd('/etc/apache2/sites-enabled/'):
        if exists('000-default'):
            sudo('rm 000-default')
            print(green('Site par défaut d’Apache supprimé'))


def apache_vhost():
    if(env.websrv == 1):
        vhost_context = {
            'user' : env.user,
            'domain' : env.domain,
            'projet' : env.projet
        }
        upload_template('fab_templates/vhost.txt','/etc/apache2/sites-available/%(domain)s' % env, context=vhost_context, use_sudo=True)
        with cd('/etc/apache2/'):
            sudo('rm sites-enabled/%(domain)s' % env)
            sudo('ln -s `pwd`/sites-available/%(domain)s sites-enabled/%(domain)s' % env)
            print(green('VirtualHost Apache pour %(domain)s configuré.' % env))
    elif(env.websrv == 2):
        print(red('Pas encore écrit !!!')) #TODO
    sudo('apachectl restart')
        


def lang():
    '''Règlage des locale de l'OS'''
    lang = run("echo $LANG")
    if(lang != 'fr_FR.UTF-8'):
        sudo('locale-gen fr_FR.UTF-8')
        sudo('/usr/sbin/update-locale LANG=fr_FR.UTF-8')
        print(green('Locale mise à jour.'))


def postgis_template():
    '''creation du template postgis - pour PostGIS 1.5 et Ubuntu > 10.10'''
    if not 'template_postgis' in run('echo|psql -l'):
        run('createdb -E UTF8 template_postgis')
        run('createlang -d template_postgis plpgsql')
        run('''psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"''')
        run('psql -d template_postgis -f `pg_config --sharedir`/contrib/postgis-1.5/postgis.sql')
        run('psql -d template_postgis -f `pg_config --sharedir`/contrib/postgis-1.5/spatial_ref_sys.sql')
        run('psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"')
        run('psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"')
        run('psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"')
        print(green('template_postgis pour PostgreSQL créé'))


def postgresql_net_access():
    with cd('/etc/postgresql/8.4/main/'):
        change = False
        if not contains('pg_hba.conf','local   all         all                               password',use_sudo=True): 
            sudo("sed -i 's/local   all         all                               ident/local   all         all                               password/g' pg_hba.conf",user='postgres')
            change = True
            print(green('Accés local PostgreSQL pour Django'))
        if not contains('pg_hba.conf','host    all         all         0.0.0.0/0             md5'):
            append('pg_hba.conf','host    all         all         0.0.0.0/0             md5',use_sudo=True)
            change = True
            print(green('Accés à PostgreSQL via interfaces IP externes'))
        if not contains('postgresql.conf','listen_addresses = \'\\*\'',use_sudo=True):
            sudo('echo "listen_addresses = \'*\'"|cat - postgresql.conf > /tmp/out && mv /tmp/out postgresql.conf')
            change = True
            print(green('PostgreSQL écoute sur toutes les interfaces IP'))
        if change : sudo('/etc/init.d/postgresql restart')


