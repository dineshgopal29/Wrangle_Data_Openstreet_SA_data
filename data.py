import csv
import codecs
import pprint
import re
import xml.etree.cElementTree as ET
import cerberus
import schema
import sys
reload(sys)
sys.setdefaultencoding('utf8')

OSM_PATH = "sa_map"


NODES_PATH = "nodes.csv"
NODE_TAGS_PATH = "nodes_tags.csv"
WAYS_PATH = "ways.csv"
WAY_NODES_PATH = "ways_nodes.csv"
WAY_TAGS_PATH = "ways_tags.csv"

LOWER_COLON = re.compile(r'^([a-z]|_)+:([a-z]|_)+')
PROBLEMCHARS = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')

SCHEMA = schema.schema

# Make sure the fields order in the csvs matches the column order in the sql table schema
NODE_FIELDS = ['id', 'lat', 'lon', 'user', 'uid', 'version', 'changeset', 'timestamp']
NODE_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_FIELDS = ['id', 'user', 'uid', 'version', 'changeset', 'timestamp']
WAY_TAGS_FIELDS = ['id', 'key', 'value', 'type']
WAY_NODES_FIELDS = ['id', 'node_id', 'position']

street_type_re = re.compile(r'\b\S+\.?$', re.IGNORECASE)
phonePattern = re.compile(r'(\d{3})\D*(\d{3})\D*(\d{3,4})\D*(\d*)$')
phoneNumRegex = re.compile(r'(\d\d\d)-(\d\d\d-\d\d\d\d)')

expected = ["Street", "Avenue", "Boulevard", "Drive", "Court", "Place", "Square", "Lane", "Road",
            "Trail", "Parkway", "Commons"]

# Address Mapping
mapping = { "St": "Street",
            "St.": "Street",
            "Rd.": "Road",
            "Ave": "Avenue",
            "street":"Street"
            }


def shape_element(element, node_attr_fields=NODE_FIELDS, way_attr_fields=WAY_FIELDS, problem_chars=PROBLEMCHARS,
                  default_tag_type='regular'):
    """Clean and shape node or way XML element to Python dict"""
    node_attribs = {}
    way_attribs = {}
    way_nodes = []
    tags = []  # Handle secondary tags the same way for both node and way elements

    # YOUR CODE HERE
    if element.tag == 'node':
        #Get all the attribute of the element in a dictionary using attrib() method
        for a in element.attrib:
            if a in NODE_FIELDS:
                node_attribs[a] = element.attrib[a]
        for t in element.iter('tag'):
            temp_tag = {}
            if PROBLEMCHARS.match(t.attrib['k']):
                continue
            elif LOWER_COLON.match(t.attrib['k']):
                temp_tag["id"] = element.attrib['id']
                temp_tag["key"] = t.attrib['k'].split(":", 1)[1]
                temp_tag["type"] = t.attrib['k'].split(":", 1)[0]
                if t.attrib["k"] == 'addr:street' and t.attrib["k"] != '':
                    print(str(t.attrib["v"]))
                    temp_tag["value"] = update_name(str(t.attrib["v"].encode('utf-8')).strip(), mapping)
                    temp_tag["type"] = t.attrib['k'].split(":", 1)[0]
                else:
                    temp_tag["value"] = t.attrib["v"]
            else:
                if t.attrib["k"] == 'phone':
                    temp_tag["value"] = t.attrib["v"].strip("()")
                temp_tag["id"] = element.attrib['id']
                temp_tag["key"] = t.attrib['k']
                temp_tag["value"] = t.attrib['v']
                temp_tag["type"] = default_tag_type
                #if temp_tag["key"] == 'phone':
                    #temp_tag["value"] = isPhoneNumber(t.attrib["v"])
                    #print(temp_tag["value"])
            tags.append(temp_tag)
        print({"node": node_attribs, "node_tags": tags})
        return {'node': node_attribs, 'node_tags': tags}
    elif element.tag == 'way':
        count = 0
        for a in element.attrib:
            if a in WAY_FIELDS:
                way_attribs[a] = element.attrib[a]
        for t in element.iter('tag'):
            temp_tag = {}
            if PROBLEMCHARS.match(t.attrib['k']):
                continue
            elif LOWER_COLON.match(t.attrib['k']):
                temp_tag["id"] = element.attrib['id']
                temp_tag["key"] = t.attrib['k'].split(":",1)[1]
                temp_tag["type"] = t.attrib['k'].split(":",1)[0]
                if t.attrib["k"] == 'addr:street' and t.attrib["k"] != '':
                    temp_tag["value"] = update_name(str(t.attrib["v"]), mapping)
                    temp_tag["type"] = t.attrib['k'].split(":", 1)[0]
                else:
                    temp_tag["value"] = t.attrib["v"]
            else:
                temp_tag["id"] = element.attrib['id']
                temp_tag["key"] = t.attrib['k']
                temp_tag["value"] = t.attrib["v"]
                temp_tag["type"] = default_tag_type
            tags.append(temp_tag)
        for n in element.iter('nd'):
            temp_node = {}
            temp_node = \
                {
                    'id': element.attrib['id'],
                    'node_id': n.attrib['ref'],
                    'position': count
                }
            count = count + 1
            way_nodes.append(temp_node)
        print({"way": way_attribs, "way_nodes": way_nodes, "way_tags": tags})
        return {'way': way_attribs, 'way_nodes': way_nodes, 'way_tags': tags}


