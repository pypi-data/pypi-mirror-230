from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from typer import Context, Exit, Option, Typer

from abin_sim import __version__

from .config import settings
from .core.file_manager import make_envjs, make_return
from .core.functions import (
    convert_to_json,
    get_environment,
    get_metadata,
    get_secret,
    make_conf,
    query_yes_no,
    update_secret,
)

console = Console()
app = Typer()


def version_func(flag):
    if flag:
        print(__version__)
        raise Exit(code=0)

def conf_func(flag):
    if flag:
        configuration = make_conf()
        if configuration['Status']:
            console.print(configuration['Message'])
        else:
            console.print(configuration['Message'])
        raise Exit(code=0)
    

@app.callback(invoke_without_command=True)
def main(
    ctx: Context,
    version: bool = Option(False, callback=version_func, is_flag=True),
    configure: bool = Option(False, callback=conf_func, is_flag=True),
):
    message = """
[b]ABIN[/] - SIM Tech Solutions

Forma de uso: [b]abin [SUBCOMANDO] [ARGUMENTOS][/]

Existem 4 subcomandos disponíveis para essa aplicação

- [b]list[/]: Fornece, em tela, uma árvore com todas as aplicações e ambientes cadastrados no Vault
- [b]get[/]: Fornece os secrets cadastrados em uma aplicação. Este retorno pode ser em tela ou arquivo
- [b]update[/]: Envia uma nova coleção de ENV para uma determinada aplicação [red](Uso restrito, somente TL e SRE)[/]
- [b]compare[/]: Compara o ENV de uma aplicação em 2 ambientes

[b]Exemplos de uso:[/]
 [b][blue]LIST[/][/]
    [green][b]abin[/][/] [b]list[/]

 [b][blue]GET[/][/]
    [green][b]abin[/][/] [b]get[/] --app api-auth --env dev --proj sim [magenta](para retorno em tela use [green][b]--no-file[/][/])[/]

 [b][blue]UPDATE[/][/]
    [green][b]abin[/][/] [b]update[/] --app api-auth --env dev --proj sim --file .env [magenta](para atualizar outro secret use [green][b]--secret NOME[/][/])[/]

 [b][blue]COMPARE[/][/]
    [green][b]abin[/][/] [b]compare[/] --app api-auth --env qa,dev --proj sim

---
[b]Help:[/]
 [b]Para mais informações[/]
    [green][b]abin[/][/] --help

 [b]Para ver a versão instalada[/]
    [green][b]abin[/][/] --version

 [b]Para gerar o arquivo de configuração[/]
    [green][b]abin[/][/] --configure

 [b]Para informações detalhadas
    [blue][link=https://github.com/SIM-Rede/abin-sim/tree/main]Repo no GIT SIM[/][/] | [blue][link=https://pypi.org/project/abin-sim/]Publicação no PyPI[/][/]
"""
    if ctx.invoked_subcommand:
        return
    console.print(message)

@app.command('get')
def get(
    app: str = Option(
        ...,
        help='Nome da aplicação que deseja recuperar os secrets.',
    ),
    env: str = Option(
        ...,
        help='Ambiente da aplicação que deseja recuperar (Envs: local, dev, qa, main).'
    ),
    proj: str = Option(
        ...,
        help='Projeto que deseja conectar para recuperar os secrets (Projs: sim, charrua)'
    ),
    file: bool = Option(
        True,
        help='Grava em arquivo os secrets do Vault.',
    ),
):
    vault_token = settings.params.vault_token
    vault_url = settings.params.vault_url
    metadata = get_metadata(app, env, proj, vault_token, vault_url)
    if not 'Erro' in metadata:
        if file == None or file == False:
            for conf in metadata:
                secret = get_secret(app, env, proj, conf, vault_token, vault_url)
                console.print(f'--- {conf} ---')
                console.print(secret)
                console.print('\n')
        else:
            for conf in metadata:
                secret = get_secret(app, env, proj, conf, vault_token, vault_url)
                if conf == 'env' and 'front' in app: conf_envjs = secret
                if 'Erro' not in secret:
                    conf_file = make_return(env, secret, settings.params.path, conf)
            if 'front' in app:
                location_envjs = query_yes_no(f'Será gerado o arquivo env.js em {settings.params.path}src/assets. Local existe?', 'yes')
                if location_envjs:
                    envjs = make_envjs(conf_envjs, settings.params.path)
                else:
                    console.print('Crie a pasta e rode novamente o métdo GET para gerar o env.js.')
            if conf_file['Status']:
                if 'front' in app and location_envjs:
                    if envjs['Status']:
                        console.print(f'Arquivo env.js salvo em:\n {"-> " + settings.params.path+"src/assets/"}')
                console.print(f'{app} secrets salvos em:\n {"-> " + settings.params.path if conf_file["ConfFiles"] else ""} {"-> " + settings.params.path+"src/assets/" if conf_file["EnvJS"] else ""}')
            else:
                console.print(conf_file['Message'])
    else:
        console.print(f'Erro ao buscar metadata -> {metadata}')

