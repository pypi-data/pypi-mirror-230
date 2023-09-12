import os
import ethos as ethos
from ethos import ethos_client
from ethos.ethos_client.rest import ApiException
import urllib3
import random, string

__all__ = [
    "Config",
    "Model",
    "ModelVersion",
    "ModelVersionConfig",
    "ModelVersion",
    "Resource",
]


class Config:
    def __init__(self, *, api_key=None, host=None, org_id=None):
        self.api_key = api_key or os.environ["ETHOS_API_KEY"]
        self.host = host or os.environ.get("ETHOS_API", "https://api.ethosai.com")
        self.org_id = org_id or os.environ["ETHOS_ORG"]
        self.client_config = ethos_client.Configuration(host=self.host, access_token=self.api_key)


class EthosObject:
    def __init__(self):
        self._loaded = False
        self._object = None
        self._config = ethos.config()  # TODO.

    @property
    def _client(self):
        return ethos_client.ApiClient(self._config.client_config)


class Model(EthosObject):
    def __init__(self, *, project, name):
        self.project_name = project
        self.name = name
        self.__model = None
        super().__init__()

    def __repr__(self):
        return f"<Model {self.name}>"

    @property
    def _model(self):
        if self.__model:
            return self.__model

        with self._client as api_client:
            projects_api = ethos_client.ProjectsApi(api_client)
            projects_data = projects_api.get_projects(
                org=self._config.org_id, name=self.project_name
            )

            if projects_data.data:
                project = projects_data.data[0]
            else:
                raise ApiException(
                    f"Project name not found - must be created in Ethos first. "
                    f"Got name: {self.project_name}"
                )

            models_api = ethos_client.ModelsApi(api_client)
            models_data = models_api.get_models(project=project["id"], name=self.name)
            if models_data.data:
                model = models_data.data[0]
            else:
                raise ApiException(
                    f"Model name not found - must be created in Ethos first. "
                    f"Got name: {self.name}"
                )
        self.__model = model
        return self.__model

    def new_version(self):
        return ModelVersion(_loaded_model=self._model)


class ModelVersionConfig:
    decision_threshold = None


class ModelVersion(EthosObject):
    def __init__(self, id=None, _loaded_model=None):
        super().__init__()

        self.model = _loaded_model
        self._model_version_config = ModelVersionConfig()

        if id:
            self.id = id  # TODO: load if ID is provided, and set self.model.
            raise NotImplementedError
        else:
            self._create()

    def __repr__(self):
        return f"<ModelVersion {self.id}>"

    def _create(self):
        with self._client as api_client:
            models_api = ethos_client.ModelsApi(api_client)
            model_version_create = ethos_client.ModelVersionCreate(model=self.model["id"])
            model_version = models_api.create_model_version(model_version_create)

        self.id = model_version.id
        self._model_version = model_version

    @property
    def config(self):
        return self._model_version_config

    def track_training_data(
        self,
        name,
        *,
        df,
        id_column,
        target,
        version_tags=None,
        tags=None,
    ):
        Resource(related=self).track_dataset(
            name=name,
            version_tags=version_tags,
            tags=["train"] + (tags or []),
            df=df,
            id_column=id_column,
            target=target,
        )

    def track_inference_data(
        self,
        name,
        *,
        df,
        id_column,
        actual_values,
        predict=None,
        predict_proba=None,
        version_tags=None,
        tags=None,
    ):
        Resource(related=self).track_dataset(
            name=name,
            df=df,
            version_tags=version_tags,
            tags=["inference"] + (tags or []),
            id_column=id_column,
            actual_values=actual_values,
            predict=predict,
            predict_proba=predict_proba,
        )

    def track_protected_data(
        self,
        name,
        *,
        df,
        id_column,
        version_tags=None,
        tags=None,
    ):
        Resource(related=self).track_dataset(
            name=name,
            version_tags=version_tags,
            tags=["protected"] + (tags or []),
            df=df,
            id_column=id_column,
        )

    def track_dataset(self, name, *, df, id_column=None, version_tags=None, tags=None):
        Resource(related=self).track_dataset(
            name=name,
            df=df,
            id_column=id_column,
            version_tags=version_tags,
            tags=tags or [],
        )


