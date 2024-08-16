from airflow import DAG 
from airflow.utils.dates import days_ago
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from airflow.macros import ds_add
from os.path import join
import pendulum
import pandas as pd


    ## | teste de primeiro dag essa dag não  executa ações relevantes.
with DAG(
    dag_id = 'my_first_dag',
    start_date = days_ago(1),
    schedule_interval="@daily"
) as dag:
    
    task_01 = EmptyOperator(task_id="first_task")
    task_02 = EmptyOperator(task_id="second_task")
    task_03 = EmptyOperator(task_id="tird_task")
    task_04 = BashOperator(
        task_id="create_folder",
        bash_command = 'mkdir -p "/home/kai/Documents/airflowalura/new_folder"'

        )
    
    task_01 >> [task_02, task_03]
    task_03 >> task_04


## DEFINIR A FUNÇÃO DE EXTRAÇÃO
def extract_clima_data(data_interval):
    """Função para extrair dados climáticos de uma API e salvar resultaado em arquivos CSV.

    Args:
        data_interval (str): Data de termino do intervalo de dados, usando consultas e nomeação de arquivos
    return: 
        none
    """     
    print(data_interval)
    city = 'Boston'                        # CIDADE DE EXRAÇÂO dos dados 
 
    key = 'Y9U75QT9M9XLMPJ3LRGWQ97XY'      # CHAVE DA API

    api_path = join(f'https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/',
                f"{city}/{data_interval}/{ds_add(data_interval, 7)}?unitGroup=metric&include=days&key={key}&contentType=csv")
    
    clima_data = pd.read_csv(api_path)

    current_folder_path = f"/home/kai/Documents/airflowalura/semana={data_interval}/"
    
    clima_data.to_csv(current_folder_path + 'raw_data.csv')
    clima_data[["datetime", "tempmin", "temp", "tempmax"]].to_csv(current_folder_path + "temperatura.csv")
    clima_data[["datetime", "description", "icon"]].to_csv(current_folder_path+'condiction.csv')


with DAG(
        dag_id = "clima_process_extractor",                   # identificador do dag
        start_date = pendulum.datetime(2024,6,6, tz="UTC"),   # Ajusta a data de inicio do dag
        schedule_interval = '0 0 * * 1',                      # ajusta o calendário de automação das dags
) as dag:

    task_01 = BashOperator(
        # Executa comandos do bash para criar pasta de datass

        task_id = "Creator_folder_with_datetime",
        bash_command = "mkdir -p '/home/kai/Documents/airflowalura/semana={{data_interval_end.strftime('%Y-%m-%d')}}/'"
    )

    task_02 = PythonOperator(
        # Eecuta funções em python para extrair dados climáticos

        task_id = 'extract_clima_files',
        python_callable = extract_clima_data,
        op_kwargs = {"data_interval": "{{data_interval_end.strftime('%Y-%m-%d')}}"}
    )

    task_01 >> task_02