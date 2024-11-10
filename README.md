# Projeto Conway Game of Life

## Instruções de uso para o usuário
Ainda não há instruções para o uso do projeto.

## Instruções de uso para o colaborador

### Instalação
1. Instale o *Python* e o *Git* no seu computador.

### (Opcional) Criar um ambiente virtual
1. Crie uma pasta para o projeto com o nome de sua escolha.
2. Abra o terminal e execute o comando:
   ```bash
   python -m venv .venv
   ```

### Obter o progresso atual do GitHub
1. Assumindo que você já tem instalado o git, você vai executar no git bash:
	```bash
	git init
	```
2. Depois disso:
	```bash
	git pull https://github.com/PauloVitorOliv/conwayGame
	```
3. E em seguida:
	```bash
	git remote add origin https://github.com/PauloVitorOliv/conwayGame
	```

### Obter dependências
1. Para baixar as dependências, execute também no terminal:
	```bash
	pip install mesa
	```
2. E também:
	```bash
	pip install scipy
	pip install pygame
	```

### Criar seu próprio Branch
1. No git bash, substituindo nomeSobrenome por seu nome e sobrenome, respectivamente, execute:
	```bash
	git checkout -b nomeSobrenome
	```
2. Começe a programar! A partir de agora você pode começar a realizar alterações no código.

### Atualizar suas mudanças
1. Você só precisa fazer os passos acima uma vez, e toda vez que você editar o código e quiser fazer uma atualização concreta, deve fazer os passos abaixo:
2. Digite no git bash o comando abaixo com o nome dos arquivos que você editou (se mais de um, separe-os por espaço):
	```bash
	git add nomeArquivo.py
	```
3. Digite novamente no bash um commit com um resumo do que você fez:
	```bash
	git commit -m "Descrição curta do que foi realizado"
	```
4. Digite no git bash, novamente substituindo seu nome:
	```bash
	git push -u origin nomeSobrenome
	```

**(Opcional) Caso não for feito, algum administrador do projeto fará depois)**

3. Entre no site do GitHub com o login feito em https://github.com/PauloVitorOliv/conwayGame e clique em **Compare and Pull Request**. Descreva a alteração que você fez no título e descrição e clique em **Create Pull Request**.
