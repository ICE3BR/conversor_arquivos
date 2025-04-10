#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Módulo que contém a classe responsável pela conversão de arquivos
"""

import os
import time
import json
import subprocess
import tempfile
import shutil
import threading
from PIL import Image

class Conversor:
    """
    Classe responsável por converter diferentes tipos de arquivos
    """
    
    def __init__(self):
        """
        Inicializa o conversor com configurações padrão
        """
        # Mapeamento de extensões para tipos de conversão
        self.extensao_para_tipo = {
            # Áudio
            ".mp3": "áudio", ".wav": "áudio", ".ogg": "áudio", 
            ".flac": "áudio", ".aac": "áudio",
            # Vídeo
            ".mp4": "vídeo", ".avi": "vídeo", ".mkv": "vídeo", 
            ".mov": "vídeo", ".webm": "vídeo",
            # Imagem
            ".jpg": "imagem", ".jpeg": "imagem", ".png": "imagem", 
            ".gif": "imagem", ".bmp": "imagem", ".webp": "imagem",
            # Documento
            ".pdf": "documento", ".txt": "documento", ".docx": "documento", 
            ".doc": "documento", ".html": "documento", ".htm": "documento"
        }
        
        # Formatos de conversão disponíveis por tipo
        self.formatos_conversao = {
            "áudio": ["mp3", "wav", "ogg", "flac", "aac"],
            "vídeo": ["mp4", "avi", "mkv", "mov", "webm"],
            "imagem": ["jpg", "png", "gif", "bmp", "webp"],
            "documento": ["pdf", "txt", "docx", "html"]
        }
        
        # Flag para cancelamento
        self.cancelado = threading.Event()
    
    def converter_arquivo(self, arquivo_entrada, arquivo_saida, formato_saida, opcoes=None, callback_progresso=None):
        """
        Converte o arquivo para o formato especificado
        
        Args:
            arquivo_entrada (str): Caminho do arquivo a ser convertido
            arquivo_saida (str): Caminho onde o arquivo convertido será salvo
            formato_saida (str): Formato de saída desejado
            opcoes (dict): Opções adicionais para a conversão
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a conversão foi bem-sucedida, False caso contrário
        """
        # Reinicia a flag de cancelamento
        self.cancelado.clear()
        
        # Inicializa opções se não fornecidas
        if opcoes is None:
            opcoes = {}
        
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
        
        # Verifica se o formato de saída é válido para o tipo de arquivo
        if formato_saida not in self.formatos_conversao.get(tipo_arquivo, []):
            raise ValueError(
                f"Formato de saída '{formato_saida}' não é válido para arquivos do tipo '{tipo_arquivo}'"
            )
        
        # Executa a conversão de acordo com o tipo de arquivo
        if tipo_arquivo == "imagem":
            return self._converter_imagem(
                arquivo_entrada, 
                arquivo_saida, 
                formato_saida,
                opcoes,
                callback_progresso
            )
        
        elif tipo_arquivo == "vídeo":
            # Verifica se é para extrair áudio
            if opcoes.get("extracao_audio", False):
                return self._extrair_audio_de_video(
                    arquivo_entrada, 
                    arquivo_saida, 
                    opcoes,
                    callback_progresso
                )
            else:
                return self._converter_video(
                    arquivo_entrada, 
                    arquivo_saida, 
                    formato_saida,
                    opcoes,
                    callback_progresso
                )
        
        elif tipo_arquivo == "áudio":
            return self._converter_audio(
                arquivo_entrada, 
                arquivo_saida, 
                formato_saida,
                opcoes,
                callback_progresso
            )
        
        elif tipo_arquivo == "documento":
            return self._converter_documento(
                arquivo_entrada, 
                arquivo_saida, 
                formato_saida,
                opcoes,
                callback_progresso
            )
        
        else:
            raise ValueError(f"Conversão não implementada para o tipo de arquivo: {tipo_arquivo}")
    
    def _converter_imagem(self, arquivo_entrada, arquivo_saida, formato_saida, opcoes, callback_progresso=None):
        """
        Converte uma imagem para o formato especificado
        
        Args:
            arquivo_entrada (str): Caminho da imagem a ser convertida
            arquivo_saida (str): Caminho onde a imagem convertida será salva
            formato_saida (str): Formato de saída desejado
            opcoes (dict): Opções adicionais para a conversão
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a conversão foi bem-sucedida, False caso contrário
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
                
                # Processa opções
                qualidade = int(opcoes.get("qualidade", 90))
                redimensionar = opcoes.get("redimensionar", "original")
                
                # Redimensiona a imagem se solicitado
                if redimensionar != "original":
                    try:
                        largura, altura = map(int, redimensionar.split("x"))
                        img = img.resize((largura, altura), Image.LANCZOS)
                    except (ValueError, AttributeError):
                        # Se houver erro no formato, usa a imagem original
                        pass
                
                # Atualiza o progresso
                if callback_progresso:
                    callback_progresso(60)
                
                # Verifica cancelamento
                if self.cancelado.is_set():
                    return False
                
                # Configurações para formatos específicos
                save_options = {}
                
                if formato_saida.lower() == "jpg" or formato_saida.lower() == "jpeg":
                    save_options["quality"] = qualidade
                    save_options["optimize"] = True
                    save_options["progressive"] = True
                    
                    # Converte para RGB se for RGBA (para evitar erro com JPEG)
                    if img.mode == "RGBA":
                        img = img.convert("RGB")
                
                elif formato_saida.lower() == "png":
                    save_options["optimize"] = True
                    # Para PNG, o parâmetro de qualidade é substituído por level de compressão
                    compress_level = max(0, min(9, 9 - (qualidade // 10)))
                    save_options["compress_level"] = compress_level
                
                elif formato_saida.lower() == "webp":
                    save_options["quality"] = qualidade
                    save_options["lossless"] = qualidade >= 95
                
                # Salva a imagem no formato desejado
                img.save(arquivo_saida, format=formato_saida.upper(), **save_options)
            
            # Atualiza o progresso
            if callback_progresso:
                callback_progresso(100)
            
            return True
        
        except Exception as e:
            print(f"Erro ao converter imagem: {str(e)}")
            raise
    
    def _converter_video(self, arquivo_entrada, arquivo_saida, formato_saida, opcoes, callback_progresso=None):
        """
        Converte um vídeo para o formato especificado
        
        Args:
            arquivo_entrada (str): Caminho do vídeo a ser convertido
            arquivo_saida (str): Caminho onde o vídeo convertido será salvo
            formato_saida (str): Formato de saída desejado
            opcoes (dict): Opções adicionais para a conversão
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a conversão foi bem-sucedida, False caso contrário
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
                    "Por favor, instale o FFmpeg para converter vídeos."
                )
            
            # Cria o diretório temporário para logs
            temp_dir = tempfile.mkdtemp()
            log_file = os.path.join(temp_dir, "ffmpeg_progress.txt")
            
            # Processa opções
            resolucao = opcoes.get("resolucao", "original")
            fps = opcoes.get("fps", "original")
            
            # Constrói o comando base
            cmd = ["ffmpeg", "-i", arquivo_entrada]
            
            # Adiciona opções de resolução
            if resolucao != "original":
                if resolucao == "720p":
                    cmd.extend(["-vf", "scale=-1:720"])
                elif resolucao == "1080p":
                    cmd.extend(["-vf", "scale=-1:1080"])
                elif resolucao == "480p":
                    cmd.extend(["-vf", "scale=-1:480"])
                elif resolucao == "360p":
                    cmd.extend(["-vf", "scale=-1:360"])
            
            # Adiciona opções de FPS
            if fps != "original":
                try:
                    fps_value = int(fps)
                    if "-vf" in cmd:
                        # Se já tem um filtro de vídeo, concatena
                        vf_index = cmd.index("-vf")
                        cmd[vf_index + 1] = f"{cmd[vf_index + 1]},fps={fps_value}"
                    else:
                        # Caso contrário, adiciona novo filtro
                        cmd.extend(["-vf", f"fps={fps_value}"])
                except ValueError:
                    pass
            
            # Adiciona configurações de codec com base no formato
            if formato_saida == "mp4":
                cmd.extend(["-c:v", "libx264", "-crf", "23", "-c:a", "aac", "-b:a", "128k"])
            elif formato_saida == "webm":
                cmd.extend(["-c:v", "libvpx-vp9", "-crf", "30", "-b:v", "0", "-c:a", "libopus"])
            elif formato_saida == "mkv":
                cmd.extend(["-c:v", "libx264", "-crf", "23", "-c:a", "flac"])
            elif formato_saida == "avi":
                cmd.extend(["-c:v", "mpeg4", "-q:v", "6", "-c:a", "libmp3lame", "-q:a", "3"])
            elif formato_saida == "mov":
                cmd.extend(["-c:v", "prores_ks", "-profile:v", "2", "-c:a", "pcm_s16le"])
            
            # Adiciona arquivo de saída e opções de progresso
            cmd.extend([
                "-progress", log_file,
                "-y",
                arquivo_saida
            ])
            
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
            print(f"Erro ao converter vídeo: {str(e)}")
            raise
    
    def _converter_audio(self, arquivo_entrada, arquivo_saida, formato_saida, opcoes, callback_progresso=None):
        """
        Converte um arquivo de áudio para o formato especificado
        
        Args:
            arquivo_entrada (str): Caminho do áudio a ser convertido
            arquivo_saida (str): Caminho onde o áudio convertido será salvo
            formato_saida (str): Formato de saída desejado
            opcoes (dict): Opções adicionais para a conversão
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a conversão foi bem-sucedida, False caso contrário
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
                    "Por favor, instale o FFmpeg para converter áudios."
                )
            
            # Cria o diretório temporário para logs
            temp_dir = tempfile.mkdtemp()
            log_file = os.path.join(temp_dir, "ffmpeg_progress.txt")
            
            # Processa opções
            bitrate = opcoes.get("bitrate", "192k")
            canais = opcoes.get("canais", "2")
            
            # Constrói o comando base
            cmd = ["ffmpeg", "-i", arquivo_entrada]
            
            # Adiciona configurações de codec com base no formato
            if formato_saida == "mp3":
                cmd.extend(["-c:a", "libmp3lame", "-b:a", bitrate])
            elif formato_saida == "ogg":
                cmd.extend(["-c:a", "libvorbis", "-b:a", bitrate])
            elif formato_saida == "flac":
                cmd.extend(["-c:a", "flac"])
            elif formato_saida == "wav":
                cmd.extend(["-c:a", "pcm_s16le"])
            elif formato_saida == "aac":
                cmd.extend(["-c:a", "aac", "-b:a", bitrate, "-strict", "experimental"])
            
            # Adiciona configuração de canais
            cmd.extend(["-ac", canais])
            
            # Adiciona arquivo de saída e opções de progresso
            cmd.extend([
                "-progress", log_file,
                "-y",
                arquivo_saida
            ])
            
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
            print(f"Erro ao converter áudio: {str(e)}")
            raise
    
    def _extrair_audio_de_video(self, arquivo_entrada, arquivo_saida, opcoes, callback_progresso=None):
        """
        Extrai o áudio de um arquivo de vídeo
        
        Args:
            arquivo_entrada (str): Caminho do vídeo
            arquivo_saida (str): Caminho onde o áudio será salvo
            opcoes (dict): Opções adicionais para a extração
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a extração foi bem-sucedida, False caso contrário
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
                    "Por favor, instale o FFmpeg para extrair áudio de vídeos."
                )
            
            # Cria o diretório temporário para logs
            temp_dir = tempfile.mkdtemp()
            log_file = os.path.join(temp_dir, "ffmpeg_progress.txt")
            
            # Processa opções
            bitrate = opcoes.get("bitrate", "192k")
            canais = opcoes.get("canais", "2")
            
            # Comando para extrair o áudio
            cmd = [
                "ffmpeg",
                "-i", arquivo_entrada,
                "-vn",  # Não usar vídeo
                "-c:a", "libmp3lame",  # Usar codec MP3
                "-b:a", bitrate,
                "-ac", canais,
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
            print(f"Erro ao extrair áudio: {str(e)}")
            raise
    
    def _converter_documento(self, arquivo_entrada, arquivo_saida, formato_saida, opcoes, callback_progresso=None):
        """
        Converte um documento para o formato especificado
        
        Args:
            arquivo_entrada (str): Caminho do documento a ser convertido
            arquivo_saida (str): Caminho onde o documento convertido será salvo
            formato_saida (str): Formato de saída desejado
            opcoes (dict): Opções adicionais para a conversão
            callback_progresso (function): Função de callback para atualização do progresso
            
        Returns:
            bool: True se a conversão foi bem-sucedida, False caso contrário
        """
        # Nota: Para conversão de documentos, seria necessário usar bibliotecas específicas
        # como python-docx, PyPDF2, etc. Ou ferramentas externas como LibreOffice, Pandoc, etc.
        # Aqui temos apenas uma implementação básica.
        
        # Atualiza o progresso inicial
        if callback_progresso:
            callback_progresso(10)
        
        try:
            # Verifica cancelamento
            if self.cancelado.is_set():
                return False
            
            # Obtém as extensões
            _, extensao_entrada = os.path.splitext(arquivo_entrada)
            extensao_entrada = extensao_entrada.lower()
            
            # Atualiza o progresso
            if callback_progresso:
                callback_progresso(20)
            
            # Verifica cancelamento
            if self.cancelado.is_set():
                return False
            
            # Verifica se temos suporte para a conversão
            conversao_suportada = False
            
            # Conversão de PDF para TXT (usando PyPDF2)
            if extensao_entrada == ".pdf" and formato_saida == "txt":
                try:
                    import PyPDF2
                    conversao_suportada = True
                    
                    with open(arquivo_entrada, 'rb') as file:
                        reader = PyPDF2.PdfReader(file)
                        total_pages = len(reader.pages)
                        
                        with open(arquivo_saida, 'w', encoding='utf-8') as output:
                            for i, page in enumerate(reader.pages):
                                # Verifica cancelamento
                                if self.cancelado.is_set():
                                    return False
                                
                                # Extrai o texto da página
                                text = page.extract_text()
                                output.write(text + "\n\n")
                                
                                # Atualiza o progresso
                                progress = 20 + int((i / total_pages) * 80)
                                if callback_progresso:
                                    callback_progresso(progress)
                except ImportError:
                    conversao_suportada = False
            
            # Conversão de TXT para HTML (conversão simples)
            elif extensao_entrada == ".txt" and formato_saida == "html":
                conversao_suportada = True
                
                with open(arquivo_entrada, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Escapa caracteres HTML
                    content = content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                    
                    # Converte quebras de linha para tags <br>
                    content = content.replace("\n", "<br>\n")
                    
                    # Cria o documento HTML
                    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>{os.path.basename(arquivo_entrada)}</title>
</head>
<body>
    <pre>{content}</pre>
</body>
</html>
"""
                    
                    with open(arquivo_saida, 'w', encoding='utf-8') as output:
                        output.write(html_content)
                    
                    # Atualiza o progresso
                    if callback_progresso:
                        callback_progresso(100)
            
            # Se a conversão não for suportada diretamente
            if not conversao_suportada:
                # Tenta usar ferramentas externas (pandoc, libreoffice, etc.)
                # Aqui seria necessário implementar chamadas para essas ferramentas
                
                # Por enquanto, retorna erro
                raise ValueError(
                    f"Conversão de {extensao_entrada} para {formato_saida} não é suportada diretamente. "
                    "É necessário instalar ferramentas externas como Pandoc ou LibreOffice."
                )
            
            return True
        
        except Exception as e:
            print(f"Erro ao converter documento: {str(e)}")
            raise
    
    def cancelar(self):
        """
        Cancela a operação de conversão em andamento
        """
        self.cancelado.set()