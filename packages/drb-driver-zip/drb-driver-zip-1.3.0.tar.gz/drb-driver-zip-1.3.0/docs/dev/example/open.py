from zipfile import ZipExtFile

from drb.drivers.file import DrbFileNode

from drb.drivers.zip import DrbBaseZipNode
from drb.drivers.zip.zip import DrbZipAttributeNames

path = 'path/to/a/container.zip'

baseNode = DrbFileNode(path)
zipNode = DrbBaseZipNode(baseNode)

# Access a children with his name
zipNode['subFile']
zipNode['subDirectory']['subFile']

# Check if a file has children
zipNode['subDirectory']['subFile'].has_child()

# Check if a specific child his present
zipNode.has_child(name='subDirectory')

# Get the first child
zipNode[0]

# Get all the attributes of the zip node
zipNode.attributes

# search for a specific attributes
zipNode.get_attribute(name=DrbZipAttributeNames.DIRECTORY.value)

# Read the content of a file in the container
zipNode.get_impl(ZipExtFile)
