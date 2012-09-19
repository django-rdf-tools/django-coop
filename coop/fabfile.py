# -*- coding: utf-8 -*-
from fabric.api import env, local, run, sudo, cd, hide, show, settings, prefix, prompt
from fabric.contrib.console import confirm
from fabric.colors import red, green, yellow
from fabric.decorators import task
from fabric.contrib.files import append, contains, exists, sed, upload_template
from fabtools import icanhaz
import fabtools

#Paramétres Vagrant
env.vm_path = "/Users/dom/VM/devcoop"

#Paramétres serveur
env.locale = 'fr_FR.UTF-8'

#Paramétres par défaut
domaine = "localhost"
projet = "coop_test"
alias = "coop_test"

pgpass = '123456'

# Paramétres Déploiement
env.websrv = 1


def pretty_apt(pkglist):
    for pkg in (pkglist):
        icanhaz.deb.package(pkg)
        print(green(u'Paquet Debian "' + unicode(pkg) + u'" : installé.'))


def pretty_pip(pkglist):
    for pkg in (pkglist):
        icanhaz.python.install(pkg)
        print(green(u'Module Python "' + unicode(pkg) + u'" : installé.'))

@task
def local_vm():
    '''First command to use for a Vagrant VM'''
    # change from the default user to 'vagrant'
    env.user = 'vagrant'
    # connect to the port-forwarded ssh
    env.hosts = ['127.0.0.1:2222']
    # use vagrant ssh key
    #with cd(env.vm_path):
    result = local('vagrant ssh_config | grep IdentityFile', capture=True)
    env.key_filename = result.split()[1]

    # si le partage de dossier ne marche pas bien encore ensuite :
    #mise à jour guest additions
    #icanhaz.deb.packages(['dkms','linux-headers-2.6.38-8-generic','linux-headers-generic'])
    # sudo('/etc/init.d/vboxadd setup') # puis "vagrant reload"


@task
def remote():
    '''First command to use for a SSH remote host'''
    env.hosts = [prompt('Alias SSH:', default=alias)]

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
    #sudo apt-get install nano
    #update-alternatives  --config editor
    #visudo
    #Dans le fichier, rendez vous à la ligne %admin ALL=(ALL) ALL.
    #Remplacez %admin ALL=(ALL) ALL par %admin ALL=(ALL) NOPASSWD: ALL


def project():
    if 'projet' not in env.keys():
        prompt('Nom du projet :', default=projet, key='projet')


def domain():
    if 'domaine' not in env.keys():
        prompt('DNS:', default=domaine, key='domaine')

#prompt('Config : (1)Apache seul ou (2)Apache+Nginx :',key='websrv',validate=int,default=env.websrv)


def gandi():
    '''Ajoute le dépôt APT Gandi'''
    with hide('running', 'stdout', 'stderr'):
        run('wget http://mirrors.gandi.net/gandi/pubkey')
        sudo('apt-key add pubkey')
        print(green('Gandi public key added.'))


def pip_bootstrap():
    with cd("/tmp"):
        run("curl --silent -O https://raw.github.com/pypa/pip/master/contrib/get-pip.py")
        sudo("python get-pip.py")


@task
def server_setup():
    '''Installation serveur pour Ubuntu >= 10.10'''
    with settings(show('user'), hide('warnings', 'running', 'stdout', 'stderr')):
        project()
        domain()
        #if gandi
        locale()
        sudo('apt-get -y install aptitude')  # demande un input
        print(yellow('Mise à jour de l’index APT...'))
        fabtools.deb.update_index()  # apt-get quiet update
        print(yellow('Mise à jour des paquets debian installés...'))
        fabtools.deb.upgrade()
        # paquets communs à tous les serveurs Django+geodjango
        print(yellow('Installation des paquets de base...'))
        pretty_apt(['git-core', 'mercurial', 'gcc', 'curl', 'build-essential',
                    'libfreetype6', 'libfreetype6-dev', 'liblcms1-dev', 'libpng12-dev',
                    'libjpeg8-dev', 'python-imaging',
                    'python-setuptools', 'nano', 'python-dev', 'swig',
                    'memcached', 'python-memcache'])

        # pip special case
        if not fabtools.python.is_pip_installed():
            fabtools.python.install_pip()
            print(green('pip : installé.'))

        virtualenv_setup()
        #config apache
        if(env.websrv == 1):
            apache_setup()
        elif(env.websrv == 2):
            apache_nginx()

        postgresql()


