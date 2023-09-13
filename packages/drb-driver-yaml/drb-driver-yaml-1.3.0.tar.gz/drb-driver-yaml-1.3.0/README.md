# YamlNode Implementation

This `drb-driver-yaml` module implements yaml format access with DRB data
model. It is able to navigates among the yaml contents.

## Yaml Factory and Yaml Node

The module implements the basic factory model defined in DRB in its node
resolver. Based on the python entry point mechanism, this module can be
dynamically imported into applications.

The entry point group reference is `drb.driver`.<br/>
The implementation name is `yaml`.<br/>
The factory class is encoded into `drb.drivers.yaml:YamlNodeFactory`.<br/>

The yaml factory creates a YamlNode from an existing yaml content. It uses a
base node to access the content data using the streamed base node
implementation.

The base node can be a FileNode (See drb-driver-file), HttpNode, ZipNode or
any other node able to provide streamed (`BufferedIOBase`, `RawIOBase`, `IO`)
yaml content.

## limitations

The current version does not manage child modification and insertion. yamlNode
is currently read only.

## Using this module

To include this module into your project, the `drb-driver-yaml` module shall be
referenced into `requirement.txt` file, or the following pip line can be run:

```commandline
pip install drb-driver-yaml
```

### Node Creation:

The implementation can create a yamlNode by giving the path to a yaml file:

```
from drb.driver.yaml import YamlNode

node = YamlNode(PATH_yaml)
```

If the baseNode is an HttpNode, FileNode... the implementation can retrieve the data of your yaml with this:

 ```
from drb.drivers.yaml import YamlNodeFactory

FACTORY = YamlNodeFactory()
FILE_NODE = DrbFileNode(PATH_TO_YOUR_YAML)
NODE = FACTORY.create(FILE_NODE)
```

### Documentation

The documentation of this implementation can be found here https://drb-python.gitlab.io/impl/yaml