-- Queries for copying, transforming, and aggregating NHANES data
-- To a more patient history friendly format
-- Create name pool for random name generation

CREATE TABLE pool.first_name (id SMALLSERIAL, name VARCHAR, ethnicity VARCHAR, gender VARCHAR(1));

CREATE INDEX pool.ethnic_index_first ON pool.first_name (ethnicity);

CREATE TABLE pool.last_name (id SMALLSERIAL, name VARCHAR, ethnicity VARCHAR);

CREATE INDEX pool.ethnic_index_last ON pool.last_name (ethnicity);

-- Copy NHANES data in order to transform it to a more aggregate friendly format
-- Also filter for people over 18

CREATE SCHEMA nhanes_copy;
CREATE TABLE nhanes_copy.demo_l AS SELECT * FROM "Translated"."DEMO_L" WHERE "RIDAGEYR" >= 18;
CREATE TABLE nhanes_copy.demo_j AS SELECT * FROM "Translated"."DEMO_J" WHERE "RIDAGEYR" >= 18;
CREATE TABLE nhanes_copy.acq_l AS SELECT acq_l.* FROM "Translated"."ACQ_L" acq_l INNER JOIN nhanes_copy.demo_l ON (acq_l."SEQN" = demo_l."SEQN");
CREATE TABLE nhanes_copy.smq_l AS SELECT smq_l.* FROM "Translated"."SMQ_L" smq_l INNER JOIN nhanes_copy.demo_l ON (smq_l."SEQN" = demo_l."SEQN");
CREATE TABLE nhanes_copy.smqrtu_l AS SELECT smqrtu_l.* FROM "Translated"."SMQRTU_L" smqrtu_l INNER JOIN nhanes_copy.demo_l ON (smqrtu_l."SEQN" = demo_l."SEQN");
CREATE TABLE nhanes_copy.alq_l AS SELECT alq_l.* FROM "Translated"."ALQ_L" alq_l INNER JOIN nhanes_copy.demo_l ON (alq_l."SEQN" = demo_l."SEQN");
CREATE TABLE nhanes_copy.duq_j AS SELECT duq_j.* FROM "Translated"."DUQ_J" duq_j INNER JOIN nhanes_copy.demo_j ON (duq_j."SEQN" = demo_j."SEQN");


UPDATE nhanes_copy.demo_l
SET "RIDRETH3" = 
    CASE 
        WHEN "RIDRETH3" ILIKE 'Mexican%' OR "RIDRETH3" ILIKE 'Other Hispanic' THEN 'Hispanic' 
        WHEN "RIDRETH3" ILIKE '%Asian' THEN 'AAPI'
        WHEN "RIDRETH3" ILIKE '%Black' THEN 'Black' 
        WHEN "RIDRETH3" ILIKE '%White' THEN 'White' 
        ELSE 'Other/Multi-Racial' 
    END;

UPDATE nhanes_copy.acq_l
SET "ACD040" = 
    CASE 
        WHEN "ACD040" IN('Only Spanish,', 'More Spanish than English') THEN 'Spanish'
        WHEN "ACD040" IS NULL THEN NULL
        ELSE 'English'
    END;

UPDATE nhanes_copy.smq_l
SET "SMD650" = "SMD650" / 3 + 1;

UPDATE nhanes_copy.alq_l
SET "ALQ121" = NULL
WHERE "ALQ121" IN ('Don''t know', 'Refused');

UPDATE nhanes_copy.duq_j
SET "DUQ215U" = 
    CASE 
        WHEN "DUQ215U" IN ('Days', 'Weeks') THEN 'Current'
        WHEN "DUQ215U" IN ('Months', 'Years') THEN 'Former'
        ELSE "DUQ215U"
    END,
"DUQ270U" = 
    CASE 
        WHEN "DUQ270U" IN ('Days', 'Weeks') THEN 'Current'
        WHEN "DUQ270U" IN ('Months', 'Years') THEN 'Former'
        ELSE "DUQ270U"
    END,
"DUQ272" =
    CASE
        WHEN "DUQ272" ILIKE 'Don''t know' THEN NULL
        ELSE "DUQ272"
    END,
"DUQ310U" = 
    CASE 
        WHEN "DUQ310U" IN ('Days', 'Weeks') THEN 'Current'
        WHEN "DUQ310U" IN ('Months', 'Years') THEN 'Former'
        ELSE "DUQ310U"
    END,
"DUQ350U" = 
    CASE 
        WHEN "DUQ350U" IN ('Days', 'Weeks') THEN 'Current'
        WHEN "DUQ350U" IN ('Months', 'Years') THEN 'Former'
        ELSE "DUQ350U"
    END,
"DUQ352" =
    CASE
        WHEN "DUQ272" ILIKE 'Refused' THEN NULL
        ELSE "DUQ272"
    END;

