from domain_models import DomainModel, DomainModels


def get_resolver(entity: DomainModel) -> str:
    return f'''import {{ Injectable }} from '@angular/core';
import {{
  ActivatedRouteSnapshot,
  Resolve,
  Router,
  RouterStateSnapshot
}} from '@angular/router';
import {{ EMPTY, Observable, mergeMap, of }} from 'rxjs';
import {{ {entity.name} }} from '../../models/{entity.name_kebab_case}';
import {{ {entity.name}Service }} from '../../services/{entity.name_kebab_case}.service';

@Injectable({{
  providedIn: 'root'
}})
export class {entity.name}Resolver implements Resolve<{entity.name} | boolean> {{
  
  constructor(
    private service: {entity.name}Service, 
    private router: Router) {{

  }}
  
  resolve(route: ActivatedRouteSnapshot, state: RouterStateSnapshot): Observable<{entity.name} | boolean> {{
    const id = route.params['id'];
    if (id) {{
      return this.service.findOne(id)
        .pipe(
          mergeMap(response => {{
            if (response?.body) {{
              return of(response.body)
            }} else {{
              return this.router.navigate(['404']);
            }}
          }})
        );
    }}
    this.router.navigate(['404']);
    return EMPTY 
  }}
}}
'''


def get_auth_guard() -> str:
    return '''import { Injectable } from '@angular/core';
import { ActivatedRouteSnapshot, CanActivate, RouterStateSnapshot, UrlTree } from '@angular/router';
import { Observable } from 'rxjs';
import { AccountService } from '../services/account.service'

@Injectable({
  providedIn: 'root'
})
export class AuthenticatedGuard implements CanActivate {

  constructor(private accountService: AccountService){}

  canActivate(
    route: ActivatedRouteSnapshot,
    state: RouterStateSnapshot): Observable<boolean | UrlTree> | Promise<boolean | UrlTree> | boolean | UrlTree {
    return !!this.accountService.account;
  }
  
}
'''


def get_login_component_ts() -> str:
    return '''import { Component, OnInit } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { Router } from '@angular/router';
import { AccountService } from 'src/app/services/account.service';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss']
})
export class LoginComponent implements OnInit {

  loginForm = new FormGroup({
    login: new FormControl('', Validators.required ),
    password: new FormControl('', Validators.required ),
  });
  constructor(
    private accountService: AccountService,
    private router: Router
  ) { }

  ngOnInit(): void {
  }

  onSubmit(): void {
    const login = this.loginForm.value.login
    const password = this.loginForm.value.password
    if (login && password) {
      this.accountService.login(
        login,
        password
      )
      .subscribe({
        next: account => {
          console.log(`logged in as: ${account.username}`);
          this.router.navigate(['/'])
        },
        error: (error) => {
          console.error(`${error.status}: ${error.statusText}`, error.error);
          this.loginForm.get('password')?.reset();
        }
      })
    }
  }
}
'''


def get_login_component_html() -> str:
    return '''<div class="row container center">
    <form [formGroup]="loginForm" (ngSubmit)="onSubmit()" class="col s12">
        <div class="row">
            <div class="input-field col s12">
                <i class="material-icons prefix">account_circle</i>
                
                <input
                    formControlName="login" 
                    [required]="true"
                    id="icon_login" 
                    type="text" 
                    class="validate">
                <label for="icon_login">Login</label>
            </div>
        </div>
        <div class="row">
            <div class="input-field col s12">
                <i class="material-icons prefix">key</i>
                <input 
                    formControlName="password"
                    [required]="true"
                    id="icon_password" 
                    type="password" 
                    class="validate">
                <label for="icon_password">Password</label>
            </div>
        </div>
        <div class="row">
            <div class="col s12">
                <button 
                    type="submit"
                    [disabled]="loginForm.invalid"
                    class="waves-effect waves-light btn">
                    <i class="material-icons left">login</i>
                    Login
                </button>
            </div>
        </div>
    </form>
</div>
'''


def get_logout_component_ts() -> str:
    return '''import { Component, OnInit } from '@angular/core';
import { Router } from '@angular/router';
import { AccountService } from 'src/app/services/account.service';

@Component({
  selector: 'app-logout',
  templateUrl: './logout.component.html',
  styleUrls: ['./logout.component.scss']
})
export class LogoutComponent implements OnInit {

  constructor(
    private accountService: AccountService,
    private router: Router
  ) { }

  ngOnInit(): void {
    this.accountService.logout();
    this.router.navigate(['/']);
    console.log("logged out")
  }

}
'''


