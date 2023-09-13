from typing import List, Tuple, Dict, Set
import json


class IOVector(list):
    def __init__(self, *args):
        super().__init__(*args)

    def __hash__(self):
        return hash(tuple(self))

    def __eq__(self, other):
        return tuple(self) == tuple(other)

    def __str__(self):
        return str(tuple(self))

    def __repr__(self):
        return str(tuple(self))


IOVectorSet = Set[IOVector]
IOPair = Tuple[IOVector, IOVector]


class ReportTable:
    def __init__(self, max_output_len: int = 5):
        self.max_output_len = max_output_len
        self.table: Dict[str, ExecHashMap] = {}

    def report(self, func_name: str, io: IOPair):
        if func_name not in self.table:
            self.table[func_name] = ExecHashMap()
        self.table[func_name].insert(io)

    def clear(self):
        self.table.clear()

    def __str__(self) -> str:
        return str(self.table)


class ExecHashMap:
    def __init__(self, cap: int = 5):
        self.value_capacity = cap
        self.map: Dict[IOVector, IOVectorSet] = {}

    def insert(self, io: IOPair):
        inputs = io[0]
        outputs = io[1]
        if inputs not in self.map:
            self.map[inputs] = set()
            self.map[inputs].add(outputs)
        else:
            if len(self.map[inputs]) < self.value_capacity:
                self.map[inputs].add(outputs)

    def __getitem__(self, key: IOVector) -> IOVectorSet:
        return self.map[key]

    def __sizeof__(self) -> int:
        return len(self.map)

    def __len__(self) -> int:
        return len(self.map)

    def __str__(self) -> str:
        return str(self.map)

    def __repr__(self) -> str:
        return str(self.map)


class ReportTableJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, ExecHashMap):
            io_pairs = [[inputs, outputs] for inputs, outputs in obj.map.items()]
            return io_pairs
        elif isinstance(obj, IOVector):
            return list(obj)
        elif type(obj) is set and all(isinstance(item, IOVector) for item in obj):
            return list(obj)
        elif isinstance(obj, ReportTable):
            return obj.table
        return json.JSONEncoder.default(self, obj)
