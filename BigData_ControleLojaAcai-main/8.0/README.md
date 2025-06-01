
# 🟣 Açaí do Senna - Controle de Acesso

Sistema em Python com Streamlit para **registrar**, **visualizar** e **analisar** o fluxo de pessoas por turno (manhã, tarde, noite) em uma loja. Gera relatórios semanais automáticos e recomendações de escala.

---

## ✅ Pré-requisitos

1. **Python 3.10 ou superior**
2. **pip** (gerenciador de pacotes do Python)
3. **Internet** (para instalação de bibliotecas)

Verifique se o Python está instalado:

```bash
python --version
```

Se não estiver, baixe em: [https://www.python.org/downloads/](https://www.python.org/downloads/)

---

## 🔧 Instalação dos Pacotes

Navegue até a pasta do projeto e execute:

```bash
pip install streamlit pandas matplotlib pillow
```

---

## 📁 Estrutura Esperada

```
controle_acesso_streamlit.py
movimento_loja.csv
escala_funcionarios.csv
relatorio_semanal.csv
grafico_turnos.png
iniciar_acesso_acai.bat
img/
 └── acai_do_senna_img.png
```

A pasta `img` deve conter a logo do projeto.

---

## ▶️ Como Executar

Na pasta do projeto, digite no terminal (Prompt de Comando):

```bash
streamlit run controle_acesso_streamlit.py
```

Ou clique duas vezes no arquivo:
```
iniciar_acesso_acai.bat
```

Isso abrirá o sistema no navegador padrão.

---

## 📊 Funcionalidades

- Registro diário de fluxo por turno
- Visualização em gráfico por dia e turno
- Escala recomendada de funcionários
- Relatório semanal (segunda a domingo)
- Exportação de dados para CSV

---

## 📌 Observações

- O sistema considera sempre a **semana anterior completa (segunda a domingo)**.
- Se um dia da semana não tiver dados, ele é tratado como movimento zero.

---

Sistema desenvolvido por:

**Marcos Vinicius Nascimento Pinto**  
**Lucas de Souza Faria**  
**Luís Arthur Belli Fernandes**