def get_app_component_ts() -> str:
    return '''import { NgIfContext } from '@angular/common';
import { Component, OnInit } from '@angular/core';
import { AccountService } from './services/account.service';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss']
})
export class AppComponent implements OnInit {
  title = 'to_do_frontend';

  constructor(private accountService: AccountService){}

  ngOnInit(): void {
      this.accountService.init()
  }
}
'''


def get_header_component_ts() -> str:
    return '''import { Component, OnInit } from '@angular/core';
import { AccountService } from 'src/app/services/account.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {

  constructor(private accountService: AccountService) { }

  ngOnInit(): void {
  }

  isLoggedIn(): boolean {
    return !!this.accountService.account
  }
}
'''


def get_home_component_html(domain_models: DomainModels) -> str:
    return f'''<div class="container">
    <div class="row center">
        <h1>Welcome to {domain_models.app_name}</h1>
    </div>
    <div class="card">
        <div class="card-image">
            <div class="row center">
                <img style="display: unset; width: 600px" src="assets/logo.png">
            </div>
        </div>
        <div class="card-content">
            <span class="card-title">
                This app was generated using <a href="https://github.com/roymanigley/django-ninja-restapi-generator" target="_blank">django-ninja-restapi-generator</a>
            </span>
        <div>
            - default login is admin admin 🤓
        </div>            
        </div>
    </div>
</div>
'''


def get_header_component_html(domain_models: DomainModels) -> str:
    entity_links = ''
    for entity in domain_models.entities:
        entity_links += f'                <li routerLinkActive="active"><a [routerLink]="[\'/{entity.name_kebab_case}\']">{entity.name}</a></li>\n'
    return f'''<nav>
    <div class="nav-wrapper teal mg-1">
        <a style="margin-left: 1em" [routerLink]="['']" class="brand-logo">{domain_models.app_name}</a>
        <ul class="right hide-on-med-and-down">
            <ng-container *ngIf="isLoggedIn()">
{entity_links}
                <li routerLinkActive="active"><a [routerLink]="['/logout']"><i class="material-icons left">logout</i>Logout</a></li>
            </ng-container>
            <li *ngIf="!isLoggedIn()" routerLinkActive="active"><a [routerLink]="['/login']"><i class="material-icons left">login</i>Login</a></li>

        </ul>
    </div>
</nav>
'''


def get_custom_http_header_service() -> str:
    return '''import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Router } from '@angular/router';
import { Observable, tap } from 'rxjs';
import { AccountService } from './account.service';

@Injectable({
  providedIn: 'root'
})
export class CustomHttpInjectorService implements HttpInterceptor {

  constructor(
    private accountService: AccountService,
    private router: Router
  ) { }

  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const token = localStorage.getItem('token');
    if (token && token !== 'undefined') {
      const clonedRequest = req.clone(
        { setHeaders: { 
          Authorization: `Bearer ${JSON.parse(token)}` 
        } 
      });
      return next.handle(clonedRequest)
        .pipe(
          tap({ next: () => {},
            error:  error => {
              if (error.status === 401) {
                this.accountService.logout()
                this.router.navigate(['login'])
              } else if (error.status === 404) {
                this.router.navigate(['404'])
              }
            }
          })
        );
    } else {
      return next.handle(req);
    }
  }
}
'''

def get_account_service() -> str:
    return '''import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Observable, map, tap } from 'rxjs';
import { Buffer } from "buffer";
import { JsonPipe } from '@angular/common';

@Injectable({
  providedIn: 'root'
})
export class AccountService {

  account?: IAccount;
  
  constructor(
    private http: HttpClient
  ) { }

  init(): void {
    const account = localStorage.getItem('account');
    const token = localStorage.getItem('token');
    if (account && token) {
      this.account = JSON.parse(account);
    } else {
      this.logout();
    }
  }

  login(login: string, password: string): Observable<IAccount> {
    return this.http.post<IToken>(`/api/login?username=${login}&password=${password}`, undefined)
      .pipe(
        map(response => this.handleTokenResponse(response.token))
      )
  }

  logout(): void {
    this.account = undefined;
    localStorage.removeItem('account')
    localStorage.removeItem('token')
  }

  private handleTokenResponse(token: string): IAccount {
    const tokenDecoded = this.decodeB64(
      token.replace(/\..+/g, '')
    );
    this.account = {
      username: JSON.parse(tokenDecoded).username
    } as IAccount
    localStorage.setItem('account', JSON.stringify(this.account))
    localStorage.setItem('token', JSON.stringify(token))
    return this.account;
  }

  private decodeB64(str: string): string {
    return Buffer.from(str, 'base64').toString('binary');
  }
}

interface IToken {
  token: string
}

interface IAccount {
  username: string
}'''