def postgresql():
    '''PostgreSQL 9.1 + PostGIS 1.5'''
    with settings(show('user'), hide('warnings', 'running', 'stdout', 'stderr')):
        project()
        if 'pgpass' not in env.keys():
            prompt('Passe PostgreSQL :', default=pgpass, key='pgpass')
        print(yellow('Configuration PostgreSQL+PostGIS...'))
        pretty_apt(['postgresql', 'binutils', 'gdal-bin', 'libproj-dev', 'postgresql-9.1-postgis',
                    'postgresql-server-dev-9.1', 'python-psycopg2', 'libgeoip1'])
        # print(yellow('Upgrading all packages...'))
        # fabtools.deb.upgrade()
        # création d'un utilisateur postgresql avec le meme nom d'utilisateur
        if not fabtools.postgres.user_exists(env.user):
            fabtools.postgres.create_user(env.user, env.pgpass)
            sudo('''psql -c "ALTER ROLE %(user)s CREATEDB;"''' % env, user='postgres')
            sudo('''psql -c "ALTER USER %(user)s with SUPERUSER;"''' % env, user='postgres')
            print(green('Création d’un superuser "%(user)s" PostgreSQL.' % env))
        if not exists('.pgpass'):
            run('echo "*:*:*:%(user)s:%(pgpass)s" >> .pgpass' % env)
            sudo('chmod 0600 .pgpass')
            print(green('Création du fichier .pgpass.'))
        run('curl https://docs.djangoproject.com/en/dev/_downloads/create_template_postgis-debian.sh -o postgis.sh')
        run('chmod +x postgis.sh')
        run('./postgis.sh')
        #postgresql_net_access()
        icanhaz.postgres.server()  # start server


def project_setup():
    # recolte des variables
    project()
    domain()
    locale()

    # creation du projet django (startproject)
    django_project()
    apache_vhost()
    django_wsgi()

    #créer la db avec le nom du projet (idempotent)
    create_pg_db()
    dependencies()
    sudo('apachectl restart')


@task
def coop_setup():
    """Creation d'un nouveau projet django-coop"""
    project()
    domain()
    locale()
    coop_project()
    dependencies()
    apache_vhost()
    create_pg_db()
    sudo('apachectl restart')


def coop_project():
    '''Créer un projet django dans son virtualenv'''
    project()
    domain()
    with settings(show('user'), hide('warnings', 'running', 'stdout', 'stderr')):
        if not exists('/home/%(user)s/.virtualenvs/%(projet)s' % env):
            # if confirm('Pas de virtualenv "%(projet)s", faut-il le créer ?' % env, default=False):
            run('mkvirtualenv %(projet)s' % env)
            run('source .bash_profile')
        with prefix('workon %(projet)s' % env):
            run('pip install django-coop')
            print(green('Django et django-coop installé.'))
        if not exists('projects/%s/' % (env.projet)):
            print(yellow('le projet %(projet)s n’existe pas encore' % env))
            if confirm('Créer un projet django nommé "%(projet)s" ?' % env,
                        default=False):
                with cd('projects/'):
                    with prefix('workon %(projet)s' % env):
                        run('coop-admin.py startproject %(projet)s --domain %(domaine)s' % env)
                        print(green('Projet Django-coop "%(projet)s" : Installé.' % env))
                        # coop-admin scripts creates the WSGI script so we won't call django_wsgi()
                with cd('projects/%(projet)s' % env):
                    with prefix('workon %(projet)s' % env):
                        run('chmod +x manage.py')
                        sudo('chmod -R g+rw media')
        else:
            print(yellow('Projet Django-coop nommé "%(projet)s" : déjà installé.' % env))


def apache_vhost():
    '''Configuration Vhost apache'''
    project()
    domain()
    #with prefix('workon %(projet)s' % env):
    if(env.websrv == 1):
        vhost_context = {
            'user': env.user,
            'domain': env.domaine,
            'projet': env.projet
        }
        import coop
        coop_path = coop.__path__[0]
        upload_template('%s/fab_templates/vhost.txt' % coop_path,
                        '/etc/apache2/sites-available/%(domaine)s' % env,
                        context=vhost_context, use_sudo=True)
        with cd('/etc/apache2/'):
            with settings(hide('warnings', 'running', 'stdout', 'stderr')):
                sudo('rm sites-enabled/%(domaine)s' % env)
            sudo('ln -s `pwd`/sites-available/%(domaine)s sites-enabled/%(domaine)s' % env)
            print(green('VirtualHost Apache pour %(domaine)s : OK.' % env))
    elif(env.websrv == 2):
        print(red('Script de déploiement pas encore écrit !!!'))  # TODO
    sudo('apachectl restart')


