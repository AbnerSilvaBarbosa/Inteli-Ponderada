CREATE VIEW IF NOT EXISTS working_data_view AS
SELECT
    data_ingestao,
    JSONExtractString(dado_linha, 'title_en') AS manga_name,
    JSONExtractString(dado_linha, 'status') AS status,
    JSONExtractInt(dado_linha, 'year') AS year,
    JSONExtractString(dado_linha, 'content_rating') AS content_rating
FROM working_data;