# jogos_python

Pacote para facilitar a criação de jogos com Python, usando pygame por baixo dos panos.

## Instalação

```
pip install jogos_python
```

## Ajuda

Para aprender como usar este pacote, veja a documentação, lá explicamos como funciona e damos exemplos.

* [Documentação](https://jogos-python.readthedocs.io).

Se você busca contribuir com o desenvolvimento deste pacote, você pode acessar o repositório oficial com o código-fonte, e ver a seção sobre Desenvolvimento.

* [Código-fonte](https://gitlab.com/LIpE-UFRJ/jogos-python).

## Desenvolvimento

Para desenvolver é essencial ser capaz de rodar o programa e conferir as modificações em tempo real. Para isto, siga os passos abaixo, a partir da pasta raiz do reporitório. É necessário ter o `pip` instalado em seu sistema. Se necessário instale o `venv` com `pip install venv`.

### Ambiente virtual

Crie um ambiente virtual para desenvolvimento. Só é preciso fazer isto uma vez.

```
python3 -m venv .venv
```

Será criada uma pasta oculta `.venv` na pasta do projeto.

Ative o ambiente com o comando:

```
source ./.venv/bin/activate
```

Quando quiser desativar o ambiente use o comando `deactivate`. Para rodas o programa em desenvolvimento é recomentado fazer no ambiente virtual, com um ambiente controlado para rodar o pacote.

### Instalação editável do pacote
Para desenvolver faça uma instalação editável do pacote com o comando

```
pip install -e .
``` 

Instalando desta maneira o pacote sempre conterá o código atual em desenolvimento. Este passo precisa ser feito apenas uma vez no ambiente virtual e permitirá importar o pacote nos testes e exemplos da mesma forma que o usuário do pacote faria.

### Testes automáticos

Para este projeto pretende-se usar o framework de testes `Pytest`. Então para ainda rodar os testes (quando houver), instale o pacote de testes com comando `pip install pytest` e, depois, rode os testes unitários  (futuramente) pelo comando `pytest`.

### Atualização da distribuição do pacote no PyPI

#### Build

```
python3 setup.py sdist bdist_wheel
```

Para os passos a seguir é preciso garantir que possui instalado o pacote `twine`. Se necessário instale com `pip install twine`.

#### Checkagem

```
twine check dist/*
```

#### Upload

Para realizar o upload é preciso ser um desenvolvedor do pacote e possuir as credenciais para upload no PyPI.

```
twine upload dist/*
```