def django_wsgi():
    '''paramétrage WSGI/Apache'''
    project()
    if not exists('/home/%(user)s/%(projet)s/coop_local/wsgi.py' % env):
        with prefix('workon %(projet)s' % env):
            sp_path = run('cdsitepackages ; pwd')
            import coop
            coop_path = coop.__path__[0]
            wsgi_context = {
                'site-packages': sp_path,
                'user': env.user,
                'projet': env.projet
            }
        upload_template('%s/fab_templates/wsgi.txt' % coop_path,
                        '/home/%(user)s/projects/%(projet)s/coop_local/wsgi.py' % env,
                        context=wsgi_context, use_sudo=True)
        print(green('Script WSGI pour %(projet)s créé.' % env))
    else:
        print(yellow('Script WSGI pour %(projet)s déjà existant.' % env))


def django_project():
    '''Créer un projet django dans son virtualenv'''
    with settings(show('user'), hide('warnings', 'running', 'stdout', 'stderr')):
        if not exists('/home/%(user)s/.virtualenvs/%(projet)s' % env):
            # if confirm('Pas de virtualenv "%(projet)s", faut-il le créer ?' % env, default=False):
            run('mkvirtualenv %(projet)s' % env)
            run('source .bash_profile')
        with prefix('workon %(projet)s' % env):
            run('pip install django')
            pretty_pip('psycopg2', 'Pillow')
            print(green('Django installé.'))
        if not exists('projects/%s/' % (env.projet)):
            print(yellow('le projet %(projet)s n’existe pas encore' % env))
            if confirm('Créer un projet django nommé "%(projet)s" ?' % env,
                        default=False):
                with cd('projects/'):
                    with prefix('workon %(projet)s' % env):
                        run('django-admin.py startproject %s' % (env.projet))
                        with cd('%(projet)s' % env):
                            run('mkdir logs')
                        print(green('Projet Django "%(projet)s" : OK.' % env))

        else:
            print(green('Projet Django nommé "%(projet)s" : OK.' % env))


def first_syncdb():
    project()
    with cd('projects/%(projet)s' % env):
        with prefix('workon %(projet)s' % env):
            run('./manage.py syncdb --all --noinput')
            run('./manage.py migrate --fake')
            # for f in ('auth_users.json','coop_geo.json','coop_local.json'):
            #     run('./manage.py loaddata fixtures/'+f)


def apache_nginx():
    '''Apache + mod_wsgi pour Django avec Nginx en proxy'''
    icanhaz.deb.packages(['apache2', 'libapache2-mod-wsgi'])
    with cd('/etc/apache2/'):
        if not contains('ports.conf', '127.0.0.1', use_sudo=True):
            sed('ports.conf', 'NameVirtualHost \\*:80', 'NameVirtualHost 127.0.0.1:80', use_sudo=True)
            sed('ports.conf', 'Listen 80', 'Listen 127.0.0.1:80', use_sudo=True)
            print(green('/etc/apache2/ports.conf updated'))
    with cd('/etc/apache2/'):
        if not contains('apache2.conf', 'ServerName localhost', use_sudo=True):
            sudo("echo 'ServerName localhost'|cat - apache2.conf > /tmp/out && mv /tmp/out apache2.conf")
            sudo("sed -i 's/KeepAlive On/KeepAlive Off/g' apache2.conf")
            print(green('/etc/apache2/apache2.conf updated'))
    #sudo("apache2ctl graceful") #plante de toute façon sans virtualhosts
    pretty_apt(['nginx'])
    with cd('/etc/nginx/'):
        if not contains('nginx.conf', 'worker_processes 2;', use_sudo=True):
            sudo("sed -i 's/worker_processes 4;/worker_processes 2;/g' nginx.conf")
            print(green('/etc/nginx/nginx.conf updated'))
    #to be continued...proxy.conf, vhosts...


