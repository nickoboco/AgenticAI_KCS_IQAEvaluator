import streamlit as st
import pandas as pd
from openai import OpenAI
import requests

import json
import html
from io import BytesIO

client = OpenAI(api_key=st.secrets['OPENAI_KEY'])

def consultar_procedimentos():
    url = f"{st.secrets['KCS_BASE_URL']}/api/consultar/listar"

    payload = json.dumps({
        "termo": "%%%","dominio": st.secrets['KCS_DOMINIO'],
        "pesquisaTags": "false", "pesquisaTitulo": "true",
        "pesquisaDescricao": "false", "ativo":"true"
    })

    headers = {
        'Content-Type': 'application/json',
        'Authorization': st.secrets['KCS_KEY']
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    if response.status_code == 200:
        return json.loads(response.text)
    else:
        st.error("Erro ao consultar a API")
        return []

def buscaKCS (id):
    url = f"{st.secrets['KCS_BASE_URL']}/api/consultar/buscar-detalhe-conhecimento"

    payload = json.dumps({
    "id": [id],
    "dominio": st.secrets['KCS_DOMINIO']
    })
    headers = {
    'Content-Type': 'application/json',
    'Authorization': st.secrets['KCS_KEY']
    }

    response = requests.request("POST", url, headers=headers, data=payload, verify=False)

    response_json = json.loads(response.text)

    def extrair_primeira_descricao(lista_resultados):
        for item in lista_resultados:
            descricao = item.get("descricao", "").strip()
            if descricao:  
                return html.unescape(descricao).replace("&nbsp;", " ").replace("\\n", "\n")
        return None 
    
    descricao_formatada = extrair_primeira_descricao(response_json)
    return descricao_formatada


def ajustar_descricao_gpt(texto_desconfigurado):
    prompt = (
        "O texto abaixo está desconfigurado. Por favor, ajuste a estrutura para que ele fique claro e legível, "
        "mantendo as informações originais organizadas em tópicos numerados, subtópicos, e adicionando quebras de linha apropriadas.\n\n"
        "Retorne somente com o texto ajustado, mantenha somente as informações originais."
        f"Texto desconfigurado:\n{texto_desconfigurado}\n\n"
        "Texto ajustado:"
    )

    try:
 
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": prompt}
            ]
        )

        texto_ajustado = completion.choices[0].message.content.strip()
        return texto_ajustado
    
    except Exception as e:
        st.error(f"Erro ao chamar a API OpenAI: {e}")
        return None

def carregar_prompt_com_variaveis(unicoartigo, descricao, ambiente, tags, titulo, resolucao, instrucoes):
    try:
        with open('avaliadorIQA.txt', 'r', encoding='utf-8') as file:
            promptSys = file.read()

    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {e}")
        return ""
        
    promptSys = promptSys.format(
        unicoartigo=unicoartigo,
        descricao=descricao,
        ambiente=ambiente,
        tags=tags,
        titulo=titulo,
        resolucao=resolucao,
        instrucoes=instrucoes
    )
    
    return promptSys

def avalia_IQA(promptUser):

    try:
 
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Você é um especialista KCS"},
                {"role": "user", "content": promptUser}
            ]
        )

        avaliacao = completion.choices[0].message.content.strip()
        return avaliacao
    
    except Exception as e:
        st.error(f"Erro ao chamar a API OpenAI: {e}")
        return None
    

st.title("Especialista IQA")

if 'procedimentos' not in st.session_state:
    if st.button('Carregar Procedimentos'):
        procedimentos = consultar_procedimentos()
        if procedimentos:
             st.session_state.procedimentos = sorted(procedimentos, key=lambda x: x['titulo'])
        else:
            st.session_state.procedimentos = []

