from pydantic import BaseModel

class Data (BaseModel):
    filenames: list[str]
    documents: list[str]
    inverted_index: dict[str, list[tuple[int,int]]]
    titles: list[str]
    inverted_index_titles: dict[str, list[tuple[int,int]]]