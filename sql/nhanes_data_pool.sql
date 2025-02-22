CREATE TABLE pool.nhanes_patient_seqn (
    seqn INT PRIMARY KEY,
    table_suffix VARCHAR(10)
);

INSERT INTO pool.nhanes_patient_seqn
SELECT DISTINCT seqn, suffix FROM (
    SELECT a."SEQN" AS seqn, NULL AS suffix FROM "DEMO" a WHERE "RIDAGEYR" >= 18 and "RIDAGEYR" < 80
    UNION
    SELECT b."SEQN" AS seqn, '_B' AS suffix from "DEMO_B" b WHERE "RIDAGEYR" >= 18 and "RIDAGEYR" < 80
    UNION
    SELECT c."SEQN" AS seqn, '_C' AS suffix from "DEMO_C" c WHERE "RIDAGEYR" >= 18 and "RIDAGEYR" < 80
    UNION
    SELECT d."SEQN" AS seqn, '_D' AS suffix from "DEMO_D" d WHERE "RIDAGEYR" >= 18 and "RIDAGEYR" < 80
    UNION
    SELECT e."SEQN" AS seqn, '_E' AS suffix from "DEMO_E" e WHERE "RIDAGEYR" >= 18 and "RIDAGEYR" < 80
    UNION
    SELECT f."SEQN" AS seqn, '_F' AS suffix from "DEMO_F" f WHERE "RIDAGEYR" >= 18 and "RIDAGEYR" < 80
    UNION
    SELECT g."SEQN" AS seqn, '_G' AS suffix from "DEMO_G" g WHERE "RIDAGEYR" >= 18 and "RIDAGEYR" < 80
    UNION
    SELECT h."SEQN" AS seqn, '_H' AS suffix from "DEMO_H" h WHERE "RIDAGEYR" >= 18 and "RIDAGEYR" < 80
    UNION
    SELECT i."SEQN" AS seqn, '_I' AS suffix from "DEMO_I" i WHERE "RIDAGEYR" >= 18 and "RIDAGEYR" < 80
    UNION
    SELECT j."SEQN" AS seqn, '_J' AS suffix from "DEMO_J" j WHERE "RIDAGEYR" >= 18 and "RIDAGEYR" < 80
    UNION
    SELECT l."SEQN" AS seqn, '_L' AS suffix from "DEMO_L" l WHERE "RIDAGEYR" >= 18 and "RIDAGEYR" < 80)
ORDER BY seqn;
