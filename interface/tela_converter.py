#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que contém a interface de conversão de arquivos
"""

import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from threading import Thread
import queue
from utils.conversor import Conversor

class TelaConverter(ttk.Frame):
    """
    Tela para conversão de arquivos
    """
    
    def __init__(self, parent, controller):
        """
        Inicializa a tela de conversão
        
        Args:
            parent: Widget pai
            controller: Controlador da aplicação
        """
        super().__init__(parent)
        self.controller = controller
        
        # Inicializa o conversor
        self.conversor = Conversor()
        
        # Fila para comunicação com threads
        self.queue = queue.Queue()
        
        # Lista de arquivos selecionados para conversão
        self.arquivos_selecionados = []
        
        # Dicionário para armazenar as tarefas de conversão
        self.tarefas_conversao = {}
        
        # Variáveis de controle
        self.conversao_em_andamento = False
        self.diretorio_saida = os.path.join(os.path.expanduser("~"), "Downloads", "convertidos")
        
        # Verifica se o diretório padrão existe, se não, cria
        if not os.path.exists(self.diretorio_saida):
            os.makedirs(self.diretorio_saida)
        
        # Formatos de conversão disponíveis por tipo
        self.formatos_conversao = {
            "áudio": ["mp3", "wav", "ogg", "flac", "aac"],
            "vídeo": ["mp4", "avi", "mkv", "mov", "webm"],
            "imagem": ["jpg", "png", "gif", "bmp", "webp"],
            "documento": ["pdf", "txt", "docx", "html"]
        }
        
        # Mapeamento de extensões para tipos
        self.extensao_para_tipo = {
            # Áudio
            ".mp3": "áudio", ".wav": "áudio", ".ogg": "áudio", ".flac": "áudio", ".aac": "áudio",
            # Vídeo
            ".mp4": "vídeo", ".avi": "vídeo", ".mkv": "vídeo", ".mov": "vídeo", ".webm": "vídeo",
            # Imagem
            ".jpg": "imagem", ".jpeg": "imagem", ".png": "imagem", ".gif": "imagem", 
            ".bmp": "imagem", ".webp": "imagem",
            # Documento
            ".pdf": "documento", ".txt": "documento", ".docx": "documento", 
            ".doc": "documento", ".html": "documento", ".htm": "documento"
        }
        
        # Configuração da interface
        self.criar_interface()
    
    def criar_interface(self):
        """
        Cria a interface da tela de conversão
        """
        # Título da seção
        titulo = ttk.Label(
            self, 
            text="Conversão de Arquivos", 
            font=("Helvetica", 14, "bold")
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
            frame_selecao,
            text="Selecionar Arquivos",
            command=self.selecionar_arquivos
        )
        self.btn_selecionar.pack(side="left", padx=5)
        
        # Contador de arquivos selecionados
        self.lbl_arquivos_selecionados = ttk.Label(
            frame_selecao, 
            text="Nenhum arquivo selecionado"
        )
        self.lbl_arquivos_selecionados.pack(side="left", padx=10)
        
        # --- Seção 2: Formato de conversão ---
        frame_formato = ttk.LabelFrame(frame_controles, text="Formato de Conversão")
        frame_formato.pack(fill="x", pady=5)
        
        # Frame para os controles de formato
        frame_formato_controles = ttk.Frame(frame_formato)
        frame_formato_controles.pack(fill="x", padx=10, pady=5)
        
        # Rótulo para formato de saída
        ttk.Label(frame_formato_controles, text="Converter para:").pack(side="left", padx=5)
        
        # Variável para armazenar o formato de saída
        self.formato_saida = tk.StringVar()
        
        # Combobox para seleção do formato
        self.combo_formato = ttk.Combobox(
            frame_formato_controles,
            textvariable=self.formato_saida,
            width=15,
            state="readonly"
        )
        self.combo_formato.pack(side="left", padx=5)
        
        # Opções avançadas
        self.var_opcoes_avancadas = tk.BooleanVar(value=False)
        self.check_opcoes_avancadas = ttk.Checkbutton(
            frame_formato_controles,
            text="Opções Avançadas",
            variable=self.var_opcoes_avancadas,
            command=self.mostrar_opcoes_avancadas
        )
        self.check_opcoes_avancadas.pack(side="left", padx=15)
        
        # --- Seção 3: Opções avançadas (inicialmente oculta) ---
        self.frame_opcoes_avancadas = ttk.Frame(frame_controles)
        
        # Para áudio
        self.frame_opcoes_audio = ttk.LabelFrame(self.frame_opcoes_avancadas, text="Opções de Áudio")
        
        # Taxa de bits
        frame_bitrate = ttk.Frame(self.frame_opcoes_audio)
        frame_bitrate.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_bitrate, text="Taxa de bits:").pack(side="left", padx=5)
        
        self.bitrate_audio = tk.StringVar(value="192k")
        self.combo_bitrate_audio = ttk.Combobox(
            frame_bitrate,
            textvariable=self.bitrate_audio,
            values=["64k", "128k", "192k", "256k", "320k"],
            width=10,
            state="readonly"
        )
        self.combo_bitrate_audio.pack(side="left", padx=5)
        
        # Canais
        frame_canais = ttk.Frame(self.frame_opcoes_audio)
        frame_canais.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_canais, text="Canais:").pack(side="left", padx=5)
        
        self.canais_audio = tk.StringVar(value="2")
        self.combo_canais_audio = ttk.Combobox(
            frame_canais,
            textvariable=self.canais_audio,
            values=["1", "2"],
            width=10,
            state="readonly"
        )
        self.combo_canais_audio.pack(side="left", padx=5)
        
        # Para vídeo
        self.frame_opcoes_video = ttk.LabelFrame(self.frame_opcoes_avancadas, text="Opções de Vídeo")
        
        # Resolução
        frame_resolucao = ttk.Frame(self.frame_opcoes_video)
        frame_resolucao.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_resolucao, text="Resolução:").pack(side="left", padx=5)
        
        self.resolucao_video = tk.StringVar(value="original")
        self.combo_resolucao_video = ttk.Combobox(
            frame_resolucao,
            textvariable=self.resolucao_video,
            values=["original", "720p", "1080p", "480p", "360p"],
            width=10,
            state="readonly"
        )
        self.combo_resolucao_video.pack(side="left", padx=5)
        
        # Taxa de quadros
        frame_fps = ttk.Frame(self.frame_opcoes_video)
        frame_fps.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_fps, text="FPS:").pack(side="left", padx=5)
        
        self.fps_video = tk.StringVar(value="original")
        self.combo_fps_video = ttk.Combobox(
            frame_fps,
            textvariable=self.fps_video,
            values=["original", "24", "30", "60"],
            width=10,
            state="readonly"
        )
        self.combo_fps_video.pack(side="left", padx=5)
        
        # Para imagem
        self.frame_opcoes_imagem = ttk.LabelFrame(self.frame_opcoes_avancadas, text="Opções de Imagem")
        
        # Qualidade
        frame_qualidade = ttk.Frame(self.frame_opcoes_imagem)
        frame_qualidade.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_qualidade, text="Qualidade:").pack(side="left", padx=5)
        
        self.qualidade_imagem = tk.StringVar(value="90")
        self.combo_qualidade_imagem = ttk.Combobox(
            frame_qualidade,
            textvariable=self.qualidade_imagem,
            values=["100", "90", "80", "70", "60", "50"],
            width=10,
            state="readonly"
        )
        self.combo_qualidade_imagem.pack(side="left", padx=5)
        
        # Redimensionar
        frame_redimensionar = ttk.Frame(self.frame_opcoes_imagem)
        frame_redimensionar.pack(fill="x", padx=10, pady=5)
        ttk.Label(frame_redimensionar, text="Redimensionar:").pack(side="left", padx=5)
        
        self.redimensionar_imagem = tk.StringVar(value="original")
        self.combo_redimensionar_imagem = ttk.Combobox(
            frame_redimensionar,
            textvariable=self.redimensionar_imagem,
            values=["original", "1920x1080", "1280x720", "800x600", "640x480"],
            width=10,
            state="readonly"
        )
        self.combo_redimensionar_imagem.pack(side="left", padx=5)
        
        # --- Seção 4: Diretório de saída ---
        frame_saida = ttk.LabelFrame(frame_controles, text="Saída")
        frame_saida.pack(fill="x", pady=5)
        
        # Frame para controles de saída
        frame_saida_controles = ttk.Frame(frame_saida)
        frame_saida_controles.pack(fill="x", padx=10, pady=5)
        
        # Variável para armazenar o caminho de saída
        self.var_caminho_saida = tk.StringVar(value=self.diretorio_saida)
        
        # Entrada de texto para o caminho
        self.entrada_saida = ttk.Entry(
            frame_saida_controles, 
            textvariable=self.var_caminho_saida,
            width=50
        )
        self.entrada_saida.pack(side="left", padx=5, fill="x", expand=True)
        
        # Botão para selecionar diretório
        self.btn_selecionar_saida = ttk.Button(
            frame_saida_controles,
            text="Selecionar",
            command=self.selecionar_diretorio_saida
        )
        self.btn_selecionar_saida.pack(side="right", padx=5)
        
        # --- Seção 5: Área de progresso ---
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
            command=self.canvas_arquivos.yview
        )
        self.scrollable_frame = ttk.Frame(self.canvas_arquivos)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas_arquivos.configure(
                scrollregion=self.canvas_arquivos.bbox("all")
            )
        )
        
        self.canvas_arquivos.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas_arquivos.configure(yscrollcommand=self.scrollbar.set)
        
        self.canvas_arquivos.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")
        
        # --- Seção 6: Botões de ação ---
        frame_botoes = ttk.Frame(self)
        frame_botoes.pack(fill="x", padx=20, pady=10)
        
        # Botão para iniciar a conversão
        self.btn_converter = ttk.Button(
            frame_botoes,
            text="Converter",
            command=self.iniciar_conversao,
            state="disabled"
        )
        self.btn_converter.pack(side="left", padx=5)
        
        # Botão para extrair áudio de vídeo
        self.btn_extrair_audio = ttk.Button(
            frame_botoes,
            text="Extrair Áudio",
            command=self.extrair_audio,
            state="disabled"
        )
        self.btn_extrair_audio.pack(side="left", padx=5)
        
        # Botão para voltar
        self.btn_voltar = ttk.Button(
            frame_botoes,
            text="Voltar",
            command=self.controller.mostrar_tela_inicial
        )
        self.btn_voltar.pack(side="right", padx=5)
        
        # Inicia o verificador de fila
        self.verificar_fila()
    
    def mostrar_opcoes_avancadas(self):
        """
        Mostra ou oculta as opções avançadas com base no estado do checkbox
        """
        if self.var_opcoes_avancadas.get():
            # Mostra as opções avançadas
            self.frame_opcoes_avancadas.pack(fill="x", padx=20, pady=5)
            
            # Mostra as opções específicas do tipo atualmente selecionado
            self.atualizar_opcoes_avancadas()
        else:
            # Oculta todas as opções avançadas
            self.frame_opcoes_avancadas.pack_forget()
            self.frame_opcoes_audio.pack_forget()
            self.frame_opcoes_video.pack_forget()
            self.frame_opcoes_imagem.pack_forget()
    
    def atualizar_opcoes_avancadas(self):
        """
        Atualiza as opções avançadas com base no formato selecionado
        """
        # Oculta todas as opções primeiro
        self.frame_opcoes_audio.pack_forget()
        self.frame_opcoes_video.pack_forget()
        self.frame_opcoes_imagem.pack_forget()
        
        # Se não há formato selecionado, não faz nada
        if not self.formato_saida.get():
            return
        
        # Determina o tipo do formato
        formato = self.formato_saida.get()
        tipo = None
        
        for tipo_formato, formatos in self.formatos_conversao.items():
            if formato in formatos:
                tipo = tipo_formato
                break
        
        # Mostra as opções correspondentes ao tipo
        if tipo == "áudio":
            self.frame_opcoes_audio.pack(fill="x", padx=10, pady=5)
        elif tipo == "vídeo":
            self.frame_opcoes_video.pack(fill="x", padx=10, pady=5)
        elif tipo == "imagem":
            self.frame_opcoes_imagem.pack(fill="x", padx=10, pady=5)
    
    def selecionar_arquivos(self):
        """
        Abre diálogo para seleção de arquivos
        """
        # Se houver conversão em andamento, não permite seleção
        if self.conversao_em_andamento:
            messagebox.showwarning(
                "Atenção", 
                "Não é possível selecionar arquivos durante a conversão."
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
                ("Documentos", "*.pdf *.doc *.docx *.txt")
            ]
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
        
        # Determina o tipo dos arquivos selecionados
        self.atualizar_formatos_disponiveis()
        
        # Habilita ou desabilita botões com base na seleção
        self.atualizar_estado_botoes()
    
    def atualizar_formatos_disponiveis(self):
        """
        Atualiza os formatos disponíveis com base nos arquivos selecionados
        """
        # Verifica se há arquivos selecionados
        if not self.arquivos_selecionados:
            self.combo_formato.set("")
            self.combo_formato["values"] = []
            return
        
        # Determina o tipo do primeiro arquivo
        _, extensao = os.path.splitext(self.arquivos_selecionados[0])
        extensao = extensao.lower()
        
        # Verifica se todos os arquivos são do mesmo tipo
        mesmo_tipo = True
        tipo_arquivo = self.extensao_para_tipo.get(extensao)
        
        if not tipo_arquivo:
            # Tipo de arquivo não reconhecido
            self.combo_formato.set("")
            self.combo_formato["values"] = []
            return
        
        for arquivo in self.arquivos_selecionados[1:]:
            _, ext = os.path.splitext(arquivo)
            ext = ext.lower()
            if self.extensao_para_tipo.get(ext) != tipo_arquivo:
                mesmo_tipo = False
                break
        
        if not mesmo_tipo:
            # Se os arquivos forem de tipos diferentes, limpa as opções
            messagebox.showwarning(
                "Atenção", 
                "Selecione apenas arquivos do mesmo tipo para conversão."
            )
            self.arquivos_selecionados = []
            self.lbl_arquivos_selecionados.config(text="Nenhum arquivo selecionado")
            self.combo_formato.set("")
            self.combo_formato["values"] = []
            self.atualizar_lista_arquivos()
            return
        
        # Atualiza os formatos disponíveis com base no tipo
        formatos = self.formatos_conversao.get(tipo_arquivo, [])
        self.combo_formato["values"] = formatos
        
        # Se houver formatos disponíveis, seleciona o primeiro
        if formatos:
            self.combo_formato.set(formatos[0])
            
            # Atualiza as opções avançadas
            if self.var_opcoes_avancadas.get():
                self.atualizar_opcoes_avancadas()
        else:
            self.combo_formato.set("")
    
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
                command=lambda idx=idx: self.cancelar_conversao(idx),
                state="disabled"
            )
            btn_cancelar.pack(side="right", padx=5)
            
            # Rótulo de status
            lbl_status = ttk.Label(frame_arquivo, text="Aguardando", width=15)
            lbl_status.pack(side="right", padx=5)
            
            # Guarda referências para atualização posterior
            self.tarefas_conversao[idx] = {
                "arquivo": arquivo,
                "progresso": progresso,
                "status": lbl_status,
                "botao_cancelar": btn_cancelar,
                "cancelado": False
            }
    
    def selecionar_diretorio_saida(self):
        """
        Abre diálogo para seleção do diretório de saída
        """
        # Se houver conversão em andamento, não permite seleção
        if self.conversao_em_andamento:
            messagebox.showwarning(
                "Atenção", 
                "Não é possível alterar o diretório durante a conversão."
            )
            return
        
        # Diálogo para seleção de diretório
        diretorio = filedialog.askdirectory(
            title="Selecionar Diretório de Saída",
            initialdir=self.diretorio_saida
        )
        
        if diretorio:
            self.diretorio_saida = diretorio
            self.var_caminho_saida.set(diretorio)
    
    def atualizar_estado_botoes(self):
        """
        Atualiza o estado dos botões com base na seleção atual
        """
        # Botão de conversão
        if self.arquivos_selecionados and self.formato_saida.get():
            self.btn_converter.config(state="normal")
        else:
            self.btn_converter.config(state="disabled")
        
        # Botão de extração de áudio
        tem_video = False
        for arquivo in self.arquivos_selecionados:
            _, extensao = os.path.splitext(arquivo)
            if self.extensao_para_tipo.get(extensao.lower()) == "vídeo":
                tem_video = True
                break
        
        if tem_video:
            self.btn_extrair_audio.config(state="normal")
        else:
            self.btn_extrair_audio.config(state="disabled")
    
    def iniciar_conversao(self):
        """
        Inicia o processo de conversão dos arquivos
        """
        # Verifica se há arquivos selecionados e formato definido
        if not self.arquivos_selecionados or not self.formato_saida.get():
            messagebox.showwarning(
                "Atenção", 
                "Selecione arquivos e um formato de saída para converter."
            )
            return
        
        # Verifica se o diretório de saída existe
        if not os.path.exists(self.diretorio_saida):
            try:
                os.makedirs(self.diretorio_saida)
            except Exception as e:
                messagebox.showerror(
                    "Erro", 
                    f"Não foi possível criar o diretório de saída: {str(e)}"
                )
                return
        
        # Altera o estado da interface para conversão em andamento
        self.conversao_em_andamento = True
        self.btn_converter.config(text="Parar", command=self.parar_conversao)
        self.btn_extrair_audio.config(state="disabled")
        self.btn_selecionar.config(state="disabled")
        self.btn_selecionar_saida.config(state="disabled")
        self.combo_formato.config(state="disabled")
        
        # Habilita os botões de cancelamento individuais
        for tarefa in self.tarefas_conversao.values():
            tarefa["botao_cancelar"].config(state="normal")
            tarefa["status"].config(text="Na fila")
        
        # Obtém o formato de saída selecionado
        formato = self.formato_saida.get()
        
        # Obtém as opções avançadas se ativadas
        opcoes = {}
        if self.var_opcoes_avancadas.get():
            # Determina o tipo do formato
            tipo = None
            for tipo_formato, formatos in self.formatos_conversao.items():
                if formato in formatos:
                    tipo = tipo_formato
                    break
            
            # Adiciona as opções específicas do tipo
            if tipo == "áudio":
                opcoes["bitrate"] = self.bitrate_audio.get()
                opcoes["canais"] = self.canais_audio.get()
            elif tipo == "vídeo":
                opcoes["resolucao"] = self.resolucao_video.get()
                opcoes["fps"] = self.fps_video.get()
            elif tipo == "imagem":
                opcoes["qualidade"] = self.qualidade_imagem.get()
                opcoes["redimensionar"] = self.redimensionar_imagem.get()
        
        # Inicia as threads de conversão
        for idx, tarefa in self.tarefas_conversao.items():
            if not tarefa["cancelado"]:
                thread = Thread(
                    target=self.executar_conversao,
                    args=(idx, tarefa["arquivo"], formato, opcoes),
                    daemon=True
                )
                thread.start()
    
    def executar_conversao(self, idx, arquivo, formato, opcoes):
        """
        Executa a conversão de um arquivo em uma thread separada
        
        Args:
            idx (int): Índice do arquivo na lista
            arquivo (str): Caminho completo do arquivo
            formato (str): Formato de saída
            opcoes (dict): Opções avançadas de conversão
        """
        try:
            # Atualiza o status
            self.queue.put(("status", idx, "Convertendo"))
            
            # Nome do arquivo de saída
            nome_arquivo = os.path.basename(arquivo)
            nome_base, _ = os.path.splitext(nome_arquivo)
            arquivo_saida = os.path.join(
                self.diretorio_saida, 
                f"{nome_base}.{formato}"
            )
            
            # Callback para atualização do progresso
            def atualizar_progresso(progresso):
                self.queue.put(("progresso", idx, progresso))
            
            # Executa a conversão
            resultado = self.conversor.converter_arquivo(
                arquivo, 
                arquivo_saida, 
                formato,
                opcoes,
                atualizar_progresso
            )
            
            # Verifica se foi cancelado durante a execução
            if self.tarefas_conversao[idx]["cancelado"]:
                self.queue.put(("status", idx, "Cancelado"))
                # Remove o arquivo parcialmente convertido
                if os.path.exists(arquivo_saida):
                    os.remove(arquivo_saida)
            else:
                self.queue.put(("status", idx, "Concluído"))
                self.queue.put(("progresso", idx, 100))
        
        except Exception as e:
            self.queue.put(("status", idx, "Erro"))
            self.queue.put(("erro", idx, str(e)))
    
    def extrair_audio(self):
        """
        Extrai o áudio de arquivos de vídeo
        """
        # Verifica se há arquivos de vídeo selecionados
        arquivos_video = []
        for arquivo in self.arquivos_selecionados:
            _, extensao = os.path.splitext(arquivo)
            if self.extensao_para_tipo.get(extensao.lower()) == "vídeo":
                arquivos_video.append(arquivo)
        
        if not arquivos_video:
            messagebox.showwarning(
                "Atenção", 
                "Selecione pelo menos um arquivo de vídeo para extrair o áudio."
            )
            return
        
        # Verifica se o diretório de saída existe
        if not os.path.exists(self.diretorio_saida):
            try:
                os.makedirs(self.diretorio_saida)
            except Exception as e:
                messagebox.showerror(
                    "Erro", 
                    f"Não foi possível criar o diretório de saída: {str(e)}"
                )
                return
        
        # Altera o estado da interface para conversão em andamento
        self.conversao_em_andamento = True
        self.btn_extrair_audio.config(text="Parar", command=self.parar_conversao)
        self.btn_converter.config(state="disabled")
        self.btn_selecionar.config(state="disabled")
        self.btn_selecionar_saida.config(state="disabled")
        self.combo_formato.config(state="disabled")
        
        # Habilita os botões de cancelamento individuais
        for idx, tarefa in self.tarefas_conversao.items():
            if self.extensao_para_tipo.get(os.path.splitext(tarefa["arquivo"])[1].lower()) == "vídeo":
                tarefa["botao_cancelar"].config(state="normal")
                tarefa["status"].config(text="Na fila")
            else:
                tarefa["status"].config(text="Ignorado")
        
        # Formato de áudio padrão para extração
        formato = "mp3"
        
        # Opções de áudio
        opcoes = {
            "bitrate": self.bitrate_audio.get() if self.var_opcoes_avancadas.get() else "192k",
            "canais": self.canais_audio.get() if self.var_opcoes_avancadas.get() else "2",
            "extracao_audio": True
        }
        
        # Inicia as threads de extração
        for idx, tarefa in self.tarefas_conversao.items():
            arquivo = tarefa["arquivo"]
            _, extensao = os.path.splitext(arquivo)
            
            if self.extensao_para_tipo.get(extensao.lower()) == "vídeo" and not tarefa["cancelado"]:
                thread = Thread(
                    target=self.executar_conversao,
                    args=(idx, arquivo, formato, opcoes),
                    daemon=True
                )
                thread.start()
    
    def cancelar_conversao(self, idx):
        """
        Cancela a conversão de um arquivo específico
        
        Args:
            idx (int): Índice do arquivo na lista
        """
        # Marca como cancelado
        self.tarefas_conversao[idx]["cancelado"] = True
        self.tarefas_conversao[idx]["status"].config(text="Cancelando...")
        self.tarefas_conversao[idx]["botao_cancelar"].config(state="disabled")
    
    def parar_conversao(self):
        """
        Para todos os processos de conversão em andamento
        """
        # Cancela todas as tarefas
        for idx, tarefa in self.tarefas_conversao.items():
            if tarefa["status"].cget("text") in ["Na fila", "Convertendo"]:
                tarefa["cancelado"] = True
                tarefa["status"].config(text="Cancelando...")
                tarefa["botao_cancelar"].config(state="disabled")
        
        # Restaura os botões para o estado inicial
        self.btn_converter.config(text="Converter", command=self.iniciar_conversao)
        self.btn_extrair_audio.config(text="Extrair Áudio", command=self.extrair_audio)
        
        # Restaura o estado da interface
        self.conversao_em_andamento = False
        self.btn_selecionar.config(state="normal")
        self.btn_selecionar_saida.config(state="normal")
        self.combo_formato.config(state="readonly")
        
        # Atualiza o estado dos botões
        self.atualizar_estado_botoes()
    
    def verificar_fila(self):
        """
        Verifica a fila de mensagens das threads e atualiza a interface
        """
        try:
            # Verifica se todas as tarefas estão concluídas ou canceladas
            todas_concluidas = True
            
            for idx, tarefa in self.tarefas_conversao.items():
                status = tarefa["status"].cget("text")
                if status in ["Na fila", "Convertendo", "Cancelando..."]:
                    todas_concluidas = False
                    break
            
            # Se todas estiverem concluídas, restaura a interface
            if self.conversao_em_andamento and todas_concluidas:
                self.conversao_em_andamento = False
                self.btn_converter.config(text="Converter", command=self.iniciar_conversao)
                self.btn_extrair_audio.config(text="Extrair Áudio", command=self.extrair_audio)
                self.btn_selecionar.config(state="normal")
                self.btn_selecionar_saida.config(state="normal")
                self.combo_formato.config(state="readonly")
                
                # Atualiza o estado dos botões
                self.atualizar_estado_botoes()
            
            # Processa as mensagens na fila
            while not self.queue.empty():
                tipo, idx, valor = self.queue.get()
                
                if tipo == "progresso":
                    # Atualiza a barra de progresso
                    self.tarefas_conversao[idx]["progresso"]["value"] = valor
                
                elif tipo == "status":
                    # Atualiza o status
                    self.tarefas_conversao[idx]["status"].config(text=valor)
                    
                    # Se foi concluído ou cancelado, desabilita o botão de cancelamento
                    if valor in ["Concluído", "Cancelado", "Erro"]:
                        self.tarefas_conversao[idx]["botao_cancelar"].config(state="disabled")
                
                elif tipo == "erro":
                    # Exibe mensagem de erro
                    messagebox.showerror(
                        "Erro de Conversão", 
                        f"Erro ao converter {os.path.basename(self.tarefas_conversao[idx]['arquivo'])}: {valor}"
                    )
        
        except Exception as e:
            print(f"Erro ao processar fila: {str(e)}")
        
        # Agenda a próxima verificação
        self.after(100, self.verificar_fila)