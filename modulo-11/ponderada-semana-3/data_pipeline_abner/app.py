from flask import Flask, request, jsonify
from datetime import datetime
from data_pipeline_abner.minio_client import create_bucket_if_not_exists, upload_file, download_file, list_files
from data_pipeline_abner.clickhouse_client import execute_sql_script, get_client, insert_dataframe,execute_sql_script_with_params
from data_pipeline_abner.data_processing import process_data, prepare_dataframe_for_insert
from fetchs.fetch_manga import fetch_manga_data
import pandas as pd

app = Flask(__name__)

# Criar bucket se não existir
create_bucket_if_not_exists("raw-data")

# Executar o script SQL para criar as tabelas
execute_sql_script('sql/create_table.sql')
execute_sql_script('sql/create_table_view.sql')

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




@app.route('/data', methods=['POST'])
def get_manga_info():

    data = request.get_json()

    if not data or 'name' not in data:
        return jsonify({"error": "Formato de dados inválido"}), 400

    manga_name = data['name']

    try:
        params = {'manga_name':manga_name}
        result = execute_sql_script_with_params("sql/select_view.sql",params)

        if not result:
            return jsonify({"error": "Mangá não encontrado"}), 404
        
        print(result)

        # Formatar a resposta
        response_data = {
            "manga_name": result[0],
            "status": result[1],
            "year": result[2],
            "content_rating": result[3],
        }

        return jsonify(response_data), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)