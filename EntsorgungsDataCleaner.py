# -*- coding: utf-8 -*-

import os, os.path
import json
import io
from pprint import pprint
import fileinput
import re

path = '<Path>'
path_summary = '<Path>'


month_mapping = { "btMCMonth1":"Januar", "btMCMonth2":"Februar", "btMCMonth3":"März", "btMCMonth4":"April", "btMCMonth5":"Mai", "btMCMonth6":"Juni", "btMCMonth7":"Juli", "btMCMonth8":"August", "btMCMonth9":"September", "btMCMonth10":"Oktober", "btMCMonth11":"November", "btMCMonth12":"Dezember" }


def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    '''
    alist.sort(key=natural_keys) sorts in human order
    http://nedbatchelder.com/blog/200712/human_sorting.html
    (See Toothy's implementation in the comments)
    '''
    return [ atoi(c) for c in re.split('(\d+)', text) ]

def main():
    files = [name for name in os.listdir(path) if os.path.isfile(os.path.join(path, name)) and name != '.DS_Store']
    files = map(lambda n: unicode(n, 'utf-8'), files)
    files.sort(key=lambda x: get_streetname(x))

    print "Anzahl Straßen: " + str(len(files))

    all_streets = []
    filename = files[0]
    print "Hole Straßeninformationen für " + str(filename)
    #for filename in files:
    f = path + filename

    with io.open(f, encoding='utf-8') as data_file:
        street_id = filename.split(' ')[0]
        street_name = ' '.join(filename.split('.')[0].split(' ')[1:])

        # print street_name

        street = {
            "id": street_id,
            "name": street_name # street_name.decode('cp1250')
        }

        data = json.load(data_file)
        months = data.itervalues().next()

        # Sort months in human sorting
        m = []
        for key in months.keys():
            m.append(key);

        month_values = []
        m.sort(key=natural_keys)
        for month_label in m:
            month_name = month_mapping[month_label]
            print month_name

            print months[month_label]

            # Create descriptions
            months[month_label] = map(lambda day: dayMapping(day), months[month_label])

            print '\n'

            month_obj = {
                "month": month_name,
                "values": months[month_label]
            }

            month_values.append(month_obj)

        street['months'] = month_values

        all_streets.append(street)
        data_file.close()

    # Write to summary file
    print "Schreibe Gesamtübersicht..."
    write_summary(street)

def dayMapping(day):
    d = {
        "date": day['date'],
        "descr": createDescriptionArray(day['descr'])
    }
    return d

def createDescriptionArray(descrStr):
    return descrStr.split(', ')


def get_streetname(str):
    return ' '.join(str.split('.')[0].split(' ')[1:])

def write_summary(all_streets_arr):
    sum_file = path_summary + 'entsorgungstermine.json'
    if os.path.exists(sum_file):
        os.remove(sum_file)

    with open(sum_file, 'w') as outfile:
        json.dump(all_streets_arr, outfile)

if __name__ == '__main__':
    main()