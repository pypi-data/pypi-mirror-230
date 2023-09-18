from typing import Union, Dict, List, Set, Any



class ReservedKeywordsException(Exception):
    def __init__(self,
                 offending_keyword: str,
                 reserved_keywords: List[str],
                 ):
        self.reserved_keywords = reserved_keywords
        self.offending_keyword = offending_keyword

    def __str__(self):
        return f'You have used an offending keyword **{self.offending_keyword}** - {self.reserved_keywords=}'


class NoMatchesFoundForJsonPathException(Exception):
    def __init__(self,
                 deserialised_json: Union[Dict, List, None],
                 json_path: str
                 ):
        self.deserialised_json = deserialised_json
        self.json_path = json_path

    def __str__(self):
        return f'No matches found for {self.json_path=} in {self.deserialised_json=}'


class CircularDependencyException(Exception):
    def __init__(self,
                 visiting_nodes: Set[str],
                 offending_node: str,
                 ):
        self.visiting_nodes = visiting_nodes
        self.offending_node = offending_node

    def __str__(self):
        return f"Circular Dependency Detected in {self.offending_node=} - {self.visiting_nodes=}"


class NonExistentNodeException(Exception):
    def __init__(self,
                 nodes,
                 non_existent_node,
                 ):
        self.nodes = nodes
        self.non_existent_node = non_existent_node

    def __str__(self):
        return f'{self.non_existent_node=} does not exist! Available nodes are {self.nodes=}'


class NoMatchesFoundWithFilter(Exception):
    def __init__(self,
                 filter: Dict,
                 collection: List[Any],
                 ):
        self.filter = filter
        self.collection = collection

    def __str__(self):
        return f"No matches found with {self.filter=} in below collection {self.collection=}"
