import logging
import os
from os import walk
from os.path import basename

import xmltodict
from jinja2 import Environment, PackageLoader, select_autoescape


class GenerateSalesforceObjectDict(object):
    filename = ''
    d = {}

    def __init__(self, fn):
        self.d = generate_template_dict(fn)
        if self.d != {}:
            self.create_field_validation_rule_links()

    def load_dict(self):
        pass

    def create_field_validation_rule_links(self):
        self.fields = self.d['fields'].keys()
        self.d['field_errors'] = {}
        for rule in self.d.get('rules'):
            for f in self.fields:
                if f in rule.get('errorConditionFormula', '') or f in rule.get('errorDisplayField', ''):
                    if self.d['fields'][f].get('field_errors', False) is not False:
                        self.d['fields'][f]['field_errors'].append(rule.get('fullName'))
                    else:
                        self.d['fields'][f]['field_errors'] = [rule.get('fullName')]


def ensure_list(generic):
    try:
        generic[0]
    except:
        generic = [generic]
    return generic


def generate_template_dict(fn):
    """Loads a Salesforce Object and converts it into a dict we can use for our template."""
    with open(fn) as fd:
        o = xmltodict.parse(fd)
        # print json.dumps(o, indent=2)
        try:
            if o['CustomObject'].get('fields', False) is False:
                o['CustomObject']['fields'] = []
            else:
                o['CustomObject']['fields'][0] # Throw an exception if this doesn't eixist
        except:
            o['CustomObject']['fields'] = [o['CustomObject']['fields']]

        try:
            if o['CustomObject'].get('validationRules', False) is False:
                o['CustomObject']['validationRules'] = []
            else:
                o['CustomObject']['validationRules'][0]
        except:
            o['CustomObject']['validationRules'] = [o['CustomObject']['validationRules']]



        try:
            ret = {
                'name': os.path.splitext(basename(fn))[0],
                'description': o.get('description', '@todo: Add Object Description'),
                'fields': {field['fullName']:
                    {
                        'fullName': field['fullName'],
                        'description': field['description'] if field.get('description',
                                                                         False) is not False else '@todo: Add Field Description',
                        'formula': field['formula'] if field.get('formula', False) is not False else '',
                        'label': field['label'],
                        'type': field['type'],
                        'length': field['length'] if field.get('length', False) is not False else '0',
                        'picklist': [plv['fullName'] for plv in ensure_list(field['picklist']['picklistValues'])]
                        if field.get('picklist', False) is not False else []
                    } for field in o['CustomObject'].get('fields', [])
                },
                'rules': o['CustomObject'].get('validationRules',[])
            }
        except TypeError as e:
            logging.exception(e)

            #logging.exception(json.dumps(o, indent=2))
            logging.exception(o['CustomObject'].keys())
            logging.exception(o['CustomObject']['fields'])
            logging.warning(fn)
            ret = {}

    return ret


def generate_template(d):
    """Generates a Jinja2 Template using data from generate_template_dict"""
    env = Environment(
        loader=PackageLoader('SFDCObjectDocGenerator', 'templates'),
        autoescape=select_autoescape(['html', 'xml'])
    )
    template = env.get_template('index.html')
    return template.render(**d).encode('utf8')


def generate_all_templates(source, output):
    allfiles = (os.path.join(source, fn) for (dirpath, dirnames, filenames) in walk(source) for fn in filenames)

    for fn in allfiles:
        print fn
        obj = GenerateSalesforceObjectDict(fn)

        with open("{0}/{1}.html".format(output, os.path.splitext(basename(fn))[0]), "wb") as fh:
            fh.write(generate_template(obj.d))

"""
    for fn in filenames:
        fullfn = os.path.join(directory, fn)
        print repr(fullfn)
"""
"""    
obj = GenerateSalesforceObjectDict('/SAPS_Application__c.object')
print json.dumps(obj.d, indent=2)

with open("/Users/jawaad/PycharmProjects/untitled2/SFDCObjectDocGenerator/output/index.html", "wb") as fh:
    fh.write(generate_template(obj.d))

"""