def get_entity_service(entity: DomainModel) -> str:
    return f'''import {{ HttpClient, HttpResponse }} from '@angular/common/http';
import {{ Injectable }} from '@angular/core';
import {{ Observable }} from 'rxjs';
import {{ {entity.name}, {entity.name}Payload }} from '../models/{entity.name_kebab_case}';

interface I{entity.name}ListWrapper {{
  items: {entity.name}[]
  count: number
}}

@Injectable({{
  providedIn: 'root'
}})
export class {entity.name}Service {{

  private readonly RESOURCE_PATH = '/api/{entity.name_snake_case}'

  constructor(private http: HttpClient) {{ }}

  findAll(search?: string, filters?: any, page: number=1, size=20): Observable<HttpResponse<I{entity.name}ListWrapper>> {{
    if (search) {{
        search = `&search=${{search}}`;
    }} else {{
        search = '';
    }}
    return this.http.get<I{entity.name}ListWrapper>(`${{this.RESOURCE_PATH}}?$offset=${{page - 1}}&limit=${{size}}{{search}}`, {{observe: 'response'}});
  }}

  findOne(id: number): Observable<HttpResponse<{entity.name}>> {{
    return this.http.get<{entity.name}>(`${{this.RESOURCE_PATH}}/${{id}}`, {{observe: 'response'}});
  }}

  create(payload: {entity.name}Payload): Observable<HttpResponse<{entity.name}>> {{
    return this.http.post<{entity.name}>(`${{this.RESOURCE_PATH}}`, payload, {{observe: 'response'}});
  }}

  update(id: number, payload: {entity.name}Payload): Observable<HttpResponse<{entity.name}>> {{
    return this.http.put<{entity.name}>(`${{this.RESOURCE_PATH}}/${{id}}`, payload, {{observe: 'response'}});
  }}

  update_partial(id: number, payload: {entity.name}Payload): Observable<HttpResponse<{entity.name}>> {{
    return this.http.patch<any>(`${{this.RESOURCE_PATH}}/${{id}}`, payload, {{observe: 'response'}});
  }}

  delete(id: number): Observable<void> {{
    return this.http.delete<any>(`${{this.RESOURCE_PATH}}/${{id}}`);
  }}
}}
'''


def get_layout_module() -> str:
    return '''import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { HeaderComponent } from './header/header.component';
import { RouterModule } from '@angular/router';



@NgModule({
  declarations: [
    HeaderComponent
  ],
  exports: [
    HeaderComponent
  ],
  imports: [
    CommonModule,
    RouterModule
  ]
})
export class LayoutModule { }
'''


def get_shared_module() -> str:
    return '''import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LayoutModule } from '../views/layout/layout.module';


@NgModule({
  declarations: [],
  imports: [
    CommonModule,
    LayoutModule
  ], 
  exports: [
    LayoutModule
  ]
})
export class SharedModule { }
'''


def get_index_html(domain_models: DomainModels) -> str:
    return f'''<!DOCTYPE html>
  <html>
    <head>
      <title>{domain_models.app_name}</title>
      <meta charset="utf-8">
      <base href="/">
      <!--Import Google Icon Font-->
      <link href="https://fonts.googleapis.com/icon?family=Material+Icons" rel="stylesheet">
      <!-- Compiled and minified CSS -->
      <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css">

        
      <!--Let browser know website is optimized for mobile-->
      <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    </head>

    <body>
      <app-root></app-root>
      <!--JavaScript at end of body for optimized loading-->
      <!-- Compiled and minified JavaScript -->
      <script src="https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js"></script>
    </body>
  </html>
'''


