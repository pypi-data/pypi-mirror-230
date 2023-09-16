import io
from typing import Any, Dict, List, Optional, Tuple, Union
from urllib.request import pathname2url

import xarray
from deprecated.classic import deprecated
from drb.core import DrbFactory, DrbNode, ParsedPath
from drb.drivers.http import DrbHttpNode
from drb.drivers.json import JsonBaseNode
from drb.exceptions.core import (
    DrbException,
    DrbFactoryException,
    DrbNotImplementationException,
)
from drb.nodes.abstract_node import AbstractNode
from drb.topics.resolver import create
from requests.auth import AuthBase
import pandas as pd
import xarray as xr


class DrbDiscodataRowList(list):
    def __init__(self, table: DrbNode):
        super().__init__()
        self._skip = 0
        self._table = table
        self._page = None
        self._count_page = None
        self._page_size = None
        self._count = -1

    def __perform_query(self, num_page):
        rep_json = self._table.get_elts(num_page)
        if rep_json is None:
            return []
        rep_json = rep_json[0]
        self._page = [e for e in rep_json if e.name == "Rows"]
        return self._page

    def __init_query(self):
        rep_json = self._table.get_elts(0)
        if rep_json is None:
            return []
        rep_json = rep_json[0]
        self._count = rep_json["TotalRows"].value
        self._count_page = rep_json["NumPages"].value

        self._page = [e for e in rep_json if e.name == "Rows"]
        self._page_size = len(self._page)

        return self._page

    def __compute_index(self, item: Union[int, slice]) -> Tuple[int, int]:
        if isinstance(item, int):
            if item < 0:
                return item + len(self), -1
            return item, -1
        # item is a slice
        start = item.start if item.start is not None else 0
        if start < 0:
            start = start + len(self)
        stop = item.stop if item.stop is not None else len(self)
        if stop < 0:
            stop = stop + len(self)
        return start, stop

    def append(self, obj: Any) -> None:
        raise NotImplementedError

    def clear(self) -> None:
        raise NotImplementedError

    def copy(self) -> List[DrbNode]:
        raise NotImplementedError

    def count(self, value: Any) -> int:
        raise NotImplementedError

    def index(self, value: Any, start: int = ..., stop: int = ...) -> int:
        raise NotImplementedError

    def insert(self, index: int, obj: DrbNode) -> None:
        raise NotImplementedError

    def pop(self, index: int = ...):
        raise NotImplementedError

    def remove(self, value: Any) -> None:
        raise NotImplementedError

    def reverse(self) -> None:
        raise NotImplementedError

    def sort(self: List, *, key: None = ..., reverse: bool = ...) -> None:
        raise NotImplementedError

    def __getitem_index(self, index):
        if index not in range(self._skip, self._skip + self._page_size):
            page_number = index // self._page_size
            self._skip = page_number * self._page_size
            self.__perform_query(page_number)
        return self._page[index % self._page_size]

    def __getitem__(self, item):
        if self._count == -1:
            self.__init_query()

        if isinstance(item, int):
            index, _ = self.__compute_index(item)
            return self.__getitem_index(index)
        elif isinstance(item, slice):
            start, stop = self.__compute_index(item)
            result = []
            for index in range(start, stop):
                node = self.__getitem_index(index)
                result.append(node)
            return result
        else:
            raise KeyError(f"Invalid key: {type(item)}")

    def __iter__(self):
        def generator(count, page_size):
            page_num = 0
            buffer = None
            for i in range(count):
                if i % page_size == 0:
                    rep = self._table.get_elts(page_num)
                    if rep is None:
                        return None
                    elts = rep[0]
                    buffer = [e for e in elts if e.name == "Rows"]
                    page_num += 1
                idx = i % page_size
                yield buffer[idx]

        return generator(len(self), self._page_size)

    def __len__(self):
        if self._count == -1:
            self.__init_query()
        return self._count

    def __contains__(self, item):
        raise NotImplementedError

    def __iadd__(self, other):
        raise NotImplementedError

    def __imul__(self, other):
        raise NotImplementedError


