import os
import shutil
from tkinter import *
from tkinter import messagebox
from prettytable import PrettyTable

def get_size(path):
    """Retorna o tamanho total dos arquivos e diretórios dentro do caminho especificado em MB."""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                total_size += os.path.getsize(filepath)
            except OSError:
                continue
    return total_size / (1024 * 1024)  # Converte para MB

def list_large_files(path, threshold_mb=100):
    """Lista arquivos maiores que o limite especificado (em MB)."""
    large_files = []
    for dirpath, dirnames, filenames in os.walk(path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            try:
                file_size = os.path.getsize(filepath) / (1024 * 1024)  # Tamanho em MB
                if file_size > threshold_mb:
                    large_files.append((filepath, file_size))
            except OSError:
                continue
    return large_files

def check_disk_health(path):
    """Verifica a saúde do disco: espaço total, usado e disponível em GB, e o status de saúde do disco."""
    try:
        total, used, free = shutil.disk_usage(path)
    except FileNotFoundError:
        path = os.path.abspath(os.sep)  # Caminho raiz do sistema
        total, used, free = shutil.disk_usage(path)

    # Converte para GB
    total_gb = total / (1024 * 1024 * 1024)
    used_gb = used / (1024 * 1024 * 1024)
    free_gb = free / (1024 * 1024 * 1024)

    # Calcular o percentual de espaço livre
    free_percentage = (free / total) * 100

    # Avaliar a saúde do disco com base no espaço livre
    if free_percentage > 20:
        health_status = "Saudável"
    elif 10 < free_percentage <= 20:
        health_status = "Alerta"
    else:
        health_status = "Necessita Troca"

    # Print para depuração, verifica se a saúde do disco está sendo calculada corretamente
    print(f"Saúde do Disco: {health_status}")
    print(f"Espaço Total: {total_gb:.2f} GB | Espaço Usado: {used_gb:.2f} GB | Espaço Livre: {free_gb:.2f} GB")
    
    return total_gb, used_gb, free_gb, health_status

def print_report(path, threshold_mb=100):
    """Gera um relatório de uso de espaço e arquivos grandes."""
    total_size = get_size(path)
    large_files = list_large_files(path, threshold_mb)

    result = f"Uso total de espaço em '{path}': {total_size:.2f} MB\n"
    
    if large_files:
        result += "\nArquivos maiores que o limite especificado:\n"
        table = PrettyTable()
        table.field_names = ["Caminho do Arquivo", "Tamanho (MB)"]
        for file_path, file_size in large_files:
            table.add_row([file_path, f"{file_size:.2f} MB"])
        result += str(table)
    else:
        result += "\nNenhum arquivo grande encontrado."

    return result

def on_analyze():
    """Função para analisar o diretório e exibir o relatório."""
    path = entry_path.get()
    threshold = entry_threshold.get()

    # Verifica se o caminho está vazio
    if not path:
        messagebox.showerror("Erro", "Por favor, insira o caminho do diretório.")
        return

    # Verifica se o valor do limite está vazio ou não é um número
    try:
        threshold = float(threshold) if threshold else 100.0
    except ValueError:
        messagebox.showerror("Erro", "Por favor, insira um número válido para o limite de tamanho (em MB).")
        return

    # Gera o relatório e exibe na área de texto
    result = print_report(path, threshold)

    # Verifica a saúde do disco
    total_gb, used_gb, free_gb, health_status = check_disk_health(path)
    disk_health = (f"\nSaúde do Disco:\n"
                   f"Espaço Total: {total_gb:.2f} GB\n"
                   f"Espaço Usado: {used_gb:.2f} GB\n"
                   f"Espaço Livre: {free_gb:.2f} GB\n"
                   f"Status de Saúde: {health_status}")
    
    result += disk_health

    text_result.delete(1.0, END)  # Limpa a área de texto
    text_result.insert(END, result)  # Insere o resultado na área de texto

# Configuração da interface gráfica
root = Tk()
root.title("Analisador de Espaço em Disco")

# Labels
label_path = Label(root, text="Caminho do Diretório:")
label_path.pack(pady=5)

# Entry para o caminho do diretório
entry_path = Entry(root, width=50)
entry_path.pack(pady=5)

label_threshold = Label(root, text="Limite de Tamanho (MB, padrão 100MB):")
label_threshold.pack(pady=5)

# Entry para o limite de tamanho
entry_threshold = Entry(root, width=50)
entry_threshold.pack(pady=5)

# Botão para iniciar a análise
btn_analyze = Button(root, text="Analisar", command=on_analyze)
btn_analyze.pack(pady=10)

# Área de texto para exibir os resultados
text_result = Text(root, width=80, height=20)
text_result.pack(pady=10)

# Iniciar o loop da interface gráfica
root.mainloop()
