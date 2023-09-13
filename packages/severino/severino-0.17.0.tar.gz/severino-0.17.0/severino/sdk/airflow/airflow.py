from severino.sdk.helpers.http_requests import Http
from severino.settings import SEVERINO_API_URL


class Airflow:
    def __init__(self):
        self.http = Http()
        self.severino_api_url = SEVERINO_API_URL
        self.path = "/airflow/dag"

    def create(self, dag_id: str):
        return self.http.post(
            url=f"{self.severino_api_url}{self.path}/", data={"dag_id": dag_id}
        )

    def read(self, dag_id: str):
        return self.http.get(url=f"{self.severino_api_url}{self.path}/{dag_id}/")

    def list(self):
        return self.http.get(url=f"{self.severino_api_url}{self.path}/")

    def update(self, airflow_id: str, dag_id: str):
        return self.http.put(
            url=f"{self.severino_api_url}{self.path}/{airflow_id}/",
            data={"dag_id": dag_id},
        )

    def delete(self, airflow_id):
        return self.http.delete(url=f"{self.severino_api_url}{self.path}/{airflow_id}")


class KeyValueStorage:
    """
    Class that provides key-value data storage functionality.

    Methods:
    --------
    create(key, value)
        Creates a record with the specified key and value.

    update(key, value)
        Updates the value of an existing record with the specified key.

    get(key)
        Retrieves the value associated with the specified key.

    delete(key)
        Deletes a record with the specified key.
    """

    def __init__(self):
        self.http = Http()
        self.severino_api_url = SEVERINO_API_URL
        self.path = "/airflow/key-value-storage"

    def create(self, key: str, value: dict):
        """
        Creates a record with the key `key` and the value `value`.

        Parameters:
        -----------
        key : str
            The key of the record to be created.
        value : dict
            The value associated with the key.

        """
        return self.http.post(
            url=f"{self.severino_api_url}{self.path}/",
            data={"key": key, "json_data": value},
        )

    def get(self, key: str, only_json_data: bool = True):
        """
        Retrieves the value associated with the key `key`.

        Parameters:
        -----------
        key : str
            The key of the record to be retrieved.
        """
        result = self.http.get(url=f"{self.severino_api_url}{self.path}/{key}/")

        if result.status_code != 200 and result.status_code < 500:
            return None

        if not only_json_data:
            return result.json()

        return result.json()["json_data"]

    def update(self, key: str, value: dict):
        """
        Updates the value of an existing record with the key `key`.

        Parameters:
        -----------
        key : str
            The key of the record to be updated.
        value : dict
            The new value associated with the key.
        """

        return self.http.patch(
            url=f"{self.severino_api_url}{self.path}/{key}/",
            data={"json_data": value},
        )

    def delete(self, key):
        """
        Deletes a record with the key `key`.

        Parameters:
        -----------
        key : str
            The key of the record to be deleted.
        """
        return self.http.delete(url=f"{self.severino_api_url}{self.path}/{key}")
