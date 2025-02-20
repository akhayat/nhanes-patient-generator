CREATE TABLE pool.nhanes_patient_seqn (
    seqn INT PRIMARY KEY,
    table_suffix VARCHAR(10)
);

INSERT INTO pool.nhanes_patient_seqn
SELECT DISTINCT seqn, suffix FROM (
    SELECT a."SEQN" AS seqn, NULL AS suffix FROM "DEMO" a
    UNION
    SELECT b."SEQN" AS seqn, '_B' AS suffix from "DEMO_B" b
    UNION
    SELECT c."SEQN" AS seqn, '_C' AS suffix from "DEMO_C" c
    UNION
    SELECT d."SEQN" AS seqn, '_D' AS suffix from "DEMO_D" d
    UNION
    SELECT e."SEQN" AS seqn, '_E' AS suffix from "DEMO_E" e
    UNION
    SELECT f."SEQN" AS seqn, '_F' AS suffix from "DEMO_F" f
    UNION
    SELECT g."SEQN" AS seqn, '_G' AS suffix from "DEMO_G" g
    UNION
    SELECT h."SEQN" AS seqn, '_H' AS suffix from "DEMO_H" h
    UNION
    SELECT i."SEQN" AS seqn, '_I' AS suffix from "DEMO_I" i
    UNION
    SELECT j."SEQN" AS seqn, '_J' AS suffix from "DEMO_J" j
    UNION
    SELECT l."SEQN" AS seqn, '_L' AS suffix from "DEMO_L" l)
ORDER BY seqn;
