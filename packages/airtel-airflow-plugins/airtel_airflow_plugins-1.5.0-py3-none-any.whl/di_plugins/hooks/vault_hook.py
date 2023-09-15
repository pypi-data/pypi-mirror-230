from typing import Optional
from airflow.providers.hashicorp.hooks.vault import VaultHook


class DIVault:

    def __init__(self, vault_conn_id: Optional[str] = None, url: Optional[str] = 'https://divault.india.airtel.itm/',
                 secret_path: Optional[str] = None, mount_point: Optional[str] = None):
        self.conn_id = vault_conn_id
        self.vault_url = url
        self.vault_secret_path = secret_path
        self.vault_mount_point = mount_point

    def get_secret_from_vault(self) -> dict:
        try:
            vault_obj = VaultHook(self.conn_id)
            vault_obj.vault_client.kwargs = {'verify': '/opt/airflow/dags/BhartiCA.cer'}
            vault_obj.vault_client.url = self.vault_url
            connection = vault_obj.get_conn()
            secret = connection.secrets.kv.v2.read_secret_version(path=self.vault_secret_path,
                                                                  mount_point=self.vault_mount_point)
            return secret

        except Exception as ex:
            print(ex)
