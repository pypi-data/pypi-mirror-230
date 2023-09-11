import os, pdb
from os import path
from urllib.request import urlretrieve

default_config_url = 'https://ultronsandbox.oss-cn-hangzhou.aliyuncs.com/config.zip'

g_sandbox_url = default_config_url if 'JDWDATA_CONFIG_URL' not in os.environ else os.environ[
    'JDWDATA_CONFIG_URL']

root_drive = path.expanduser('~')
g_project_root = path.join(root_drive, '.jdw')
g_project_data = os.path.join(g_project_root, 'data/config')


def enable_config():
    if not os.path.exists(g_project_data):
        data_example_zip = os.path.join(g_project_root, "config.zip")
        if not os.path.exists(g_project_root):
            os.mkdir(g_project_root)
        print("download config data")
        urlretrieve(g_sandbox_url, data_example_zip)
        try:
            from zipfile import ZipFile
            zip_csv = ZipFile(data_example_zip, "r")
            unzip_dir = os.path.join(g_project_root, "data/")
            print(unzip_dir)
            for csv in zip_csv.namelist():
                zip_csv.extract(csv, unzip_dir)
            zip_csv.close()
        except Exception as e:
            # 解压测试数据zip失败，就不开启测试数据模式了
            print('example env failed! e={}'.format(e))
            return


def checkout_config():
    if not os.path.exists(g_project_data):
        enable_config()
    os.environ['EXPORT_CFG_PATH'] = os.path.join(g_project_data,
                                                 'tableCfg.yaml')
    os.environ['MAPPING_CFG_PATH'] = os.path.join(g_project_data,
                                                  'mapping.yaml')
