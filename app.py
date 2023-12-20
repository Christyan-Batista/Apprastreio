import requests, time
from tkinter import *
from tkinter import ttk
from customtkinter import *
import threading
from funcoesdb import *


paleta_cores = {'escuro': '#1A3F4D', 'claro': '#53ADEA', 'intermediario': '#286175'}

class Correios:
    def __init__(self, codigorastreio):
        self.tentativas = 0
        self.erro = False
        self.url = f"https://api.linketrack.com/track/json?user=teste&token=1abcd00b2731640e886fb41a8a9671ad1434c599dbaa0a0de9a5aa619f29a83f&codigo={codigorastreio}"

        if codigorastreio is not None:
            while True:
                try:
                    self.resposta = requests.request("GET", self.url, headers={}, data={}).json()
                    self.tentativas = 0
                    break
                except:
                    time.sleep(3)
                    self.tentativas += 1
                    if self.tentativas >= 10:
                        self.erro = True
                        break
                    continue



    def todoseventos(self):
        if self.erro is not True:
            return self.resposta['eventos']
        else:
            return False

    def ultimoevento(self):
        if self.erro is not True:
            self.ordernareventos()
            return self.resposta['eventos'][len(self.resposta['eventos'])-1]
        else:
            return False

    def ordernareventos(self):
        info_dados = []
        for eventos in self.resposta['eventos']:
            temp = {}
            temp['dia'] = int(eventos['data'][0:2])
            temp['mes'] = int(eventos['data'][3:5])
            temp['ano'] = int(eventos['data'][6::])
            temp['hora'] = int(eventos['hora'][0:2])
            temp['min'] = int(eventos['hora'][3:5])
            info_dados.append(temp)

        for num in range(0, len(info_dados)-1, 1):
            for num_dois in range(num+1, len(info_dados), 1):
                if info_dados[num]['ano'] >= info_dados[num_dois]['ano'] and info_dados[num]['mes'] >= info_dados[num_dois]['mes'] and info_dados[num]['dia'] >= info_dados[num_dois]['dia']:
                    if info_dados[num]['dia'] == info_dados[num_dois]['dia']:
                        if (info_dados[num]['hora'] >= info_dados[num_dois]['hora']):
                            temporario = self.resposta['eventos'][num_dois]
                            self.resposta['eventos'][num_dois] = self.resposta['eventos'][num]
                            self.resposta['eventos'][num] = temporario

                            temporario = info_dados[num_dois]
                            info_dados[num_dois] = info_dados[num]
                            info_dados[num] = temporario
                    else:
                        temporario = self.resposta['eventos'][num_dois]
                        self.resposta['eventos'][num_dois] = self.resposta['eventos'][num]
                        self.resposta['eventos'][num] = temporario

                        temporario = info_dados[num_dois]
                        info_dados[num_dois] = info_dados[num]
                        info_dados[num] = temporario