def get_entity_update_component_html(entity: DomainModel) -> str:
    input_fields: str = ''
    for field in entity.fields:
        html5_type = ''
        if field.class_type == 'str':
            html5_type = 'text'
        elif field.class_type == 'int':
            html5_type = 'number'
        elif field.class_type == 'float':
            html5_type = 'number" step="0.00001'
        elif field.class_type in ['date', 'datetime']:
            html5_type = field.class_type

        if field.class_type.startswith('.enum'):

            input_fields += f'''
                        <div class="row">
                            <div class="input-field col s12">
                                <select 
                                    formControlName="{field.name}"
                                    required="{'true' if field.required else 'false'}" 
                                    id="{field.name}"
                                    class="validate">
                                    <option value="" disabled selected>Choose your option</option>
                                    <option *ngFor="let value of {field.name}List" 
                                        [value]="value">
                                        {{{{ value }}}}
                                    </option>
                                </select>
                                <label for="{field.name}">{' *' if field.required else ''}</label>
                            </div>
                        </div>
'''
        elif field.is_fk():
            input_fields += f'''
                        <div class="row">
                            <div class="input-field col s12">
                                <input 
                                    formControlName="{field.name}"
                                    required="{'true' if field.required else 'false'}" 
                                    id="{field.name}" 
                                    type="text" 
                                    class="validate"
                                    (keyup)="find{field.name.title()}($event)"
                                    list="{field.name}List"
                                    autocomplete="off">
                                <datalist id="{field.name}List">
                                    <option *ngFor="let item of {field.name}List" [value]="item.id">{{{{ item | json }}}}</option>
                                </datalist> 
                                <label for="{field.name}">{field.name}{' *' if field.required else ''}</label>
                            </div>
                        </div>
'''
        else:
            input_fields += f'''
                        <div class="row">
                            <div class="input-field col s12">
                                <input 
                                    formControlName="{field.name}"
                                    required="{'true' if field.required else 'false'}" 
                                    id="{field.name}" 
                                    type="{html5_type}" 
                                    class="validate">
                                <label for="{field.name}">{field.name}{' *' if field.required else ''}</label>
                            </div>
                        </div>
'''
    return f'''<div class="container">
    <div class="row">
        <h1 *ngIf="selected?.id">{entity.name} Update</h1>
        <h1 *ngIf="!selected?.id">{entity.name} Create</h1>
    </div>
    <div class="card" *ngIf="formGroup">
        <div class="card-content">
            <span *ngIf="selected?.id" class="card-title">Id: {{{{ selected?.id }}}}</span>
            <span *ngIf="!selected?.id" class="card-title">New</span>

            
            <div class="row">
                <form [formGroup]="formGroup" class="col s12">
                {input_fields}
                </form>
            </div>


        </div>
        <div class="card-action center">
            <button 
                style="margin-right: 3em;" 
                (click)="back()" 
                class="waves-effect waves-light btn-floating">
                <i class="material-icons left grey">arrow_back</i>back
            </button>
            <button 
                (click)="save()"
                [disabled]="formGroup.invalid" 
                class="waves-effect waves-light btn-floating">
                <i class="material-icons left">save</i>delete
            </button>
        </div>
    </div>
</div>'''


