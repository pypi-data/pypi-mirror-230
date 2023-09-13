import openi
from concurrent.futures import ThreadPoolExecutor

# Define the function to upload a file
def upload_file(file):
    openi.dataset.upload_file(
        file=file,
        username="",
        repository="",
        token="",
        app_url="http://192.168.207.34:8110/api/v1/"
    )

# Create a list of file paths
filelist =["./data1","./data2","./data3"]

# Create a ThreadPoolExecutor
with ThreadPoolExecutor() as executor:
    # Submit tasks to upload files
    tasks = [executor.submit(upload_file, file) for file in filelist]

    # Wait for all tasks to complete
    for task in tasks:
        task.result()