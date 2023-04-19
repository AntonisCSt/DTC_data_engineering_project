
##set-up prefect enviroment

create prefect_env with conda

install requirements.txt

`conda activate prefect_env`
## prefect set scheduler
`cd Batch_processing/`
`prefect deployment build ./etl_web_to_gcs.py:etl_parent_web_to_gcs -n"parameterized ETL gcs to bucket"`
`deployment apply etl_parent_web_to_gcs-deployment.yaml `
`prefect deployment apply etl_parent_web_to_gcs-deployment.yaml `
`prefect deployment build ./etl_gcs_to_bq.py:etl_parent_gcs_to_bq -n"parameterized ETL bucket to bigquery"`
`prefect deployment apply etl_parent_gcs_to_bq-deployment.yaml `

