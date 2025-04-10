#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que contém a interface de compressão de arquivos
"""

import os
import queue
import tkinter as tk
from threading import Thread
from tkinter import filedialog, messagebox, ttk

from utils.compressor import Compressor


class TelaComprimir(ttk.Frame):
    """
    Tela para compressão de arquivos
    """

    def __init__(self, parent, controller):
        """
        Inicializa a tela de compressão

        Args:
            parent: Widget pai
            controller: Controlador da aplicação
        """
        super().__init__(parent)
        self.controller = controller

        # Inicializa o compressor
        self.compressor = Compressor()

        # Fila para comunicação com threads
        self.queue = queue.Queue()

        # Lista de arquivos selecionados para compressão
        self.arquivos_selecionados = []

        # Dicionário para armazenar as tarefas de compressão
        self.tarefas_compressao = {}

        # Variáveis de controle
        self.compressao_em_andamento = False
        self.diretorio_saida = os.path.join(
            os.path.expanduser("~"), "Downloads", "comprimidos"
        )

        # Verifica se o diretório padrão existe, se não, cria
        if not os.path.exists(self.diretorio_saida):
            os.makedirs(self.diretorio_saida)

        # Configuração da interface
        self.criar_interface()

    def criar_interface(self):
        """
        Cria a interface da tela de compressão
        """
        # Título da seção
        titulo = ttk.Label(
            self, text="Compressão de Arquivos", font=("Helvetica", 14, "bold")
        )
        titulo.pack(pady=(10, 20))

        # Frame para os controles principais
        frame_controles = ttk.Frame(self)
        frame_controles.pack(fill="x", padx=20, pady=5)

        # --- Seção 1: Seleção de arquivos de entrada ---
        frame_entrada = ttk.LabelFrame(frame_controles, text="Entrada")
        frame_entrada.pack(fill="x", pady=5)

        # Frame para botão e exibição de arquivos selecionados
        frame_selecao = ttk.Frame(frame_entrada)
        frame_selecao.pack(fill="x", padx=10, pady=5)

        # Botão para selecionar arquivos
        self.btn_selecionar = ttk.Button(
            frame_selecao, text="Selecionar Arquivos", command=self.selecionar_arquivos
        )
        self.btn_selecionar.pack(side="left", padx=5)

        # Contador de arquivos selecionados
        self.lbl_arquivos_selecionados = ttk.Label(
            frame_selecao, text="Nenhum arquivo selecionado"
        )
        self.lbl_arquivos_selecionados.pack(side="left", padx=10)

        # --- Seção 2: Nível de compressão ---
        frame_nivel = ttk.LabelFrame(frame_controles, text="Nível de Compressão")
        frame_nivel.pack(fill="x", pady=5)

        # Frame para os controles de nível
        frame_nivel_controles = ttk.Frame(frame_nivel)
        frame_nivel_controles.pack(fill="x", padx=10, pady=5)

        # Rótulo para nível de compressão
        ttk.Label(frame_nivel_controles, text="Nível:").pack(side="left", padx=5)

        # Variável para armazenar o nível de compressão
        self.nivel_compressao = tk.StringVar(value="médio")

        # Combobox para seleção do nível
        self.combo_nivel = ttk.Combobox(
            frame_nivel_controles,
            textvariable=self.nivel_compressao,
            values=["baixo", "médio", "alto", "máximo"],
            width=15,
            state="readonly",
        )
        self.combo_nivel.pack(side="left", padx=5)

        # Informação sobre tempo
        ttk.Label(
            frame_nivel_controles, text="(quanto maior o nível, mais tempo demora)"
        ).pack(side="left", padx=5)

        # --- Seção 3: Diretório de saída ---
        frame_saida = ttk.LabelFrame(frame_controles, text="Saída")
        frame_saida.pack(fill="x", pady=5)

        # Frame para controles de saída
        frame_saida_controles = ttk.Frame(frame_saida)
        frame_saida_controles.pack(fill="x", padx=10, pady=5)

        # Variável para armazenar o caminho de saída
        self.var_caminho_saida = tk.StringVar(value=self.diretorio_saida)

        # Entrada de texto para o caminho
        self.entrada_saida = ttk.Entry(
            frame_saida_controles, textvariable=self.var_caminho_saida, width=50
        )
        self.entrada_saida.pack(side="left", padx=5, fill="x", expand=True)

        # Botão para selecionar diretório
        self.btn_selecionar_saida = ttk.Button(
            frame_saida_controles,
            text="Selecionar",
            command=self.selecionar_diretorio_saida,
        )
        self.btn_selecionar_saida.pack(side="right", padx=5)

        # --- Seção 4: Área de progresso ---
        frame_progresso = ttk.LabelFrame(self, text="Progresso")
        frame_progresso.pack(fill="both", expand=True, padx=20, pady=5)

        # Frame para lista de arquivos e barras de progresso
        self.frame_lista_arquivos = ttk.Frame(frame_progresso)
        self.frame_lista_arquivos.pack(fill="both", expand=True, padx=10, pady=5)

        # Canvas e scrollbar para a lista de arquivos
        self.canvas_arquivos = tk.Canvas(self.frame_lista_arquivos)
        self.scrollbar = ttk.Scrollbar(
            self.frame_lista_arquivos,
            orient="vertical",
            command=self.canvas_arquivos.yview,
        )
        self.scrollable_frame = ttk.Frame(self.canvas_arquivos)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas_arquivos.configure(
                scrollregion=self.canvas_arquivos.bbox("all")
            ),
        )

        self.canvas_arquivos.create_window(
            (0, 0), window=self.scrollable_frame, anchor="nw"
        )
        self.canvas_arquivos.configure(yscrollcommand=self.scrollbar.set)

        self.canvas_arquivos.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        # --- Seção 5: Botões de ação ---
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=10)

        # Botão para iniciar a compressão
        self.btn_comprimir = ttk.Button(
            frame_botoes,
            text="Comprimir",
            command=self.iniciar_compressao,
            state="disabled",
        )
        self.btn_comprimir.pack(side="left", padx=5)

        # Botão para voltar
        self.btn_voltar = ttk.Button(
            frame_botoes, text="Voltar", command=self.controller.mostrar_tela_inicial
        )
        self.btn_voltar.pack(side="right", padx=5)

        # Inicia o verificador de fila
        self.verificar_fila()

    def selecionar_arquivos(self):
        """
        Abre diálogo para seleção de arquivos
        """
        # Se houver compressão em andamento, não permite seleção
        if self.compressao_em_andamento:
            messagebox.showwarning(
                "Atenção", "Não é possível selecionar arquivos durante a compressão."
            )
            return

        # Diálogo para seleção de arquivos
        arquivos = filedialog.askopenfilenames(
            title="Selecionar Arquivos",
            filetypes=[
                ("Todos os arquivos", "*.*"),
                ("Arquivos de Imagem", "*.jpg *.jpeg *.png *.gif *.bmp"),
                ("Arquivos de Vídeo", "*.mp4 *.avi *.mkv *.mov"),
                ("Arquivos de Áudio", "*.mp3 *.wav *.ogg *.flac"),
                ("Documentos", "*.pdf *.doc *.docx *.txt"),
                ("Arquivos ZIP", "*.zip"),
                ("Arquivos RAR", "*.rar"),
            ],
        )

        if not arquivos:
            return

        # Limpa a lista atual
        self.arquivos_selecionados = []

        # Adiciona os novos arquivos
        for arquivo in arquivos:
            self.arquivos_selecionados.append(arquivo)

        # Atualiza a interface
        self.atualizar_lista_arquivos()

        # Atualiza o contador de arquivos
        self.lbl_arquivos_selecionados.config(
            text=f"{len(self.arquivos_selecionados)} arquivo(s) selecionado(s)"
        )

        # Habilita o botão de compressão se houver arquivos
        if self.arquivos_selecionados:
            self.btn_comprimir.config(state="normal")
        else:
            self.btn_comprimir.config(state="disabled")

    def atualizar_lista_arquivos(self):
        """
        Atualiza a lista de arquivos e barras de progresso na interface
        """
        # Limpa a lista atual
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Adiciona os arquivos à lista
        for idx, arquivo in enumerate(self.arquivos_selecionados):
            # Frame para cada arquivo
            frame_arquivo = ttk.Frame(self.scrollable_frame)
            frame_arquivo.pack(fill="x", padx=5, pady=2)

            # Nome do arquivo (somente o nome do arquivo, não o caminho completo)
            nome_arquivo = os.path.basename(arquivo)
            lbl_nome = ttk.Label(frame_arquivo, text=nome_arquivo, width=30, anchor="w")
            lbl_nome.pack(side="left", padx=5)

            # Barra de progresso
            progresso = ttk.Progressbar(frame_arquivo, length=400, mode="determinate")
            progresso.pack(side="left", padx=5, fill="x", expand=True)

            # Botão de cancelamento (inicialmente desabilitado)
            btn_cancelar = ttk.Button(
                frame_arquivo,
                text="X",
                width=2,
                command=lambda idx=idx: self.cancelar_compressao(idx),
                state="disabled",
            )
            btn_cancelar.pack(side="right", padx=5)

            # Rótulo de status
            lbl_status = ttk.Label(frame_arquivo, text="Aguardando", width=15)
            lbl_status.pack(side="right", padx=5)

            # Guarda referências para atualização posterior
            self.tarefas_compressao[idx] = {
                "arquivo": arquivo,
                "progresso": progresso,
                "status": lbl_status,
                "botao_cancelar": btn_cancelar,
                "cancelado": False,
            }

    def selecionar_diretorio_saida(self):
        """
        Abre diálogo para seleção do diretório de saída
        """
        # Se houver compressão em andamento, não permite seleção
        if self.compressao_em_andamento:
            messagebox.showwarning(
                "Atenção", "Não é possível alterar o diretório durante a compressão."
            )
            return

        # Diálogo para seleção de diretório
        diretorio = filedialog.askdirectory(
            title="Selecionar Diretório de Saída", initialdir=self.diretorio_saida
        )

        if diretorio:
            self.diretorio_saida = diretorio
            self.var_caminho_saida.set(diretorio)

    def iniciar_compressao(self):
        """
        Inicia o processo de compressão dos arquivos
        """
        # Verifica se há arquivos selecionados
        if not self.arquivos_selecionados:
            messagebox.showwarning(
                "Atenção", "Selecione pelo menos um arquivo para comprimir."
            )
            return

        # Verifica se o diretório de saída existe
        if not os.path.exists(self.diretorio_saida):
            try:
                os.makedirs(self.diretorio_saida)
            except Exception as e:
                messagebox.showerror(
                    "Erro", f"Não foi possível criar o diretório de saída: {str(e)}"
                )
                return

        # Altera o estado da interface para compressão em andamento
        self.compressao_em_andamento = True
        self.btn_comprimir.config(text="Parar", command=self.parar_compressao)
        self.btn_selecionar.config(state="disabled")
        self.btn_selecionar_saida.config(state="disabled")
        self.combo_nivel.config(state="disabled")

        # Habilita os botões de cancelamento individuais
        for tarefa in self.tarefas_compressao.values():
            tarefa["botao_cancelar"].config(state="normal")
            tarefa["status"].config(text="Na fila")

        # Obtém o nível de compressão selecionado
        nivel = self.nivel_compressao.get()

        # Inicia as threads de compressão
        for idx, tarefa in self.tarefas_compressao.items():
            if not tarefa["cancelado"]:
                thread = Thread(
                    target=self.executar_compressao,
                    args=(idx, tarefa["arquivo"], nivel),
                    daemon=True,
                )
                thread.start()

    def executar_compressao(self, idx, arquivo, nivel):
        """
        Executa a compressão de um arquivo em uma thread separada

        Args:
            idx (int): Índice do arquivo na lista
            arquivo (str): Caminho completo do arquivo
            nivel (str): Nível de compressão selecionado
        """
        try:
            # Atualiza o status
            self.queue.put(("status", idx, "Comprimindo"))

            # Nome do arquivo de saída
            nome_arquivo = os.path.basename(arquivo)
            nome_base, extensao = os.path.splitext(nome_arquivo)
            arquivo_saida = os.path.join(
                self.diretorio_saida, f"{nome_base}_comprimido{extensao}"
            )

            # Callback para atualização do progresso
            def atualizar_progresso(progresso):
                self.queue.put(("progresso", idx, progresso))

            # Executa a compressão
            resultado = self.compressor.comprimir_arquivo(
                arquivo, arquivo_saida, nivel, atualizar_progresso
            )

            # Verifica se foi cancelado durante a execução
            if self.tarefas_compressao[idx]["cancelado"]:
                self.queue.put(("status", idx, "Cancelado"))
                # Remove o arquivo parcialmente comprimido
                if os.path.exists(arquivo_saida):
                    os.remove(arquivo_saida)
            else:
                self.queue.put(("status", idx, "Concluído"))
                self.queue.put(("progresso", idx, 100))

        except Exception as e:
            self.queue.put(("status", idx, "Erro"))
            self.queue.put(("erro", idx, str(e)))

    def cancelar_compressao(self, idx):
        """
        Cancela a compressão de um arquivo específico

        Args:
            idx (int): Índice do arquivo na lista
        """
        # Marca como cancelado
        self.tarefas_compressao[idx]["cancelado"] = True
        self.tarefas_compressao[idx]["status"].config(text="Cancelando...")
        self.tarefas_compressao[idx]["botao_cancelar"].config(state="disabled")

    def parar_compressao(self):
        """
        Para todos os processos de compressão em andamento
        """
        # Cancela todas as tarefas
        for idx, tarefa in self.tarefas_compressao.items():
            if tarefa["status"].cget("text") in ["Na fila", "Comprimindo"]:
                tarefa["cancelado"] = True
                tarefa["status"].config(text="Cancelando...")
                tarefa["botao_cancelar"].config(state="disabled")

        # Restaura o botão para o estado inicial
        self.btn_comprimir.config(text="Comprimir", command=self.iniciar_compressao)

        # Restaura o estado da interface
        self.compressao_em_andamento = False
        self.btn_selecionar.config(state="normal")
        self.btn_selecionar_saida.config(state="normal")
        self.combo_nivel.config(state="readonly")

    def verificar_fila(self):
        """
        Verifica a fila de mensagens das threads e atualiza a interface
        """
        try:
            # Verifica se todas as tarefas estão concluídas ou canceladas
            todas_concluidas = True

            for idx, tarefa in self.tarefas_compressao.items():
                status = tarefa["status"].cget("text")
                if status in ["Na fila", "Comprimindo", "Cancelando..."]:
                    todas_concluidas = False
                    break

            # Se todas estiverem concluídas, restaura a interface
            if self.compressao_em_andamento and todas_concluidas:
                self.compressao_em_andamento = False
                self.btn_comprimir.config(
                    text="Comprimir", command=self.iniciar_compressao
                )
                self.btn_selecionar.config(state="normal")
                self.btn_selecionar_saida.config(state="normal")
                self.combo_nivel.config(state="readonly")

            # Processa as mensagens na fila
            while not self.queue.empty():
                tipo, idx, valor = self.queue.get()

                if tipo == "progresso":
                    # Atualiza a barra de progresso
                    self.tarefas_compressao[idx]["progresso"]["value"] = valor

                elif tipo == "status":
                    # Atualiza o status
                    self.tarefas_compressao[idx]["status"].config(text=valor)

                    # Se foi concluído ou cancelado, desabilita o botão de cancelamento
                    if valor in ["Concluído", "Cancelado", "Erro"]:
                        self.tarefas_compressao[idx]["botao_cancelar"].config(
                            state="disabled"
                        )

                elif tipo == "erro":
                    # Exibe mensagem de erro
                    messagebox.showerror(
                        "Erro de Compressão",
                        f"Erro ao comprimir {os.path.basename(self.tarefas_compressao[idx]['arquivo'])}: {valor}",
                    )

        except Exception as e:
            print(f"Erro ao processar fila: {str(e)}")

        # Agenda a próxima verificação
        self.after(100, self.verificar_fila)
