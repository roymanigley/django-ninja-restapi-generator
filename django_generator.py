from os import path
from subprocess import call

from domain_models import DomainModels
from resources.django_templates import get_index_html, get_docker_compose_yml, get_build_local_script, \
    get_build_prod_script, get_run_local_script, get_run_prod_script, get_run_test_script, get_requirements_txt, \
    get_views, get_error_mapping, get_rest_helper, get_rest_login, get_rest_auth, get_env_file, get_read_me, \
    get_test_rest_helper, get_test_login, get_entity_rest_test, get_entity_rest_api, get_filter_schema, \
    get_entity_schema


class DjangoGenerator(object):

    def __init__(self, models: DomainModels, base_path: str = None):
        self.models = models
        self.base_path = base_path if base_path is not None else f'/tmp/{self.models.app_name_snake_case}'

    def __create_django_project__(self):

        project_path = f'{self.base_path}/{self.models.app_name_snake_case}_project'
        print(f'[+] generating project: {project_path}')
        if path.exists(self.base_path):
            call(['rm', '-rf', f'{self.base_path}'])
        call(['mkdir', '-p', f'{self.base_path}'])
        call(['django-admin', 'startproject', f'{self.models.app_name_snake_case}_project', f'{self.base_path}'])
        if not path.exists(f'{project_path}'):
            print(f'[!] project generation failed: {self.base_path}')
            raise Exception(f'project generation failed: {self.base_path}')

        print(f'[+] project generated: {project_path}')

    def __create_django_app__(self):
        app_path = f'{self.base_path}/{self.models.app_name_snake_case}_app'
        print(f'[+] generating app: {app_path}')
        call(['django-admin', 'startapp', f'{self.models.app_name_snake_case}_app'], cwd=self.base_path)
        if not path.exists(f'{app_path}'):
            print(f'[!] app generation failed: {self.base_path}')
            raise Exception(f'app generation failed: {self.base_path}')
        print(f'[+] app generated: {app_path}')

    def __adapt_project_settings__(self):
        settings_path = f'{self.base_path}/{self.models.app_name_snake_case}_project/settings.py'
        print(f'[+] adapting settings: {settings_path}')
        with open(settings_path) as f:
            lines = f.readlines()
            processing_installed_apps = False
            processing_databases = False
            processing_templates = False
            lines_new = ''
            for line in lines:
                if line.startswith('from '):
                    lines_new += line
                    lines_new += f'''
import os
import dj_database_url
from Crypto.PublicKey import RSA
from time import sleep

from {self.models.app_name_snake_case}_project.env import APP_SECRET_KEY, APP_ENV, APP_PROD, APP_TEST, APP_DEBUG, APP_DATABASE_URL, APP_PRIVATE_KEY_PATH, APP_PUBLIC_KEY_PATH

NINJA_PAGINATION_PER_PAGE=20

if not os.path.exists(APP_PRIVATE_KEY_PATH) or not os.path.exists(APP_PUBLIC_KEY_PATH):
    print('[+] generating RSA keys')
    keys = RSA.generate(4096)
    with open(APP_PRIVATE_KEY_PATH, 'w') as f:
        f.write(keys.exportKey('PEM', pkcs=1).decode('utf-8'))
    with open(APP_PUBLIC_KEY_PATH, 'w') as f:
        f.write(keys.publickey().exportKey('PEM', pkcs=1).decode('utf-8'))
'''
                elif line.startswith('DEBUG ='):
                    lines_new += 'PROD = APP_PROD\n'
                    lines_new += 'TEST = APP_TEST\n'
                    lines_new += 'DEBUG = APP_DEBUG\n'
                    lines_new += f'''
if not PROD and not TEST:
    with os.popen('docker ps | grep docker_{self.models.app_name_snake_case}_db') as p:
        if p.read() == '':
            print("[+] Starting docker env")
            os.system("docker-compose -f ./docker/docker-compose.yml up -d --remove-orphans")
            sleep(10)
            print("[+] docker env started")
'''
                elif line.startswith('ALLOWED_HOSTS ='):
                    lines_new += 'ALLOWED_HOSTS = ["*"]\n'
                elif line.startswith('SECRET_KEY ='):
                    lines_new += 'SECRET_KEY = APP_SECRET_KEY\n'
                elif 'django.middleware.security.SecurityMiddleware' in line:
                    lines_new += line
                    lines_new += '    \'whitenoise.middleware.WhiteNoiseMiddleware\',\n'
                elif line.startswith('INSTALLED_APPS =') or processing_installed_apps:
                    processing_installed_apps = True
                    if ']' in line:
                        lines_new += f'    \'{self.models.app_name_snake_case}_app\',\n'
                        processing_installed_apps = False
                    lines_new += line
                elif line.startswith('TEMPLATES =') or processing_templates:
                    processing_templates = True
                    if '\'DIRS\':' in line:
                        lines_new += line.replace('[]', '[TEMPLATES_ROOT]')
                        processing_templates = False
                    else:
                        lines_new += line
                elif line.startswith('DATABASES =') or processing_databases:
                    processing_databases = True
                    if line.startswith('}'):
                        lines_new += '''
db_config = dj_database_url.config(default=APP_DATABASE_URL)
db_config['ATOMIC_REQUESTS'] = True
DATABASES = {
    'default': db_config,
}'''
                        processing_databases = False
                elif line.startswith('BASE_DIR ='):
                    lines_new += line
                    lines_new += 'TEMPLATES_ROOT = os.path.join(BASE_DIR, "templates")\n'
                    lines_new += 'STATIC_ROOT = os.path.join(BASE_DIR, "static")\n'
                else:
                    lines_new += line
            with open(settings_path, 'w') as f:
                f.write(lines_new)
        print(f'[+] adapted settings: {settings_path}')
        pass

    def __adapt_urls__(self):
        urls_path = f'{self.base_path}/{self.models.app_name_snake_case}_project/urls.py'
        print(f'[+] adapting urls: {urls_path}')
        with open(urls_path, 'w') as f:
            f.write(f'''from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from django.views.generic import TemplateView

from {self.models.app_name_snake_case}_app.views import api

urlpatterns = [
  path('admin/', admin.site.urls),
  path('api/', api.urls),
  path('', TemplateView.as_view(template_name='index.html')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
''')
        print(f'[+] adapted urls: {urls_path}')

    def __create_template_and_statics__(self):
        static_path = f'{self.base_path}/static'
        templates_path = f'{self.base_path}/templates'
        print(f'[+] creating directory: {static_path}')
        call(['mkdir', '-p', static_path])
        print(f'[+] created directory: {static_path}')
        print(f'[+] creating directory: {templates_path}')
        call(['mkdir', '-p', templates_path])
        print(f'[+] created directory: {templates_path}')
        index_html = f'{templates_path}/index.html'
        print(f'[+] creating welcome page: {index_html}')
        with open(index_html, 'w') as f:
            f.write(get_index_html(self.models))
        print(f'[+] created welcome page: {index_html}')

    def __crate_docker__(self):
        docker_path = f'{self.base_path}/docker'
        docker_compose_file = f'{docker_path}/docker-compose.yml'
        print(f'[+] creating directory: {docker_path}')
        call(['mkdir', '-p', docker_path])
        print(f'[+] created directory: {docker_path}')
        print(f'[+] creating docker-compose.yml: {docker_compose_file}')
        with open(docker_compose_file, 'w') as f:
            f.write(get_docker_compose_yml(self.models))
        print(f'[+] created docker-compose.yml: {docker_compose_file}')

    def __create_build_and_run_scripts__(self):
        build_local_script = f'{self.base_path}/build_local.sh'
        build_prod_script = f'{self.base_path}/build_prod.sh'
        run_local_script = f'{self.base_path}/run_local.sh'
        run_prod_script = f'{self.base_path}/run_prod.sh'
        print(f'[+] creating script: {build_local_script}')
        with open(build_local_script, 'w') as f:
            f.write(get_build_local_script(self.models))
        print(f'[+] created script: {build_local_script}')
        print(f'[+] creating script: {build_prod_script}')
        with open(build_prod_script, 'w') as f:
            f.write(get_build_prod_script())
        print(f'[+] created script: {build_prod_script}')
        print(f'[+] creating script: {run_local_script}')
        with open(run_local_script, 'w') as f:
            f.write(get_run_local_script(self.models))
        print(f'[+] created script: {run_local_script}')
        print(f'[+] creating script: {run_prod_script}')
        with open(run_prod_script, 'w') as f:
            f.write(get_run_prod_script(self.models))
        print(f'[+] created script: {run_prod_script}')

        run_tests_script = f'{self.base_path}/run_tests.sh'
        print(f'[+] creating script: {run_tests_script}')
        with open(run_tests_script, 'w') as f:
            f.write(get_run_test_script())
        print(f'[+] created script: {run_tests_script}')

        print('[+] adapting permissions for build and run scripts')
        call(['chmod', '+x', build_local_script])
        call(['chmod', '+x', build_prod_script])
        call(['chmod', '+x', run_local_script])
        call(['chmod', '+x', run_prod_script])
        call(['chmod', '+x', run_tests_script])
        print('[+] adapted permissions for build and run scripts')

    def __create_requirements_txt__(self):
        requirements_txt_path = f'{self.base_path}/requirements.txt'
        print(f'[+] creating requirements.txt: {requirements_txt_path}')
        with open(requirements_txt_path, 'w') as f:
            f.write(get_requirements_txt())
        print(f'[+] created requirements.txt: {requirements_txt_path}')

    def __atapt_views__(self):
        for entity in self.models.entities:
            rest_resource_file = f'{self.base_path}/{self.models.app_name_snake_case}_app/rest/{entity.name_snake_case}.py'
            print(f'[+] creating REST resource file: {rest_resource_file}')
            with open(rest_resource_file, 'w') as f:
                f.write(get_entity_rest_api(self.models, entity))
            print(f'[+] created REST resource file: {rest_resource_file}')

        views_path = f'{self.base_path}/{self.models.app_name_snake_case}_app/views.py'
        print(f'[+] adapting views: {views_path}')
        with open(views_path, 'w') as f:
            f.write(get_views(self.models))
        print(f'[+] adapted views: {views_path}')

        rest_errors_file = f'{self.base_path}/{self.models.app_name_snake_case}_app/rest/errors.py'
        print(f'[+] creating rest errors file: {rest_errors_file}')
        with open(rest_errors_file, 'w') as f:
            f.write(get_error_mapping())
        print(f'[+] created rest errors file: {rest_errors_file}')

        rest_helper_file = f'{self.base_path}/{self.models.app_name_snake_case}_app/rest/helper.py'
        print(f'[+] creating rest helper file: {rest_helper_file}')
        with open(rest_helper_file, 'w') as f:
            f.write(get_rest_helper(self.models))
        print(f'[+] created rest helper file: {rest_helper_file}')

    def __create_login__(self):
        rest_dir = f'{self.base_path}/{self.models.app_name_snake_case}_app/rest'
        rest_login_file = f'{rest_dir}/login.py'
        rest_auth_file = f'{rest_dir}/auth.py'
        print(f'[+] creating rest directory: {rest_dir}')
        call(['mkdir', '-p', rest_dir])
        print(f'[+] created rest directory: {rest_dir}')
        print(f'[+] creating rest_login file: {rest_login_file}')
        with open(rest_login_file, 'w') as f:
            f.write(get_rest_login(self.models))
        print(f'[+] created rest_login: {rest_login_file}')
        print(f'[+] creating rest_auth file: {rest_auth_file}')
        with open(rest_auth_file, 'w') as f:
            f.write(get_rest_auth(self.models))
        print(f'[+] created rest_auth: {rest_auth_file}')

    def __adapt_models__(self):
        django_models = self.models.to_django_models()
        models_file = f'{self.base_path}/{self.models.app_name_snake_case}_app/models.py'
        print(f'[+] adapting models file: {models_file}')
        with open(models_file, 'w') as f:
            f.write(django_models)
        print(f'[+] adapted models file: {models_file}')

    def __adapt_schemas__(self):
        django_ninja_schemas = get_entity_schema(self.models)
        models_file = f'{self.base_path}/{self.models.app_name_snake_case}_app/schemas.py'
        print(f'[+] adapting schemas file: {models_file}')
        with open(models_file, 'w') as f:
            f.write(django_ninja_schemas)
        print(f'[+] adapted schemas file: {models_file}')

    def __create_filters_schemas__(self):
        django_ninja_schemas = get_filter_schema(self.models)
        models_file = f'{self.base_path}/{self.models.app_name_snake_case}_app/filters.py'
        print(f'[+] adapting filters file: {models_file}')
        with open(models_file, 'w') as f:
            f.write(django_ninja_schemas)
        print(f'[+] adapted filters file: {models_file}')

    def __create_env_file__(self):
        env_file = f'{self.base_path}/{self.models.app_name_snake_case}_project/env.py'
        print(f'[+] creating env file {env_file}')
        with open(env_file, 'w') as f:
            f.write(get_env_file())
        print(f'[+] created env file {env_file}')

    def __create_readme__(self):

        with open(f'{self.base_path}/README.md', 'w') as f:
            f.write(get_read_me(self.models))

    def __build_project__(self):
        print(f'[+] running {self.base_path}/build_local.sh')
        call(['./build_local.sh'], cwd=self.base_path)
        print(f'[+] completed {self.base_path}/build_local.sh')

    def __create_tests__(self):
        tests_rest_base_path = f'{self.base_path}/{self.models.app_name_snake_case}_app/tests_rest'
        call(['mkdir', '-p', tests_rest_base_path])
        call(['touch', f'{tests_rest_base_path}/__init__.py'])

        tests_rest_helper_file = f'{tests_rest_base_path}/helper.py'
        print(f'[+] creating helper file for tests: {tests_rest_helper_file}')
        with open(tests_rest_helper_file, 'w') as f:
            f.write(get_test_rest_helper(self.models))
        print(f'[+] created helper file for tests: {tests_rest_helper_file}')

        tests_login_file = f'{tests_rest_base_path}/tests_login.py'
        print(f'[+] creating tests for login: {tests_rest_helper_file}')
        with open(tests_login_file, 'w') as f:
            f.write(get_test_login(self.models))
        print(f'[+] created tests for login: {tests_rest_helper_file}')

        for entity in self.models.entities:
            entity_test_file = f'{tests_rest_base_path}/tests_{entity.name_snake_case}.py'
            print(f'[+] creating tests for {entity.name}: {entity_test_file}')

            with open(entity_test_file, 'w') as f:
                f.write(get_entity_rest_test(self.models, entity))
            print(f'[+] created tests for {entity.name}: {entity_test_file}')

    def __run_tests__(self):

        run_tests_file = f'{self.base_path}/run_tests.sh'
        print(f'[+] started running tests {run_tests_file}')
        call([run_tests_file], cwd=self.base_path)
        print(f'[+] completer running tests {run_tests_file}')

    def generate(self):
        print("[+] start generating the application")
        self.__create_django_project__()
        self.__create_django_app__()
        self.__adapt_project_settings__()
        self.__adapt_urls__()
        self.__create_template_and_statics__()
        self.__crate_docker__()
        self.__create_build_and_run_scripts__()
        self.__create_requirements_txt__()
        self.__create_login__()
        self.__adapt_models__()
        self.__adapt_schemas__()
        self.__create_filters_schemas__()
        self.__atapt_views__()
        self.__create_env_file__()
        self.__create_tests__()
        self.__create_readme__()
        self.__build_project__()
        self.__run_tests__()
        print("[+] generation completed")