class Resource(EthosObject):
    def __init__(self, *, related, defer=True):
        self._default_datasource = None
        self.related = related
        super().__init__()

    @property
    def default_datasource(self):
        if self._default_datasource:
            return self._default_datasource
        with self._client as api_client:
            datasources_api = ethos_client.DatasourcesApi(api_client)
            datasources = datasources_api.get_datasources(org=self._config.org_id)

            if len(datasources.data) == 1:
                self._default_datasource = datasources.data[0]
            else:
                raise NotImplementedError(
                    f"Multi-datasource support has not been implemented. "
                    f"Expected exactly one, got: {len(datasources.data)}"
                )
        return self._default_datasource

    def _upload_blob(self, *, signed_upload_url, content):
        http = urllib3.PoolManager()
        headers = {"Content-Type": "application/octet-stream"}
        response = http.request("PUT", signed_upload_url, body=content, headers=headers)

        if response.status not in (200, 201):
            raise ApiException(f"Failed to upload blob. Got status code: {response.status}")
        return response

    def track_dataset(
        self,
        name,
        *,
        df,
        version_tags=None,
        tags=None,
        id_column=None,
        actual_values=None,
        target=None,
        predict=None,
        predict_proba=None,
    ):
        version_tags = version_tags or []
        tags = tags or []
        with self._client as api_client:
            blobs_api = ethos_client.BlobsApi(api_client)
            resources_api = ethos_client.ResourcesApi(api_client)

            try:
                # 1) Create blob:
                random_string = "".join(
                    random.choices(string.ascii_uppercase + string.digits, k=10)
                )
                gcs_filename = f"{name}-{random_string}.csv"
                datasource = self.default_datasource
                blob_create = ethos_client.BlobCreate(
                    datasource=datasource["id"], filename=gcs_filename, mimetype="text/csv"
                )
                blob = blobs_api.create_blob(blob_create)

                # 2) Upload the CSV to the blob:
                self._upload_blob(
                    signed_upload_url=blob.signed_upload_url,
                    content=df.to_csv(index=False),
                )

                # 3) Create the dataset schema:
                column_creates = []
                if id_column:
                    column_create = {
                        "name": id_column,
                        "type": "id",
                        "dtype": df[id_column].dtype.name,
                    }
                    column_creates.append(column_create)
                if target:
                    column_create = {
                        "name": target,
                        "type": "target",
                        "dtype": df[target].dtype.name,
                    }
                    column_creates.append(column_create)
                if actual_values:
                    column_create = {
                        "name": actual_values,
                        "type": "actual_values",
                        "dtype": df[actual_values].dtype.name,
                    }
                    column_creates.append(column_create)
                if predict:
                    column_create = {
                        "name": predict,
                        "type": "predict",
                        "dtype": df[predict].dtype.name,
                    }
                    column_creates.append(column_create)
                if predict_proba:
                    column_create = {
                        "name": predict_proba,
                        "type": "predict_proba",
                        "dtype": df[predict_proba].dtype.name,
                    }
                    column_creates.append(column_create)
                if "protected" in tags:
                    for column in set(df.columns):
                        if column == id_column:
                            continue
                        column_create = {
                            "name": column,
                            "type": "protected",
                            "dtype": df[column].dtype.name,
                        }
                        column_creates.append(column_create)

                dataset_schema_create = {
                    "columns": column_creates,
                }

                # Add any columns that are not already in the schema.
                # TODO: we will likely remove this in preference for server-side detection later.
                column_create_names = [column["name"] for column in column_creates]
                for column in [
                    column for column in df.columns if column not in column_create_names
                ]:
                    column_create = {
                        "name": column,
                        "type": "default",
                        "dtype": df[column].dtype.name,
                    }
                    column_creates.append(column_create)

                # 4) Create the resource:
                resource_blob_creates = [ethos_client.ResourceBlobCreate(blob=blob.id)]
                resource_create = ethos_client.ResourceCreate(
                    type="dataset",
                    name=name,
                    related=self.related.id,
                    version_tags=version_tags,
                    tags=tags,
                    value=resource_blob_creates,
                    dataset_schema=dataset_schema_create,
                )
                resources_api.create_resource(resource_create)
            except ApiException as e:
                print("Exception when calling API: %s\n" % e)
