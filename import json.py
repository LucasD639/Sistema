import tkinter as tk
from tkinter import ttk
import sqlite3
import os

class SistemaCadastroLivros:
    LIMITE_GRADE_LIVROS = 50

    def __init__(self):
        if os.path.exists("livros.db"):
            os.remove("livros.db")

        self.conexao = sqlite3.connect("livros.db")
        self.cursor = self.conexao.cursor()

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS livros (
                                ID INTEGER PRIMARY KEY,
                                Titulo TEXT,
                                Autor TEXT,
                                Ano_Publicacao INTEGER,
                                Preco REAL,
                                Genero TEXT,
                                Quantidade INTEGER)''')
        self.conexao.commit()

    def cadastrar_livro(self, titulo, autor, ano_publicacao, preco, genero, quantidade):
        if self.obter_quantidade_livros() >= self.LIMITE_GRADE_LIVROS:
            print(f"Limite de livros atingido. Não é possível cadastrar mais livros (limite: {self.LIMITE_GRADE_LIVROS}).")
            return

        if not autor.replace(" ", "").isalpha():
            print("Erro: O nome do autor deve conter apenas letras.")
            return

        if not ano_publicacao.isdigit() or not quantidade.isdigit():
            print("Erro: O ano de publicação e a quantidade devem conter apenas números inteiros.")
            return

        self.cursor.execute("INSERT INTO livros (Titulo, Autor, Ano_Publicacao, Preco, Genero, Quantidade) VALUES (?, ?, ?, ?, ?, ?)",
                            (titulo, autor, ano_publicacao, preco, genero, quantidade))
        self.conexao.commit()
        print("Livro cadastrado com sucesso.")

    def excluir_livro(self, livro_id=None):
        if livro_id is None:
            print("Erro: ID do livro deve ser fornecido para excluir o livro.")
            return

        self.cursor.execute("SELECT * FROM livros WHERE ID=?", (livro_id,))
        if livro := self.cursor.fetchone():
            if livro[6] > 1:
                self.cursor.execute("UPDATE livros SET Quantidade = Quantidade - 1 WHERE ID=?", (livro_id,))
                print(f"Uma unidade do Livro com ID {livro_id} foi excluída com sucesso.")
            else:
                self.cursor.execute("DELETE FROM livros WHERE ID=?", (livro_id,))
                print(f"Livro com ID {livro_id} excluído com sucesso.")
        else:
            print(f"Livro com ID {livro_id} não encontrado.")

        self.conexao.commit()

    def listar_livros(self):
        self.cursor.execute("SELECT * FROM livros")
        return self.cursor.fetchall()

    def obter_quantidade_livros(self):
        self.cursor.execute("SELECT COUNT(*) FROM livros")
        return self.cursor.fetchone()[0]

def cadastrar_livro_interface():
    titulo = entry_titulo.get()
    autor = entry_autor.get()
    ano_publicacao = entry_ano.get()
    preco = entry_preco.get()
    genero = entry_genero.get()
    quantidade = entry_quantidade.get()

    sistema_cadastro.cadastrar_livro(titulo, autor, ano_publicacao, preco, genero, quantidade)
    atualizar_interface()

def excluir_livro_interface():
    livro_id = entry_id_excluir.get()

    if livro_id:
        sistema_cadastro.excluir_livro(int(livro_id))
        listar_livros_interface()
        atualizar_quantidade_livros()
    else:
        print("Erro: ID do livro deve ser fornecido para excluir o livro.")

def atualizar_interface():
    listar_livros_interface()
    atualizar_quantidade_livros()

def listar_livros_interface():
    tree.delete(*tree.get_children())
    livros = sistema_cadastro.listar_livros()
    for livro in livros:
        tree.insert('', 'end', values=(livro[0], livro[1], livro[2], livro[3], livro[4], livro[5], livro[6]))

def atualizar_quantidade_livros():
    quantidade_livros.set(f"Quantidade de Livros: {sistema_cadastro.obter_quantidade_livros()}")

sistema_cadastro = SistemaCadastroLivros()

root = tk.Tk()
root.title("Cadastro de Livros")

frame = ttk.Frame(root, padding="10")
frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

label_titulo = ttk.Label(frame, text="Título:")
label_titulo.grid(column=0, row=0, sticky=tk.W)

label_autor = ttk.Label(frame, text="Autor:")
label_autor.grid(column=0, row=1, sticky=tk.W)

label_ano = ttk.Label(frame, text="Ano de Publicação:")
label_ano.grid(column=0, row=2, sticky=tk.W)

label_preco = ttk.Label(frame, text="Preço:")
label_preco.grid(column=0, row=3, sticky=tk.W)

label_genero = ttk.Label(frame, text="Gênero:")
label_genero.grid(column=0, row=4, sticky=tk.W)

label_quantidade = ttk.Label(frame, text="Quantidade:")
label_quantidade.grid(column=0, row=5, sticky=tk.W)

entry_titulo = ttk.Entry(frame, width=30)
entry_titulo.grid(column=1, row=0, sticky=(tk.W, tk.E))

entry_autor = ttk.Entry(frame, width=30)
entry_autor.grid(column=1, row=1, sticky=(tk.W, tk.E))

entry_ano = ttk.Entry(frame, width=10)
entry_ano.grid(column=1, row=2, sticky=(tk.W, tk.E))

entry_preco = ttk.Entry(frame, width=10)
entry_preco.grid(column=1, row=3, sticky=(tk.W, tk.E))

entry_genero = ttk.Entry(frame, width=10)
entry_genero.grid(column=1, row=4, sticky=(tk.W, tk.E))

entry_quantidade = ttk.Entry(frame, width=10)
entry_quantidade.grid(column=1, row=5, sticky=(tk.W, tk.E))

button_cadastrar = ttk.Button(frame, text="Cadastrar Livro", command=cadastrar_livro_interface)
button_cadastrar.grid(column=0, row=6, columnspan=2, pady=10)

label_id_excluir = ttk.Label(frame, text="ID do Livro para Excluir:")
label_id_excluir.grid(column=0, row=7, sticky=tk.W)

entry_id_excluir = ttk.Entry(frame, width=10)
entry_id_excluir.grid(column=1, row=7, sticky=(tk.W, tk.E))

button_excluir = ttk.Button(frame, text="Excluir Livro", command=excluir_livro_interface)
button_excluir.grid(column=0, row=8, columnspan=2, pady=10)

tree = ttk.Treeview(frame, columns=("ID", "Título", "Autor", "Ano de Publicação", "Preço", "Gênero", "Quantidade"), show="headings")
tree.heading("ID", text="ID")
tree.heading("Título", text="Título")
tree.heading("Autor", text="Autor")
tree.heading("Ano de Publicação", text="Ano de Publicação")
tree.heading("Preço", text="Preço")
tree.heading("Gênero", text="Gênero")
tree.heading("Quantidade", text="Quantidade")
tree.grid(column=0, row=9, columnspan=2, sticky=(tk.W, tk.E))

quantidade_livros = tk.StringVar()
label_quantidade = ttk.Label(frame, textvariable=quantidade_livros)
label_quantidade.grid(column=0, row=10, columnspan=2, pady=10)

atualizar_interface()

root.mainloop()
