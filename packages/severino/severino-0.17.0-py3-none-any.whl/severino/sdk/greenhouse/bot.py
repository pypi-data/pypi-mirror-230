import datetime

from severino.sdk.helpers.http_requests import Http
from severino.settings import SEVERINO_API_URL


class GHMigration:
    def __init__(self):
        self.http = Http()
        self.severino_api_url = SEVERINO_API_URL
        self.path = "/vagas-dot-com/gh/"

    def create(
        self,
        last_migration_at: datetime,
    ):
        return self.http.post(
            url=f"{self.severino_api_url}{self.path}/",
            data={
                "last_migration_at": last_migration_at.strftime("%Y-%m-%d %H:%M:%S"),
            },
        )

    def read(self, migration_uuid: str):
        """Read

        Args:
            migration_uuid (str): Migration id

        Returns:
            request: Request object
        """
        return self.http.get(
            url=f"{self.severino_api_url}{self.path}/{migration_uuid}/"
        )

    def last_migration_at(self):
        """Last migration at

        Returns:
            request: Request object
        """
        return self.http.get(
            url=f"{self.severino_api_url}{self.path}/last-migration-at/"
        )

    def list(self, filters: dict = {}):
        """List

        Args:
            filters (dict, optional): List of filters: vagas_job_id, gh_job_id, last_migration_at E.g: {"vagas_job_id": 999999}.

        Returns:
            _type_: _description_
        """
        return self.http.get(url=f"{self.severino_api_url}{self.path}/", params=filters)

    def update(
        self,
        migration_uuid: str,
        last_migration_at: datetime = None,
    ):
        data = {"last_migration_at": None}

        if last_migration_at:
            data["last_migration_at"] = last_migration_at.strftime("%Y-%m-%d %H:%M:%S")

        return self.http.put(
            url=f"{self.severino_api_url}{self.path}/{migration_uuid}/",
            data=data,
        )

    def delete(self, migration_uuid):
        return self.http.delete(
            url=f"{self.severino_api_url}{self.path}/{migration_uuid}/"
        )
