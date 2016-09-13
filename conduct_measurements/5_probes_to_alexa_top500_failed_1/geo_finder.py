
import csv
from geoip import geolite2
import time

# To record the codes execution time
start_time = time.time()

dict_country = {}
dict_continent = {}

IN_FILE = 'exp_input_v1.csv'
OUT_FILE = 'exp_input_bck.csv'

with open(OUT_FILE, 'w') as out_csvfile:
    spamewriter = csv.writer(out_csvfile, dialect='excel', delimiter=';')
    spamewriter.writerow(['Site name', 'Site IP', 'Country', 'Continent'])

    with open(IN_FILE, 'r') as f_handler:
        next(f_handler)
        for line in f_handler:
            row = [line.split(';')[0].strip()]
            ip = line.split(';')[1].strip()
            row.append(ip)
            match = geolite2.lookup(ip)

            country = match.country
            continent = match.continent
            row.append(country)
            row.append(continent)
            spamewriter.writerow(row)
            if country not in dict_country.keys():
                dict_country[country] = 1
            else:
                dict_country[country] += 1
            if continent not in dict_continent.keys():
                dict_continent[continent] = 1
            else:
                dict_continent[continent] += 1

            print row

    continents = []
    for key in dict_continent.keys():
        continents.append('{0}: {1}'.format(key, dict_continent[key]))
    spamewriter.writerow(continents)

print "dict_country:", dict_country
print "dict_continent:", dict_continent
print (time.time() - start_time), "seconds are used to execute the codes"