if 'procedimentos' in st.session_state and st.session_state.procedimentos:

    status_opcoes = ['Todos'] + list(set([proc['status'] for proc in st.session_state.procedimentos]))
    status_selecionado = st.selectbox('Filtrar por Status', status_opcoes)

    if status_selecionado != 'Todos':
        procedimentos_filtrados = [proc for proc in st.session_state.procedimentos if proc['status'] == status_selecionado]
    else:
        procedimentos_filtrados = st.session_state.procedimentos

    opcoes = {proc['id']: proc['titulo'] for proc in procedimentos_filtrados}
    procedimento_selecionado = st.selectbox('Escolha um Procedimento', list(opcoes.values()))

    espaco_esquerda, coluna1, coluna2, espaco_direita = st.columns([1, 2, 2, 1])

    if coluna1.button('Consultar Detalhes'):

        id_selecionado = [id for id, titulo in opcoes.items() if titulo == procedimento_selecionado][0]

        procedimento = next((proc for proc in procedimentos_filtrados if proc['id'] == id_selecionado), None)
        st.session_state.procedimento = procedimento

        if procedimento:
            descricaoOriginal = buscaKCS(id_selecionado)
            descricao = ajustar_descricao_gpt(descricaoOriginal)
            st.session_state.descricao = descricao

            dados_procedimento = {
                'Campo': ['Título','ID', 'Descrição', 'Versão', 'Tipo', 'Público', 'Ambiente', 'Status', 'Empresa', 'Tags'],
                'Valor': [
                    procedimento.get('titulo', 'N/A'),
                    procedimento.get('id', 'N/A'),
                    procedimento.get('descricao', 'N/A'),
                    procedimento.get('versao', 'N/A'),
                    procedimento.get('tipo', 'N/A'),
                    procedimento.get('publico', 'N/A'),
                    procedimento.get('ambiente', 'N/A'),
                    procedimento.get('status', 'N/A'),
                    procedimento.get('empresa', 'N/A'),
                    procedimento.get('tags', 'N/A')
                    ]
                }
            st.subheader("Detalhes do Procedimento", divider="gray")
            st.subheader(procedimento.get('titulo', 'N/A'))
            st.write(descricao)

            df = pd.DataFrame(dados_procedimento)
            st.table(df)
        else:
            st.error("Detalhes não encontrados.")

    if coluna2.button('Avaliar com IA'):
        if 'descricao' and 'procedimento' in st.session_state:
            #st.write("Iniciando a avaliação com IA...")

            prompt_atualizado = carregar_prompt_com_variaveis(
                unicoartigo="Sim",
                descricao=st.session_state.procedimento.get('descricao', ''),
                ambiente=st.session_state.procedimento.get('ambiente', ''),
                tags=st.session_state.procedimento.get('tags', ''),
                titulo=st.session_state.procedimento.get('titulo', ''),
                resolucao=st.session_state.descricao,
                instrucoes=st.session_state.descricao
            )
            resultado = avalia_IQA(prompt_atualizado)
            #st.write(resultado)

            try:
                avaliacao = json.loads(resultado)
            except json.JSONDecodeError as e:
                st.error(f"Erro ao parsear o JSON: {e}")
                avaliacao = None

            if avaliacao:
                st.subheader("Resultado da Avaliação com IA")
                dados = [
                    {
                        "Critério": criterio,
                        "Nota": valores["nota"],
                        "Sugestão": valores["sugestão"] if valores["sugestão"] else "Nenhuma sugestão."
                    }
                    for criterio, valores in avaliacao.items() if criterio != "soma"
                ]

                df = pd.DataFrame(dados)
                soma_notas = df["Nota"].sum()
                st.table(df)
                st.write(f"Soma das notas: {soma_notas}")

                @st.cache_data
                def to_excel(df):
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False, sheet_name="Sheet1")
                    processed_data = output.getvalue()
                    return processed_data

                excel_data = to_excel(df)

                st.download_button(
                    label="Clique aqui para baixar o Excel",
                    data=excel_data,
                    file_name="IQA.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

            else:
                st.write("Não foi possível obter a avaliação.")

        else:
            st.error("Por favor, consulte os detalhes do procedimento antes de avaliar.")

else:
    st.write("Carregue os procedimentos clicando no botão acima.")