@app.command('update')
def update(
    app: str = Option(
        ...,
        help='Nome da aplicação que deseja recuperar os secrets.',
    ),
    env: str = Option(
        ...,
        help='Ambiente da aplicação que deseja recuperar (Envs: local, dev, qa, main).'
    ),
    proj: str = Option(
        ...,
        help='Projeto que deseja conectar para recuperar os secrets (Projs: sim, charrua)'
    ),
    secret: str = Option(
        ...,
        help='Secret que será atualizada no Vault (Ex.: env, gcp.json, config.yaml ...)',
    ),
    file: str = Option(
        ...,
        help='Arquivo que será enviado ao Vault',
    ),
):
    vault_token = settings.params.vault_token
    vault_url = settings.params.vault_url
    if secret == 'env':
        payload = convert_to_json(file)
    else:
        payload = file

    confirm = query_yes_no(f'Gostaria de atualizar a secret "{secret}" para o app {app}, no projeto {env.upper()}-{proj.upper()} ?', 'no')
    if confirm:
        ret = update_secret(app, env, proj, secret, vault_token, vault_url, payload)
        console.print(ret)
    else:
        console.print({'Status': 'Canceled'})
    

@app.command('list')
def list():
    vault_environment = get_environment(settings.params.vault_token, settings.params.vault_url)
    console.print('''
╭─ [i]Referência[/i] ──────────────────────╮

    [b][cyan]Vault Environment:[/b][/]
        ├── [blue](env)-(proj)[/]
        │    ├── [green](api)[/]

╰─ [i]Referência[/i] ──────────────────────╯
    ''')
    tree = Tree('[cyan][b]Vault Environment[/b][/]')
    for k, v in vault_environment.items():
        kv = tree.add(f'[blue]{k}')
        for value in v:
            kv.add(f'[green]{value}') 
    
    console.print(tree)

@app.command('compare')
def compare(
    app: str = Option(
        ...,
        help='Nome da aplicação que deseja comparar os secrets.',
    ),
    env: str = Option(
        ...,
        help='Dois ambientes, separados por vírgula, que deseja comparar (Envs: local, dev, qa, main).'
    ),
    proj: str = Option(
        ...,
        help='Projeto que deseja conectar para comparar os secrets (Projs: sim, charrua)'
    ),
):
    # envs = []
    envs_a = []
    envs_b = []
    envs = env.split(',')
    if len(envs) == 2:
        pass
    else:
        console.print('2 ambientes devem ser informados no parâmetro --env.')        
        exit()

    vault_token = settings.params.vault_token
    vault_url = settings.params.vault_url
    for environ in envs:
        if len(envs_a) == 0: 
            dados = get_secret(app, environ, proj, 'env', vault_token, vault_url)
            for item, value in dados.items():
                envs_a.append(item)
        else: 
            dados = get_secret(app, environ, proj, 'env', vault_token, vault_url)
            for item, value in dados.items():
                envs_b.append(item)
    envs_a.sort()
    envs_b.sort()
        
    tbl_envs = Table(title=f'Environments {envs[0]} x {envs[1]}', style="cyan", width=settings.console.table_width)
    for environment in envs:
        tbl_envs.add_column(environment.upper(), justify='left')
    counter = len(envs_a) if len(envs_a) > len(envs_b) else len(envs_b)
    for num in range(0, counter):
        if 0 <= num < len(envs_a): value_a = str(envs_a[num])
        else: value_a = ''
        if 0 <= num < len(envs_b): value_b = str(envs_b[num])
        else: value_b = ''
        tbl_envs.add_row(value_a, value_b, style='green')

    tbl_diferences = Table(title=f'Diferenças {envs[0]} x {envs[1]}', width=settings.console.table_width, style="red")
    for environment in envs:
        tbl_diferences.add_column(environment.upper(), justify='left')
    envs_a_diff = [x for x in envs_a if x not in envs_b]
    envs_b_diff = [x for x in envs_b if x not in envs_a]
    counter = len(envs_a_diff) if len(envs_a_diff) > len(envs_b_diff) else len(envs_b_diff)
    for num in range(0, counter):
        if 0 <= num < len(envs_a_diff): value_a = str(envs_a_diff[num])
        else: value_a = ''
        if 0 <= num < len(envs_b_diff): value_b = str(envs_b_diff[num])
        else: value_b = ''
        tbl_diferences.add_row(value_a, value_b, style='red')
    console.print(tbl_envs, tbl_diferences)
