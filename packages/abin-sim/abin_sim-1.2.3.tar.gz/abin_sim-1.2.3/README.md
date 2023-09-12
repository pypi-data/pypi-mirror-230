# ABIN
[![CI](https://github.com/SIM-Rede/abin-sim/actions/workflows/pipeline.yaml/badge.svg)](https://github.com/SIM-Rede/abin-sim/actions/workflows/pipeline.yaml)
[![PyPI version](https://badge.fury.io/py/abin-sim.svg)](https://badge.fury.io/py/abin-sim)

## Instalação

Utilize o pipx para instalar o abin no seu computador.
```
sudo apt install pipx
pipx install abin_sim
```
A versão da aplicação no README será atualizada sempre que um novo build rodar.

Se você estiver rodando no PopOS precisa criar um link simbólico para a aplicação ou adicionar $HOME/.local/bin no path do SO
```
sudo ln -s $HOME/.local/bin/abin /usr/local/bin/abin
```


## Configuração

Após realizar a instalação do App, será necessário iniciar o arquivo de configuração
Para isso execute a instrução abaixo:
```
abin --configure
```

A instrução acima criará um arquivo chamado 'settings.toml' em $HOME/abin/
Com o arquivo em mãos, altere o valor de **vault_token** para o seu token, o valor deverá focar entre " "

*vault_token* -> Seu token de autenticação no Vault

Para ter acesso seu token basta autenticar no Web UI do Vault.
Acesse no seu navegador o endereço https://aspirina.simtech.solutions
*PS*: O acesso devera ser solicitado ao time de SRE da SIMTech

Na tela de login:

* Mude **Method** para ***Username***
* Entre com o seu usuário em **Username**
* Entre com a sua senha em **Password**
* Clique em **More Options**
* Em **Mount Path** digite ***simtech***
* Clique em **Sign in**

Após o login clique no boneco localizao no canto superior direito e, após, clique em **Copy Token**

**Importante:** O Token é válido por 30 dias, portanto lembre de renová-lo.

## Funções

### DESCRITIVO
    Uso: abin

    Retorna uma breve explicação sobre a funcionalidade do CLI.
    Traz exemplos de uso e link para projeto no GitHub

### VERSION
    Uso: abin --version

    Retorna a versão atualmente instalada no SO.
    Para atualizá-la:

    pipx upgrade abin_sim

### CONFIGURE
    Uso: abin --configure

    Gera o arquivo de configuração da aplicação.

## LIST
    Uso: abin list

    Retorna a árvore de Secrets cadastradas no Path obedecendo a referência abaixp
    ╭─ Referência ──────────────────╮
    │                               │ 
    │ Vault Environment:            │
    │     ├── (env)-(proj)          │
    │     │    ├── (api)            │
    │                               │
    ╰─ Referência ──────────────────╯

### GET
    Uso: abin get [OPTIONS]                                                                                                                            
                                                                                                                                                      
    ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ *  --app                  TEXT  Nome da aplicação que deseja recuperar os secrets. [default: None] [required]                                        │
    │ *  --env                  TEXT  Ambiente da aplicação que deseja recuperar (Envs possíveis: dev, qa, main). [default: None] [required]               │
    │ *  --proj                 TEXT  Projeto que deseja conectar para recuperar os secrets (Projs possíveis: sim, charrua) [default: None] [required]     │
    │    --file    --no-file          Cria um arquivo para cada path cadastrada no secrets. [default: file]                                                │
    │    --help                       Show this message and exit.                                                                                          │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

    Examplo:
    * Imprime os dados no StdOut (Tela)
        abin get --app api-auth --env dev --proj sim --no-file
    * Imprime os dados em arquivo (Com base no arquivo $HOME/abin/settings.toml)
        abin get --app api-auth --env dev --proj sim

### UPDATE
    Uso: abin update [OPTIONS] 
                                               
    ╭─ Options─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ *  --app         TEXT  Nome da aplicação que deseja recuperar os secrets. [default: None]  [required]                                        │
    │ *  --env         TEXT  Ambiente da aplicação que deseja recuperar (Envs possíveis: dev, qa, main). [default: None] [required]                │
    │ *  --proj        TEXT  Projeto que deseja conectar para recuperar os secrets (Projs possíveis: sim, charrua) [default: None] [required]      │
    │    --secret      TEXT  Secret que será atualizada no Vault (Ex.: env, gcp.json, config.yaml ...) [default: env]                              │
    │ *  --file        TEXT  Arquivo com variárias de ambiente [default: None] [required]                                                          │
    │    --help              Show this message and exit.                                                                                           │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

    Eexamplo:
        abin update --app api-auth --env dev --proj sim --file .env  (para atualizar outro secret use --secret NOME)

### COMPARE
    Uso: abin compare [OPTIONS]

    ╭─ Options ────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
    │ *  --app                  TEXT  Nome da aplicação que deseja recuperar os secrets. [default: None] [required]                                            │
    │ *  --env                  TEXT  Ambiente da aplicação que deseja recuperar (Envs possíveis: dev, qa, main). [default: None] [required]                   │
    │ *  --proj                 TEXT  Projeto que deseja conectar para recuperar os secrets (Projs possíveis: sim, charrua) [default: None] [required]         │
    │    --help                       Show this message and exit.                                                                                              │
    ╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯

    Eexamplo:
        abin compare --app api-auth --env qa,dev --proj sim