
import csv
from geoip import geolite2
import time

# To record the codes execution time
start_time = time.time()

dict_country = {}
dict_continent = {}

IN_FILE = 'top_510_websites_fr.csv'
OUT_FILE = 'top_510_websites_fr_geo_statistics.csv'

with open(OUT_FILE, 'w') as out_csvfile:
    spamewriter = csv.writer(out_csvfile, dialect='excel', delimiter=';')
    spamewriter.writerow(['Site name', 'Site IPv4', 'Country', 'Continent', 'Site IPv6', 'Country', 'Continent'])

    counter = 0
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

            # Make a statistics for geoIPv4
            if country not in dict_country.keys():
                dict_country[country] = 1
            else:
                dict_country[country] += 1
            if continent not in dict_continent.keys():
                dict_continent[continent] = 1
            else:
                dict_continent[continent] += 1

            # Geolocate ipv6
            if len(line.split(';')) > 4:
                counter += 1
                print "counter", counter
                ipv6 = line.split(';')[4].strip()
                print ipv6
                row.append(ipv6)
                matchv6 = geolite2.lookup(ipv6)
                countryv6 = matchv6.country
                continentv6 = matchv6.continent
                row.append(countryv6)
                row.append(continentv6)

                # Make a statistics for geoIPv6
                if countryv6 not in dict_country.keys():
                    dict_country[countryv6] = 1
                else:
                    dict_country[countryv6] += 1
                if continentv6 not in dict_continent.keys():
                    dict_continent[continentv6] = 1
                else:
                    dict_continent[continentv6] += 1

            spamewriter.writerow(row)
            print row

    countries = []
    for key in dict_country.keys():
        countries.append('{0}: {1}'.format(key, dict_country[key]))
    spamewriter.writerow(countries)

    continents = []
    for key in dict_continent.keys():
        continents.append('{0}: {1}'.format(key, dict_continent[key]))
    spamewriter.writerow(continents)

print "dict_country:", dict_country
print "dict_continent:", dict_continent
print (time.time() - start_time), "seconds are used to execute the codes"