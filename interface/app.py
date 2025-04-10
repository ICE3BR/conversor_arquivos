#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que contém a interface principal da aplicação
"""

import os
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from interface.tela_comprimir import TelaComprimir
from interface.tela_converter import TelaConverter

class Application(tk.Tk):
    """
    Classe principal da aplicação que gerencia as diferentes telas
    """
    
    def __init__(self):
        """
        Inicializa a aplicação principal
        """
        super().__init__()
        
        # Configuração da janela principal
        self.title("Conversor e Compressor de Arquivos")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Centraliza a janela na tela
        self.center_window()
        
        # Configura o estilo da aplicação
        self.style = ttk.Style()
        self.style.theme_use('clam')  # Pode usar 'clam', 'alt', 'default', 'classic'
        
        # Cores e estilo
        self.bg_color = "#f0f0f0"
        self.configure(bg=self.bg_color)
        
        # Frame principal que conterá todas as telas
        self.container = ttk.Frame(self)
        self.container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Dicionário para armazenar as telas
        self.frames = {}
        
        # Cria o menu principal da aplicação
        self.criar_menu_principal()
        
        # Inicializa a tela inicial (Seleção de modo)
        self.mostrar_tela_inicial()
    
    def center_window(self):
        """
        Centraliza a janela na tela
        """
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')
    
    def criar_menu_principal(self):
        """
        Cria o menu principal da aplicação
        """
        self.menu_bar = tk.Menu(self)
        
        # Menu Arquivo
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Início", command=self.mostrar_tela_inicial)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.confirmar_saida)
        
        # Menu Modos
        mode_menu = tk.Menu(self.menu_bar, tearoff=0)
        mode_menu.add_command(label="Converter", command=lambda: self.mostrar_tela("converter"))
        mode_menu.add_command(label="Comprimir", command=lambda: self.mostrar_tela("comprimir"))
        
        # Menu Ajuda
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="Sobre", command=self.mostrar_sobre)
        
        # Adiciona os menus à barra de menu
        self.menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        self.menu_bar.add_cascade(label="Modos", menu=mode_menu)
        self.menu_bar.add_cascade(label="Ajuda", menu=help_menu)
        
        # Configura a barra de menu
        self.config(menu=self.menu_bar)
    
    def mostrar_tela_inicial(self):
        """
        Exibe a tela inicial de seleção de modo
        """
        # Limpa o container
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Frame central para os botões de modo
        frame_centro = ttk.Frame(self.container)
        frame_centro.pack(expand=True, fill="both")
        
        # Título da tela inicial
        titulo = ttk.Label(
            frame_centro, 
            text="Selecione o modo de operação", 
            font=("Helvetica", 16, "bold")
        )
        titulo.pack(pady=20)
        
        # Frame para os botões
        frame_botoes = ttk.Frame(frame_centro)
        frame_botoes.pack(pady=30)
        
        # Estilo para os botões grandes
        self.style.configure(
            "Grande.TButton", 
            font=("Helvetica", 12, "bold"),
            padding=10
        )
        
        # Botão de Conversão
        btn_converter = ttk.Button(
            frame_botoes,
            text="Converter Arquivos",
            style="Grande.TButton",
            width=25,
            command=lambda: self.mostrar_tela("converter")
        )
        btn_converter.pack(pady=10)
        
        # Botão de Compressão
        btn_comprimir = ttk.Button(
            frame_botoes,
            text="Comprimir Arquivos",
            style="Grande.TButton",
            width=25,
            command=lambda: self.mostrar_tela("comprimir")
        )
        btn_comprimir.pack(pady=10)
    
    def mostrar_tela(self, nome_tela):
        """
        Exibe a tela especificada pelo nome
        
        Args:
            nome_tela (str): Nome da tela a ser exibida ('converter' ou 'comprimir')
        """
        # Limpa o container
        for widget in self.container.winfo_children():
            widget.destroy()
        
        # Cria a nova tela conforme solicitado
        if nome_tela == "converter":
            # Cria a tela de conversão
            tela_converter = TelaConverter(self.container, self)
            tela_converter.pack(fill="both", expand=True)
            
        elif nome_tela == "comprimir":
            # Cria a tela de compressão
            tela_comprimir = TelaComprimir(self.container, self)
            tela_comprimir.pack(fill="both", expand=True)
    
    def mostrar_sobre(self):
        """
        Exibe informações sobre a aplicação
        """
        messagebox.showinfo(
            "Sobre", 
            "Conversor e Compressor de Arquivos\n"
            "Versão 1.0\n\n"
            "Aplicação para conversão e compressão de diversos tipos de arquivos."
        )
    
    def confirmar_saida(self):
        """
        Confirma a saída da aplicação
        """
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.destroy()