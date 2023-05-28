from os import path
from subprocess import call

from angular_generator import AngularGenerator
from django_generator import DjangoGenerator
from domain_models import DomainModels


class MainGenerator(object):

    def __init__(self, models: DomainModels, base_path: str = None, generate_frontend=True):
        self.models = models
        self.base_path = base_path if base_path is not None else f'/tmp/{self.models.app_name_snake_case}'
        self.generate_frontend = generate_frontend

    def __create_backup_git__(self):

        if path.exists(f'{self.base_path}/.git'):
            call(['mkdir', '-p', f'{self.base_path}__back__'])
            call(['mv', f'{self.base_path}/.git', f'{self.base_path}__back__'])

    def __restore_or_init_git_and_commit__(self):
        if path.exists(f'{self.base_path}__back__/.git'):
            call(['mv', f'{self.base_path}__back__/.git', f'{self.base_path}'])
            call(['rm', '-rf', f'{self.base_path}__back__'])

        gitignore_file = f'{self.base_path}/.gitignore'
        print(f'[+] creating gitignore file: {gitignore_file}')
        with open(gitignore_file, 'w') as f:
            f.write('''.env
.idea
__pycache__
migrations
rsa_private.pem
rsa_public.pem
static
node_modules
''')
        is_git_already_initialized = path.exists(f'{self.base_path}/.git')
        commit_message = 'Update: updated using Django Ninja REST API Generator'
        if not is_git_already_initialized:
            print(f'[+] created gitignore file: {gitignore_file}')
            print(f'initializing git repository: {self.base_path}')
            call(['git', 'init', '--initial-branch=master'], cwd=self.base_path)
            print(f'initialized git repository: {self.base_path}')
            print(f'preparing initial commit: {self.base_path}')
            commit_message = 'Initial Commit: generated using Django Ninja REST API Generator'
        call(['git', 'add', '.'], cwd=self.base_path)
        call(['git', 'commit', '--author="Django-Ninja-REST-API-Generator <no-email@local>"', '-m', commit_message], cwd=self.base_path)
        print(f'completed initial commit: {self.base_path}')

    def generate(self):
        print("[+] start generating the application")
        self.__create_backup_git__()
        DjangoGenerator(self.models).generate()
        if self.generate_frontend:
            AngularGenerator(self.models).generate()
        self.__restore_or_init_git_and_commit__()
        print("[+] generation completed")
