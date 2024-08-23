from flask import Flask, request, jsonify
from data_pipeline_abner.minio_client import create_bucket_if_not_exists
from data_pipeline_abner.clickhouse_client import execute_sql_script,execute_sql_script_with_params
from data_pipeline_abner.start_script import start_verification_for_storage

app = Flask(__name__)

# Criar bucket se não existir
create_bucket_if_not_exists("raw-data")

# Executar o script SQL para criar as tabelas
execute_sql_script('sql/create_table.sql')
execute_sql_script('sql/create_table_view.sql')

start_verification_for_storage()

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