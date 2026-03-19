import warnings
warnings.filterwarnings("ignore", category=UserWarning, module="pygame")

import os
import sys
import subprocess
import re
import pygame
import speech_recognition as sr
import ollama
import threading
import psycopg2
from flask import Flask, jsonify
from flask_cors import CORS
from ddgs import DDGS
import keyboard
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

pygame.mixer.init()

estado_zeno = {
    "status": "ONLINE",
    "usuario": "Aguardando comando...",
    "zeno": "Sistemas iniciados."
}

app = Flask(__name__)
CORS(app)

@app.route('/estado')
def estado():
    return jsonify(estado_zeno)

def rodar_servidor():
    import logging
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(port=5000, debug=False, use_reloader=False)

def inicializar_banco():
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memoria (
            id SERIAL PRIMARY KEY,
            usuario TEXT,
            informacao TEXT
        )
    ''')
    conn.commit()
    conn.close()

def salvar_memoria(usuario, informacao):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('INSERT INTO memoria (usuario, informacao) VALUES (%s, %s)', (usuario, informacao))
    conn.commit()
    conn.close()

def carregar_memoria(usuario):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('SELECT informacao FROM memoria WHERE usuario = %s', (usuario,))
    resultados = cursor.fetchall()
    conn.close()
    if resultados:
        return "\n".join([f"* {r[0]}" for r in resultados])
    return "Nenhuma informacao salva."

def limpar_texto_para_fala(texto):
    texto_limpo = re.sub(r'\[CMD\].*?\[/CMD\]', '', texto, flags=re.DOTALL)
    texto_limpo = re.sub(r'\[MEM\].*?\[/MEM\]', '', texto_limpo, flags=re.DOTALL)
    texto_limpo = re.sub(r'[*#_]', '', texto_limpo)
    return texto_limpo

def falar(texto):
    global estado_zeno
    texto_limpo = limpar_texto_para_fala(texto)
    if not texto_limpo.strip():
        return
        
    estado_zeno["status"] = "FALANDO..."
    voz = "pt-BR-AntonioNeural"
    arquivo = "resposta.mp3"
    
    try:
        subprocess.run(["edge-tts", "--voice", voz, "--text", texto_limpo, "--write-media", arquivo])
        pygame.mixer.music.load(arquivo)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            if keyboard.is_pressed('space'):
                pygame.mixer.music.stop()
                print("\n[Zeno interrompido]")
                break
            pygame.time.Clock().tick(10)
            
        pygame.mixer.music.unload()
        if os.path.exists(arquivo):
            os.remove(arquivo)
    except Exception as e:
        print(f"\n[Erro de Audio: {e}]")

def ouvir():
    global estado_zeno
    reconhecedor = sr.Recognizer()
    reconhecedor.pause_threshold = 2.0
    with sr.Microphone() as fonte:
        estado_zeno["status"] = "OUVINDO..."
        print("\n[Zeno ouvindo...]")
        reconhecedor.adjust_for_ambient_noise(fonte, duration=0.5)
        try:
            audio = reconhecedor.listen(fonte, timeout=5)
            texto = reconhecedor.recognize_google(audio, language='pt-BR')
            print(f"Voce (Voz): {texto}")
            return texto
        except sr.WaitTimeoutError:
            return ""
        except sr.UnknownValueError:
            return ""
        except Exception:
            return ""

def executar_comando(comando):
    try:
        resultado = subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)
        return resultado.stdout
    except subprocess.CalledProcessError as erro:
        return erro.stderr

def processar_tags_ocultas(texto, usuario_atual):
    comandos = re.findall(r'\[CMD\](.*?)\[/CMD\]', texto)
    for cmd in comandos:
        print(f"\n[Executando comando: {cmd}]")
        saida = executar_comando(cmd)
        if saida:
            print(f"[Saida do Sistema]: {saida.strip()}")
            
    memorias = re.findall(r'\[MEM\](.*?)\[/MEM\]', texto)
    for mem in memorias:
        print(f"\n[Gravando na memoria: {mem}]")
        salvar_memoria(usuario_atual, mem)

def obter_caminho_desktop():
    caminho_usuario = os.environ.get('USERPROFILE') or os.path.expanduser('~')
    caminhos = [
        os.path.join(caminho_usuario, 'OneDrive', 'Área de Trabalho'),
        os.path.join(caminho_usuario, 'OneDrive', 'Desktop'),
        os.path.join(caminho_usuario, 'Desktop'),
        os.path.join(caminho_usuario, 'Área de Trabalho')
    ]
    for caminho in caminhos:
        if os.path.exists(caminho):
            return caminho
    return os.path.join(caminho_usuario, 'Desktop')

def buscar_na_internet(consulta):
    try:
        resultados = DDGS().text(consulta, region='br-pt', timelimit='w', max_results=3)
        if not resultados:
            resultados = DDGS().text(consulta, region='br-pt', timelimit='m', max_results=3)
        if not resultados:
            return "Nenhuma informacao recente encontrada."
        
        texto_compilado = "Dados extraidos da internet:\n"
        for r in resultados:
            texto_compilado += f"* Titulo: {r['title']}\n  Resumo: {r['body']}\n"
        return texto_compilado
    except Exception as e:
        return f"Falha na conexao com a rede externa: {e}"

def iniciar_zeno_core():
    global estado_zeno
    print("==================================================")
    print("Zeno System Iniciado")
    print("==================================================")
    
    inicializar_banco()
    thread_servidor = threading.Thread(target=rodar_servidor, daemon=True)
    thread_servidor.start()

    caminho_desktop = obter_caminho_desktop()
    
    usuario_db = input("\nIdentificacao de usuario necessaria. Digite seu nome: ").strip()
    if usuario_db == "":
        usuario_db = "Visitante"
        
    memoria_banco = carregar_memoria(usuario_db)

    mensagens = [
        {
            "role": "system", 
            "content": f"""Voce e o Zeno, um assistente virtual de elite.
Voce TEM PERMISSAO TOTAL para executar comandos no Windows do usuario. NUNCA diga que nao pode abrir programas.
O diretorio da Area de Trabalho e: {caminho_desktop}

MEMORIA DE CONTEXTO PESSOAL:
Nome do usuario atual na sessao: {usuario_db}
Fatos armazenados:
{memoria_banco}

REGRAS OBRIGATORIAS DE MEMORIA:
1. Grave fatos novos em tags separadas usando EXCLUSIVAMENTE [MEM] e [/MEM]. 
2. Exemplo de uso correto: [MEM]O usuario e arquiteto.[/MEM] [MEM]O usuario mora em Sao Paulo.[/MEM]
3. PROIBICAO ABSOLUTA: NUNCA crie tags inventadas como [AÇÃO], [CADA FATO NOVA] ou [FATOS].

REGRAS PARA USO DE COMANDOS:
1. Para abrir programas, forneca o comando APENAS dentro de [CMD] e [/CMD].
2. Exemplo para sites: [CMD]start https://www.youtube.com[/CMD].
3. Exemplo VS Code: [CMD]code[/CMD]. Bloco de Notas: [CMD]notepad[/CMD].
4. PROIBICAO ABSOLUTA: NUNCA crie marcacoes de logica de sistema no texto.

COMUNICACAO:
Responda em portugues do Brasil de forma direta.
Fale de forma natural.
NUNCA imprima o seu raciocinio de etapas na tela."""
        }
    ]

    while True:
        try:
            estado_zeno["status"] = "ONLINE"
            entrada = input(f"\n{usuario_db} (Digite ou de Enter para Voz): ")
            
            if entrada.lower() in ['sair', 'exit', 'quit']:
                estado_zeno["status"] = "DESLIGANDO..."
                falar("Encerrando protocolos. Ate a proxima, senhor.")
                break
            
            if entrada == "":
                pergunta = ouvir()
                if pergunta == "":
                    continue
            else:
                pergunta = entrada

            estado_zeno["usuario"] = pergunta
            
            gatilhos = ["pesquise", "busque", "internet", "resultado", "último", "hoje", "notícia", "quem ganhou", "quanto foi", "atual"]
            
            if any(gatilho in pergunta.lower() for gatilho in gatilhos):
                estado_zeno["status"] = "BUSCANDO NA REDE..."
                sys.stdout.write("Zeno varrendo a internet...")
                sys.stdout.flush()
                
                dados_web = buscar_na_internet(pergunta)
                instrucao = "Responda de forma direta usando os dados acima."
                pergunta_formatada = f"Resultados da web:\n{dados_web}\n\nPergunta: {pergunta}\n\nInstrucao: {instrucao}"
                sys.stdout.write("\r" + " " * 30 + "\r")
            else:
                pergunta_formatada = pergunta

            estado_zeno["status"] = "PENSANDO..."
            mensagens.append({"role": "user", "content": pergunta_formatada})
            
            sys.stdout.write("Zeno processando...")
            sys.stdout.flush()

            resposta_streaming = ollama.chat(model='llama3.2', messages=mensagens, stream=True)
            sys.stdout.write("\r" + " " * 20 + "\r")
            
            print("Zeno: ", end="")
            texto_resposta_completa = ""
            for chunk in resposta_streaming:
                texto_chunk = chunk['message']['content']
                print(texto_chunk, end="", flush=True)
                texto_resposta_completa += texto_chunk
            print() 
            
            estado_zeno["zeno"] = limpar_texto_para_fala(texto_resposta_completa)
            
            processar_tags_ocultas(texto_resposta_completa, usuario_db)
            falar(texto_resposta_completa)
            
            mensagens.append({"role": "assistant", "content": texto_resposta_completa})

        except KeyboardInterrupt:
            sys.exit()
        except Exception as e:
            print(f"\nOcorreu um erro: {e}")

if __name__ == "__main__":
    iniciar_zeno_core()