-- Aggregate NHANES data to quickly generate randomized patient history

CREATE TABLE pool.nhanes_aggregated (
    id SERIAL PRIMARY KEY,
    field_name TEXT NOT NULL,
    value TEXT NOT NULL,
    gender VARCHAR(1),
    race TEXT,
    count INT NOT NULL,
    range_of_values BOOLEAN DEFAULT FALSE,
    mean NUMERIC,
    median NUMERIC,
    mode NUMERIC,
    stdev NUMERIC,
    variance NUMERIC,
    q1 NUMERIC,
    q2 NUMERIC GENERATED ALWAYS AS (median) STORED,
    q3 NUMERIC,
    is_int BOOLEAN DEFAULT FALSE
);

-- Race

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT
    'race' field_name,
    "RIDRETH3" value,
    COUNT(*) count
FROM nhanes_copy.demo_l
GROUP BY "RIDRETH3";

-- Age 

INSERT INTO pool.nhanes_aggregated (field_name, value, count, range_of_values, mean, median, mode, stdev, variance, q1, q3, is_int)
SELECT DISTINCT
    'age' field_name,
    '18 to 79' value,
    COUNT(*) count,
    TRUE range_of_values,
    AVG("RIDAGEYR") mean,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "RIDAGEYR") median,
    MODE() WITHIN GROUP (ORDER BY "RIDAGEYR") mode,
    STDDEV("RIDAGEYR") stdev,
    VARIANCE("RIDAGEYR") variance,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "RIDAGEYR") q1,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "RIDAGEYR") q3,
    TRUE is_int
FROM nhanes_copy.demo_l
WHERE "RIDAGEYR" >= 18 AND "RIDAGEYR" < 80;

-- Primary Language

INSERT INTO pool.nhanes_aggregated (field_name, value, count, race)
SELECT DISTINCT
    'primary_language' field_name,
    'English' value,
    COUNT(*) count,
    NULL
FROM nhanes_copy.acq_l
WHERE "ACD010A" = 'English'
UNION
SELECT DISTINCT
    'primary_language' field_name,
    'Other' value,
    COUNT(*) count,
    NULL
FROM nhanes_copy.acq_l
WHERE "ACD010C" = 'Other'
UNION
SELECT DISTINCT
    'primary_language' field_name,
    "ACD040" value,
    COUNT(*) count,
    'Hispanic' race
FROM nhanes_copy.acq_l
WHERE "ACD040" IS NOT NULL
GROUP BY "ACD040";

-- Tobacco Use

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'tobacco_former' field_name,
    "SMQ020" value,
    COUNT(*) count
FROM nhanes_copy.smq_l
WHERE "SMQ020" IN ('Yes', 'No') GROUP BY "SMQ020";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'tobacco_current' field_name,
    "SMQ040" value,
    COUNT(*) count
FROM nhanes_copy.smq_l
WHERE "SMQ040" IN ('Every day', 'Some days', 'Not at all') GROUP BY "SMQ040";

INSERT INTO pool.nhanes_aggregated (field_name, value, count, range_of_values, mean, median, mode, stdev, variance, q1, q3, is_int)
SELECT DISTINCT
    'tobacco_pack_per_day' field_name,
    '1 to 5' value,
    COUNT(*) count,
    TRUE range_of_values,
    AVG("SMD650") mean,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "SMD650") median,
    MODE() WITHIN GROUP (ORDER BY "SMD650") mode,
    STDDEV("SMD650") stdev,
    VARIANCE("SMD650") variance,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "SMD650") q1,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "SMD650") q3,
    TRUE is_int
FROM nhanes_copy.smq_l
WHERE "SMD650" IS NOT NULL;

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'tobacco_last_few_days' field_name,
    "SMQ681" value,
    COUNT(*) count
FROM nhanes_copy.smqrtu_l
WHERE "SMQ681" ILIKE 'Yes' GROUP BY "SMQ681";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'tobacco_cigarettes' field_name,
    "SMQ690A" value,
    COUNT(*) count
FROM nhanes_copy.smqrtu_l
WHERE "SMQ690A" ILIKE 'Cigarettes' GROUP BY "SMQ690A";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'tobacco_pipes' field_name,
    "SMQ690B" value,
    COUNT(*) count
FROM nhanes_copy.smqrtu_l
WHERE "SMQ690B" ILIKE 'Pipes' GROUP BY "SMQ690B";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'tobacco_cigars' field_name,
    "SMQ690C" value,
    COUNT(*) count
FROM nhanes_copy.smqrtu_l
WHERE "SMQ690C" ILIKE 'Cigar%' GROUP BY "SMQ690C";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'tobacco_hookah' field_name,
    "SMQ690G" value,
    COUNT(*) count
FROM nhanes_copy.smqrtu_l
WHERE "SMQ690G" ILIKE 'Water%' GROUP BY "SMQ690G";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'tobacco_e_cig' field_name,
    "SMQ846" value,
    COUNT(*) count
