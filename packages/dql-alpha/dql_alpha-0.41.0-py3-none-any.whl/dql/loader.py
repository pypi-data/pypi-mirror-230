from typing import List, Optional

from dql.catalog import Catalog, get_catalog
from dql.dataset import DatasetRow
from dql.query import DatasetQuery


class DataView:
    def __init__(
        self,
        contents: List[DatasetRow],
        reader,
        transform,
        cache: bool = True,
        catalog: Optional[Catalog] = None,
        client_config=None,
    ):
        self.contents = contents
        self.reader = reader
        self.transform = transform
        self.cache = cache
        self.client_config = client_config or {}
        if catalog is None:
            catalog = get_catalog(self.client_config)
        self.catalog = catalog

    @classmethod
    def from_dataset(
        cls,
        name: str,
        reader,
        transform,
        num_workers: Optional[int] = None,
        worker_id: int = 0,
        *,
        cache: bool = True,
        catalog=None,
        client_config=None
    ):
        if num_workers is not None:
            query = DatasetQuery(name=name, catalog=catalog).chunk(
                worker_id, num_workers
            )
            return cls.from_query(
                query,
                reader,
                transform,
                cache=cache,
                catalog=catalog,
                client_config=client_config,
            )
        if catalog is None:
            catalog = get_catalog(client_config)
        contents = list(catalog.ls_dataset_rows(name))
        return cls(contents, reader, transform, cache=cache, catalog=catalog)

    @classmethod
    def from_query(
        cls,
        query,
        reader,
        transform,
        *,
        cache: bool = True,
        catalog=None,
        client_config=None
    ):
        if catalog is None:
            catalog = get_catalog(client_config)
        contents = query.results(row_factory=DatasetRow.from_result_row)
        return cls(contents, reader, transform, cache=cache, catalog=catalog)

    def __len__(self):
        return len(self.contents)

    def __getitem__(self, i):
        row = self.contents[i]
        if self.cache:
            client, _ = self.catalog.parse_url(row.source)
            client.download(row.as_uid())
        with self.catalog.open_object(row) as f:
            sample = self.reader(f)
        return self.transform(row, sample)