def apache_setup():
    '''Config générale Apache + mod_wsgi sans media proxy'''
    print(yellow('Configuration d’Apache...'))
    pretty_apt(['apache2', 'libapache2-mod-wsgi'])
    #virer le site par défaut
    with cd('/etc/apache2/'):
        if not contains('apache2.conf', 'ServerName localhost', use_sudo=True):
            if not contains('apache2.conf', 'ServerName %(domaine)s' % env, use_sudo=True):
                sudo("echo 'ServerName %(domaine)s'|cat - apache2.conf > /tmp/out && mv /tmp/out apache2.conf" % env)
    with cd('/etc/apache2/sites-enabled/'):
        if exists('000-default'):
            sudo('rm 000-default')
            print(green('Site par défaut d’Apache supprimé'))


def create_pg_db():
    '''Créer une base de données postgres au nom du projet'''
    with settings(show('user'), hide('warnings', 'running', 'stdout', 'stderr')):
        project()
        icanhaz.postgres.database(env.projet, env.user, template='template_postgis', locale=env.locale)
        print(green('Création base de données PostgreSQL nommée "%(projet)s" : OK.' % env))


def virtualenv_setup():
    '''setup virtualenv'''
    print(yellow('Environnement virtuel et dossier "projects"...'))
    icanhaz.python.package('virtualenv', use_sudo=True)
    icanhaz.python.package('virtualenvwrapper', use_sudo=True)
    #icanhaz.python.package('virtualenvwrapper.django',use_sudo=True)
    print(green('Virtualenv installé.'))
    if not 'www-data' in run('echo | groups %(user)s' % env):
        sudo('usermod -a -G www-data %(user)s' % env)
        print(green('Utilisateur %(user)s ajouté au groupe "www-data".' % env))
    if not exists('projects/'):
        run('mkdir projects .python-eggs .virtualenvs')
        sudo('chown %(user)s:www-data .python-eggs' % env)
        sudo('chgrp -R www-data projects/')
        sudo('chmod -R 2750 projects/')
        print(green('Dossier "projects" créé.'))
    # sur .bashrc et pas .bashrc
    # + fix pour https://bitbucket.org/dhellmann/virtualenvwrapper/issue/62/hooklog-permissions
    if not contains('.bashrc', 'WORKON_HOME'):
        append('.bashrc', 'if [ $USER == %(user)s ]; then' % env)
        append('.bashrc', '    export WORKON_HOME=$HOME/.virtualenvs')
        append('.bashrc', '    export PROJECT_HOME=$HOME/projects')
        append('.bashrc', '    export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python')
        append('.bashrc', '    export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv')
        append('.bashrc', '    source /usr/local/bin/virtualenvwrapper.sh')
        append('.bashrc', 'fi')
        #append('.bash_profile','if [ -f ~/.bashrc ]; then') #fabric source .bash_profile, pas .bashrc
        #append('.bash_profile','    source ~/.bashrc')
        #append('.bash_profile','fi')
        append('.bash_profile', 'if [ $USER == %(user)s ]; then' % env)
        append('.bash_profile', '    export WORKON_HOME=$HOME/.virtualenvs')
        append('.bash_profile', '    export PROJECT_HOME=$HOME/projects')
        append('.bash_profile', '    export VIRTUALENVWRAPPER_PYTHON=/usr/bin/python')
        append('.bash_profile', '    export VIRTUALENVWRAPPER_VIRTUALENV=/usr/local/bin/virtualenv')
        append('.bash_profile', '    source /usr/local/bin/virtualenvwrapper.sh')
        append('.bash_profile', 'fi')
        run('source .bashrc')
        print(green('Virtualenv et Virtualenvwrapper configurés.'))
    # stop warning from bitbucket https://bitbucket.org/site/master/issue/2780/getting-warning-while-using-https-and-ssh
    if not contains('.hgrc', 'bitbucket.org'):
        append('.hgrc', '[hostfingerprints]')
        append('.hgrc', 'bitbucket.org = 24:9c:45:8b:9c:aa:ba:55:4e:01:6d:58:ff:e4:28:7d:2a:14:ae:3b')


def push():
    '''Pull code from github on the server'''
    gitsrv = 'git+git://github.com/quinode/'
    app = prompt('app to update ?', default='django-coop')
    #with settings(show('user'),hide('warnings', 'running', 'stdout', 'stderr')):
    with prefix('workon coop'):
        try:
            print(yellow('desinstallation du paquet...'))
            run('pip uninstall -q %s' % app)
        except:
            print(red('paquet non installé'))
            pass
        print(yellow('réinstallation du paquet depuis github...'))
        run('pip install %s%s.git' % (gitsrv, app))
        if app == 'django-coop':
            for site in ('apeas', 'alliance', 'credis', 'extramarche', 'mesclun', 'varennes'):
                with cd('projects/%s' % site):
                    with settings(warn_only=True):
                        print(yellow('%s : migration de coop_local' % site))
                        sudo('python manage.py schemamigration coop_local --auto', user='admin')
                        sudo('python manage.py migrate coop_local', user='admin')
                    print(yellow('%s : collecte des fichiers statiques...' % site))
                    sudo('python manage.py collectstatic --noinput', user='admin')
                    sudo('python manage.py clean_pyc', user='admin')

    sudo('apachectl restart')
    print(green('Les mises à jour ont été appliquées.'))


