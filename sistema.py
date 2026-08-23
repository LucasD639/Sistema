import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
import os
import json

class SistemaCadastroLivros:
    LIMITE_GRADE_LIVROS = 50

    def __init__(self, db_path="livros.db"):
        self.conexao = sqlite3.connect(db_path)
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
            err = f"Limite de livros atingido. Não é possível cadastrar mais livros (limite: {self.LIMITE_GRADE_LIVROS})."
            print(err)
            return False, err

        if not titulo or not str(titulo).strip():
            err = "Erro: O título do livro não pode ser vazio."
            print(err)
            return False, err

        if not autor or not str(autor).strip():
            err = "Erro: O nome do autor não pode ser vazio."
            print(err)
            return False, err

        # Allow letters, spaces, dots, hyphens and apostrophes
        if not all(c.isalpha() or c in " .'-" for c in str(autor)):
            err = "Erro: O nome do autor deve conter apenas letras e caracteres válidos."
            print(err)
            return False, err

        if not str(ano_publicacao).isdigit():
            err = "Erro: O ano de publicação deve conter apenas números inteiros."
            print(err)
            return False, err

        try:
            preco_float = float(preco)
            if preco_float < 0:
                err = "Erro: O preço deve ser um número positivo."
                print(err)
                return False, err
        except (ValueError, TypeError):
            err = "Erro: O preço deve ser um número válido."
            print(err)
            return False, err

        if not str(quantidade).isdigit():
            err = "Erro: A quantidade deve conter apenas números inteiros."
            print(err)
            return False, err

        if int(quantidade) <= 0:
            err = "Erro: A quantidade deve ser maior que zero."
            print(err)
            return False, err

        self.cursor.execute("INSERT INTO livros (Titulo, Autor, Ano_Publicacao, Preco, Genero, Quantidade) VALUES (?, ?, ?, ?, ?, ?)",
                            (str(titulo).strip(), str(autor).strip(), int(ano_publicacao), preco_float, str(genero).strip(), int(quantidade)))
        self.conexao.commit()
        msg = "Livro cadastrado com sucesso."
        print(msg)
        return True, msg

    def excluir_livro(self, livro_id=None):
        if livro_id is None:
            err = "Erro: ID do livro deve ser fornecido para excluir o livro."
            print(err)
            return False, err

        try:
            id_int = int(livro_id)
        except (ValueError, TypeError):
            err = "Erro: O ID deve ser um número inteiro."
            print(err)
            return False, err

        self.cursor.execute("SELECT * FROM livros WHERE ID=?", (id_int,))
        livro = self.cursor.fetchone()
        if livro:
            qty = int(livro[6])
            if qty > 1:
                self.cursor.execute("UPDATE livros SET Quantidade = Quantidade - 1 WHERE ID=?", (id_int,))
                msg = f"Uma unidade do Livro com ID {id_int} foi excluída com sucesso."
                print(msg)
            else:
                self.cursor.execute("DELETE FROM livros WHERE ID=?", (id_int,))
                msg = f"Livro com ID {id_int} excluído com sucesso."
                print(msg)
            self.conexao.commit()
            return True, msg
        else:
            err = f"Erro: Livro com ID {id_int} não encontrado."
            print(err)
            return False, err

    def listar_livros(self):
        self.cursor.execute("SELECT * FROM livros")
        return self.cursor.fetchall()

    def obter_quantidade_livros(self):
        self.cursor.execute("SELECT COUNT(*) FROM livros")
        return self.cursor.fetchone()[0]

    def _obter_valor_chave(self, d, chaves_alvo, default=""):
        import unicodedata
        
        def normalizar(s):
            s = str(s).lower().strip()
            s = "".join(c for c in unicodedata.normalize('NFD', s) if unicodedata.category(c) != 'Mn')
            for char in [" ", "_", "-"]:
                s = s.replace(char, "")
            return s
            
        chaves_alvo_norm = [normalizar(k) for k in chaves_alvo]
        for k, v in d.items():
            if normalizar(k) in chaves_alvo_norm:
                return v
        return default

    def exportar_json(self, caminho):
        livros = self.listar_livros()
        dados = [
            {
                "ID": l[0],
                "Titulo": l[1],
                "Autor": l[2],
                "Ano_Publicacao": l[3],
                "Preco": l[4],
                "Genero": l[5],
                "Quantidade": l[6],
            }
            for l in livros
        ]
        with open(caminho, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False, indent=2)
        print(f"Dados exportados para {caminho}.")

    def importar_json(self, caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as f:
                dados = json.load(f)
        except Exception as e:
            err = f"Erro ao ler arquivo JSON: {str(e)}"
            print(err)
            return False, err
            
        if isinstance(dados, dict):
            if all(isinstance(v, dict) for v in dados.values()):
                lista_livros = list(dados.values())
            else:
                lista_livros = [dados]
        elif isinstance(dados, list):
            lista_livros = dados
        else:
            lista_livros = []
            
        importados = 0
        for livro in lista_livros:
            titulo = str(self._obter_valor_chave(livro, ["titulo", "title", "name"], ""))
            autor = str(self._obter_valor_chave(livro, ["autor", "author"], ""))
            ano = str(self._obter_valor_chave(livro, ["ano_publicacao", "anopublicacao", "anodepublicacao", "ano", "year"], ""))
            preco_val = self._obter_valor_chave(livro, ["preco", "preço", "price"], 0.0)
            genero = str(self._obter_valor_chave(livro, ["genero", "gênero", "genre"], ""))
            quantidade = str(self._obter_valor_chave(livro, ["quantidade", "quantity", "qty"], "1"))
            
            success, _ = self.cadastrar_livro(titulo, autor, ano, preco_val, genero, quantidade)
            if success:
                importados += 1
                
        msg = f"{importados} livro(s) importado(s) de {caminho} com sucesso."
        print(msg)
        return True, msg

def cadastrar_livro_interface():
    titulo = entry_titulo.get()
    autor = entry_autor.get()
    ano_publicacao = entry_ano.get()
    preco = entry_preco.get()
    genero = entry_genero.get()
    quantidade = entry_quantidade.get()

    sucesso, mensagem = sistema_cadastro.cadastrar_livro(titulo, autor, ano_publicacao, preco, genero, quantidade)
    if sucesso:
        messagebox.showinfo("Sucesso", mensagem)
        # Limpar campos de entrada
        entry_titulo.delete(0, tk.END)
        entry_autor.delete(0, tk.END)
        entry_ano.delete(0, tk.END)
        entry_preco.delete(0, tk.END)
        entry_genero.delete(0, tk.END)
        entry_quantidade.delete(0, tk.END)
    else:
        messagebox.showerror("Erro", mensagem)
    atualizar_interface()

def excluir_livro_interface():
    livro_id = entry_id_excluir.get()

    if livro_id:
        sucesso, mensagem = sistema_cadastro.excluir_livro(livro_id)
        if sucesso:
            messagebox.showinfo("Sucesso", mensagem)
            entry_id_excluir.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", mensagem)
        atualizar_interface()
    else:
        messagebox.showerror("Erro", "Erro: ID do livro deve ser fornecido para excluir o livro.")

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

def exportar_json_interface():
    caminho = filedialog.asksaveasfilename(
        defaultextension=".json",
        filetypes=[("JSON files", "*.json")],
        title="Exportar livros para JSON",
    )
    if caminho:
        sistema_cadastro.exportar_json(caminho)
        messagebox.showinfo("Exportação", f"Dados exportados para:\n{caminho}")

def importar_json_interface():
    caminho = filedialog.askopenfilename(
        filetypes=[("JSON files", "*.json")],
        title="Importar livros de JSON",
    )
    if caminho:
        sucesso, mensagem = sistema_cadastro.importar_json(caminho)
        if sucesso:
            atualizar_interface()
            messagebox.showinfo("Importação", mensagem)
        else:
            messagebox.showerror("Erro de Importação", mensagem)

if __name__ == "__main__":
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

    button_exportar = ttk.Button(frame, text="Exportar JSON", command=exportar_json_interface)
    button_exportar.grid(column=0, row=11, pady=5)

    button_importar = ttk.Button(frame, text="Importar JSON", command=importar_json_interface)
    button_importar.grid(column=1, row=11, pady=5)

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
    label_quantidade_total = ttk.Label(frame, textvariable=quantidade_livros)
    label_quantidade_total.grid(column=0, row=10, columnspan=2, pady=10)

    atualizar_interface()

    root.mainloop()
