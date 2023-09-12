from pathlib3x import Path


def make_return(env: str, secret: dict, filepath: str, file: str) -> dict:
    try:
        # path = Path(filepath) / app
        envjs = False
        conffiles = False
        path = Path(filepath)
        # path.rmtree(ignore_errors=True)
        # path.mkdir()
        if file == 'env':
            arqenv = open(f'{path}/.env', 'w')
            conffiles = True
        elif file == 'env.js' and env == 'local':
            envjs = True
            arqenv = open(f'{path}/src/assets/env.js', 'w')
        else:
            arqenv = open(f'{path}/{file}', 'w')
            conffiles = True
    except Exception as e:
        retorno = {'Status': False, 'Message': e, 'EnvJS': envjs, 'ConfFiles': conffiles}
    else:
        if file == 'env':
            for k, v in secret.items():
                if 'PUBSUB' in k and (env == 'qa' or env == 'main'):
                    arqenv.write(f'#TODO Evitar usar este ENV, pois criará conflito com o ambiente {env} -> {k}={v}' + '\n')
                else:
                    arqenv.write(f'{k}={v}' + '\n')
        else: 
            arqenv.write(secret)
        arqenv.close()
        if envjs:
            retorno = {'Status': True, 'Message': '', 'EnvJS': envjs, 'ConfFiles': conffiles}
        else:
            retorno = {'Status': True, 'Message': '', 'EnvJS': envjs, 'ConfFiles': conffiles}
    return retorno


def make_envjs(secret: dict, filepath: str) -> dict:
    path = Path(filepath)
    try:
        arq_envjs = open(f'{path}/src/assets/env.js', 'w')
    except Exception as e:
        retorno = {'Status': False, 'Message': e}
    else:
        try:
            arq_envjs.write('(function (window) {\n  window["env"] = window["env"] || {};\n')
            for k, v in secret.items():
                if '"' in v or "'" in v or v == True or v == False or v == 'true' or v == 'false':
                    arq_envjs.write(f'  window["env"].{k} = {v};\n')
                else:
                    arq_envjs.write(f'  window["env"].{k} = "{v}";\n')
            arq_envjs.write('})(this);')
        except Exception as e:
            retorno = {'Status': False, 'Message': e}
        else:
            retorno = {'Status': True, 'Message': 'Success'}
        arq_envjs.close()
    return retorno