import json
from typing import Optional
import anytree

from pydantic import BaseModel

JSON_PATH = (
    '/home/david/data/snapshots/single_file_val'
    '/643d27dfb883dd0011f16500/document.json'
)


class Field(BaseModel):
    _id: str
    name: str
    value: str
    valueFormula: Optional[str]
    tags: list
    dataType: str
    fieldType: str
    group: Optional[str]
    groupKey: Optional[str]
    classes: Optional[str]
    hasCategories: bool
    srcFieldId: str


with open(JSON_PATH, 'r') as f:
    doc_dict = json.load(f)

input_fields = doc_dict['input_fields']

all_fields = []
for pname, fields in input_fields.items():
    for field in fields:
        field_obj = Field.parse_obj(field)
        all_fields.append(field_obj)


root = anytree.Node('root')
