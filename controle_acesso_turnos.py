
import pandas as pd
import matplotlib.pyplot as plt
from tkinter import Tk, Label, Entry, Button, messagebox, StringVar, OptionMenu
from datetime import datetime
import os

DATA_FILE = "movimento_loja.csv"
ESCALA_FILE = "escala_funcionarios.csv"

def calcular_funcionarios(media_pessoas):
    if media_pessoas < 25: #50
        return 1
    elif media_pessoas < 50: #100
        return 2
    elif media_pessoas < 100: #200
        return 3
    else:
        return 4

def salvar_dados(data, turno, quantidade):
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["data", "dia_da_semana", "turno", "quantidade_pessoas"])
    
    dia_da_semana = pd.to_datetime(data).day_name()
    nova_linha = {"data": data, "dia_da_semana": dia_da_semana, "turno": turno, "quantidade_pessoas": int(quantidade)}
    df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)
    return df

def gerar_grafico(df):
    pivot = df.pivot_table(values='quantidade_pessoas', index='dia_da_semana', columns='turno', aggfunc='mean').fillna(0)
    dias_ordenados = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    pivot = pivot.reindex(dias_ordenados)

    pivot.plot(kind='bar', figsize=(12, 7))
    plt.title("Média de Pessoas por Dia e Turno da Semana")
    plt.xlabel("Dia da Semana")
    plt.ylabel("Quantidade Média de Pessoas")
    plt.xticks(rotation=45)
    plt.legend(title="Turno")
    plt.tight_layout()
    plt.savefig("grafico_turnos.png")
    plt.close()

def gerar_escala_funcionarios(df):
    escala = df.groupby(["dia_da_semana", "turno"])["quantidade_pessoas"].mean().reset_index()
    escala["funcionarios_necessarios"] = escala["quantidade_pessoas"].apply(calcular_funcionarios)
    escala.to_csv(ESCALA_FILE, index=False)

def enviar():
    data = entry_data.get()
    turno = turno_var.get()
    quantidade = entry_quantidade.get()
    try:
        datetime.strptime(data, "%Y-%m-%d")
        quantidade = int(quantidade)
        df = salvar_dados(data, turno, quantidade)
        gerar_grafico(df)
        gerar_escala_funcionarios(df)
        messagebox.showinfo("Sucesso", "Dados salvos, gráfico e escala atualizados!")
    except ValueError:
        messagebox.showerror("Erro", "Data inválida ou quantidade não numérica.")

root = Tk()
root.title("Controle de Acesso - Loja de Açaí por Turno")

Label(root, text="Data (AAAA-MM-DD):").grid(row=0, column=0, padx=10, pady=10)
entry_data = Entry(root)
entry_data.grid(row=0, column=1, padx=10, pady=10)

Label(root, text="Turno:").grid(row=1, column=0, padx=10, pady=10)
turno_var = StringVar(root)
turno_var.set("Manhã")  # valor padrão
turno_menu = OptionMenu(root, turno_var, "Manhã", "Tarde", "Noite")
turno_menu.grid(row=1, column=1, padx=10, pady=10)

Label(root, text="Quantidade de Pessoas:").grid(row=2, column=0, padx=10, pady=10)
entry_quantidade = Entry(root)
entry_quantidade.grid(row=2, column=1, padx=10, pady=10)

Button(root, text="Enviar", command=enviar).grid(row=3, column=0, columnspan=2, pady=20)

root.mainloop()
