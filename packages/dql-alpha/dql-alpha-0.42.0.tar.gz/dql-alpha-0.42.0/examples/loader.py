from PIL import Image

from dql.catalog import get_catalog
from dql.loader import DataView
from dql.query import C, DatasetQuery

catalog = get_catalog(client_config={"aws_anon": True})
DatasetQuery(
    path="s3://ldb-public/remote/data-lakes/dogs-and-cats/",
    catalog=catalog,
).filter(C.name.glob("*cat*.jpg")).save("cats")


def load(buf):
    img = Image.open(buf)
    img.load()
    return img


def transform(row, sample):
    return sample


images = DataView.from_dataset(
    "cats", reader=load, transform=transform, catalog=catalog
)
for i in range(5):
    images[i].show()
