# Sistema de Gestão de Dados – Protótipo

Protótipo de sistema de gestão de dados desenvolvido em Python com interface gráfica (Tkinter) e banco de dados SQLite.

## Funcionalidades

- **Cadastrar livros**: título, autor, ano de publicação, preço, gênero e quantidade.
- **Excluir livros**: por ID (decrementa a quantidade; remove o registro quando chega a zero).
- **Listar livros**: exibe todos os livros cadastrados em uma tabela.
- **Exportar para JSON**: salva todos os livros em um arquivo `.json`.
- **Importar de JSON**: carrega livros a partir de um arquivo `.json`.

## Requisitos

- Python 3.8+
- Tkinter (incluso na instalação padrão do Python)

## Como executar

```bash
python sistema.py
```

## Estrutura do projeto

```
Sistema/
├── sistema.py     # Aplicação principal
├── livros.json    # Exemplo de dados em JSON
└── README.md
```
