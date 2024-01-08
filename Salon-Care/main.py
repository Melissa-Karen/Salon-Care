from tkinter import *
import tkinter as tk
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import defaultdict

dict_titulo = {
    'controle': 'Controle',
    'de': ' de ',
    'atendimentos': 'Atendimentos'
}

titulo = ''

tamanho = len(dict_titulo)
cont = 0

while cont < tamanho:
    titulo += dict_titulo['controle']
    titulo += dict_titulo['de']
    titulo += dict_titulo['atendimentos']
    cont = 3

class App:
    def __init__(self):
        # Conectar ao banco de dados SQLite
        self.conexao = sqlite3.connect('salao.db')

        self.janela = tk.Tk()
        self.janela.title("Controle de atendimento de Salão")
        self.janela.geometry('800x500')
        self.janela.resizable(width=False, height=False)
        self.janela.configure(bg='white')

        # Criar a tabela "agenda" no banco de dados
        cursor = self.conexao.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS agenda (dia TEXT, hora TEXT)")
        self.conexao.commit()


        # CABEÇALHO
        self.frameCabecalho = tk.Frame(self.janela)
        self.labelCabecalho = tk.Label(self.frameCabecalho, text=f"{titulo}", bg='#CB275C', fg='white',
                                       font='Helvetica 18', padx='10', pady='15')
        self.labelCabecalho.pack(fill="x", expand=True)
        self.frameCabecalho.pack(side="top", fill="both", expand=False)

        # CORPO - LOGO
        self.frameCorpo = tk.Frame(self.janela, width=800, height=600) 
        self.frameCorpo.pack_propagate(False)
        self.imagem = PhotoImage(file='logo.png')
        self.imagem_reduzida = self.imagem.subsample(4)
        self.labelImagem = tk.Label(self.frameCorpo, image=self.imagem_reduzida)
        self.labelImagem.image = self.imagem_reduzida
        self.labelImagem.place(x=20, y=30)

        # CORPO - BOTÕES
        self.botao1 = tk.Button(self.frameCorpo, text="Adcionar agendamento", width=25, height=2, bg='#CB275C', fg='white', font='Heveltica 12', command=self.mostrar_frame_inclusao)
        self.botao2 = tk.Button(self.frameCorpo, text="Consultar horários", width=25, height=2, bg='#CB275C', fg='white', font='Heveltica 12', command=self.mostrar_frame_listar)
        self.botao3 = tk.Button(self.frameCorpo, text="Excluir horário agendado", width=25, height=2, bg='#CB275C', fg='white', font='Heveltica 12', command=self.mostrar_frame_excluir)
        self.botao4 = tk.Button(self.frameCorpo, text="Estatistícas", width=25, height=2, bg='#CB275C', fg='white', font='Heveltica 12',command=self.mostrar_frame_estatistica)
        

        self.botao1.place(x=450, y=50)
        self.botao2.place(x=450, y=150)
        self.botao3.place(x=450, y=250)
        self.botao4.place(x=450,y=350)

        self.frameCorpo.pack(side="top", fill="both", expand=True)


        # FRAME DE AGENDAR HORÁRIO
        self.frameInclusao = tk.Frame(self.janela, bg='#7897ab')
        self.label_frame_inclusao = tk.Label(self.frameInclusao, text="Adcionar horário na agenda", font='Helvetica 16', padx='10', pady='15',bg='#7897ab', fg='white')
        self.label_frame_inclusao.pack()

        self.botao_agendar_horario = tk.Button(self.frameInclusao, text="Agendar Horário", font='Helvetica 14', bg='#CB275C', fg='white',command=self.incluir_horario)
        self.botao_voltar_inclusao = tk.Button(self.frameInclusao, text="Voltar", command=self.mostrar_frame_corpo, font='Heveltica 10', bg='#CB275C',fg='white')
        self.botao_agendar_horario.place(x=330, y=350)
        self.botao_voltar_inclusao.place(x=50,y=50)

        # Campos para que o usuário agende um horário
        self.label_dia = tk.Label(self.frameInclusao, text="Dia[dd/mm/aa]:", font='Helvetica 20', bg='#7897AB', fg='white')
        self.label_hora = tk.Label(self.frameInclusao, text="Hora:", font='Helvetica 20', bg='#7897AB', fg='white')

        self.entry_dia = tk.Entry(self.frameInclusao, font='Helvetica 20')
        self.entry_hora = tk.Entry(self.frameInclusao, font='Helvetica 20')

        self.label_dia.place(x=180, y=100)
        self.label_hora.place(x=250, y=200)
        self.entry_dia.place(x=390, y=100)
        self.entry_hora.place(x=350, y=200)

       # FRAME DE LISTAR HORÁRIOS
        self.frameListar = tk.Frame(self.janela, bg='#7897ab')
        self.label_frame_listar = tk.Label(self.frameListar, text="Horários ocupados na agenda", font='Helvetica 16', padx='10', pady='15',bg='#7897ab', fg='white')
        self.label_frame_listar.pack()

        self.botao_voltar_listar = tk.Button(self.frameListar, text="Voltar", command=self.mostrar_frame_corpo, font='Heveltica 10', bg='#CB275C',fg='white')
        self.botao_voltar_listar.place(x=50,y=50)

        # Adiciona uma listabox para mostrar os agendamentos
        self.lista_agendamentos = Listbox(self.frameListar, font='Helvetica 12', width=50, height=10, bg='#7897ab', fg='white')
        self.lista_agendamentos.place(x=200, y=150)
        self.atualizar_lista_agendamentos()

        # FRAME DE EXCLUIR HORÁRIO
        self.frameExcluir = tk.Frame(self.janela, bg='#7897ab')
        self.label_frame_excluir = tk.Label(self.frameExcluir, text="Excluir horário agendado", font='Helvetica 16', padx='10', pady='15',bg='#7897ab', fg='white')
        self.label_frame_excluir.pack()

        self.botao_voltar_excluir = tk.Button(self.frameExcluir, text="Voltar", command=self.mostrar_frame_corpo, font='Heveltica 10', bg='#CB275C',fg='white')
        self.botao_voltar_excluir.place(x=50,y=50)

        self.label_excluir_dia = tk.Label(self.frameExcluir, text="Dia[dd/mm/aa]:", font='Helvetica 20', bg='#7897AB', fg='white')
        self.label_excluir_hora = tk.Label(self.frameExcluir, text="Hora:", font='Helvetica 20', bg='#7897AB', fg='white')

        self.entry_excluir_dia = tk.Entry(self.frameExcluir, font='Helvetica 20')
        self.entry_excluir_hora = tk.Entry(self.frameExcluir, font='Helvetica 20')

        self.label_excluir_dia.place(x=180, y=100)
        self.label_excluir_hora.place(x=250, y=200)
        self.entry_excluir_dia.place(x=390, y=100)
        self.entry_excluir_hora.place(x=350, y=200)

        self.botao_excluir_horario = tk.Button(self.frameExcluir, text="Excluir Horário", font='Helvetica 14', bg='#CB275C', fg='white', command=self.excluir_horario)
        self.botao_excluir_horario.place(x=330, y=350)

        # FRAME DE ESTATÍSTICAS
        self.frameEstatisticas = tk.Frame(self.janela, bg='white')
        self.label_frame_estatisticas = tk.Label(self.frameEstatisticas, text="Estatísticas", font='Helvetica 16', padx='10', pady='15',bg='white', fg='#CB275C')
        self.label_frame_estatisticas.pack()

        self.botao_voltar_estatisticas = tk.Button(self.frameEstatisticas, text="Voltar", command=self.mostrar_frame_corpo, font='Heveltica 10', bg='#CB275C',fg='white')
        self.botao_voltar_estatisticas.place(x=50, y=50)

        self.botao_gerar_grafico = tk.Button(self.frameEstatisticas, text="Gerar Gráfico", font='Helvetica 14', bg='#CB275C', fg='white', command=self.mostrar_grafico)
        self.botao_gerar_grafico.place(x=330, y=350)

        self.frameEstatisticas.pack_forget()

        self.janela.mainloop()

    def atualizar_lista_agendamentos(self):
        self.lista_agendamentos.delete(0, END)
        cursor = self.conexao.cursor()
        cursor.execute("SELECT * FROM agenda")
        agendamentos = cursor.fetchall()
        for agendamento in agendamentos:
            self.lista_agendamentos.insert(END, f"Dia: {agendamento[0]} - Hora: {agendamento[1]}")

    def incluir_horario(self):
        dia = self.entry_dia.get()
        hora = self.entry_hora.get()
        if not dia or not hora:
            return

        cursor = self.conexao.cursor()
        cursor.execute("INSERT INTO agenda (dia, hora) VALUES (?, ?)", (dia, hora))
        self.conexao.commit()

        self.entry_dia.delete(0, END)
        self.entry_hora.delete(0, END)

        mensagem_sucesso = tk.Label(self.frameInclusao, text="Horário agendado com sucesso!", font='Helvetica 14', bg='green', fg='white')
        mensagem_sucesso.place(x=250, y=300)

    def excluir_horario(self):
        dia = self.entry_excluir_dia.get()
        hora = self.entry_excluir_hora.get()
        if not dia or not hora:
            return

        cursor = self.conexao.cursor()
        cursor.execute("DELETE FROM agenda WHERE dia=? AND hora=?", (dia, hora))
        self.conexao.commit()

        self.entry_excluir_dia.delete(0, END)
        self.entry_excluir_hora.delete(0, END)

        mensagem_sucesso = tk.Label(self.frameExcluir, text="Horário excluído com sucesso!", font='Helvetica 14', bg='green', fg='white')
        mensagem_sucesso.place(x=250, y=300)

        self.atualizar_lista_agendamentos()


    def mostrar_grafico(self):
        cursor = self.conexao.cursor()
        cursor.execute("SELECT dia, COUNT(*) AS total FROM agenda GROUP BY dia")
        dados = cursor.fetchall()

        dias = [dia for dia, _ in dados]
        total_agendamentos = [total for _, total in dados]

        self.janela.resizable(width=True, height=True)

        fig, ax = plt.subplots(figsize=(5, 4))
        ax.bar(dias, total_agendamentos, color='#CB275C')
        ax.set_xlabel('Data do Agendamento')
        ax.set_ylabel('Quantidade de Agendamentos')
        ax.set_title('Quantidade de Agendamentos por Dia')

        plt.xticks(rotation=15, ha='right')

        canvas = FigureCanvasTkAgg(fig, master=self.frameEstatisticas)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack()


    def mostrar_frame_corpo(self):
        self.frameInclusao.pack_forget()
        self.frameListar.pack_forget()
        self.frameExcluir.pack_forget()
        self.frameEstatisticas.pack_forget()
        self.frameCorpo.pack(side="top", fill="both", expand=True)
        

    def mostrar_frame_inclusao(self):
        self.frameCorpo.pack_forget()
        self.frameListar.pack_forget()
        self.frameExcluir.pack_forget()
        self.frameInclusao.pack(side="top", fill="both", expand=True)

    def mostrar_frame_listar(self):
        self.frameCorpo.pack_forget()
        self.frameInclusao.pack_forget()
        self.frameExcluir.pack_forget()
        self.frameListar.pack(side="top", fill="both", expand=True)
        self.atualizar_lista_agendamentos()

    def mostrar_frame_excluir(self):
        self.frameCorpo.pack_forget()
        self.frameInclusao.pack_forget()
        self.frameListar.pack_forget()
        self.frameExcluir.pack(side="top", fill="both", expand=True)

    def mostrar_frame_estatistica(self):
        self.frameCorpo.pack_forget()
        self.frameInclusao.pack_forget()
        self.frameListar.pack_forget()
        self.frameExcluir.pack_forget()
        self.frameEstatisticas.pack(side="top", fill="both", expand=True)

App()