FROM nhanes_copy.smqrtu_l
WHERE "SMQ846" in ('Yes', 'No') GROUP BY "SMQ846";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'tobacco_smokeless' field_name,
    "SMQ851" value,
    COUNT(*) count
FROM nhanes_copy.smqrtu_l
WHERE "SMQ851" in ('Yes', 'No') GROUP BY "SMQ851";

-- Alcohol Use

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'alcohol_ever' field_name,
    "ALQ111" value,
    COUNT(*) count
FROM nhanes_copy.alq_l
WHERE "ALQ111" in ('Yes', 'No') GROUP BY "ALQ111";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'alcohol_frequency' field_name,
    "ALQ121" value,
    COUNT(*) count
FROM nhanes_copy.alq_l
WHERE "ALQ121" IS NOT NULL GROUP BY "ALQ121";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'alcohol_drinks_per_day' field_name,
    "ALQ130" value,
    COUNT(*) count
FROM nhanes_copy.alq_l
WHERE "ALQ130" IS NOT NULL AND "ALQ130" >= 15 
GROUP BY "ALQ130";

INSERT INTO pool.nhanes_aggregated (field_name, value, count, range_of_values, mean, median, mode, stdev, variance, q1, q3, is_int)
SELECT DISTINCT
    'alcohol_drink_per_day' field_name,
    '1 to 14' value,
    COUNT(*) count,
    TRUE range_of_values,
    AVG("ALQ130") mean,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY "ALQ130") median,
    MODE() WITHIN GROUP (ORDER BY "ALQ130") mode,
    STDDEV("ALQ130") stdev,
    VARIANCE("ALQ130") variance,
    PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY "ALQ130") q1,
    PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY "ALQ130") q3,
    TRUE is_int
FROM nhanes_copy.alq_l
WHERE "ALQ130" IS NOT NULL AND "ALQ130" < 15;

-- Drug Use

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_marijuana' field_name,
    "DUQ200" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ200" IN ('Yes', 'No') GROUP BY "DUQ200";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_marijuana_current' field_name,
    "DUQ215U" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ215U" IS NOT NULL GROUP BY "DUQ215U";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_marijuana_frequency' field_name,
    trim(substring("DUQ217", '[^\(]*')) value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ217" IS NOT NULL GROUP BY "DUQ217";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_used_hard_drugs' field_name,    
    "DUQ240" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ240" IN ('Yes', 'No') GROUP BY "DUQ240";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_cocaine' field_name,    
    "DUQ250" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ250" IN ('Yes', 'No') GROUP BY "DUQ250";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_cocaine_current' field_name,
    "DUQ270U" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ270U" IS NOT NULL GROUP BY "DUQ270U";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_cocaine_frequency' field_name,
    "DUQ272" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ272" IS NOT NULL GROUP BY "DUQ272";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_heroin' field_name,    
    "DUQ290" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ290" IN ('Yes', 'No') GROUP BY "DUQ290";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_heroin_current' field_name,
    "DUQ310U" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ310U" IS NOT NULL GROUP BY "DUQ310U";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_meth' field_name,    
    "DUQ330" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ330" IN ('Yes', 'No') GROUP BY "DUQ330";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_meth_current' field_name,
    "DUQ350U" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ350U" IS NOT NULL GROUP BY "DUQ350U";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_meth_frequency' field_name,
    "DUQ352" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ352" IS NOT NULL GROUP BY "DUQ352";

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'drugs_ivdu' field_name,    
    "DUQ370" value,
    COUNT(*) count
FROM nhanes_copy.duq_j
WHERE "DUQ370" IN ('Yes', 'No') GROUP BY "DUQ370";

-- Education

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'education' field_name,
    "DMDEDUC2" value,
    COUNT(*) count
FROM nhanes_copy.demo_l
WHERE "DMDEDUC2" IS NOT NULL AND "DMDEDUC2" != 'Don''t know'
GROUP BY "DMDEDUC2";

-- Marital Status

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'marital_status' field_name,
    "DMDMARTZ" value,
    COUNT(*) count
FROM nhanes_copy.demo_l
WHERE "DMDMARTZ" IS NOT NULL AND "DMDMARTZ" NOT IN ('Don''t know', 'Refused')
GROUP BY "DMDMARTZ";

-- Children (using J since L doesn't have this info)

INSERT INTO pool.nhanes_aggregated (field_name, value, count)
SELECT DISTINCT 
    'children' field_name,
    CASE WHEN left("DMDHHSZA", 1)::int + left("DMDHHSZB", 1)::int >= 3 THEN '3 or more'
        ELSE  (left("DMDHHSZA", 1)::int + left("DMDHHSZB", 1)::int)::text
    END value,
    COUNT(*) count
FROM nhanes_copy.demo_j
GROUP BY value;

