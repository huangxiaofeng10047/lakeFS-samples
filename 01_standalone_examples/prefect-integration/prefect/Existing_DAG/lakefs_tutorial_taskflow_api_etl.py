# [START tutorial]
# [START import_module]
import json
from prefect import flow, task, runtime, variables
from prefect_lakefs.credentials import LakeFSCredentials
from prefect_lakefs.tasks import upload_object
from io import StringIO
from lakefs_demo import generate_flow_run_name
# [END import_module]

class NamedStringIO(StringIO):
    def __init__(self, content: str, name: str) -> None:
        super().__init__(content)
        self.name = name
        
# [START extract]
@task(name='Extract')
def extract():
    """
    #### Extract task
    A simple Extract task to get data ready for the rest of the data
    pipeline. In this case, getting data is simulated by reading from a
    hardcoded JSON string.
    """
    data_string = '{"1001": 301.27, "1002": 433.21, "1003": 502.22}'

    order_data_dict = json.loads(data_string)
    return order_data_dict
# [END extract]

# [START transform]
@task(name='Transformation')
def transform(order_data_dict: dict):
    """
    #### Transform task
    A simple Transform task which takes in the collection of order data and
    computes the total order value.
    """
    total_order_value = 0

    for value in order_data_dict.values():
        total_order_value += value

    return total_order_value
# [END transform]

# [START load]
@flow(name='Load', flow_run_name=generate_flow_run_name)
def load(total_order_value: float, new_branch: str):
    """
    #### Load task
    A simple Load task which takes in the result of the Transform task and
    instead of saving it to end us  er review, just prints it out.
    """

    print(f"Total order value is: {total_order_value:.2f}")

    # [START of lakeFS Code]
    contentToUpload = NamedStringIO(content=f"Total order value is: {total_order_value:.2f}", name='content')
    object_stat = upload_object(
        lakefs_credentials=LakeFSCredentials.load(variables.get('lakefs_credential_name')),
        repository=variables.get('repo'),
        #branch=runtime.flow_run.parameters['new_branch'],
        branch=new_branch,
        path="total_order_value.txt",
        content=contentToUpload
    )
    # [END of lakeFS Code]
# [END load]

@flow(name='ETL Tutorial', flow_run_name=generate_flow_run_name)
def lakefs_tutorial_taskflow_api_etl(new_branch: str, *args):
    # [START main_flow]
    extract_future = extract.submit()
    transform_future = transform.submit(extract_future.result())
    load(transform_future.result(), new_branch)
    # [END main_flow]
    
# [END tutorial]
