from data_pipeline_abner.minio_client import  upload_file, download_file, list_files
from data_pipeline_abner.clickhouse_client import  get_client, insert_dataframe
from data_pipeline_abner.data_processing import process_data, prepare_dataframe_for_insert
from fetchs.fetch_manga import fetch_manga_data
import pandas as pd

def start_verification_for_storage():
    # Nome do arquivo esperado
    expected_filename = "manga_data.parquet"

    # Listar arquivos no bucket
    existing_files = list_files("raw-data")

    if expected_filename in existing_files:
        # Arquivo já existe, então baixar e usar o dado existente
        download_file("raw-data", expected_filename, f"downloaded_{expected_filename}")
        df_parquet = pd.read_parquet(f"downloaded_{expected_filename}")
        print("Arquivos ja existentes")
    else:
        # Arquivo não existe, então faz a requisição à API, processa e salva o dado
        
        # Executa o fetch
        url = "https://api.mangadex.dev/manga?limit=100&includedTagsMode=AND&excludedTagsMode=OR&contentRating%5B%5D=safe&contentRating%5B%5D=suggestive&contentRating%5B%5D=erotica&order%5BlatestUploadedChapter%5D=desc"
        response = fetch_manga_data(url)

        # Processar e salvar dados
        datas_api = process_data(response)  # Processa o dado recebido da API
        upload_file("raw-data", datas_api)

        # Baixar o arquivo Parquet do MinIO
        download_file("raw-data", datas_api, f"downloaded_{datas_api}")
        df_parquet = pd.read_parquet(f"downloaded_{datas_api}")

        # Preparar e inserir dados no ClickHouse
        df_prepared = prepare_dataframe_for_insert(df_parquet)
        client = get_client()  # Obter o cliente ClickHouse
        insert_dataframe(client, 'working_data', df_prepared)
        print("Arquivo salvado no storage :)")
