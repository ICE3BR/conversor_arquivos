#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que contém a classe responsável pela compressão de arquivos
"""

import os
import time
import shutil
import zipfile
import threading
from PIL import Image
import subprocess
import tempfile
import json

class Compressor:
    """
    Classe responsável por comprimir diferentes tipos de arquivos
    """
    
    def __init__(self):
        """
        Inicializa o compressor com configurações padrão
        """
        # Mapeamento de níveis de compressão para parâmetros específicos
        self.niveis_compressao = {
            "baixo": {
                "imagem": 90,
                "video": "28",
                "audio": "192k",
                "zip": zipfile.ZIP_STORED
            },
            "médio": {
                "imagem": 75,
                "video": "23",
                "audio": "128k",
                "zip": zipfile.ZIP_DEFLATED
            },
            "alto": {
                "imagem": 60,
                "video": "18",
                "audio": "96k",
                "zip": zipfile.ZIP_DEFLATED
            },
            "máximo": {
                "imagem": 40,
                "video": "15",
                "audio": "64k",
                "zip": zipfile.ZIP_DEFLATED
            }
        }
        
        # Mapeamento de extensões para tipos de compressão
        self.extensao_para_tipo = {
            # Imagens
            ".jpg": "imagem", ".jpeg": "imagem", ".png": "imagem", 
            ".gif": "imagem", ".bmp": "imagem", ".webp": "imagem",
            # Vídeos
            ".mp4": "video", ".avi": "video", ".mkv": "video", 
            ".mov": "video", ".webm": "video",
            # Áudios
            ".mp3": "audio", ".wav": "audio", ".ogg": "audio", 
            ".flac": "audio", ".aac": "audio",
            # Arquivos ZIP
            ".zip": "zip", ".rar": "zip", ".7z": "zip",
            # Documentos
            ".pdf": "documento", ".docx": "documento", ".doc": "documento", 
            ".txt": "documento", ".xlsx": "documento", ".pptx": "documento"
        }
        
        # Flag para cancelamento
        self.cancelado = threading.Event()
    
    def comprimir_arquivo(self, arquivo_entrada, arquivo_saida, nivel_compressao, callback_progresso=None):
        """
        Comprime o arquivo de acordo com seu tipo e nível de compressão
        
        Args:
            arquivo_entrada (str): Caminho do arquivo a ser comprimido
            arquivo_saida (str): Caminho onde o arquivo comprimido será salvo
            nivel_compressao (str): Nível de compressão ('baixo', 'médio', 'alto', 'máximo')
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a compressão foi bem-sucedida, False caso contrário
        """
        # Reinicia a flag de cancelamento
        self.cancelado.clear()
        
        # Verifica se o arquivo existe
        if not os.path.exists(arquivo_entrada):
            raise FileNotFoundError(f"Arquivo não encontrado: {arquivo_entrada}")
        
        # Obtém a extensão do arquivo
        _, extensao = os.path.splitext(arquivo_entrada)
        extensao = extensao.lower()
        
        # Determina o tipo de arquivo
        tipo_arquivo = self.extensao_para_tipo.get(extensao)
        
        if not tipo_arquivo:
            raise ValueError(f"Tipo de arquivo não suportado: {extensao}")
        
        # Obtém o nível de compressão para o tipo de arquivo
        params_compressao = self.niveis_compressao.get(nivel_compressao, self.niveis_compressao["médio"])
        
        # Executa a compressão de acordo com o tipo de arquivo
        if tipo_arquivo == "imagem":
            return self._comprimir_imagem(
                arquivo_entrada, 
                arquivo_saida, 
                params_compressao["imagem"],
                callback_progresso
            )
        
        elif tipo_arquivo == "video":
            return self._comprimir_video(
                arquivo_entrada, 
                arquivo_saida, 
                params_compressao["video"],
                callback_progresso
            )
        
        elif tipo_arquivo == "audio":
            return self._comprimir_audio(
                arquivo_entrada, 
                arquivo_saida, 
                params_compressao["audio"],
                callback_progresso
            )
        
        elif tipo_arquivo == "zip":
            return self._comprimir_zip(
                arquivo_entrada, 
                arquivo_saida, 
                params_compressao["zip"],
                callback_progresso
            )
        
        elif tipo_arquivo == "documento":
            return self._comprimir_documento(
                arquivo_entrada, 
                arquivo_saida, 
                nivel_compressao,
                callback_progresso
            )
        
        else:
            # Para outros tipos de arquivo, faz uma cópia simples
            return self._fazer_copia(arquivo_entrada, arquivo_saida, callback_progresso)
    
    def _comprimir_imagem(self, arquivo_entrada, arquivo_saida, qualidade, callback_progresso=None):
        """
        Comprime uma imagem usando a biblioteca PIL
        
        Args:
            arquivo_entrada (str): Caminho da imagem a ser comprimida
            arquivo_saida (str): Caminho onde a imagem comprimida será salva
            qualidade (int): Valor de qualidade (0-100)
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a compressão foi bem-sucedida, False caso contrário
        """
        try:
            # Atualiza o progresso
            if callback_progresso:
                callback_progresso(10)
            
            # Verifica cancelamento
            if self.cancelado.is_set():
                return False
            
            # Abre a imagem
            with Image.open(arquivo_entrada) as img:
                # Atualiza o progresso
                if callback_progresso:
                    callback_progresso(30)
                
                # Verifica cancelamento
                if self.cancelado.is_set():
                    return False
                
                # Redimensiona a imagem se ela for muito grande (opcional)
                max_size = (1920, 1080)
                if img.width > max_size[0] or img.height > max_size[1]:
                    img.thumbnail(max_size, Image.LANCZOS)
                
                # Atualiza o progresso
                if callback_progresso:
                    callback_progresso(60)
                
                # Verifica cancelamento
                if self.cancelado.is_set():
                    return False
                
                # Salva a imagem com a qualidade especificada
                img.save(
                    arquivo_saida, 
                    quality=qualidade, 
                    optimize=True,
                    progressive=True
                )
            
            # Atualiza o progresso
            if callback_progresso:
                callback_progresso(100)
            
            return True
        
        except Exception as e:
            print(f"Erro ao comprimir imagem: {str(e)}")
            raise
    
    def _comprimir_video(self, arquivo_entrada, arquivo_saida, crf, callback_progresso=None):
        """
        Comprime um vídeo usando FFmpeg
        
        Args:
            arquivo_entrada (str): Caminho do vídeo a ser comprimido
            arquivo_saida (str): Caminho onde o vídeo comprimido será salvo
            crf (str): Constant Rate Factor (valor de qualidade)
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a compressão foi bem-sucedida, False caso contrário
        """
        try:
            # Verifica se o FFmpeg está disponível
            try:
                subprocess.run(
                    ["ffmpeg", "-version"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    check=True
                )
            except (subprocess.SubprocessError, FileNotFoundError):
                raise RuntimeError(
                    "FFmpeg não está instalado ou não está disponível no PATH. "
                    "Por favor, instale o FFmpeg para comprimir vídeos."
                )
            
            # Cria o diretório temporário para logs
            temp_dir = tempfile.mkdtemp()
            log_file = os.path.join(temp_dir, "ffmpeg_progress.txt")
            
            # Comando para comprimir o vídeo
            cmd = [
                "ffmpeg",
                "-i", arquivo_entrada,
                "-c:v", "libx264",
                "-crf", crf,
                "-preset", "medium",
                "-c:a", "aac",
                "-b:a", "128k",
                "-progress", log_file,
                "-y",
                arquivo_saida
            ]
            
            # Inicia o processo FFmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Obtém a duração total do vídeo
            duration_cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                arquivo_entrada
            ]
            
            duration_process = subprocess.run(
                duration_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            duration_data = json.loads(duration_process.stdout)
            total_duration = float(duration_data["format"]["duration"])
            
            # Monitora o progresso
            last_progress = 0
            while process.poll() is None:
                # Verifica cancelamento
                if self.cancelado.is_set():
                    process.terminate()
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return False
                
                # Tenta ler o arquivo de log
                try:
                    if os.path.exists(log_file):
                        with open(log_file, "r") as f:
                            content = f.read()
                            if "out_time_ms" in content:
                                # Extrai o tempo atual
                                time_ms = 0
                                for line in content.split("\n"):
                                    if line.startswith("out_time_ms="):
                                        time_ms = int(line.split("=")[1]) / 1000000  # Converter para segundos
                                        break
                                
                                progress = min(int((time_ms / total_duration) * 100), 99)
                                
                                # Atualiza o progresso se houve mudança
                                if progress > last_progress:
                                    last_progress = progress
                                    if callback_progresso:
                                        callback_progresso(progress)
                except Exception:
                    pass
                
                time.sleep(0.5)
            
            # Limpa o diretório temporário
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Verifica se o processo foi bem-sucedido
            if process.returncode == 0:
                if callback_progresso:
                    callback_progresso(100)
                return True
            else:
                error = process.stderr.read() if process.stderr else "Erro desconhecido"
                raise RuntimeError(f"Erro no FFmpeg: {error}")
        
        except Exception as e:
            print(f"Erro ao comprimir vídeo: {str(e)}")
            raise
    
    def _comprimir_audio(self, arquivo_entrada, arquivo_saida, bitrate, callback_progresso=None):
        """
        Comprime um arquivo de áudio usando FFmpeg
        
        Args:
            arquivo_entrada (str): Caminho do áudio a ser comprimido
            arquivo_saida (str): Caminho onde o áudio comprimido será salvo
            bitrate (str): Taxa de bits para o áudio comprimido
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a compressão foi bem-sucedida, False caso contrário
        """
        try:
            # Verifica se o FFmpeg está disponível
            try:
                subprocess.run(
                    ["ffmpeg", "-version"], 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE, 
                    check=True
                )
            except (subprocess.SubprocessError, FileNotFoundError):
                raise RuntimeError(
                    "FFmpeg não está instalado ou não está disponível no PATH. "
                    "Por favor, instale o FFmpeg para comprimir áudios."
                )
            
            # Cria o diretório temporário para logs
            temp_dir = tempfile.mkdtemp()
            log_file = os.path.join(temp_dir, "ffmpeg_progress.txt")
            
            # Comando para comprimir o áudio
            cmd = [
                "ffmpeg",
                "-i", arquivo_entrada,
                "-c:a", "libmp3lame",
                "-b:a", bitrate,
                "-progress", log_file,
                "-y",
                arquivo_saida
            ]
            
            # Inicia o processo FFmpeg
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Obtém a duração total do áudio
            duration_cmd = [
                "ffprobe",
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "json",
                arquivo_entrada
            ]
            
            duration_process = subprocess.run(
                duration_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            duration_data = json.loads(duration_process.stdout)
            total_duration = float(duration_data["format"]["duration"])
            
            # Monitora o progresso
            last_progress = 0
            while process.poll() is None:
                # Verifica cancelamento
                if self.cancelado.is_set():
                    process.terminate()
                    shutil.rmtree(temp_dir, ignore_errors=True)
                    return False
                
                # Tenta ler o arquivo de log
                try:
                    if os.path.exists(log_file):
                        with open(log_file, "r") as f:
                            content = f.read()
                            if "out_time_ms" in content:
                                # Extrai o tempo atual
                                time_ms = 0
                                for line in content.split("\n"):
                                    if line.startswith("out_time_ms="):
                                        time_ms = int(line.split("=")[1]) / 1000000  # Converter para segundos
                                        break
                                
                                progress = min(int((time_ms / total_duration) * 100), 99)
                                
                                # Atualiza o progresso se houve mudança
                                if progress > last_progress:
                                    last_progress = progress
                                    if callback_progresso:
                                        callback_progresso(progress)
                except Exception:
                    pass
                
                time.sleep(0.5)
            
            # Limpa o diretório temporário
            shutil.rmtree(temp_dir, ignore_errors=True)
            
            # Verifica se o processo foi bem-sucedido
            if process.returncode == 0:
                if callback_progresso:
                    callback_progresso(100)
                return True
            else:
                error = process.stderr.read() if process.stderr else "Erro desconhecido"
                raise RuntimeError(f"Erro no FFmpeg: {error}")
        
        except Exception as e:
            print(f"Erro ao comprimir áudio: {str(e)}")
            raise
    
    def _comprimir_zip(self, arquivo_entrada, arquivo_saida, metodo_compressao, callback_progresso=None):
        """
        Comprime um arquivo em formato ZIP
        
        Args:
            arquivo_entrada (str): Caminho do arquivo a ser comprimido
            arquivo_saida (str): Caminho onde o arquivo comprimido será salvo
            metodo_compressao (int): Método de compressão ZIP
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a compressão foi bem-sucedida, False caso contrário
        """
        try:
            # Atualiza o progresso
            if callback_progresso:
                callback_progresso(10)
            
            # Verifica cancelamento
            if self.cancelado.is_set():
                return False
            
            # Determina se é um diretório ou um arquivo
            if os.path.isdir(arquivo_entrada):
                # Comprime o diretório
                with zipfile.ZipFile(arquivo_saida, 'w', metodo_compressao) as zipf:
                    total_files = sum([len(files) for _, _, files in os.walk(arquivo_entrada)])
                    processed_files = 0
                    
                    for root, _, files in os.walk(arquivo_entrada):
                        for file in files:
                            # Verifica cancelamento
                            if self.cancelado.is_set():
                                return False
                            
                            file_path = os.path.join(root, file)
                            arcname = os.path.relpath(file_path, os.path.dirname(arquivo_entrada))
                            zipf.write(file_path, arcname)
                            
                            # Atualiza o contador e o progresso
                            processed_files += 1
                            progress = min(int((processed_files / total_files) * 90) + 10, 99)
                            
                            if callback_progresso:
                                callback_progresso(progress)
            else:
                # Comprime o arquivo individual
                with zipfile.ZipFile(arquivo_saida, 'w', metodo_compressao) as zipf:
                    # Verifica cancelamento
                    if self.cancelado.is_set():
                        return False
                    
                    # Adiciona o arquivo ao ZIP
                    arcname = os.path.basename(arquivo_entrada)
                    zipf.write(arquivo_entrada, arcname)
                    
                    # Atualiza o progresso
                    if callback_progresso:
                        callback_progresso(90)
            
            # Atualiza o progresso final
            if callback_progresso:
                callback_progresso(100)
            
            return True
        
        except Exception as e:
            print(f"Erro ao comprimir para ZIP: {str(e)}")
            raise
    
    def _comprimir_documento(self, arquivo_entrada, arquivo_saida, nivel_compressao, callback_progresso=None):
        """
        Comprime um documento (para documentos, geralmente fazemos uma cópia ou
        realizamos conversões específicas)
        
        Args:
            arquivo_entrada (str): Caminho do documento a ser comprimido
            arquivo_saida (str): Caminho onde o documento comprimido será salvo
            nivel_compressao (str): Nível de compressão
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a compressão foi bem-sucedida, False caso contrário
        """
        # Para documentos, por enquanto, fazemos apenas uma cópia
        # No futuro, poderíamos implementar compressão de PDF, etc.
        return self._fazer_copia(arquivo_entrada, arquivo_saida, callback_progresso)
    
    def _fazer_copia(self, arquivo_entrada, arquivo_saida, callback_progresso=None):
        """
        Faz uma cópia do arquivo com atualizações de progresso
        
        Args:
            arquivo_entrada (str): Caminho do arquivo de origem
            arquivo_saida (str): Caminho do arquivo de destino
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a cópia foi bem-sucedida, False caso contrário
        """
        try:
            # Tamanho do arquivo
            tamanho_total = os.path.getsize(arquivo_entrada)
            tamanho_bloco = min(tamanho_total // 100, 1024 * 1024)  # 1MB ou menor
            
            if tamanho_bloco <= 0:
                tamanho_bloco = 1024  # 1KB mínimo
            
            # Atualiza o progresso inicial
            if callback_progresso:
                callback_progresso(0)
            
            # Verifica cancelamento
            if self.cancelado.is_set():
                return False
            
            with open(arquivo_entrada, 'rb') as fin, open(arquivo_saida, 'wb') as fout:
                copiado = 0
                while True:
                    # Verifica cancelamento
                    if self.cancelado.is_set():
                        return False
                    
                    # Lê um bloco de dados
                    bloco = fin.read(tamanho_bloco)
                    if not bloco:
                        break
                    
                    # Escreve o bloco no arquivo de saída
                    fout.write(bloco)
                    
                    # Atualiza o contador e o progresso
                    copiado += len(bloco)
                    progresso = min(int((copiado / tamanho_total) * 100), 100)
                    
                    if callback_progresso:
                        callback_progresso(progresso)
            
            return True
        
        except Exception as e:
            print(f"Erro ao copiar arquivo: {str(e)}")
            raise
    
    def cancelar(self):
        """
        Cancela a operação de compressão em andamento
        """
        self.cancelado.set()