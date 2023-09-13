from pathlib import Path
import yaml
from deprecated.classic import deprecated
from drb.core import DrbFactory, DrbNode, ParsedPath

from io import BufferedIOBase, BytesIO, RawIOBase
from typing import Union, Optional, Any, Dict, Tuple, IO, List

from drb.exceptions.core import DrbNotImplementationException
from drb.nodes.abstract_node import AbstractNode


class YamlNode(AbstractNode):
    """
    This class represents a single node of a tree
    of data. When a node has one or several children he has no value.

    Parameters:
            path (str): The path to the yaml file.
            parent (DrbNode): The parent of this node (default: None).
            data : The yaml data (default: None).
    """

    def __init__(self, path: str,
                 parent: DrbNode = None, data=None):
        super().__init__()
        if data is not None:
            self._data = data
        else:
            with open(path) as yamlFile:
                data = list(yaml.safe_load_all(yamlFile))
                if len(data) == 1:
                    self._data = data[0]
                else:
                    self._data = data
                yamlFile.close()
        self._path = ParsedPath(path)

        self.add_impl(dict, _to_dict)
        self.add_impl(list, _to_list)
        self.add_impl(str, _to_str)
        self.add_impl(BytesIO, _to_bytes_io)

        self.name = Path(path).name
        self.value = self._data
        self.parent = parent
        self._children = None

    def __setitem__(self, key, value):
        raise NotImplementedError

    def __delitem__(self, key):
        raise NotImplementedError

    @property
    def path(self) -> ParsedPath:
        return self._path

    @property
    @deprecated(version="1.2.0", reason="drb core deprecation since 2.1.0")
    def children(self) -> List[DrbNode]:
        if self._children is None:
            self._children = []
            if isinstance(self._data, list):
                self._children = [
                    YamlNode(path=self.path.path,
                             parent=self,
                             data=e)
                    for e in self._data]
            elif isinstance(self._data, dict):
                for e in self._data.keys():
                    if isinstance(self._data[e], list):
                        for x in self._data[e]:
                            self._children.append(
                                YamlNode(
                                    path=Path(self.path.path).
                                    joinpath(e).as_posix(),
                                    parent=self,
                                    data=x)
                            )
                    elif isinstance(self._data, dict):
                        self._children.append(
                            YamlNode(path=Path(self.path.path).
                                     joinpath(e).as_posix(),
                                     parent=self,
                                     data=self._data[e])
                        )
        return self._children


def _to_dict(node: YamlNode, **kwargs) -> dict:
    data = node._data
    if len(data) == 0:
        return {}
    elif len(data) == 1:
        return data[0]
    raise RuntimeError('the node more than one element')


def _to_list(node: YamlNode, **kwargs) -> list:
    data = node._data
    if len(data) == 0:
        return []
    return data


def _to_str(node: YamlNode, **kwargs) -> str:
    return yaml.dump(node._data)


def _to_bytes_io(node: YamlNode, **kwargs) -> BytesIO:
    return BytesIO(bytes(yaml.dump(node._data), 'utf-8'))


class YamlBaseNode(AbstractNode):
    """
        This class represents a single node of a tree
        of data. When the data came from another implementation.

        Parameters:
                node (DrbNode): The node where the yaml data came from.
                source (Union[BufferedIOBase, RawIOBase, IO]): The yaml data.
        """

    def __init__(self,
                 node: DrbNode,
                 source: Union[BufferedIOBase, RawIOBase, IO]):
        super().__init__()
        self.base_node = node
        self.source = source
        yaml_root = yaml.safe_load(source)
        self.yaml_node = YamlNode(node.path.path, parent=self, data=yaml_root)

    @property
    def name(self) -> str:
        return self.base_node.name

    @property
    def namespace_uri(self) -> Optional[str]:
        return self.base_node.namespace_uri

    @property
    def value(self) -> Optional[Any]:
        return self.base_node.value

    @property
    def path(self) -> ParsedPath:
        return self.base_node.path

    @property
    def parent(self) -> Optional[DrbNode]:
        return self.base_node.parent

    @property
    @deprecated(version="1.2.0", reason="drb core deprecation since 2.1.0")
    def attributes(self) -> Dict[Tuple[str, str], Any]:
        return self.base_node.attributes

    @property
    @deprecated(version="1.2.0", reason="drb core deprecation since 2.1.0")
    def children(self) -> List[DrbNode]:
        return [self.yaml_node]

    def has_child(self, name: str = None, namespace: str = None) -> bool:
        if name and self.yaml_node.name == name:
            return True
        elif namespace:
            return False
        return True

    @deprecated(version="1.2.0", reason="drb core deprecation since 2.1.0")
    def get_attribute(self, name: str) -> Any:
        return self.base_node.get_attribute(name)

    def has_impl(self, impl: type) -> bool:
        return self.base_node.has_impl(impl)

    def get_impl(self, impl: type, **kwargs) -> Any:
        return self.base_node.get_impl(impl)

    def close(self) -> None:
        if self.source:
            self.source.close()
        self.base_node.close()


class YamlNodeFactory(DrbFactory):
    """
    The YamlNodeFactory class allow us to build drb nodes according
     to the form of the yaml data you want to read.
    After this class is created you can call the _create method
     with the drb node created from the
    path of the Yaml file you want to read
    """

    def _create(self, node: Union[DrbNode, str]) -> DrbNode:
        if isinstance(node, YamlNode) or isinstance(node, YamlBaseNode):
            return node
        if isinstance(node, DrbNode):
            if node.has_impl(BufferedIOBase):
                return YamlBaseNode(node, node.get_impl(BufferedIOBase))
            else:
                return YamlBaseNode(node, node.get_impl(BytesIO))
        return YamlNode(node)