def get_entity_update_component_ts(entity: DomainModel) -> str:
    create_form_group = ''
    from_form_group = ''

    auto_complete_methods = ''
    auto_complete_services = ''
    auto_complete_services_import = ''
    auto_complete_lists = ''

    for field in entity.fields:
        if field.is_fk():
            auto_complete_services_import += f'import {{ {field.class_type}Service }} from \'src/app/services/{field.class_type_kebab_case}.service\';\n'
            auto_complete_services_import += f'import {{ {field.class_type} }} from \'src/app/models/{field.class_type_kebab_case}\';\n'
            auto_complete_services += f'    private {field.name}Service: {field.class_type}Service,\n'
            auto_complete_lists += f'  {field.name}List: {field.class_type}[] = [];\n'
            auto_complete_methods += f'''
  find{field.name.title()}($event: KeyboardEvent): void {{
    const search = (<HTMLInputElement>$event.target).value;
    this.{field.name}Service.findAll(search)
    .pipe(
      map(response => response.body)
    )
    .subscribe(data => this.{field.name}List = data?.items ?? []);
  }}
'''

    enum_imports = ''
    enum_list = ''
    for field in entity.fields:
        if field.class_type.startswith('enum.'):
            enum_imports += f'import {{ {field.class_type.replace("enum.", "")} }} from \'src/app/models/{field.class_type_kebab_case}\';\n'
            enum_list += f'  {field.name}List = Object.values({field.class_type.replace("enum.", "")});\n'

    for field in entity.fields:
        create_form_group += f'''
          {field.name}: new FormControl(record?.{field.name + '?.id' if field.is_fk() else field.name} ?? ''{', Validators.required' if field.required else ''}),'''
        from_form_group += f'''
        payload.{field.name + '_id' if field.is_fk() else field.name} = this.formGroup?.controls['{field.name}'].value'''

    return f'''import {{ Location }} from '@angular/common';
import {{ Component, OnInit }} from '@angular/core';
import {{ FormControl, FormGroup, Validators }} from '@angular/forms';
import {{ ActivatedRoute }} from '@angular/router';
import {{ {entity.name}, {entity.name}Payload }} from 'src/app/models/{entity.name_kebab_case}';
import {{ {entity.name}Service }} from 'src/app/services/{entity.name_kebab_case}.service';
import {{ map }} from 'rxjs';
{enum_imports}
{auto_complete_services_import}

@Component({{
  selector: 'app-{entity.name_kebab_case}-update',
  templateUrl: './{entity.name_kebab_case}-update.component.html',
  styleUrls: ['./{entity.name_kebab_case}-update.component.scss']
}})
export class {entity.name}UpdateComponent implements OnInit {{

  selected?: {entity.name}
  formGroup?: FormGroup;
{enum_list}
{auto_complete_lists}

  constructor(
{auto_complete_services}
    private service: {entity.name}Service,
    private location: Location,
    private route: ActivatedRoute
  ) {{ 
    route.data.subscribe(data => {{
      if (data['data']) {{
        this.selected = data['data'];
      }}
    }});
  }}

  ngOnInit(): void {{
    this.formGroup = this.createFormGroup(this.selected);
    setTimeout(() => {{
      eval('M.updateTextFields(); M.AutoInit();');
    }}, 0)

  }}

  createFormGroup(record?: {entity.name}): FormGroup {{
    return new FormGroup({{ {create_form_group}    }})
  }}

  fromFormGroup(): {entity.name}Payload {{
    const payload = {{}} as {entity.name}Payload;
    {from_form_group}
    return payload;
  }}

  save(): void {{
    const payload = this.fromFormGroup();
    if (this.selected?.id) {{
      this.service.update(this.selected.id, payload)
        .subscribe(() => this.back());
    }} else {{
      this.service.create(payload)
        .subscribe(() => this.back());
    }}

  }}

  back(): void {{
    this.location.back();
  }}

{auto_complete_methods}
}}
'''


def get_entity_delete_component_html(entity: DomainModel) -> str:
    return f'''<div class="container">
    <div class="row center">
        <h1>{entity.name} Delete</h1>
    </div>
    <div class="card">
        <div class="card-content">
            <span class="card-title">Id: {{{{ selected.id }}}}</span>
            <pre>
{{{{ selected | json }}}}
            </pre>
        </div>
        <div class="card-action center">
            <button style="margin-right: 3em;" (click)="back()" class="waves-effect waves-light btn-floating"><i class="material-icons left grey">arrow_back</i>back</button>
            <button (click)="delete()" class="waves-effect waves-light btn-floating"><i class="material-icons left red">delete</i>delete</button>
        </div>
    </div>
</div>'''


def get_entity_delete_component_ts(entity: DomainModel) -> str:
    return f'''import {{ Location }} from '@angular/common';
import {{ Component, OnInit }} from '@angular/core';
import {{ ActivatedRoute }} from '@angular/router';
import {{ {entity.name} }} from 'src/app/models/{entity.name_kebab_case}';
import {{ {entity.name}Service }} from 'src/app/services/{entity.name_kebab_case}.service';

@Component({{
  selector: 'app-{entity.name_kebab_case}-delete',
  templateUrl: './{entity.name_kebab_case}-delete.component.html',
  styleUrls: ['./{entity.name_kebab_case}-delete.component.scss']
}})
export class {entity.name}DeleteComponent implements OnInit {{
  
  selected: {entity.name} = {{ }} as {entity.name};

  constructor(
    private service: {entity.name}Service,
    private location: Location,
    private route: ActivatedRoute
  ) {{ 
    route.data.subscribe(data => this.selected = data['data']);
  }}

  ngOnInit(): void {{
  }}
  
  delete(): void {{
    this.service.delete(this.selected.id)
      .subscribe(() => this.back())
  }}

  back(): void {{
    this.location.back();
  }}
}}
'''


