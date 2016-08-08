from ipwhois import IPWhois

import csv

with open('exp_input.csv', 'r+') as f_handler:
    spamewriter = csv.writer(f_handler, dialect='excel', delimiter=';')
    next(f_handler)
    for line in f_handler:
        row = [i.strip() for i in line.split(';')]
        print row
        ip = row[-1]
        obj = IPWhois(ip)
        results = obj.lookup_rdap(depth=1)
        print results['asn_country_code']
        row.append(results['asn_country_code'])
        print row
        spamewriter.writerow(row)