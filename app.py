import os
import streamlit as st
import json
import traceback
import base64
from pathlib import Path
from engine import extract_text_from_pdf, process_text, create_docx_from_json

# Função para adicionar uma imagem de fundo a partir de um arquivo local
def add_bg_from_local(image_file):
    """
    Adiciona uma imagem de fundo ao aplicativo Streamlit a partir de um arquivo local.
    Args:
    image_file (str): Caminho para o arquivo de imagem local.
    """
    with Path(image_file).open("rb") as file:
        encoded_string = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url(data:image/png;base64,{encoded_string});
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# Função para exibir uma imagem de logo no topo a partir de um arquivo local
def add_logo_from_local(logo_file):
    """
    Exibe uma imagem de logo no topo do aplicativo Streamlit a partir de um arquivo local.
    Args:
    logo_file (str): Caminho para o arquivo de imagem do logo.
    """
    with Path(logo_file).open("rb") as file:
        encoded_string = base64.b64encode(file.read()).decode()
    st.markdown(
        f"""
        <style>
        [data-testid="stAppViewContainer"] > .main {{
            padding-top: 0px;
        }}
        .logo-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 1rem 0;
        }}
        .logo-container img {{
            max-width: 200px;
            height: auto;
        }}
        </style>
        <div class="logo-container">
            <img src="data:image/png;base64,{encoded_string}" alt="Logo">
        </div>
        """,
        unsafe_allow_html=True
    )

# Função principal do aplicativo
def main():
    # Configuração da página
    st.set_page_config(page_title="Conversor de CV PDF para DOCX", page_icon="📄", layout="centered")

    # Aplicar imagens de fundo e logo
    add_bg_from_local("bg.png")      # Definir imagem de fundo
    add_logo_from_local("logo.png")  # Exibir logo no topo
    
    # Título e descrição da página com layout aprimorado
    st.markdown(
        "<h1 style='text-align: center; color: #4A9;'>Conversor de Currículo</h1>", 
        unsafe_allow_html=True
    )
    st.markdown(
        "<p style='text-align: center; font-size: 16px; color: #5A5A5A;'>"
        "O jeito mais fácil de formatar seu currículo em um documento Word!</p>",
        unsafe_allow_html=True
    )

    # Usando formulário para upload de arquivo e submissão
    with st.form(key="upload_form"):
        # Upload do arquivo com texto explicativo
        uploaded_file = st.file_uploader(
            label="Envie seu currículo em PDF",
            type="pdf",
            help="Apenas arquivos em PDF são suportados. Verifique se o arquivo está legível e abaixo de 5MB."
        )
        
        # Botão de submissão do formulário
        submit_button = st.form_submit_button(label="Converter currículo")

    # Processo após a submissão do formulário
    if submit_button and uploaded_file:
        st.markdown("---")
        
        # Seção de indicador de progresso
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Processo de conversão com indicador de carregamento para UX aprimorada
        with st.spinner("Convertendo o seu PDF..."):
            try:
                # Salvar o PDF temporariamente
                with open("temp_uploaded_cv.pdf", "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                # Etapa 1: Extração de texto
                status_text.text("Etapa 1: Extraindo texto do PDF...")
                progress_bar.progress(20)
                pdf_text = extract_text_from_pdf("temp_uploaded_cv.pdf")
                
                if not pdf_text:
                    st.error("Não foi possível extrair texto do PDF. Verifique o arquivo e tente novamente.")
                    return
                
                # Etapa 2: Processamento do texto
                status_text.text("Etapa 2: Processando o texto do currículo...")
                progress_bar.progress(50)
                json_data = process_text(pdf_text)

                # Opcional: Salvar JSON para depuração
                with open('extracted_resume_data.json', 'w', encoding='utf-8') as f:
                    json.dump(json_data, f, indent=2)
                
                # Etapa 3: Criando documento Word
                status_text.text("Etapa 3: Convertendo texto para formato Word...")
                progress_bar.progress(80)
                output_filename = "curriculo_convertido.docx"
                create_docx_from_json('extracted_resume_data.json', output_filename)
                
                # Etapa 4: Conclusão
                progress_bar.progress(100)
                st.success("Conversão concluída com sucesso! Baixe seu currículo abaixo.")
                
                # Botão de download com instruções claras
                st.markdown("### 📥 Baixe o currículo formatado")
                with open(output_filename, "rb") as file:
                    st.download_button(
                        label="Baixar currículo em DOCX",
                        data=file.read(),
                        file_name="Curriculo_Formatado.docx",
                        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                    )
                
                # Limpar arquivos temporários
                os.remove("temp_uploaded_cv.pdf")
                os.remove(output_filename)
            
            except Exception as e:
                st.error(f"Ocorreu um erro: {e}")
                st.error(traceback.format_exc())
            
            finally:
                # Garantir a limpeza dos arquivos temporários
                if os.path.exists("temp_uploaded_cv.pdf"):
                    os.remove("temp_uploaded_cv.pdf")
                if os.path.exists("extracted_resume_data.json"):
                    os.remove("extracted_resume_data.json")

# Executar o aplicativo Streamlit
if __name__ == "__main__":
    main()
