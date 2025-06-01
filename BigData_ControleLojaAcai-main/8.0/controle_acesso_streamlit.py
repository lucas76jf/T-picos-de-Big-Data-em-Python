"""
Açaí do Senna - Otimizador de Turnos

Este sistema permite a coleta, análise e visualização do fluxo de pessoas
por turno (manhã, tarde, noite) na loja Açaí do Senna, auxiliando na
otimização da alocação de funcionários e melhoria da experiência dos clientes.

Alunos:

• Marcos Vinicius Nascimento Pinto
• Lucas de Souza Faria
• Luís Arthur Belli Fernandes

Versão: 8.0

"""

# Importação das bibliotecas
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import traceback
from PIL import Image

# Constantes globais
TURNOS = ["Manhã", "Tarde", "Noite"]
DIAS_ORDENADOS = ["segunda-feira", "terça-feira", "quarta-feira", 
                 "quinta-feira", "sexta-feira", "sábado", "domingo"]
LOGO_PATH = "img/acai_do_senna_img.png"


class GerenciadorDados:
    """
    Classe responsável pelo gerenciamento de dados e operações com arquivos CSV.
    
    Attributes:
        data_file (str): Caminho para o arquivo de dados de movimento.
        escala_file (str): Caminho para o arquivo de escala de funcionários.
        relatorio_file (str): Caminho para o arquivo de relatório semanal.
    """
    
    def __init__(self, data_file="movimento_loja.csv", 
                 escala_file="escala_funcionarios.csv", 
                 relatorio_file="relatorio_semanal.csv"):
        """
        Inicializa o gerenciador de dados com os caminhos dos arquivos.
        
        Args:
            data_file (str): Caminho para o arquivo de dados de movimento.
            escala_file (str): Caminho para o arquivo de escala de funcionários.
            relatorio_file (str): Caminho para o arquivo de relatório semanal.
        """
        self.data_file = data_file
        self.escala_file = escala_file
        self.relatorio_file = relatorio_file
    
    def carregar_dados(self):
        """
        Carrega os dados do arquivo CSV de movimento.
        
        Returns:
            pandas.DataFrame: DataFrame com os dados carregados ou um DataFrame vazio
                             se o arquivo não existir.
        """
        try:
            if os.path.exists(self.data_file):
                # Usar parse_dates e format='mixed' para lidar com diferentes formatos de data
                df = pd.read_csv(self.data_file)
                
                # Garantir que a coluna de data seja do tipo datetime
                if 'data' in df.columns:
                    # Usar format='mixed' para permitir inferência de diferentes formatos
                    df['data'] = pd.to_datetime(df['data'], errors='coerce')
                    
                    # Verificar se há datas inválidas (NaT)
                    if df['data'].isna().any():
                        st.warning("Algumas datas no arquivo não puderam ser interpretadas corretamente.")
                        # Remover linhas com datas inválidas
                        df = df.dropna(subset=['data'])
                
                return df
            else:
                return pd.DataFrame(columns=["data", "dia_da_semana", "turno", "quantidade_pessoas"])
        except Exception as e:
            st.error(f"Erro ao carregar dados: {str(e)}")
            traceback.print_exc()
            return pd.DataFrame(columns=["data", "dia_da_semana", "turno", "quantidade_pessoas"])
    
    def verificar_duplicidade(self, data, turno):
        """
        Verifica se já existe um registro para a data e turno especificados.
        
        Args:
            data (str): Data no formato YYYY-MM-DD.
            turno (str): Turno do dia (Manhã, Tarde, Noite).
            
        Returns:
            bool: True se já existe um registro, False caso contrário.
        """
        df = self.carregar_dados()
        if df.empty:
            return False
        
        try:
            # Converter a data de entrada para o mesmo formato do DataFrame
            data_dt = pd.to_datetime(data, errors='coerce')
            if pd.isna(data_dt):
                return False
            
            # Verificar se já existe um registro para esta data e turno
            # Comparar apenas as datas (sem horas/minutos/segundos)
            return ((df['data'].dt.date == data_dt.date()) & (df['turno'] == turno)).any()
        except Exception as e:
            st.error(f"Erro ao verificar duplicidade: {str(e)}")
            traceback.print_exc()
            return False
    
    def salvar_dados(self, data, turno, quantidade):
        """
        Salva os dados de movimento no arquivo CSV.
        
        Args:
            data (str): Data no formato YYYY-MM-DD.
            turno (str): Turno do dia (Manhã, Tarde, Noite).
            quantidade (int): Quantidade de pessoas.
            
        Returns:
            tuple: (DataFrame atualizado, bool indicando sucesso, mensagem)
        """
        try:
            # Verificar se a data é futura
            data_dt = pd.to_datetime(data, errors='coerce')
            if pd.isna(data_dt):
                return None, False, "Formato de data inválido."
                
            if data_dt.date() > datetime.today().date():
                return None, False, "Não é possível registrar datas futuras."
            
            # Verificar duplicidade
            if self.verificar_duplicidade(data, turno):
                return None, False, "Já existe um registro para esta data e turno."
            
            # Carregar dados existentes ou criar novo DataFrame
            df = self.carregar_dados()
            
            # Traduzir o dia da semana
            dia_en = data_dt.day_name()
            dia_pt = self.traduzir_dia(dia_en)
            
            # Criar nova linha - usar formato ISO para a data para evitar problemas
            nova_linha = {
                "data": data_dt.strftime("%Y-%m-%d"),  # Formato ISO para evitar problemas
                "dia_da_semana": dia_pt,
                "turno": turno,
                "quantidade_pessoas": int(quantidade)
            }
            
            # Adicionar ao DataFrame e salvar
            df = pd.concat([df, pd.DataFrame([nova_linha])], ignore_index=True)
            
            # Garantir que a coluna de data seja do tipo datetime antes de salvar
            if 'data' in df.columns:
                df['data'] = pd.to_datetime(df['data'], errors='coerce')
                # Remover linhas com datas inválidas
                df = df.dropna(subset=['data'])
                # Converter para string no formato ISO antes de salvar
                df['data'] = df['data'].dt.strftime("%Y-%m-%d")
            
            # Salvar no formato CSV
            df.to_csv(self.data_file, index=False)
            
            # Reconverter para datetime após salvar para uso no restante do código
            if 'data' in df.columns:
                df['data'] = pd.to_datetime(df['data'])
            
            return df, True, "Registro salvo com sucesso!"
        except Exception as e:
            st.error(f"Erro ao salvar dados: {str(e)}")
            traceback.print_exc()
            return None, False, f"Erro ao salvar dados: {str(e)}"
    
    def traduzir_dia(self, dia_en):
        """
        Traduz o nome do dia da semana do inglês para o português.
        
        Args:
            dia_en (str): Nome do dia em inglês.
            
        Returns:
            str: Nome do dia em português.
        """
        traducoes = {
            "Monday": "segunda-feira",
            "Tuesday": "terça-feira",
            "Wednesday": "quarta-feira",
            "Thursday": "quinta-feira",
            "Friday": "sexta-feira",
            "Saturday": "sábado",
            "Sunday": "domingo"
        }
        return traducoes.get(dia_en, dia_en)
    
    def obter_dados_semana(self):
        """
        Obtém os dados da última semana.
        
        Returns:
            pandas.DataFrame: DataFrame com os dados da última semana.
        """
        df = self.carregar_dados()
        if df.empty:
            return df
        
        try:
            ultima_semana = datetime.today() - timedelta(days=7)
            # Garantir que a coluna de data seja do tipo datetime
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
            # Remover linhas com datas inválidas
            df = df.dropna(subset=['data'])
            return df[df['data'] >= ultima_semana]
        except Exception as e:
            st.error(f"Erro ao obter dados da semana: {str(e)}")
            traceback.print_exc()
            return pd.DataFrame(columns=["data", "dia_da_semana", "turno", "quantidade_pessoas"])


