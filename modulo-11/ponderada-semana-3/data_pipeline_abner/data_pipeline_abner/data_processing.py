import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from datetime import datetime

def process_data(data):
    # Extrair informações relevantes do JSON
    manga_list = []
    
    for manga in data['data']:
        manga_info = {
            'id': manga['id'],
            'title_en': manga['attributes']['title'].get('en', ''),
            'original_language': manga['attributes']['originalLanguage'],
            'status': manga['attributes']['status'],
              'year': int(manga['attributes']['year']) if manga['attributes']['year'] else None,  # Converte para inteiro se não for None
            'content_rating': manga['attributes']['contentRating'],
            'description_en': manga['attributes']['description'].get('en', ''),
            'last_chapter': manga['attributes']['lastChapter'],
            'last_volume': manga['attributes']['lastVolume'],
            'created_at': manga['attributes']['createdAt'],
            'updated_at': manga['attributes']['updatedAt'],
            'latest_uploaded_chapter': manga['attributes']['latestUploadedChapter'],
            'available_translated_languages': ','.join(manga['attributes']['availableTranslatedLanguages']),
            'tags': ','.join([tag['attributes']['name']['en'] for tag in manga['attributes']['tags']])
        }
        manga_list.append(manga_info)
        
    # Criar DataFrame com as informações extraídas
    df = pd.DataFrame(manga_list)
    
    # Definir nome do arquivo Parquet
    filename = "manga_data.parquet"
    
    # Converter o DataFrame para uma tabela Arrow e salvar como Parquet
    table = pa.Table.from_pandas(df)
    pq.write_table(table, filename)
    
    return filename

def prepare_dataframe_for_insert(df):
    df['data_ingestao'] = datetime.now()
    df['dado_linha'] = df.apply(lambda row: row.to_json(), axis=1)
    df['tag'] = 'example_tag'
    return df[['data_ingestao', 'dado_linha', 'tag']]