# ================================================== #
#               Helper Functions                     #
# ================================================== #
#Function to update the street names
def update_name(name, mapping):
    m = street_type_re.search(name)
    if m:
        street_type = m.group()
        if street_type in mapping.keys():
            name = name.replace(street_type, mapping.get(street_type))
    else:
        return name
    return name

def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

def validate_element(element, validator, schema=SCHEMA):
    """Raise ValidationError if element does not match schema"""
    if validator.validate(element, schema) is not True:
        field, errors = next(validator.errors.iteritems())
        message_string = "\nElement of type '{0}' has the following errors:\n{1}"
        error_string = pprint.pformat(errors)

        raise Exception(message_string.format(field, error_string))


class UnicodeDictWriter(csv.DictWriter, object):
    """Extend csv.DictWriter to handle Unicode input"""

    def writerow(self, row):
        super(UnicodeDictWriter, self).writerow({
            k: (v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in row.iteritems()
        })

    def writerows(self, rows):
        for row in rows:
            self.writerow(row)


# ================================================== #
#               Main Function                        #
# ================================================== #
def process_map(file_in, validate):
    """Iteratively process each XML element and write to csv(s)"""

    with codecs.open(NODES_PATH, 'wb') as nodes_file, \
            codecs.open(NODE_TAGS_PATH, 'wb') as nodes_tags_file, \
            codecs.open(WAYS_PATH, 'wb') as ways_file, \
            codecs.open(WAY_NODES_PATH, 'wb') as way_nodes_file, \
            codecs.open(WAY_TAGS_PATH, 'wb') as way_tags_file:

        nodes_writer = UnicodeDictWriter(nodes_file, NODE_FIELDS)
        node_tags_writer = UnicodeDictWriter(nodes_tags_file, NODE_TAGS_FIELDS)
        ways_writer = UnicodeDictWriter(ways_file, WAY_FIELDS)
        way_nodes_writer = UnicodeDictWriter(way_nodes_file, WAY_NODES_FIELDS)
        way_tags_writer = UnicodeDictWriter(way_tags_file, WAY_TAGS_FIELDS)

        nodes_writer.writeheader()
        node_tags_writer.writeheader()
        ways_writer.writeheader()
        way_nodes_writer.writeheader()
        way_tags_writer.writeheader()

        validator = cerberus.Validator()

        for element in get_element(file_in, tags=('node', 'way')):
            el = shape_element(element)
            if el:
                if validate is True:
                    validate_element(el, validator)

                if element.tag == 'node':
                    nodes_writer.writerow(el['node'])
                    node_tags_writer.writerows(el['node_tags'])
                elif element.tag == 'way':
                    ways_writer.writerow(el['way'])
                    way_nodes_writer.writerows(el['way_nodes'])
                    way_tags_writer.writerows(el['way_tags'])


if __name__ == '__main__':
    # Note: Validation is ~ 10X slower. For the project consider using a small
    # sample of the sa_map when validating.
    process_map(OSM_PATH, validate=True)