class AnaliseDados:
    """
    Classe responsável pelas análises e cálculos sobre os dados.
    
    Attributes:
        gerenciador (GerenciadorDados): Instância do gerenciador de dados.
    """
    
    def __init__(self, gerenciador):
        """
        Inicializa o analisador de dados.
        
        Args:
            gerenciador (GerenciadorDados): Instância do gerenciador de dados.
        """
        self.gerenciador = gerenciador
    
    def calcular_funcionarios(self, media_pessoas):
        """
        Determina o número ideal de funcionários com base na média de pessoas.
        
        Args:
            media_pessoas (float): Média de pessoas no período.
            
        Returns:
            int: Número recomendado de funcionários.
        """
        if media_pessoas < 25:
            return 1
        elif media_pessoas < 50:
            return 2
        elif media_pessoas < 100:
            return 3
        else:
            return 4
    
    def gerar_escala_funcionarios(self, df=None):
        """
        Gera a escala recomendada de funcionários com base nos dados de movimento.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame com os dados. Se None,
                                           carrega os dados do arquivo.
        
        Returns:
            pandas.DataFrame: DataFrame com a escala de funcionários.
        """
        try:
            if df is None:
                df = self.gerenciador.carregar_dados()
            
            if df.empty:
                return pd.DataFrame(columns=["dia_da_semana", "turno", "quantidade_pessoas", "funcionarios_necessarios"])
            
            # Garantir que a coluna de data seja do tipo datetime
            if 'data' in df.columns:
                df['data'] = pd.to_datetime(df['data'], errors='coerce')
                # Remover linhas com datas inválidas
                df = df.dropna(subset=['data'])
            
            # Agrupar por dia da semana e turno, calcular média de pessoas
            escala = df.groupby(["dia_da_semana", "turno"])["quantidade_pessoas"].mean().reset_index()
            
            # Calcular número de funcionários necessários
            escala["funcionarios_necessarios"] = escala["quantidade_pessoas"].apply(self.calcular_funcionarios)
            
            # Ordenar dias da semana
            escala['ordem'] = escala['dia_da_semana'].map({dia: i for i, dia in enumerate(DIAS_ORDENADOS)})
            escala = escala.sort_values(['ordem', 'turno']).drop('ordem', axis=1)
            
            # Salvar no arquivo
            try:
                escala.to_csv(self.gerenciador.escala_file, index=False)
            except Exception as e:
                st.warning(f"Não foi possível salvar a escala: {str(e)}")
            
            return escala
        except Exception as e:
            st.error(f"Erro ao gerar escala: {str(e)}")
            traceback.print_exc()
            return pd.DataFrame(columns=["dia_da_semana", "turno", "quantidade_pessoas", "funcionarios_necessarios"])
    
    
    def gerar_relatorio_semanal(self):
        """
        Gera o relatório semanal com dados agregados e insights.

        Returns:
            tuple: (DataFrame com resumo, turno mais movimentado, dia mais fraco)
        """
        try:
            hoje = datetime.today()
            inicio_semana = hoje - timedelta(days=hoje.weekday() + 7)  # Segunda anterior
            fim_semana = inicio_semana + timedelta(days=6)             # Domingo anterior

            df = self.gerenciador.carregar_dados()
            if df.empty:
                return (pd.DataFrame(columns=["dia_da_semana", "turno", "quantidade_pessoas", "funcionarios_recomendados"]), 
                        None, None)

            # Garantir tipo datetime
            df['data'] = pd.to_datetime(df['data'], errors='coerce')
            df = df.dropna(subset=['data'])

            # Filtrar para a semana completa anterior (segunda a domingo)
            df_semana = df[(df['data'] >= inicio_semana) & (df['data'] <= fim_semana)].copy()
            if df_semana.empty:
                return (pd.DataFrame(columns=["dia_da_semana", "turno", "quantidade_pessoas", "funcionarios_recomendados"]), 
                        None, None)

            # Agrupar por dia e turno
            resumo = df_semana.groupby(['dia_da_semana', 'turno'])['quantidade_pessoas'].mean().reset_index()
            resumo['funcionarios_recomendados'] = resumo['quantidade_pessoas'].apply(self.calcular_funcionarios)

            # Ordenar dias da semana
            resumo['ordem'] = resumo['dia_da_semana'].map({dia: i for i, dia in enumerate(DIAS_ORDENADOS)})
            resumo = resumo.sort_values(['ordem', 'turno']).drop('ordem', axis=1)

            # Determinar turno mais movimentado
            turno_mais_movimentado = resumo.loc[resumo['quantidade_pessoas'].idxmax()] if not resumo.empty else None

            # Calcular média por dia (incluindo zeros)
            media_por_dia = resumo.groupby('dia_da_semana')['quantidade_pessoas'].mean().reindex(DIAS_ORDENADOS).fillna(0)
            dia_mais_fraco = media_por_dia.idxmin()

            # Salvar relatório
            try:
                resumo.to_csv(self.gerenciador.relatorio_file, index=False)
            except Exception as e:
                st.warning(f"Não foi possível salvar o relatório: {str(e)}")

            return resumo, turno_mais_movimentado, dia_mais_fraco
        except Exception as e:
            st.error(f"Erro ao gerar relatório semanal: {str(e)}")
            traceback.print_exc()
            return (pd.DataFrame(columns=["dia_da_semana", "turno", "quantidade_pessoas", "funcionarios_recomendados"]), 
                    None, None)


