import tkinter as tk
from tkinter import messagebox
import math
import re

def clicar_botao(valor):
    """Adiciona o caractere clicado ao visor."""
    texto_atual = visor.get()
    visor.delete(0, tk.END)
    visor.insert(tk.END, texto_atual + str(valor))

def clicar_raiz():
    """Insere ou aplica a raiz quadrada ao valor atual."""
    texto_atual = visor.get()
    if not texto_atual or texto_atual[-1] in "+-*/(^":
        visor.insert(tk.END, "√(")
    else:
        # Envolve o valor atual no visor com √( ... )
        visor.delete(0, tk.END)
        visor.insert(tk.END, f"√({texto_atual})")

def limpar():
    """Limpa o visor."""
    visor.delete(0, tk.END)

def preparar_expressao(exp):
    """Traduz a expressão para uma sintaxe válida em Python."""
    exp = exp.strip()
    if not exp:
        return ""
    
    # 1. Radiciação
    # Caso 1: número colado antes da raiz (ex: 2√(9) -> 2 * √(9))
    exp = re.sub(r'(\d+(?:\.\d+)?)\s*√', r'\1 * √', exp)
    # Caso 2: √(x) -> math.sqrt(x)
    exp = exp.replace('√(', 'math.sqrt(')
    # Caso 3: √x (sem parênteses explícitos) -> math.sqrt(x)
    exp = re.sub(r'√(\d+(?:\.\d+)?)', r'math.sqrt(\1)', exp)
    
    # 2. Potenciação: ^ -> **
    exp = exp.replace('^', '**')
    
    # 3. Porcentagem
    # Caso A: A + B% ou A - B% -> A + (A * (B / 100))
    pattern_soma_sub = r'((?<![%\d])\d+(?:\.\d+)?|\([^\(\)]+\))\s*([+\-])\s*(\d+(?:\.\d+)?)%'
    while re.search(pattern_soma_sub, exp):
        exp = re.sub(pattern_soma_sub, r'\1 \2 (\1 * (\3 / 100))', exp)
    
    # Caso B: Outros casos de % (ex: 200 * 15%, 50%) -> (/ 100)
    exp = re.sub(r'(\d+(?:\.\d+)?)%', r'(\1 / 100)', exp)
    exp = re.sub(r'\)\s*%', r') / 100', exp)
    
    # Fecha parênteses que possam ter ficado abertos
    abertos = exp.count('(')
    fechados = exp.count(')')
    if abertos > fechados:
        exp += ')' * (abertos - fechados)
        
    return exp

def calcular():
    """Calcula a expressão matemática no visor."""
    expressao = visor.get()
    if not expressao.strip():
        return

    try:
        exp_preparada = preparar_expressao(expressao)
        # Avalia a expressão matemática de forma segura com acesso ao módulo math
        resultado = eval(exp_preparada, {"__builtins__": None, "math": math})
        
        # Formata números inteiros sem o .0 desnecessário
        if isinstance(resultado, float):
            resultado = round(resultado, 10)
            if resultado.is_integer():
                resultado = int(resultado)
                
        visor.delete(0, tk.END)
        visor.insert(tk.END, str(resultado))
    except ZeroDivisionError:
        messagebox.showerror("Erro", "Não é possível dividir por zero!")
        limpar()
    except ValueError:
        messagebox.showerror("Erro", "Não é possível calcular raiz de número negativo!")
        limpar()
    except Exception:
        messagebox.showerror("Erro", "Expressão inválida!")
        limpar()

# 1. Configuração da Janela Principal
janela = tk.Tk()
janela.title("Calculadora")
janela.geometry("320x480")
janela.resizable(False, False)
janela.configure(bg="#2b2b2b")

# 2. Visor da Calculadora
visor = tk.Entry(
    janela, 
    font=("Arial", 22), 
    bg="#1e1e1e", 
    fg="#ffffff", 
    bd=0, 
    justify="right"
)
visor.grid(row=0, column=0, columnspan=4, padx=12, pady=(20, 15), ipady=12, sticky="nsew")
visor.bind("<Return>", lambda event: calcular())

# 3. Lista de botões: (Texto, Linha, Coluna, Rowspan, Colspan, Cor de Fundo, Cor do Texto)
botoes = [
    ('C', 1, 0, 1, 1, '#d9534f', '#ffffff'), 
    ('(', 1, 1, 1, 1, '#4a4a4a', '#ffffff'), 
    (')', 1, 2, 1, 1, '#4a4a4a', '#ffffff'), 
    ('/', 1, 3, 1, 1, '#f0ad4e', '#ffffff'),
    
    ('√', 2, 0, 1, 1, '#4a4a4a', '#ffffff'), 
    ('^', 2, 1, 1, 1, '#4a4a4a', '#ffffff'), 
    ('%', 2, 2, 1, 1, '#4a4a4a', '#ffffff'), 
    ('*', 2, 3, 1, 1, '#f0ad4e', '#ffffff'),
    
    ('7', 3, 0, 1, 1, '#3a3a3a', '#ffffff'), 
    ('8', 3, 1, 1, 1, '#3a3a3a', '#ffffff'), 
    ('9', 3, 2, 1, 1, '#3a3a3a', '#ffffff'), 
    ('-', 3, 3, 1, 1, '#f0ad4e', '#ffffff'),
    
    ('4', 4, 0, 1, 1, '#3a3a3a', '#ffffff'), 
    ('5', 4, 1, 1, 1, '#3a3a3a', '#ffffff'), 
    ('6', 4, 2, 1, 1, '#3a3a3a', '#ffffff'), 
    ('+', 4, 3, 1, 1, '#f0ad4e', '#ffffff'),
    
    ('1', 5, 0, 1, 1, '#3a3a3a', '#ffffff'), 
    ('2', 5, 1, 1, 1, '#3a3a3a', '#ffffff'), 
    ('3', 5, 2, 1, 1, '#3a3a3a', '#ffffff'), 
    ('=', 5, 3, 2, 1, '#5cb85c', '#ffffff'),
    
    ('0', 6, 0, 1, 2, '#3a3a3a', '#ffffff'), 
    ('.', 6, 2, 1, 1, '#3a3a3a', '#ffffff'), 
]

# 4. Criando e posicionando os botões na tela
for item in botoes:
    texto, linha, coluna, rowspan, colspan, cor_bg, cor_fg = item
    
    if texto == '=':
        comando = calcular
    elif texto == 'C':
        comando = limpar
    elif texto == '√':
        comando = clicar_raiz
    else:
        comando = lambda t=texto: clicar_botao(t)

    btn = tk.Button(
        janela, 
        text=texto, 
        font=("Arial", 14, "bold"),
        bg=cor_bg, 
        fg=cor_fg, 
        bd=0, 
        activebackground="#555555",
        command=comando
    )
    btn.grid(row=linha, column=coluna, rowspan=rowspan, columnspan=colspan, padx=4, pady=4, sticky="nsew")

# Ajuste automático das proporções das linhas e colunas
for i in range(4):
    janela.grid_columnconfigure(i, weight=1)
for i in range(1, 7):
    janela.grid_rowconfigure(i, weight=1)

# Iniciar o loop da interface gráfica
if __name__ == "__main__":
    janela.mainloop()
