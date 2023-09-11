from pingsafe_cli.psgraph.common.models.enums import CheckCategories
from pingsafe_cli.psgraph.terraform.checks.resource.gcp.AbsGooglePostgresqlDatabaseFlags import AbsGooglePostgresqlDatabaseFlags

FLAG_NAME = 'log_hostname'
FLAG_VALUES = ['on']


class GoogleCloudPostgreSqlLogHostname(AbsGooglePostgresqlDatabaseFlags):
    def __init__(self):
        name = "Ensure hostnames are logged for GCP PostgreSQL databases"
        check_id = "CKV_GCP_108"
        supported_resources = ['google_sql_database_instance']
        categories = [CheckCategories.LOGGING]
        super().__init__(
            name=name,
            id=check_id,
            categories=categories,
            supported_resources=supported_resources,
            flag_name=FLAG_NAME,
            flag_values=FLAG_VALUES
        )


check = GoogleCloudPostgreSqlLogHostname()