class VisualizacaoDados:
    """
    Classe responsável pela geração de gráficos e visualizações.
    
    Attributes:
        gerenciador (GerenciadorDados): Instância do gerenciador de dados.
    """
    
    def __init__(self, gerenciador):
        """
        Inicializa o visualizador de dados.
        
        Args:
            gerenciador (GerenciadorDados): Instância do gerenciador de dados.
        """
        self.gerenciador = gerenciador
        self.cores = ['#9b59b6', '#3498db', '#e74c3c']  # Roxo, Azul, Vermelho
    
    def gerar_grafico(self, df=None):
        """
        Gera o gráfico de média de pessoas por dia e turno.
        
        Args:
            df (pandas.DataFrame, optional): DataFrame com os dados. Se None,
                                           carrega os dados do arquivo.
        
        Returns:
            matplotlib.figure.Figure: Figura com o gráfico gerado.
        """
        try:
            if df is None:
                df = self.gerenciador.carregar_dados()
            
            if df.empty:
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.text(0.5, 0.5, "Sem dados para exibir", 
                        horizontalalignment='center', verticalalignment='center',
                        transform=ax.transAxes, fontsize=14)
                return fig
            
            # Garantir que a coluna de data seja do tipo datetime
            if 'data' in df.columns:
                df['data'] = pd.to_datetime(df['data'], errors='coerce')
                # Remover linhas com datas inválidas
                df = df.dropna(subset=['data'])
            
            # Criar tabela pivô com médias por dia e turno
            pivot = df.pivot_table(values='quantidade_pessoas', 
                                  index='dia_da_semana', 
                                  columns='turno', 
                                  aggfunc='mean').fillna(0)
            
            # Garantir que todos os turnos estejam presentes
            for turno in TURNOS:
                if turno not in pivot.columns:
                    pivot[turno] = 0
            
            # Selecionar apenas os turnos padrão e na ordem correta
            pivot = pivot[TURNOS]
            
            # Ordenar dias da semana
            pivot = pivot.reindex(DIAS_ORDENADOS)
            
            # Criar figura e eixos
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Plotar gráfico de barras
            pivot.plot(kind='bar', ax=ax, color=self.cores)
            
            # Configurar título e rótulos
            ax.set_title("Média de Pessoas por Dia e Turno da Semana", fontsize=14)
            ax.set_xlabel("Dia da Semana", fontsize=12)
            ax.set_ylabel("Quantidade Média de Pessoas", fontsize=12)
            ax.legend(title="Turno")
            plt.xticks(rotation=45)
            
            # Adicionar rótulos nas barras
            for container in ax.containers:
                ax.bar_label(container, fmt='%.0f', label_type='edge', fontsize=8)
            
            plt.tight_layout()
            
            # Salvar o gráfico como imagem
            try:
                plt.savefig("grafico_turnos.png")
            except Exception as e:
                st.warning(f"Não foi possível salvar o gráfico: {str(e)}")
            
            return fig
        except Exception as e:
            st.error(f"Erro ao gerar gráfico: {str(e)}")
            traceback.print_exc()
            
            # Retornar um gráfico de erro
            fig, ax = plt.subplots(figsize=(10, 6))
            ax.text(0.5, 0.5, f"Erro ao gerar gráfico: {str(e)}", 
                    horizontalalignment='center', verticalalignment='center',
                    transform=ax.transAxes, fontsize=12, color='red')
            return fig