class DrbDiscodataTableNode(AbstractNode):
    """
    The DrbDiscodataTableNode is used to represent a table of discodata
    Its attribute "columns" contain the list of the data available
    in this table.
    Its children is a list of DrbDiscodataRowList that can be browsed
    only by its index or slice in the table.

    Parameters:
        parent(DrbNode): The parent of the node.
    """
    def __init__(self, parent: DrbNode, table_node: DrbNode):
        super().__init__()

        self._table_node = table_node

        self.name = table_node["name"].value
        self.parent: DrbNode = parent
        self._id = table_node["id"].value
        self._table_node = table_node
        self._children: List[DrbNode] = None
        self._df_impl = None
        self.add_impl(pd.DataFrame, self._to_panda_dataframe)
        self.add_impl(xarray.Dataset, self._to_xarray_dataset)
        self.__init_attributes()

    def __init_attributes(self):
        for col in self._table_node["Columns", :]:
            dict_col = {}
            for child_col in col:
                dict_col[child_col.name] = child_col.value
            self.__imatmul__((col["name"].value, dict_col))
        columns = [c["name"].value for c in self._table_node["Columns", :]]
        self.__imatmul__(("columns", columns))

    @property
    @deprecated(version='1.2.0',
                reason='Only bracket browse should be use')
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = DrbDiscodataRowList(self)
        return self._children

    @property
    def __df_impl(self) -> pd.DataFrame:
        if self._df_impl is None:
            recs = []
            for i, c in enumerate(self.children):
                recs += c.get_impl(list)
            self._df_impl = pd.DataFrame(recs)
        return self._df_impl

    @staticmethod
    def _to_panda_dataframe(node: DrbNode, **kwargs) -> pd.DataFrame:
        if isinstance(node, DrbDiscodataTableNode):
            return node.__df_impl
        raise TypeError(f"Invalid node type: {type(node)}")

    @staticmethod
    def _to_xarray_dataset(node: DrbNode, **kwargs) -> xarray.Dataset:
        if isinstance(node, DrbDiscodataTableNode):
            return node.__df_impl.to_xarray()
        raise TypeError(f"Invalid node type: {type(node)}")

    def get_id(self):
        return self._id

    def get_elts(self, page_number):
        parent = self.parent
        table_name = self.name
        database_name_version = None
        while parent is not None and not isinstance(
            parent, DrbDiscodataServiceNode
        ):
            if isinstance(parent, DrbDiscodataDataBaseNode):
                database_name_version = parent.get_database_name_version()
            parent = parent.parent

        if database_name_version is not None and isinstance(
            parent, DrbDiscodataServiceNode
        ):
            return parent.get_elts(
                table_name, database_name_version, page_number
            )

        return None

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class DrbDiscodataDataBaseNode(AbstractNode):
    """
    The DrbDiscodataDataBaseNode is used to represent a database of discodata

    Its attribute "tables" contain the list of the data available
    in this database.
    Its children is a list of DrbDiscodataTableNode that can be browsed
    by table name.
    Parameters:
        parent(DrbNode): The parent of the node.
    """
    def __init__(self, parent: DrbNode, database_node: DrbNode):
        super().__init__()

        self._database_node = database_node
        self._version = ""
        self.name = database_node["database"].value
        self.parent: DrbNode = parent
        self._children: List[DrbNode] = None
        node_schemas = self._database_node["Schemas", :]
        latest = [n for n in node_schemas if n["schema"].value == "latest"]
        # there should be only one 'latest' version
        if len(latest) == 1:
            self._latest_node = latest[0]
            self._latest_node = self._database_node["Schemas", -1]
        # if not, we take the last one, hoping they'll stay sorted
        else:
            self._latest_node = self._database_node["Schemas", -1]
        self._version = self._latest_node["schema"].value
        self.__init_attributes()

    def __init_attributes(self):
        if self._latest_node.has_child("Tables"):
            tables = [t["name"].value for t in self._latest_node["Tables", :]]
            self @= ("tables", tables)

    @property
    @deprecated(version='1.2.0',
                reason='Usage of the bracket is recommended')
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            if self._database_node.has_child("Schemas"):
                try:
                    tables = self._latest_node["Tables", :]
                    for child_node in tables:
                        self._children.append(
                            DrbDiscodataTableNode(self, child_node)
                        )
                except Exception:
                    pass
        return self._children

    def get_database_name_version(self):
        return f"[{self.name}].[{self._version}]"

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class DrbDiscodataServiceNode(AbstractNode):
    """
    Represent a node for browsing Discodata data.

    Its attribute "databases" contain the list of all the available
    databases in the discodata service.
    Its children is a list of DrbDiscodataDataBaseNode
    This node has no implementations.
    """
    def __init__(
        self,
        path="https://discodata.eea.europa.eu",
        auth: Union[AuthBase, str] = None,
    ):
        super().__init__()
        path = path.replace("+discodata", "") if "+discodata" in path else path

        self._children = None
        self.name = "DISCODATA"
        if path.endswith("/"):
            path = path[:-1]
        self._path = path
        self._auth = auth
        self._path_map = path.replace("discodata", "discomap")
        md_node = DrbHttpNode(self._path + "/md")
        self._metadata = create(md_node)
        self.__init_attributes()

    def __init_attributes(self):
        if self._metadata.has_child("md"):
            databases = [
                c.value["database"] for c in self._metadata["md"].children
            ]

            self @= ("databases", databases)

    @property
    def path(self) -> ParsedPath:
        return ParsedPath(self._path)

    @property
    @deprecated(version='1.2.0',
                reason='Only bracket browse should be use')
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []

            for database in self._metadata["md"]:
                dt_child = DrbDiscodataDataBaseNode(self, database)
                self._children.append(dt_child)

        return self._children

    def get_elts(self, table_name, database_name_version, page_number):
        json = {
            "Page": page_number,
            "SortBy": "",
            "SortAscending": True,
            "RequestFilter": {},
        }

        node_ret = DrbHttpNode.post(
            self._path_map + f"/App/DiscodataViewer/data?fqn="
            f"{database_name_version}.[{table_name}]",
            data=json,
        )

        return JsonBaseNode(node_ret, node_ret.get_impl(io.BufferedIOBase))

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError


class DiscodataFactory(DrbFactory):
    def _create(self, node: DrbNode) -> DrbNode:
        if isinstance(node, DrbDiscodataServiceNode):
            return node
        if isinstance(node, DrbHttpNode):
            node_discodata_service = DrbDiscodataServiceNode(
                path=node.path.original_path, auth=node.auth
            )
        else:
            node_discodata_service = DrbDiscodataServiceNode(node.path.name)
        try:
            node_discodata_service.children
        except Exception:
            final_url = node.path.name.replace("+discodata", "")
            raise DrbFactoryException(
                f"Unsupported DISCODATA service: " f"{final_url}"
            )
        return node_discodata_service