def get_entity_detail_component_html(entity: DomainModel) -> str:
    return f'''<div class="container">
    <div class="row center">
        <h1>{entity.name} Detail</h1>
    </div>
    <div class="card">
        <div class="card-content">
            <span class="card-title">Id: {{{{ selected.id }}}}</span>
            <pre>
{{{{ selected | json }}}}
            </pre>
        </div>
        <div class="card-action center">
            <button (click)="back()" class="waves-effect waves-light btn-floating"><i class="material-icons left grey">arrow_back</i>back</button>
        </div>
    </div>
</div>'''


def get_entity_detail_component_ts(entity: DomainModel) -> str:
    return f'''import {{ Location }} from '@angular/common';
import {{ Component, OnInit }} from '@angular/core';
import {{ ActivatedRoute }} from '@angular/router';
import {{ {entity.name} }} from 'src/app/models/{entity.name_kebab_case}';

@Component({{
  selector: 'app-{entity.name_kebab_case}-detail',
  templateUrl: './{entity.name_kebab_case}-detail.component.html',
  styleUrls: ['./{entity.name_kebab_case}-detail.component.scss']
}})
export class {entity.name}DetailComponent implements OnInit {{

  selected: {entity.name} = {{ }} as {entity.name};

  constructor(
    private location: Location,
    private route: ActivatedRoute
  ) {{ 
    route.data.subscribe(data => this.selected = data['data']);
  }}

  ngOnInit(): void {{
  }}
  
  back(): void {{
    this.location.back();
  }}
}}
'''


def get_entity_list_component_html(entity: DomainModel) -> str:
    return f'''<div class="container">
    <div class="row center">
        <h1>{entity.name} List</h1>
    </div>
    <div class="row">
        <table class="highlight striped">
            <thead>
                <th>Id</th>
                <th>content</th>
                <th style="width: 10em;"><a [routerLink]="['new']" class="btn-floating right"><i class="material-icons waves-light">add</i></a></th>
            </thead>
            <tbody>
                <tr *ngFor="let record of records">
                    <td>{{{{ record.id }}}}</td>
                    <td>{{{{ record | json }}}}</td>
                    <td>
                        <div class="row">
                            <div class="col s4">
                                <a [routerLink]="['detail', record.id]" class="btn-floating waves-light"><i class="material-icons grey">visibility</i></a>
                            </div>
                            <div class="col s4">
                                <a [routerLink]="['update', record.id]" class="btn-floating waves-light"><i class="material-icons">edit</i></a>
                            </div>
                            <div class="col s4">
                                <a [routerLink]="['delete', record.id]" class="btn-floating waves-light"><i class="material-icons red">delete</i></a>
                            </div>
                        </div>
                    </td>
                </tr>
            </tbody>
        </table>
    </div>
</div>
'''


def get_entity_list_component_ts(entity: DomainModel) -> str:
    return f'''import {{ Component, OnInit }} from '@angular/core';
import {{ map }} from 'rxjs';
import {{ {entity.name} }} from 'src/app/models/{entity.name_kebab_case}';
import {{ {entity.name}Service }} from 'src/app/services/{entity.name_kebab_case}.service';

@Component({{
  selector: 'app-{entity.name_kebab_case}-list',
  templateUrl: './{entity.name_kebab_case}-list.component.html',
  styleUrls: ['./{entity.name_kebab_case}-list.component.scss']
}})
export class {entity.name}ListComponent implements OnInit {{

  records: {entity.name}[] = []

  constructor(private service: {entity.name}Service) {{ }}

  ngOnInit(): void {{
    this.service.findAll()
    .pipe(
      map(response => response.body)
    ).subscribe({{
      next: records => this.records = records?.items ?? []
    }})
  }}

}}
'''