class InterfaceStreamlit:
    """
    Classe responsável pela interface do usuário usando Streamlit.
    
    Attributes:
        gerenciador (GerenciadorDados): Instância do gerenciador de dados.
        analise (AnaliseDados): Instância do analisador de dados.
        visualizacao (VisualizacaoDados): Instância do visualizador de dados.
    """
    
    def __init__(self):
        """Inicializa a interface do usuário."""
        self.gerenciador = GerenciadorDados()
        self.analise = AnaliseDados(self.gerenciador)
        self.visualizacao = VisualizacaoDados(self.gerenciador)
        
        # Configurar a página
        st.set_page_config(
            page_title="Açaí do Senna - Controle de Acesso",
            layout="centered",
            initial_sidebar_state="collapsed"
        )
    
    def exibir_cabecalho(self):
        """Exibe o cabeçalho da aplicação com logo e título."""
        # Layout com colunas para logo e título
        col1, col2 = st.columns([1, 3])
        
        # Exibir logo na primeira coluna
        try:
            with col1:
                if os.path.exists(LOGO_PATH):
                    logo = Image.open(LOGO_PATH)
                    st.image(logo, width=150)
                else:
                    st.warning("Logo não encontrada.")
        except Exception as e:
            st.error(f"Erro ao carregar logo: {str(e)}")
        
        # Exibir título na segunda coluna
        with col2:
            st.title("Otimizador de Turnos")
        
        # Informações sobre o projeto
        with st.expander("\U0001F4C4 Sobre o Projeto", expanded=True):
            st.markdown("""
            A empresa **Açaí do Senna** enfrenta desafios na identificação de horários estratégicos de operação.

            Este sistema foi desenvolvido em **Python** com uso de **pandas** e **Streamlit** para permitir a coleta, análise e visualização do fluxo de pessoas por turno (manhã, tarde, noite).

            Com isso, a empresa pode tomar decisões baseadas em dados, otimizar a alocação de funcionários e melhorar a experiência dos clientes.
            """)
    
    def exibir_formulario_registro(self):
        """Exibe o formulário para registro de movimento diário."""
        st.subheader("\U0001F4C5 Registrar Movimento Diário")
        
        with st.form("registro_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                data = st.date_input(
                    "Data do movimento",
                    max_value=datetime.today()
                )
            
            with col2:
                turno = st.selectbox("Turno do dia", TURNOS)
            
            quantidade = st.number_input(
                "Quantidade de Pessoas",
                min_value=0,
                max_value=1000,
                step=1,
                help="Informe a quantidade de pessoas que frequentaram a loja neste turno"
            )
            
            submitted = st.form_submit_button("Salvar Registro")
            
            if submitted:
                # Converter a data para string no formato ISO (YYYY-MM-DD)
                data_str = data.strftime("%Y-%m-%d")
                
                df, sucesso, mensagem = self.gerenciador.salvar_dados(
                    data_str,
                    turno,
                    quantidade
                )
                
                if sucesso:
                    st.success(f"\u2705 {mensagem}")
                    escala = self.analise.gerar_escala_funcionarios(df)
                    st.dataframe(escala, use_container_width=True)
                else:
                    st.error(f"\u274C {mensagem}")
    
    def exibir_visualizacoes(self):
        """Exibe as visualizações de dados se houver dados disponíveis."""
        df = self.gerenciador.carregar_dados()
        
        if not df.empty:
            # Exibir gráfico
            st.subheader("\U0001F4CA Gráfico de Média por Turno")
            fig = self.visualizacao.gerar_grafico(df)
            st.pyplot(fig)
            
            # Exibir escala de funcionários
            st.subheader("\U0001F4CB Escala Recomendada de Funcionários")
            try:
                escala = pd.read_csv(self.gerenciador.escala_file)
                st.dataframe(escala, use_container_width=True)
            except Exception:
                escala = self.analise.gerar_escala_funcionarios(df)
                st.dataframe(escala, use_container_width=True)
            
            # Exibir relatório semanal
            st.subheader("\U0001F4D1 Relatório Semanal de Movimento")
            resumo, turno_top, dia_fraco = self.analise.gerar_relatorio_semanal()
            
            if not resumo.empty:
                st.dataframe(resumo, use_container_width=True)
                
                if turno_top is not None:
                    st.markdown(f"**Turno mais movimentado:** {turno_top['dia_da_semana']} - {turno_top['turno']} com média de {turno_top['quantidade_pessoas']:.0f} pessoas")
                
                if dia_fraco is not None:
                    st.markdown(f"**Dia mais fraco da semana:** {dia_fraco}")
            else:
                st.info("Não há dados suficientes para gerar o relatório semanal.")
        else:
            st.info("Nenhum dado registrado ainda.")
    
    def exibir_opcoes_exportacao(self):
        """Exibe opções para exportação de dados."""
        df = self.gerenciador.carregar_dados()
        
        if not df.empty:
            st.subheader("\U0001F4BE Exportar Dados")
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Exportar CSV"):
                    # Garantir que a coluna de data esteja no formato ISO antes de exportar
                    if 'data' in df.columns:
                        df['data'] = pd.to_datetime(df['data'], errors='coerce')
                        df = df.dropna(subset=['data'])
                        df['data'] = df['data'].dt.strftime("%Y-%m-%d")
                    
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="Baixar CSV",
                        data=csv,
                        file_name="movimento_acai.csv",
                        mime="text/csv"
                    )
            
             
    def executar(self):
        """Executa a aplicação Streamlit."""
        self.exibir_cabecalho()
        self.exibir_formulario_registro()
        self.exibir_visualizacoes()
        self.exibir_opcoes_exportacao()


# Ponto de entrada da aplicação
if __name__ == "__main__":
    try:
        interface = InterfaceStreamlit()
        interface.executar()
    except Exception as e:
        st.error(f"Erro na aplicação: {str(e)}")
        st.error(traceback.format_exc())
