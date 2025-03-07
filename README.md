# NHANES Patient Generator

Python Django app for retrieving and analyzing data obtained from the CDC's National Health and Nutrition Examination Survey (NHANES) with the intent of generating a simulated patient for diagnostics training purposes.

*This is a work in progress.*

## Endpoints

### /generate

Retrieves a random survey respondent's SEQN and gets all data in all tables associated with that respondent. This can be used as the basis for a simulated patient

Example output: 

```
{
  "ACQ_I": {
    "SEQN": {
      "variable": 90745,
      "description": null
    },
    "ACD011A": {
      "variable": "English",
      "description": "Speak English at home - NHW or NHB"
    }
  },
  "ALB_CR_I": {
    "SEQN": {
      "variable": 90745,
      "description": null
    },
    "URXUMA": {
      "variable": 244.5,
      "description": "Albumin urine (ug/mL)"
    },
    "URDUMALC": {
      "variable": "At or above the detection limit",
      "description": "Albumin urine comment code"
    },
  },
    ...

  }
```
### /table-info

Returns a list of all NHANES tables with the year it was published, a description, and link to the CDC's documentation. 

Example output: 

```
[
  {
    "TableName": "ACQ_L",
    "DatePublished": "September 2024",
    "DocFile": "https://wwwn.cdc.gov/Nchs/Nhanes/2021-2022/ACQ_L.htm",
    "Description": "Acculturation"
  },
  {
    "TableName": "AGP_L",
    "DatePublished": "September 2024",
    "DocFile": "https://wwwn.cdc.gov/Nchs/Nhanes/2021-2022/AGP_L.htm",
    "Description": "alpha-1-Acid Glycoprotein"
  },
  {
    "TableName": "ALQ_L",
    "DatePublished": "September 2024",
    "DocFile": "https://wwwn.cdc.gov/Nchs/Nhanes/2021-2022/ALQ_L.htm",
    "Description": "Alcohol Use"
  },
 
  ...

]
  ```

  ## Running the service locally
  To run the service locally, create a file called `.env` with the database connection details:
  ```
DB_NAME={db.name.here}
DB_HOST=localhost
DB_USER={your.username.here}
DB_PASS={you.password.here}
DB_PORT=5432
```
NHANES data was loaded into a PostgreSQL database using [nhanes-postgres](https://github.com/cjendres1/nhanes) script by [cjendres1](https://github.com/cjendres1). Extra tables included are in the sql folder.

Afterwards, run

```python manage.py runserver```
