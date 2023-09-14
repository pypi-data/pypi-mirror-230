import datetime
import typing

from pydantic import BaseModel, root_validator

import rebotics_sdk


class Metadata(BaseModel):
    packed: typing.Optional[str] = datetime.datetime.now().isoformat()  # datetime of packing in %c format
    model_type: typing.Optional[str] = None
    model_codename: typing.Optional[str] = None
    sdk_version: typing.Optional[str] = rebotics_sdk.__version__
    core_version: typing.Optional[str] = None
    fvm_version: typing.Optional[str] = None
    packer_version: typing.Optional[int] = 0
    count: int = 0
    batch_size: int = 0
    images_links_expiration: typing.Optional[str] = None  # iso data format

    additional_files: typing.Optional[typing.List[typing.List[str]]] = None  # additional files in archive
    images: typing.Optional[typing.List[str]] = None  # images in archive

    # new field for metadata
    files: typing.List[dict] = []

    @root_validator
    def compute_model_type(cls, values):
        if not values.get('model_type'):
            codename = values.get('model_codename') or ''
            if 'arcface' in codename:
                values['model_type'] = 'arcface'
            else:
                values['model_type'] = 'facenet'
        return values
