import json
import os


class Book():
    """Classe de registro de livros"""

    def __init__(self, id: str, titulo: str, autor: str, genero: str, estoque: int) -> None:
        """Instâncias do livro"""
        self.id = id
        self.autor = autor
        self.titulo = titulo
        self.genero = genero
        self.estoque = estoque


    def acervo(self=None) -> dict:
        try:
            with open(".data/books.json", "r", encoding="utf-8") as file:
                conteudo = json.loads(file.read())
            
            return conteudo

        except FileNotFoundError:

            if ".data" not in os.listdir():
                os.mkdir(".data")
                os.system("attrib +h .data")

            with open(".data/books.json", "w", encoding="utf-8") as file:
                file.write("{\n}")

            if self:
                return self.acervo()
            else:
                return {}
            
    
    def registrar(self) -> bool:
        """Função para registrar o livro"""
        dados = self.acervo()
        if self.id not in dados.keys():
            dados[self.id] = {
                "Titulo": self.titulo,
                "Autor": self.autor,
                "Genero": self.genero,
                "Estoque": self.estoque
            }

            with open(".data/books.json", "w", encoding="utf-8") as file:
                json.dump(dados, file, ensure_ascii=False, indent=4)
                return True
        else:
            return False


    def view(self):
        """Vizualização de dados"""
        return {"id": self.id, "titulo": self.titulo, "autor": self.autor, "genero": self.genero, "estoque": self.estoque}


    def requirements():
        """Dados requeridos para registrar um livro"""
        return [[str, "ID"], [str, "titulo"], [str, "autor"], [str, "genero"], [int, "estoque"]]


class User():
    def __init__(self, nome: str, cpf: str, idade: int) -> None:
        """Informações do usuário"""
        self.cpf = cpf
        self.nome = nome
        self.idade = idade
    
    def usuarios(self=None) -> dict:
        try:
            with open(".data/users.json", "r", encoding="utf-8") as file:
                conteudo = json.loads(file.read())
            
            return conteudo

        except FileNotFoundError:

            if ".data" not in os.listdir():
                os.mkdir(".data")
                os.system("attrib +h .data")

            with open(".data/users.json", "w", encoding="utf-8") as file:
                file.write("{\n}")

            if self:
                return self.usuarios()
            else:
                return {}
    
    def requirements() -> list:
        """Dados requeridos para registrar um livro"""
        return [[str, "Nome"], [str, "CPF"], [int, "Idade"]]
    
    def view(self) -> dict:
        """Vizualização de dados"""
        return {"Nome": self.nome, "CPF": self.cpf, "idade": self.idade}
    
    def registrar(self) -> None:
        """Função para registrar o livro"""
        dados = self.usuarios()
        if self.cpf not in dados.keys():
            dados[self.cpf] = {
                "Nome": self.nome,
                "Idade": self.idade,
                "Locado": "-1",
                "Historico": []
            }

            with open(".data/users.json", "w", encoding="utf-8") as file:
                json.dump(dados, file, ensure_ascii=False, indent=4)
                return True
        else:
            return False

class Loc:
    def __init__(self, id: str, cpf: str) -> None:
        self.id = id
        self.cpf = cpf
    
    def locar_devo(self, type: bool) -> bool:
        """Função  de locação e devolução de livros, para locar type = True e para devolução type = False"""
        users = User.usuarios()
        books = Book.acervo()

        if self.cpf not in users.keys():
            return False
        
        if self.id not in books.keys():
            return False
        
        livro = books[self.id]
        
        if type:
            if livro["Estoque"] == 0 or users[self.cpf]["Locado"] != "-1":
                return False
        
            users[self.cpf]["Historico"].append(books[self.id]["Titulo"])
            users[self.cpf]["Locado"] = self.id

            with open(".data/users.json", "w", encoding="utf-8") as file:
                json.dump(users, file, ensure_ascii=False, indent=4)
        else:
            if users[self.cpf]["Locado"] != self.id:
                return False
            else:
                users[self.cpf]["Locado"] = "-1"
                with open(".data/users.json", "w", encoding="utf-8") as file:
                    json.dump(users, file, ensure_ascii=False, indent=4)
        
        books[self.id]["Estoque"] += -1 if type else 1

        with open(".data/books.json", "w", encoding="utf-8") as file:
            json.dump(books, file, ensure_ascii=False, indent=4)
        
        return True
    