def dependencies():
    '''Vérification des modules nécessaires au projet'''
    with settings(show('user'), hide('warnings', 'running', 'stdout', 'stderr')):
        with cd('projects/%(projet)s' % env):
            if exists('requirements.txt'):
                print(yellow('Installation des dépendances du projet...'))
                with prefix('workon %(projet)s' % env):
                    with settings(show('running', 'stdout', 'stderr')):
                        run('pip install -r requirements.txt')
            else:
                print(red('Aucun fichier "requirements.txt" trouvé.'))
        with prefix('workon %(projet)s' % env):
            with cd('projects/%(projet)s' % env):
                run('./manage.py collectstatic --noinput')

def locale():
    '''Règlage des locale de l'OS'''
    locale = run("echo $LANG")
    if(locale != env.locale):
        sudo('locale-gen ' + env.locale)
        sudo('/usr/sbin/update-locale LANG=' + env.locale)
        print(green('Locale mise à jour.'))


# PLUS BESOIN

# @task
# def postgis_template():
#     '''creation du template postgis - pour PostGIS 1.5 et Ubuntu > 10.10'''
#     if not 'template_postgis' in run('echo|psql -l'):
#         run('createdb -E UTF8 template_postgis')
#         run('createlang -d template_postgis plpgsql')
#         run('''psql -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"''')
#         run('psql -d template_postgis -f `pg_config --sharedir`/contrib/postgis-1.5/postgis.sql')
#         run('psql -d template_postgis -f `pg_config --sharedir`/contrib/postgis-1.5/spatial_ref_sys.sql')
#         run('psql -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"')
#         run('psql -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"')
#         run('psql -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"')
#         print(green('template_postgis pour PostgreSQL créé'))

# PLANTE ?

# @task
# def pg_access():
#     '''Access from external IP to PGSQL - setup your firewall'''
#     with cd('/etc/postgresql/9.1/main/'):
#         change = False
#         if not contains('pg_hba.conf', 'local   all         all                               password', use_sudo=True):
#             sudo("sed -i 's/local   all         all                               peer/local   all         all                               password/g' pg_hba.conf", user='postgres')
#             change = True
#             print(green('Accés local PostgreSQL pour Django'))
#         if not contains('pg_hba.conf', '0.0.0.0'):
#             # FIX : teste rate toujours , pourquoi ? - mais pas de double écriture grace à append()
#             append('pg_hba.conf', 'host    all         all         0.0.0.0/0             md5', use_sudo=True)
#             change = True
#             print(green('Accés à PostgreSQL via interfaces IP externes'))
#         if not contains('postgresql.conf', 'listen_addresses = \'\*\'', use_sudo=True):
#             sudo('echo "listen_addresses = \'*\'"|cat - postgresql.conf > /tmp/out && mv /tmp/out postgresql.conf')
#             change = True
#             print(green('PostgreSQL écoute sur toutes les interfaces IP'))
#         if change:
#             sudo('/etc/init.d/postgresql restart')


# Faut que le site soit sous GIT

# @task
# def update():
#     '''Met à jour un serveur depuis le depot git "origin"'''
#     project()
#     #with settings(show('user'),hide('warnings', 'running', 'stdout', 'stderr')):
#     with prefix('workon %(projet)s' % env):
#         dependencies()
#         with cd('projects/%(projet)s' % env):
#             print(yellow('Synchronisation du dépôt git...'))
#             run('git pull origin master')
#             print(yellow('Django : synchronisation des nouveaux modèles...'))
#             run('python manage.py syncdb --noinput')
#             print(yellow('South : applications des migrations...'))
#             run('python manage.py migrate')
#             print(yellow('Django : Collecte des fichiers statiques...'))
#             run('python manage.py collectstatic --noinput')
#     sudo('apachectl restart')
#     print(green('Les mises à jour ont été appliquées.'))
