import pytest
import pandas as pd
import os
from data_pipeline_abner.data_processing import process_data, prepare_dataframe_for_insert

# Dados de exemplo para os testes
test_data = {
    "data": [
        {
            "id": "1",
            "attributes": {
                "title": {"en": "Test Manga"},
                "originalLanguage": "ja",
                "status": "Ongoing",
                "year": "2020",
                "contentRating": "Safe",
                "description": {"en": "Test description"},
                "lastChapter": "10",
                "lastVolume": "5",
                "createdAt": "2020-01-01T00:00:00Z",
                "updatedAt": "2021-01-01T00:00:00Z",
                "latestUploadedChapter": "10",
                "availableTranslatedLanguages": ["en", "fr"],
                "tags": [{"attributes": {"name": {"en": "Action"}}}]
            }
        }
    ]
}

def test_process_data():
    # Testa se o process_data retorna um arquivo Parquet
    filename = process_data(test_data)
    assert filename == "manga_data.parquet"
    # Verifica se o arquivo foi criado
    assert os.path.exists(filename)

    # Carrega o arquivo Parquet e verifica o conteúdo
    df = pd.read_parquet(filename)
    assert not df.empty

def test_prepare_dataframe_for_insert():
    # Cria um DataFrame de exemplo
    df = pd.DataFrame({
        'id': ['1'],
        'title_en': ['Test Manga'],
        'original_language': ['ja'],
        'status': ['Ongoing'],
        'year': [2020],
        'content_rating': ['Safe'],
        'description_en': ['Test description'],
        'last_chapter': ['10'],
        'last_volume': ['5'],
        'created_at': ['2020-01-01T00:00:00Z'],
        'updated_at': ['2021-01-01T00:00:00Z'],
        'latest_uploaded_chapter': ['10'],
        'available_translated_languages': ['en,fr'],
        'tags': ['Action']
    })

    # Testa a preparação do DataFrame
    df_prepared = prepare_dataframe_for_insert(df)
    assert 'data_ingestao' in df_prepared.columns
    assert 'dado_linha' in df_prepared.columns
    assert 'tag' in df_prepared.columns
    assert df_prepared['data_ingestao'].notnull().all()
