import json
import re
from os import environ
from sys import stdout

import requests
from pathlib3x import Path

# def qualquer(valor: str) -> str:
#     if valor == 'a':
#         dado = 'VOCE PASSOU A'
#     else:
#         dado = 'VOCE PASSOU OUTRA COISA'
#     return dado


def get_secret(
    app: str,
    env: str,
    proj: str,
    conf: str,
    token: str,
    vault_url: str
) -> dict:
    headers = {'X-Vault-Token': token}
    try:
        response = requests.request(
            'GET', url=vault_url + f'/v1/{env}-{proj}/data/{app}/{conf}', headers=headers
        )
    except Exception as e:
        return {'Status': e}
    
    if response.status_code == 200:
        if conf == 'env':
            ret = response.json()['data']['data']
        else:
            ret = response.json()['data']['data']['content']
    else:
        ret = {'Status': 'Erro'}
    return ret

def get_metadata(
    app: str,
    env: str,
    proj: str,
    token: str,
    vault_url: str,
) -> list:
    headers = {'X-Vault-Token': token}
    try:
        response = requests.request(
            'LIST', url=vault_url + f'/v1/{env}-{proj}/metadata/{app}', headers=headers
        )
    except Exception as e:
        return [f'Erro {e}']

    if response.status_code == 200:
        ret = response.json()['data']['keys']
    else:
        ret = [f'Erro', response.text]
    return ret

def convert_to_json(
    file: str,
) -> dict:
    with open(file, 'r') as f:
        content = f.readlines()

    contentList = [x.strip().split('^#')[0].split('=', 1) for x in content if '=' in x.split('^#')[0]]
    contentDict = dict(contentList)
    for k, v in contentList:
        # for i, x in enumerate(v.split('$')[1:]):
        #     key = re.findall(r'\w+', x)[0]
        #     v = v.replace('$' + key, contentDict[key])
        if '=' in v or '$' in v or '#' in v:
            if "'" in v:
                contentDict[k] = v.strip()
            else:
                contentDict[k] = f"'{v.strip()}'"
        else:
            contentDict[k] = v.strip()

    return json.dumps(contentDict)

def replace_string(secret, search, replace):
    with open(secret, 'rt') as file_in:
        novo_arquivo = file_in.read()

    with open(secret, 'wt') as file_out:
        novo_arquivo = novo_arquivo.replace(search, replace)
        file_out.write(novo_arquivo)

def update_secret(
    app: str,
    env: str,
    proj: str,
    secret: str,
    token: str,
    vault_url: str,
    file: dict,
) -> dict:
    headers = {'X-Vault-Token': token}
    match secret:
        case 'env':
            json_file = Path('json_file.json')
            json_file.touch()
            json_file.write_text('{"data":'+file+'}')
            payload = open('json_file.json', 'rb').read()
            try:
                ret = requests.request(
                    'POST', url=vault_url + f'/v1/{env}-{proj}/data/{app}/{secret}', headers=headers, data=payload
                )
            except Exception as e:
                return {'Status': e}
            json_file.unlink()
        case _:
            if secret == 'env.js':
                replace_string(file, '\"', '\\\"')
            with open(file, 'r') as f:
                content = f.readlines()
            converted = ''
            # contentList = [x.strip().split('#')[0].split('=', 1) for x in content if '=' in x.split('#')[0]]
            for line in content:
                if converted == '':
                    converted = f'{line}'.strip()+'\\n'
                else:
                    converted = f'{converted}{line}'.strip()+'\\n'

            json_file = Path('json_file.json')
            json_file.touch()
            json_file.write_text('{"data": {"content": "'+converted+'"} }')

            payload = open('json_file.json', 'rb').read()
            try:
                ret = requests.request(
                    'POST', url=vault_url + f'/v1/{env}-{proj}/data/{app}/{secret}', headers=headers, data=payload
                )
            except Exception as e:
                return {'Status': e}
            json_file.unlink()

            if secret == 'env.js':
                replace_string(file, '\\\"', '\"')

    if ret.status_code == 200:
        return {'Status': 'Success'}
    else:
        return {'Status': (ret.text)}

def make_conf() -> dict:
    home_dir = environ['HOME']
    try:
        path = Path(home_dir) / 'abin'
        path.mkdir()
        arq_conf = open(f'{path}/settings.toml', 'w')
    except Exception as e:
        erro = f'Arquivo de configuração já criado ou pasta já existe em {home_dir}.\n Comando retornou {e}'
        retorno = {'Message': erro, 'Status': False}
    else:
        arq_conf.write('name = "ABIN"\n\n[params]\nvault_token = "ALTERAR"\nvault_url = "https://aspirina.simtech.solutions"\npath = "./"\n\n[console]\ntable_width = 40')
        arq_conf.close()
        retorno = {'Message': f'Arquivo de configuração criado em {path}', 'Status': False}
    return retorno

def get_environment(
    token: str,
    vault_url: str,
) -> dict:
    headers = {'X-Vault-Token': token }
    try:
        mounts = requests.request('GET', url=vault_url + '/v1/sys/mounts', headers=headers)
    except Exception as e:
        retorno = {'Status': f'Erro: {e}'}
    
    if mounts.status_code == 200:
        search = ['local', 'dev', 'qa', 'main']
        matches = []

        for k, v in mounts.json().items():
            if any([x in k for x in search]):
                matches.append(k)
        matches.sort()

        paths_metadata = {}
        for path in matches:
            paths_response = requests.request('LIST', url=f'https://aspirina.simtech.solutions/v1/{path}metadata', headers=headers)
            if paths_response.status_code == 200:
                paths_metadata[path] = paths_response.json()['data']['keys']
            
        retorno = paths_metadata
    else:
        retorno = {'Status': f'Erro: {mounts.text}'}
    
    return retorno

def query_yes_no(
    question: str, 
    default: str
) -> str:
    valid = {"yes": True, "y": True, "ye": True, "no": False, "n": False}
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        stdout.write(f'{question} {prompt}')
        choice = input().lower()
        if default is not None and choice == "":
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            stdout.write("Please respond with 'yes' or 'no' " "(or 'y' or 'n').\n")
