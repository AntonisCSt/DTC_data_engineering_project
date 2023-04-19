{{ config(materialized='table') }}

with ml_data as (
    select * from {{ref('stg_machine_lrn')}}
),

de_data as (
    select * from {{ref('stg_data_eng')}}
),

mlops_data as (
    select * from {{ref('stg_ml_ops')}}
),

data_unioned as (
    select * from ml_data
    union all
    select * from de_data
    union all
    select * from mlops_data
)
select * from data_unioned