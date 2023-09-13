from dataclasses import dataclass, field

from gwdc_python.jobs.meta import JobMeta

import gwlandscape_python
from gwlandscape_python.model_type import Model
from gwlandscape_python.publication_type import Publication
from gwlandscape_python.utils import file_filters


@dataclass
class Dataset(metaclass=JobMeta):
    client: gwlandscape_python.gwlandscape.GWLandscape = field(compare=False)
    id: str
    publication: Publication
    model: Model

    FILE_LIST_FILTERS = {
        'data': file_filters.data_filter
    }

    def __repr__(self):
        return f'Dataset({self.publication} - {self.model})'

    def update(self, publication=None, model=None):
        """
        Update a Dataset in the GWLandscape database

        Parameters
        ----------
        publication : Publication, optional
            The new Publication, by default None
        model : Model, optional
            The new Model, by default None

        Returns
        -------
        Dataset
            Updated Dataset
        """
        inputs = {key: val for key, val in locals().items() if ((val is not None) and (key != 'self'))}

        mutation = """
            mutation UpdateCompasDatasetModelMutation($input: UpdateCompasDatasetModelMutationInput!) {
                updateCompasDatasetModel(input: $input) {
                    result
                }
            }
        """

        params = {
            'input': {
                'id': self.id,
                **{f'compas_{key}': val.id for key, val in inputs.items()}
            }
        }

        result = self.client.request(mutation, params)

        if result['update_compas_dataset_model']['result']:
            for key, val in inputs.items():
                setattr(self, key, val)

    def delete(self):
        """
        Remove this Dataset from the GWLandscape database
        """

        mutation = """
            mutation DeleteCompasDatasetModelMutation($input: DeleteCompasDatasetModelMutationInput!) {
                deleteCompasDatasetModel(input: $input) {
                    result
                }
            }
        """

        params = {
            'input': {
                'id': self.id
            }
        }

        result = self.client.request(mutation, params)

        assert result['delete_compas_dataset_model']['result']

    def get_full_file_list(self):
        """Get information for all files associated with this dataset

        Returns
        -------
        ~gwdc_python.files.file_reference.FileReferenceList
            Contains FileReference instances for each of the files associated with this dataset
        """
        return self.client._get_files_by_dataset_id(self.id)
