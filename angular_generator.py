import shutil
from subprocess import call

from domain_models import DomainModels
from resources.angular_templates import get_resolver, get_auth_guard, get_logout_component_ts, get_login_component_ts, \
    get_app_component_ts, get_home_component_html, get_header_component_ts, get_header_component_html, \
    get_custom_http_header_service, get_account_service, get_entity_service, get_layout_module, get_shared_module, \
    get_index_html, get_entity_update_component_ts, get_entity_update_component_html, get_entity_delete_component_ts, \
    get_entity_delete_component_html, get_entity_detail_component_ts, get_entity_detail_component_html, \
    get_entity_list_component_ts, get_entity_list_component_html, get_login_component_html


class AngularGenerator(object):

    def __init__(self, models: DomainModels, base_path: str = None):
        self.models = models
        self.base_path = base_path if base_path is not None else f'/tmp/{self.models.app_name_snake_case}'

    def __generate_frontend__(self):
        frontend_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend'
        print(f'[+] generating Angular frontend: {frontend_path}')
        call(['ng', 'new', f'{self.models.app_name_snake_case}_frontend', '--routing', '--style', 'scss', '--skip-git'], cwd=self.base_path)
        call(['ng', 'generate', 'module', 'Shared'], cwd=frontend_path)
        call(['ng', 'generate', 'module', 'views/Login'], cwd=frontend_path)
        call(['ng', 'generate', 'component', 'views/Login'], cwd=frontend_path)
        call(['ng', 'generate', 'module', 'views/Logout'], cwd=frontend_path)
        call(['ng', 'generate', 'component', 'views/Logout'], cwd=frontend_path)
        call(['ng', 'generate', 'module', 'views/Home'], cwd=frontend_path)
        call(['ng', 'generate', 'component', 'views/Home'], cwd=frontend_path)
        call(['ng', 'generate', 'module', 'views/Layout'], cwd=frontend_path)
        call(['ng', 'generate', 'component', 'views/layout/Header'], cwd=frontend_path)
        call(['ng', 'generate', 'service', 'services/Account'], cwd=frontend_path)
        call(['ng', 'generate', 'service', 'services/CustomHttpInjector'], cwd=frontend_path)
        call(['ng', 'generate', 'component', 'views/NotFound'], cwd=frontend_path)
        call(['ng', 'generate', 'guard', 'shared/Authenticated', '--implements=CanActivate'], cwd=frontend_path)

        for entity in self.models.entities:
            call(['ng', 'generate', 'class', f'models/{entity.name}'], cwd=frontend_path)
            call(['ng', 'generate', 'module', f'views/{entity.name}'], cwd=frontend_path)
            call(['ng', 'generate', 'component', f'views/{entity.name_kebab_case}/{entity.name}List'], cwd=frontend_path)
            call(['ng', 'generate', 'component', f'views/{entity.name_kebab_case}/{entity.name}Detail'], cwd=frontend_path)
            call(['ng', 'generate', 'component', f'views/{entity.name_kebab_case}/{entity.name}Update'], cwd=frontend_path)
            call(['ng', 'generate', 'component', f'views/{entity.name_kebab_case}/{entity.name}Delete'], cwd=frontend_path)
            call(['ng', 'generate', 'service', f'services/{entity.name}'], cwd=frontend_path)
            call(['ng', 'generate', 'resolver', f'views/{entity.name_kebab_case}/{entity.name}'], cwd=frontend_path)

        with open(f'{frontend_path}/src/app/app.component.html', 'w') as f:
            f.write('<app-header></app-header>\n')
            f.write('<router-outlet></router-outlet>')

        with open(f'{frontend_path}/src/index.html', 'w') as f:
            f.write(get_index_html(self.models))

        print(f'[+] generated Angular frontend: {frontend_path}')

    def __adapt_frontend_model__(self):
        frontend_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend'
        for entity in self.models.entities:
            member_fields = ''
            payload_class = f'export class {entity.name}Payload {{\n'
            for field in entity.fields:
                if field.class_type.startswith('enum.') or field.class_type not in ['str', 'int', 'float', 'date', 'datetime']:
                    member_fields += f'import {{ {field.class_type.replace("enum.", "")} }} from "./{field.class_type_snake_case}";\n'
            member_fields += '\n'
            payload_class += '\n'

            ts_model_file = f'{frontend_path}/src/app/models/{entity.name_kebab_case}.ts'
            with open(ts_model_file) as f:
                member_fields += f.read().replace('}', '')

            member_fields += '    constructor(\n'
            member_fields += '        public id: number,\n'
            payload_class += '    constructor(\n'
            for field in filter(lambda f: f.required, entity.fields):
                ts_type = self.to_ts_class_type(field)
                member_fields += f'        public {field.name}: {ts_type},\n'
                if field.is_fk():
                    payload_class += f'        public {field.name}_id: number,\n'
                else:
                    payload_class += f'        public {field.name}: {self.to_ts_class_type(field)},\n'
            for field in filter(lambda f: not f.required, entity.fields):
                ts_type = self.to_ts_class_type(field)
                member_fields += f'        public {field.name}?: {ts_type},\n'
                if field.is_fk():
                    payload_class += f'        public {field.name}_id?: number,\n'
                else:
                    payload_class += f'        public {field.name}?: {self.to_ts_class_type(field)},\n'
            member_fields += '    ){}\n}\n'
            payload_class += '    ){}\n}\n'
            with open(ts_model_file, 'w') as f:
                f.write(member_fields)
                f.write('\n')
                f.write(payload_class)

        for enum in self.models.domain_enums:
            ts_enum_file = f'{frontend_path}/src/app/models/{enum.name_kebab_case}.ts'
            enum_class = f'export enum {enum.name} {{\n'
            for value in enum.values:
                enum_class += f'    {value} = \'{value}\',\n'
            enum_class += '}'
            with open(ts_enum_file, 'w') as f:
                f.write(enum_class)

    def __adapt_frontend_modules__(self):
        frontend_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend'
        shared_module_path = f'{frontend_path}/src/app/shared/shared.module.ts'
        with open(shared_module_path, 'w') as f:
            f.write(get_shared_module())

        layout_module_path = f'{frontend_path}/src/app/views/layout/layout.module.ts'
        with open(layout_module_path, 'w') as f:
            f.write(get_layout_module())

        ts_app_routing_module_file = f'{frontend_path}/src/app/app-routing.module.ts'
        updated_app_routing_module = 'import { HomeComponent } from \'./views/home/home.component\';\n'
        updated_app_routing_module += 'import { LoginComponent } from \'./views/login/login.component\';\n'
        updated_app_routing_module += 'import { LogoutComponent } from \'./views/logout/logout.component\';\n'
        updated_app_routing_module += 'import { NotFoundComponent } from \'./views/not-found/not-found.component\';\n'
        with open(ts_app_routing_module_file) as f:
            for line in f.readlines():
                if line.startswith('const routes: Routes = []'):
                    updated_app_routing_module += 'const routes: Routes = [\n'
                    updated_app_routing_module += '  { path: \'\', component: HomeComponent },\n'
                    updated_app_routing_module += '  { path: \'login\', component: LoginComponent },\n'
                    updated_app_routing_module += '  { path: \'logout\', component: LogoutComponent },\n'
                    for entity in self.models.entities:
                        updated_app_routing_module += f'  {{ path: \'{entity.name_kebab_case}\', loadChildren: () => import(\'./views/{entity.name_kebab_case}/{entity.name_kebab_case}.module\').then(m => m.{entity.name}Module) }},\n'

                    updated_app_routing_module += f'  {{path: \'404\', component: NotFoundComponent}},\n'
                    updated_app_routing_module += f'  {{path: \'**\', component: NotFoundComponent}},\n'
                    updated_app_routing_module += '];\n'
                else:
                    updated_app_routing_module += line

        with open(ts_app_routing_module_file, 'w') as f:
            f.write(updated_app_routing_module)

        ts_app_module_file = f'{frontend_path}/src/app/app.module.ts'
        updated_ts_module_content = 'import { HttpClientModule, HTTP_INTERCEPTORS } from \'@angular/common/http\';\n'
        updated_ts_module_content += 'import { ReactiveFormsModule } from \'@angular/forms\';\n'
        updated_ts_module_content += 'import { SharedModule } from \'./shared/shared.module\';'
        updated_ts_module_content += 'import { CustomHttpInjectorService } from \'./services/custom-http-injector.service\';\n'
        updated_ts_module_content += 'import { AuthenticatedGuard } from \'./shared/authenticated.guard\';\n'

        with open(ts_app_module_file) as f:
            for line in f.readlines():
                if line.find('providers: [') != -1:
                    updated_ts_module_content += '''  providers: [
    AuthenticatedGuard,
    {
      provide: HTTP_INTERCEPTORS,
      useClass: CustomHttpInjectorService,
      multi: true,
    }],
'''
                else:
                    updated_ts_module_content += line
                if line.find('imports: [') != -1:
                    updated_ts_module_content += '    HttpClientModule,\n'
                    updated_ts_module_content += '    ReactiveFormsModule,\n'
                    updated_ts_module_content += '    SharedModule,\n'
        with open(ts_app_module_file, 'w') as f:
            f.write(updated_ts_module_content)

        for entity in self.models.entities:
            adapted_entity_route = 'import { RouterModule, Routes } from \'@angular/router\';\n'
            adapted_entity_route += f'import {{ {entity.name}Resolver }} from \'./{entity.name_kebab_case}.resolver\';\n'
            adapted_entity_route += 'import { AuthenticatedGuard } from \'../../shared/authenticated.guard\';\n'
            entity_module_file = f'{frontend_path}/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}.module.ts'
            with open(entity_module_file) as f:
                for line in f.readlines():
                    if line.startswith('@NgModule({'):
                        adapted_entity_route += f'''const routes: Routes = [
  {{ path: 'new', component: {entity.name}UpdateComponent, canActivate: [AuthenticatedGuard] }},
  {{ path: 'detail/:id', component: {entity.name}DetailComponent, canActivate: [AuthenticatedGuard], resolve: {{ data: {entity.name}Resolver}} }},
  {{ path: 'update/:id', component: {entity.name}UpdateComponent, canActivate: [AuthenticatedGuard], resolve: {{ data: {entity.name}Resolver}} }},
  {{ path: 'delete/:id', component: {entity.name}DeleteComponent, canActivate: [AuthenticatedGuard], resolve: {{ data: {entity.name}Resolver}} }},
  {{ path: '', component: {entity.name}ListComponent, canActivate: [AuthenticatedGuard] }}
];

'''
                    adapted_entity_route += line
                    if line.find('imports: [') != -1:
                        adapted_entity_route += '    RouterModule.forChild(routes),\n'
            with open(entity_module_file, 'w') as f:
                f.write(adapted_entity_route)

    def __adapt_frontend_service__(self):
        frontend_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend'
        for entity in self.models.entities:
            with open(f'{frontend_path}/src/app/services/{entity.name_kebab_case}.service.ts', 'w') as f:
                f.write(get_entity_service(entity))
        with open(f'{frontend_path}/src/app/services/account.service.ts', 'w') as f:
            f.write(get_account_service())
        with open(f'{frontend_path}/src/app/services/custom-http-injector.service.ts', 'w') as f:
            f.write(get_custom_http_header_service())

    def __add_proxy_conf_frontend__(self):
        frontend_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend'
        proxy_conf_file = f'{frontend_path}/src/proxy.conf.json'
        angular_conf_file = f'{frontend_path}/angular.json'
        with open(proxy_conf_file, 'w') as f:
            f.write('''{
    "/api": {
      "target": "http://localhost:8000",
      "secure": false
    }
}
''')
        updated_angular_config = ''
        with open(angular_conf_file) as f:
            for line in f.readlines():
                if line .find(':build:development') != -1:
                    updated_angular_config += '              "proxyConfig": "src/proxy.conf.json",\n'
                updated_angular_config += line
        with open(angular_conf_file, 'w') as f:
            f.write(updated_angular_config)

    def __adapt_header_frontend__(self):
        header_html_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend/src/app/views/layout/header/header.component.html'
        header_ts_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend/src/app/views/layout/header/header.component.ts'
        with open(header_html_path, 'w') as f:
            f.write(get_header_component_html(self.models))
        with open(header_ts_path, 'w') as f:
            f.write(get_header_component_ts())

    def __adapt_components_frontend__(self):
        frontend_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend'

        with open(f'{frontend_path}/src/app/views/home/home.component.html', 'w') as f:
            f.write(get_home_component_html(self.models))

        with open(f'{frontend_path}/src/app/app.component.ts', 'w') as f:
            f.write(get_app_component_ts())

        for entity in self.models.entities:
            with open(f'{frontend_path}/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}-list/{entity.name_kebab_case}-list.component.html', 'w') as f:
                f.write(get_entity_list_component_html(entity))
            with open(f'{frontend_path}/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}-list/{entity.name_kebab_case}-list.component.ts', 'w') as f:
                f.write(get_entity_list_component_ts(entity))

        for entity in self.models.entities:
            with open(f'{frontend_path}/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}-detail/{entity.name_kebab_case}-detail.component.html', 'w') as f:
                f.write(get_entity_detail_component_html(entity))

        for entity in self.models.entities:
            with open(f'{frontend_path}/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}-detail/{entity.name_kebab_case}-detail.component.ts', 'w') as f:
                f.write(get_entity_detail_component_ts(entity))

        for entity in self.models.entities:
            with open(f'{frontend_path}/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}-delete/{entity.name_kebab_case}-delete.component.html', 'w') as f:
                f.write(get_entity_delete_component_html(entity))

        for entity in self.models.entities:
            with open(f'{frontend_path}/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}-delete/{entity.name_kebab_case}-delete.component.ts', 'w') as f:
                f.write(get_entity_delete_component_ts(entity))

        for entity in self.models.entities:
            with open(f'{frontend_path}/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}-update/{entity.name_kebab_case}-update.component.html', 'w') as f:
                f.write(get_entity_update_component_html(entity))

        for entity in self.models.entities:
            with open(f'{frontend_path}/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}-update/{entity.name_kebab_case}-update.component.ts', 'w') as f:
                f.write(get_entity_update_component_ts(entity))

        for entity in self.models.entities:
            entity_modules_content = 'import { ReactiveFormsModule } from \'@angular/forms\';\n'
            with open(f'{frontend_path}/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}.module.ts') as f:
                for line in f.readlines():
                    entity_modules_content += line
                    if line.find('imports: [') != -1:
                        entity_modules_content += '    ReactiveFormsModule,\n'
            with open(f'{frontend_path}/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}.module.ts', 'w') as f:
                f.write(entity_modules_content)


    def __create_login_frontend__(self):
        login_html_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend/src/app/views/login/login.component.html'
        login_ts_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend/src/app/views/login/login.component.ts'
        logout_ts_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend/src/app/views/logout/logout.component.ts'
        with open(login_html_path, 'w') as f:
            f.write(get_login_component_html())
        with open(login_ts_path, 'w') as f:
            f.write(get_login_component_ts())
        with open(logout_ts_path, 'w') as f:
            f.write(get_logout_component_ts())
        pass

    def __adapt_guards_frontend__(self):
        guard_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend/src/app/shared/authenticated.guard.ts'
        with open(guard_path, 'w') as f:
            f.write(get_auth_guard())

    def __adapt_resolvers__(self):
        for entity in self.models.entities:
            resolver_path = f'{self.base_path}/{self.models.app_name_snake_case}_frontend/src/app/views/{entity.name_kebab_case}/{entity.name_kebab_case}.resolver.ts'
            with open(resolver_path, 'w') as f:
                f.write(get_resolver(entity))

    def __copy__logo_image__(self):
        logo_destination_path: str = f'{self.base_path}/{self.models.app_name_snake_case}_frontend/src/assets/logo.png'
        shutil.copy('resources/logo.png', logo_destination_path)

    @staticmethod
    def to_ts_class_type(field):
        ts_type = field.class_type
        if field.class_type == 'str':
            ts_type = 'string'
        if field.class_type in ['int', 'float']:
            ts_type = 'number'
        if field.class_type in ['date', 'datetime']:
            ts_type = 'Date'
        if field.class_type.startswith('enum.'):
            ts_type = field.class_type.replace('enum.', '')
        return ts_type

    def generate(self):
        print("[+] start generating the application")
        self.__generate_frontend__()
        self.__add_proxy_conf_frontend__()
        self.__adapt_frontend_model__()
        self.__adapt_frontend_modules__()
        self.__adapt_frontend_service__()
        self.__adapt_header_frontend__()
        self.__adapt_components_frontend__()
        self.__create_login_frontend__()
        self.__adapt_guards_frontend__()
        self.__adapt_resolvers__()
        self.__copy__logo_image__()
        print("[+] generation completed")
