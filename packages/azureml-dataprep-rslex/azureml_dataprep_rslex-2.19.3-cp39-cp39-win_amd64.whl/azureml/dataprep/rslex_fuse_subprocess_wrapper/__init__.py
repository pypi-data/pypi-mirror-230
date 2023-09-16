import os
import subprocess
import sys
import tempfile
import time

def build_data_asset_uri(subscription_id: str, resource_group_name: str, workspace_name: str, path: str) -> str:
    if path.startswith('azureml:') and '/' not in path:
        path_parts = path.split(':')
        if len(path_parts) >= 2 and len(path_parts) <= 3:
            name = path_parts[1]
            version = None if len(path_parts) < 3 else path_parts[2]
            uri = f"azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group_name}/workspaces/{workspace_name}/data/{name}"
            if version is not None:
                uri += f"/versions/{version}"
            return uri
    else:
        supported_schemas = ['azureml', 'http', 'https', 'wasb', 'wasbs', 'adl', 'abfss', 'azfs']
        for schema in supported_schemas:
            if path.startswith(f'{schema}://'):
                return path
    raise ValueError("data path should be in the form of eith" +
                     "er `azureml:<data_asset_name>` " +
                     "or `azureml:<data_asset_name>:<data_asset_version>` " +
                     "or `azureml://subscriptions/<subscription_id>/resourcegroups/<resource_group_name>/workspaces/<workspace_name>/data/<data_asset_name>` " +
                     "or `azureml://subscriptions/<subscription_id>/resourcegroups/<resource_group_name>/workspaces/<workspace_name>/data/<data_asset_name>/versions/<data_asset_version>` " +
                     "or URL with one of supported schemas: http, https, wasb, wasbs, adl, abfss, azfs.")

def build_datastore_uri(subscription_id: str, resource_group_name: str, workspace_name: str, path: str) -> str:
    if ':' not in path and '/' not in path:
        # assumed to be datastore name
        return f"azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group_name}/workspaces/{workspace_name}/datastores/{path}"
    else:
        if path.startswith('azureml://'):
            SHORT_URL_PREFIX='azureml://datastores/'
            if path.startswith(SHORT_URL_PREFIX):
                suffix=path[len(SHORT_URL_PREFIX):]
                return f"azureml://subscriptions/{subscription_id}/resourcegroups/{resource_group_name}/workspaces/{workspace_name}/datastores/{suffix}"
            else:
                return path
    raise ValueError("datastore path should be in the form of eith" +
                     "er `<datastore_name>` " +
                     "or `azureml://datastores/<datastore_name>` " +
                     "or `azureml://datastores/<datastore_name>/paths/<path_in_datastore>` " +
                     "or `azureml://subscriptions/<subscription_id>/resourcegroups/<resource_group_name>/workspaces/<workspace_name>/datastores/<datastore_name>` " +
                     "or `azureml://subscriptions/<subscription_id>/resourcegroups/<resource_group_name>/workspaces/<workspace_name>/datastores/<datastore_name>/paths/<path_in_datastore>`.")

def start_fuse_mount_subprocess(source_uri: str, mount_point: str, read_only: bool, debug: bool = False):
    assert not os.path.exists(mount_point) or (os.path.isdir(mount_point) and not os.listdir(mount_point)), \
        f'mount point `{mount_point}` already exists but is not an empty directory. please specify a different mount point.'

    assert not (os.name == 'nt' and os.path.exists('/dev')), \
        'it seems that you are inside WSL (Windows Subsystem for Windows) but you are invoking Azure CLI for Windows. this particular use case is not supported. ' + \
        'please install Azure CLI **inside** WSL and try again. ' + \
        '(you can verify by running `$ which az` in WSL: it should return a native Linux path (for example `/usr/bin/az`) instead of a translated Windows path (for example `/mnt/c/Program Files (x86)/Microsoft SDKs/Azure/CLI2/wbin/az`).).'

    assert not os.name == 'nt', \
        'mount is not supported on Windows. ' + \
        'please use Linux or WSL (Windows Subsystem for Linux). '

    assert os.path.exists('/dev/fuse'), \
        'file `/dev/fuse` does not exist. ' + \
        'mount is only supported on Linux with FUSE enabled. ' + \
        'try `$ sudo apt install fuse`. if you are inside a docker container, run the container with `--privileged` argument.'

    try:
        subprocess.check_output(['which', 'fusermount'])
    except subprocess.CalledProcessError:
        raise AssertionError('`fusermount` is not found. (command `$ which fusermount` failed.) try `$ sudo apt install fuse`.')

    log_directory = os.path.join(tempfile.gettempdir(), 'azureml-logs', 'dataprep', 'rslex-fuse-cli')

    print("Mount starting...")
    start_time = time.time()
    process = subprocess.Popen([sys.executable, "-c", f"""
import sys
sys.path={sys.path}
from azureml.dataprep.rslex import PyMountOptions, RslexURIMountContext, init_environment

uri=sys.argv[1]
mount_point=sys.argv[2]
read_only=bool(sys.argv[3])
debug = bool(sys.argv[4])
log_directory = sys.argv[5]

print('Mount initializing...')
init_environment(log_directory, None, 'DEBUG' if debug else 'INFO', False, None, None, None, None, None)
options = PyMountOptions(None, None, None, None, read_only, 0o777, False)
mount_context = RslexURIMountContext(mount_point, uri, options)

print('Mount starting... ')
mount_context.start(True) # blocking

print('Mount ended.')
""",
    source_uri, mount_point, str(read_only), str(debug), log_directory],
    env=dict(
        os.environ,
        AZUREML_DATAPREP_TOKEN_PROVIDER = 'rslex_native',
        AZUREML_DATAPREP_WORKSPACE_CONNECTION_PROVIDER = 'rslex_native',
    ), 
    stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)

    while True:
        if time.time() - start_time > 15:
            process.kill()
            raise AssertionError(f'rslex-fuse-cli subprocess timed out. Logs can be found at {log_directory}')
        if process.poll() is not None:
            raise AssertionError(f'rslex-fuse-cli subprocess exited unexpectedly. Logs can be found at {log_directory}')
        output_line = process.stdout.readline()
        if output_line and 'Mount started.' in output_line.decode('utf-8'):
            print(f"Mount started successfully.")
            print(f"To unmount, run `$ umount {mount_point}`.")
            print(f"Logs can be found at {log_directory}")
            return
