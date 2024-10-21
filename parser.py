import json
import csv
import re, hashlib

DEFAULT_COMPLETE_ARRAY = [['parent_rule', 'child_rule', 'if_condition', 'boolean', 'then_behaviour']]
complete_array = DEFAULT_COMPLETE_ARRAY.copy()
complete_array1 = [['parent_rule', 'child_rule', 'if_condition', 'boolean', 'then_behaviour']]

def write2csv(data, csv_file):
    with open(csv_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

def convert_behavior(behaviors):
    print("----------------------------------------------------------------------------------------------------------------------")
    if behaviors:
        a = ''
        for x in behaviors:
            if x['name'] == 'setVariable' and x['options']:
                a += x['name']
                a += ':' + x['options']['variableName'] if 'variableName' in x['options'].items() else ""
                a += ':' + x['options']['variableValue'] if 'variableValue' in x['options'].items() else ""
                a += ':' + x['options']['extractLocation'] if 'extractLocation' in x['options'].items() else ""
            elif x['name'] == 'modifyOutgoingRequestHeader' or x['name'] == 'modifyOutgoingResponseHeader':
                pattern1 = re.compile(r'HeaderName', re.IGNORECASE)
                pattern2 = re.compile(r'value', re.IGNORECASE)
                a = a + x['name']
                a = a + ':'.join([f"{value}" for key, value in x['options'].items() if re.search(pattern1, key)])
                a = a + ':'.join([f"{value}" for key, value in x['options'].items() if re.search(pattern2, key)])
            elif x['name'] == 'denyAccess':
                a = a + x['name']
                a = a + ':' + x['options']['reason'] if 'reason' in x['options'].items() else ""
                a = a + ':' + x['options']['enabled'] if 'enabled' in x['options'].items() else ""
            else:
                a = a + x['name']
                a = a + ':' + str(x)
            return a
    else:
        return behaviors

def extract_values(array_of_dicts):
    result = ""
    for d in array_of_dicts:
        name = d.get('name')
        options = d.get('options', {})       
        if name == 'setVariable':
            variable_name = options.get('variableName', '')
            variable_value = options.get('variableValue', '')
            extract_location = options.get('extractLocation', '')
            result += variable_name+":"+variable_value+":"+extract_location
            result += "\n"
        elif name in ['modifyOutgoingRequestHeader', 'modifyOutgoingResponseHeader']:
            pattern1 = re.compile(r'HeaderName', re.IGNORECASE)
            pattern2 = re.compile(r'value', re.IGNORECASE)
            header_name_values = [value for key, value in options.items() if re.search(r'headername', key, re.IGNORECASE)]
            header_name = options.get('customHeaderName', '')
            new_header_value = options.get('newHeaderValue', '')
            result += f"Header Name: {header_name}, New Header Value: {new_header_value}\n"
            result += "\n"
        elif name == 'denyAccess':
            reason = options.get('reason', '')
            enabled = options.get('enabled', '')
            result += f"Reason: {reason}, Enabled: {enabled}\n"
            result += "\n"
        else:
            result += str(d)
    return result

def process_options_in_list(list_of_dicts):
    result = ""
    for dictionary in list_of_dicts:
        options = dictionary.get('options', {})
        dictionary.update(options)
        dictionary.pop('options', None)
        result += str(dictionary) + "\n"
    return result

def boolean_decider(a):
    if a == 'any':
        return "OR"
    else:
        return "AND"

def empty_children(a,x,name):
    if not name:
        a.append(x['name'])
        a.append(x['children'])
        a.append(process_options_in_list(x['criteria']))
        a.append(boolean_decider(x['criteriaMustSatisfy']))
        a.append(extract_values(x['behaviors']))        
        complete_array.append(a)
    else:
        a.append(name)
        if name != x['name']:
            a.append(x['name'])
        else:
            a.append('')
        a.append(process_options_in_list(x['criteria']))
        a.append(boolean_decider(x['criteriaMustSatisfy']))
        a.append(extract_values(x['behaviors']))
        complete_array.append(a)


def empty_children_1(a,x,name):
    if not name:
        a.append(x['name'])
        a.append('')
        if 'criteria' in x and x['criteria']:
            a.append(process_options_in_list(x['criteria']))
        else:
            a.append('')
        if 'criteriaMustSatisfy' in x and x['criteriaMustSatisfy']:
            a.append(boolean_decider(x['criteriaMustSatisfy']))
        else:
            a.append('')
        if 'behaviors' in x and x['behaviors']:
            a.append(extract_values(x['behaviors']))
        else:
            a.append('')        
        complete_array.append(a)
    else:
        a.append(name)
        a.append(x['name'])
        if 'criteria' in x and x['criteria']:
            a.append(process_options_in_list(x['criteria']))
        else:
            a.append('')
        if 'criteriaMustSatisfy' in x and x['criteriaMustSatisfy']:
            a.append(boolean_decider(x['criteriaMustSatisfy']))
        else:
            a.append('')
        if 'behaviors' in x and x['behaviors']:
            a.append(extract_values(x['behaviors']))
        else:
            a.append('')        
        complete_array.append(a)


def finder(x,y):
    a = []
    b = []
    d = ''
    if not x['children']:
        if not y:
            empty_children(a,x,x['name'])
        else:
            empty_children(a,x,y)
    else:
        if y:
            d =  y + '/' + x['name']
        else:
            d = x['name']
        if ('criteria' in x and x['criteria']) or ('behaviors' in x and x['behaviors']):
            if y:
                empty_children_1(a,x,y)
            else:
                empty_children_1(a,x,'')
        for k in x['children']:
            finder(k,d)

def main(json_data):
    global complete_array
    complete_array = DEFAULT_COMPLETE_ARRAY.copy()
    c = []
    if 'rules' in json_data:
        rules_data = json_data['rules']
        if 'children' in rules_data:
            first_children = rules_data['children']
            for x in first_children:
                finder(x,'')
    if 'rules' in json_data and 'advancedOverride' in json_data['rules']:
        if json_data['rules']['advancedOverride']:
            c.append("Advanced Override")
            c.append("")
            c.append("")
            c.append("")
            c.append(json_data['rules']['advancedOverride'])
            complete_array.append(c)
    return complete_array, json_data['propertyVersion']



#commenting this as its used another script
"""file_path = "input.json"
csv_file = "output.csv"

with open(file_path, "r") as file:
    json_data = json.load(file)

a = main(json_data)
#a = complete_array
#print(a)
write2csv(complete_array, csv_file)"""
