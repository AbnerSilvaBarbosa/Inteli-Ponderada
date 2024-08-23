SELECT
    manga_name,
    status,
    year,
    content_rating
FROM
    working_data_view
WHERE
    manga_name = '{manga_name}'