class App:
    def __init__(self):
        self.conexao_db = Mydatabase()
        self.rastreio_em_foco = Correios(None)
        self.window = Tk()
        self.altura_tela = self.window.winfo_screenwidth()
        self.largura_tela = self.window.winfo_screenheight()
        self.window.title('Rastreio de Encomendas')
        self.window.geometry(f'{self.altura_tela}x{self.largura_tela}')
        self.window.resizable(True, True)
        self.window.configure(bg=paleta_cores['escuro'])
        self.menu_lateral()
        self.area_principal()
        self.window.mainloop()

    def menu_lateral(self):
        self.frame_menu = Frame(self.window)
        self.frame_menu.place(relx=0,
                              rely=0,
                              relheight=1,
                              relwidth=0.15)
        self.frame_menu.configure(bg=paleta_cores['intermediario'])
        self.botao_menu()

    def area_principal(self):
        self.frame_principal = Frame(self.window)
        self.frame_principal.place(relx=0.15,
                                   rely=0,
                                   relheight=1,
                                   relwidth=0.85)
        self.frame_principal.configure(bg=paleta_cores['escuro'])

    def botao_menu(self):
        self.botao_rastrear = CTkButton(self.frame_menu, command=self.acao_botao_menu)
        self.botao_rastrear.configure(text='Rastrear Encomenda',
                                      font=('Helvetica', 15, 'bold'),
                                      corner_radius=12,
                                      border_width=0,
                                      fg_color=paleta_cores['claro'])
        self.botao_rastrear.place(relx=0.035, rely=0.1, relheight=0.05, relwidth=0.92)

        self.botao_minhasencomendas = CTkButton(self.frame_menu, command=self.minhasencomendas)
        self.botao_minhasencomendas.configure(text='Minhas Encomendas',
                                      font=('Helvetica', 15, 'bold'),
                                      corner_radius=12,
                                      border_width=0,
                                      fg_color=paleta_cores['claro'])
        self.botao_minhasencomendas.place(relx=0.035, rely=0.2, relheight=0.05, relwidth=0.92)

        self.botao_cadastrarencomenda = CTkButton(self.frame_menu, command=self.cadastrarencomenda)
        self.botao_cadastrarencomenda.configure(text='Cadastrar Encomendas',
                                              font=('Helvetica', 15, 'bold'),
                                              corner_radius=12,
                                              border_width=0,
                                              fg_color=paleta_cores['claro'])
        self.botao_cadastrarencomenda.place(relx=0.035, rely=0.3, relheight=0.05, relwidth=0.92)


    def acao_botao_menu(self): #carrega a tela para pesquisar a encomenda
        self.limpar_frames(self.frame_principal)
        self.texto_busca = Label(self.frame_principal)
        self.texto_busca.configure(text='Digite o código de rastreio',
                                   font=('Helvetica', 30, 'bold'),
                                   bg=paleta_cores['escuro'],
                                   fg='white')
        self.texto_busca.place(rely=0.3, relx=0.30)

        self.codigo_rastreio = CTkEntry(self.frame_principal,
                                        placeholder_text='Insira o Código de Rastreio',
                                        font=('Helvetica', 14))
        self.codigo_rastreio.place(rely=0.40, relx=0.30, relwidth=0.435, relheight=0.05)

        self.botao_rastreio = CTkButton(self.frame_principal, command=lambda: self.tarefa(self.retorno_rastreamento))
        self.botao_rastreio.configure(text='Rastrear',
                                      font=('Helvetica', 12, 'bold'),
                                      fg_color=paleta_cores['claro'])
        self.botao_rastreio.place(rely=0.50, relx=0.355, relwidth=0.15, relheight=0.07)

        self.botao_limpar_codigo = CTkButton(self.frame_principal,
                                             command=lambda: self.codigo_rastreio.delete(0, 'end'))
        self.botao_limpar_codigo.configure(text='Limpar',
                                      font=('Helvetica', 12, 'bold'),
                                      fg_color=paleta_cores['claro'])
        self.botao_limpar_codigo.place(rely=0.50, relx=0.525, relwidth=0.15, relheight=0.07)

    def limpar_frames(self, frame):
        for item in frame.winfo_children():
            item.destroy()

    def retorno_rastreamento(self):
        rastreio = str(self.codigo_rastreio.get())
        rastreio.upper()

        self.habilita_desabilita_menu(False) # Desabilita o menu

        if rastreio != '':
            objeto = Correios(rastreio)
            resultado = objeto.ultimoevento()

            self.data_evento = Label(self.frame_principal)
            self.status = Label(self.frame_principal)
            self.substatus = Label(self.frame_principal)
            self.substatus2 = Label(self.frame_principal)

            self.data_evento.configure(text=('Ultíma Atualização:' + str(resultado['data']) + ' às ' + str(resultado['hora'])),
                                       font=('Helvetica', 12, 'bold'),
                                       background=paleta_cores['escuro'],
                                       fg='white')
            self.data_evento.place(relx=0.365, rely=0.6, relheight=0.15, relwidth=0.3)

            self.status.configure(
                text=('Status: ' + str(resultado['status'])),
                font=('Helvetica', 12, 'bold'),
                background=paleta_cores['escuro'],
                fg='white')
            self.status.place(relx=0.365, rely=0.69, relheight=0.05, relwidth=0.3)

            self.substatus.configure(
                text=(str(resultado['subStatus'][0])),
                font=('Helvetica', 12, 'bold'),
                background=paleta_cores['escuro'],
                fg='white')
            self.substatus.place(relx=0.295, rely=0.73, relheight=0.05, relwidth=0.45)

            self.substatus2.configure(
                text=(str(resultado['subStatus'][1])),
                font=('Helvetica', 12, 'bold'),
                background=paleta_cores['escuro'],
                fg='white')
            self.substatus2.place(relx=0.295, rely=0.77, relheight=0.05, relwidth=0.45)

            self.habilita_desabilita_menu(True) # Habilita o Menu novamente

        return

    def tarefa(self, func):
        self.thread = threading.Thread(target=func)
        self.thread.start()

    def cadastrarencomenda(self):
        self.limpar_frames(self.frame_principal)
        self.texto_cadastro = CTkLabel(self.frame_principal,
                                       text='Cadastrar Encomenda',
                                       font=('Helvetica', 30, 'bold'),
                                       text_color='white')
        self.texto_cadastro.place(relx=0.36, rely=0.1)

        self.nome_encomenda = CTkLabel(self.frame_principal,
                                       text='Nome do Produto',
                                       font=('Helvetica', 20, 'bold'),
                                       text_color='white')
        self.nome_encomenda.place(relx=0.32, rely=0.20)

        self.entry_nome_encomenda = CTkEntry(self.frame_principal,
                                             placeholder_text='Insira o nome do produto',
                                             font=('Helvetica', 14))
        self.entry_nome_encomenda.place(relx=0.32, rely=0.25, relwidth=0.35)

        self.texto_codigorastreio = CTkLabel(self.frame_principal,
                                       text='Código de Rastreio',
                                       font=('Helvetica', 20, 'bold'),
                                       text_color='white')
        self.texto_codigorastreio.place(relx=0.32, rely=0.30)

        self.entry_codigorastreio = CTkEntry(self.frame_principal,
                                             placeholder_text='Insira o código de rastreio',
                                             font=('Helvetica', 14))
        self.entry_codigorastreio.place(relx=0.32, rely=0.35, relwidth=0.35)

        self.botaocadastroencomenda = CTkButton(self.frame_principal,
                                                command=self.cadastrodeencomendas)
        self.botaocadastroencomenda.configure(text='Cadastrar',
                                      font=('Helvetica', 12, 'bold'),
                                      fg_color=paleta_cores['claro'])
        self.botaocadastroencomenda.place(rely=0.45, relx=0.335, relwidth=0.15, relheight=0.07)

        self.botaolimparform = CTkButton(self.frame_principal, command=self.limpar_formulario)
        self.botaolimparform.configure(text='Limpar',
                                              font=('Helvetica', 12, 'bold'),
                                              fg_color=paleta_cores['claro'])
        self.botaolimparform.place(rely=0.45, relx=0.50, relwidth=0.15, relheight=0.07)

    def minhasencomendas(self):
        self.limpar_frames(self.frame_principal)

        self.texto_minhasencomendas = CTkLabel(self.frame_principal,
                                               text='Carregando...',
                                               font=('Helvetica', 30, 'bold'),
                                               text_color='white')
        self.texto_minhasencomendas.place(relx=0.36, rely=0.1)

        self.tarefa(self.atualizar_dados_encomenda)
        #self.dados_db = self.conexao_db.extrair_tudo()

    def limpar_formulario(self):
        self.entry_nome_encomenda.delete(0, 'end')
        self.entry_codigorastreio.delete(0, 'end')

    def cadastrodeencomendas(self):
        self.info_cadastro = None

        if (len(self.entry_nome_encomenda.get()) <= 20) and (len(self.entry_codigorastreio.get()) == 13):
            if len(self.conexao_db.cadastroexistente(self.entry_codigorastreio.get())) == 0:
                self.conexao_db.inserirencomenda(self.entry_nome_encomenda.get(), self.entry_codigorastreio.get())
                self.info_cadastro = Label(self.frame_principal,
                                           text='Cadastro realizado com sucesso!',
                                           fg='#57df09',
                                           font=('Helvetica', 14),
                                           background=paleta_cores['escuro'])
                self.info_cadastro.place(relx=0.37, rely=0.55)
            else:
                self.info_cadastro = Label(self.frame_principal,
                                           text='Cadastro já existente!',
                                           fg='#d3470d',
                                           font=('Helvetica', 14),
                                           background=paleta_cores['escuro'])
                self.info_cadastro.place(relx=0.37, rely=0.55)

        else:
            self.info_cadastro = Label(self.frame_principal,
                                       text='Cadastro não realizado, código ou nome invalidos',
                                       fg='#d3470d',
                                       font=('Helvetica', 14),
                                       background=paleta_cores['escuro'])
            self.info_cadastro.place(relx=0.31, rely=0.55)

    def atualizar_dados_encomenda(self):

        self.habilita_desabilita_menu(False)  # desabilita o menu
        self.consulta = self.conexao_db.extrair_tudo()
        for dado_extraido in self.consulta:
            obj = Correios(dado_extraido[1])
            evento = obj.ultimoevento()
            if evento is not False:
                print(evento['status'])
                self.conexao_db.atualizar_dado_encomenda(evento['status'], dado_extraido[1])

        self.consulta = self.conexao_db.extrair_tudo()

        self.texto_minhasencomendas = CTkLabel(self.frame_principal,
                                               text='Minhas Encomendas',
                                               font=('Helvetica', 30, 'bold'),
                                               text_color='white')
        self.texto_minhasencomendas.place(relx=0.36, rely=0.1)

        self.arvore_visualizacao = ttk.Treeview(self.frame_principal, columns=("nome", "codigo", "ultimaatualizacao"),
                                                selectmode='browse',
                                                show='headings')

        self.arvore_visualizacao.column('nome', width=200, minwidth=10, stretch=NO)
        self.arvore_visualizacao.heading('nome', text='Nome')
        self.arvore_visualizacao.column('codigo', width=200, minwidth=10, stretch=NO)
        self.arvore_visualizacao.heading('codigo', text='Código')
        self.arvore_visualizacao.column('ultimaatualizacao', width=300, minwidth=10, stretch=NO)
        self.arvore_visualizacao.heading('ultimaatualizacao', text='Última Atualização')

        self.arvore_visualizacao.place(relx=0.20, rely=0.18, relheight=0.6, relwidth=0.605)

        for (descricao, codigo, ultinfo) in self.consulta:
            self.arvore_visualizacao.insert("", END, values=(descricao, codigo, ultinfo))

        self.botao_verdetalhes = CTkButton(self.frame_principal)
        self.botao_verdetalhes.configure(text='Ver Detalhes', command=lambda: self.tarefa(self.ver_detalhes),
                                              font=('Helvetica', 12, 'bold'),
                                              fg_color=paleta_cores['claro'])
        self.botao_verdetalhes.place(rely=0.8, relx=0.42, relwidth=0.15, relheight=0.07)

        self.habilita_desabilita_menu(True)  # habilita o menu

        return

    def ver_detalhes(self):
        item = self.arvore_visualizacao.focus()
        dados_tabela = self.arvore_visualizacao.item(item)

        self.limpar_frames(self.frame_principal)

        self.habilita_desabilita_menu(False) #desabilita o menu

        self.texto_minhasencomendas = CTkLabel(self.frame_principal,
                                               text='Carregando...',
                                               font=('Helvetica', 30, 'bold'),
                                               text_color='white')
        self.texto_minhasencomendas.place(relx=0.36, rely=0.1)

        ver_dados = Correios(dados_tabela['values'][1])
        lista_eventos = ver_dados.todoseventos()
        pos_relativa = [0.15, 0.3]
        self.texto_minhasencomendas.configure(text=dados_tabela['values'][1])
        for evento in lista_eventos:
            try:
                label = CTkLabel(self.frame_principal,
                                   text=f'{evento["data"]} às {evento["hora"]}',
                                   font=('Helvetica', 14, 'bold'),
                                   text_color='white')
                label2 = CTkLabel(self.frame_principal,
                                   text=f'{evento["subStatus"][0]}',
                                   font=('Helvetica', 14, 'bold'),
                                   text_color='white')

                label3 = CTkLabel(self.frame_principal,
                                  text=f'{evento["subStatus"][1]}',
                                  font=('Helvetica', 14, 'bold'),
                                  text_color='white')

                label.place(relx=pos_relativa[0], rely=pos_relativa[1])
                label2.place(relx=pos_relativa[0], rely=pos_relativa[1]+0.04)
                label3.place(relx=pos_relativa[0], rely=pos_relativa[1] + 0.07)

                pos_relativa[1] += 0.12
            except:
                pass

            self.habilita_desabilita_menu(True)  # habilita o menu

        return

    def habilita_desabilita_menu(self, hab_ou_desab):
        if hab_ou_desab: # habilita os botões
            self.botao_rastrear.configure(state='normal')
            self.botao_minhasencomendas.configure(state='normal')
            self.botao_cadastrarencomenda.configure(state='normal')
        else: #desabilita os botões
            self.botao_rastrear.configure(state='disabled')
            self.botao_minhasencomendas.configure(state='disabled')
            self.botao_cadastrarencomenda.configure(state='disabled')

App()

#teste = Correios('QQ361354787BR')
#print(teste.ultimoevento())
