CREATE TABLE pool.nhanes_data_pool (
id BIGSERIAL PRIMARY KEY, 
value VARCHAR, 
count INTEGER NOT NULL, 
total INTEGER NOT NULL, 
percent NUMERIC GENERATED ALWAYS AS (ROUND((count::NUMERIC / total::NUMERIC) * 100, 2)) STORED, 
ref_table VARCHAR NOT NULL, 
ref_column VARCHAR NOT NULL,
field_name VARCHAR NOT NULL
);

INSERT INTO nhanes_data_pool (value, count, total, ref_table, ref_column, field_name) 
SELECT ":column", count(*), (SELECT count(*) FROM "Translated".":table"), ':table', ':column', "SasLabel" 
FROM "Translated".":table" INNER JOIN "Metadata"."QuestionnaireVariables" ON ("Variable" ILIKE ':column' AND "TableName" ILIKE ':table')  
group by ":column", "SasLabel";
