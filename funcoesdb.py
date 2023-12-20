import sqlite3

class Mydatabase:
    def __init__(self):
        self.conexao = sqlite3.connect('servicos.db', check_same_thread=False)
        self.cursor = self.conexao.cursor()
        self.cursor.execute("""CREATE TABLE IF NOT EXISTS encomendas
                               (descricao varchar(20), codigo varchar(13), ultinfo varchar(30))""")

    def inserirencomenda(self, descricao, codigo_rastreio):
        self.cursor.execute(f"""INSERT INTO encomendas
                                (descricao, codigo, ultinfo)
                                VALUES
                                ('{str(descricao)}', '{codigo_rastreio}', '***')""")
        self.conexao.commit()

    def cadastroexistente(self, codigo):
        resposta = self.cursor.execute(f"""SELECT codigo FROM encomendas WHERE codigo='{codigo}'""")
        self.conexao.commit()
        return resposta.fetchall()

    def apagarlinhastabela(self):
        self.cursor.execute("""DELETE FROM encomendas""")
        self.conexao.commit()

    def extrair_tudo(self):
        return self.cursor.execute("SELECT * FROM encomendas").fetchall()

    def atualizar_dado_encomenda(self, ultima_atualizacao, cod):
        self.cursor.execute(f"""UPDATE encomendas SET ultinfo='{ultima_atualizacao}' WHERE codigo='{cod}'""")
        self.conexao.commit()

    def encerrar_conexao(self):
        self.cursor.close()



#obj = Mydatabase()
#print(obj.extrair_tudo())
#t = obj.cadastroexistente('QQ361354787BR')
#obj.apagarlinhastabela()
