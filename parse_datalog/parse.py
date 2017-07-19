#!/usr/bin/python
__author__ = 'Nathan.Airey'

# import modules used here -- sys is a very standard one
import sys
import json
import requests
import csv
import unicodedata
import time
import pytz
from datetime import datetime, tzinfo
import dateutil.parser
from pytz import timezone
import pytz
import ast
import re
import jellyfish
# Gather our code in a main() function
def main():
  # Command line args are in sys.argv[1], sys.argv[2] ..
  # sys.argv[0] is the script name itself and can be ignored

    print "out yay!"
    tz = timezone('Australia/Melbourne')
    print tz

    try:
        clients = fetch_clients('clients.txt')
        print clients[0]
    except:
        print "no clients!"

    try:
        services = fetch_services('services.txt')
        print services[0]
    except:
        print "no services!"

    try:
        appointments = fetch_appointments('appointments.csv')
        print appointments[0]
        print "total appts: "+ str(len(appointments))
    except:
        print "no appointments!"

    print "fin!"



def process_appointments(appointments, clients, services):
    no_clients = 0
    no_service = 0
    count = 0
    parsed_appointments = []
    clients_to_import = []
    for appt in appointments:
        count += 1
        # find client id
        client_id = ""
        for client in clients:
            if appt['client'].upper() == client['first_name'].upper() +' '+ client['last_name'].upper():
                client_id = client['id']
                break

        if not client_id:
            no_clients += 1
            # print appt['client']

        service_id = '17592187703495'

        appointment_note = (
         'booking_notes: ' + appt['booking_notes'] + '\n\n'
         'client: ' + appt['client'] + '\n'
         'phone: ' + appt['phone'] + '\n'
         'service: ' + appt['service'] + '\n'
         'status: ' + appt['status'] + '\n'
         'operator: ' + appt['operator' ] + '\n'
         'booking_type: ' + appt['booking_type' ]
        )

        start = appt['service_date'] + ' ' + appt['start_time']
        end = appt['service_date'] + ' ' + appt['end_time']
        # print datetime.strptime(start, "%d/%m/%Y %I:%M %p")

        appt_data = {
            'start_time': start,
            'end_time': end,
            'duration': appt['duration'],
            'price': appt['price'],
            'service_id': str(service_id),
            'client_id': str(client_id),
            'appointment_note': appointment_note
        }

        # write_data(appt_data, 'out.csv')
        parsed_appointments.append(appt_data)

    with open('export_appointments.csv', 'wb') as csvfile:
        fieldnames = ['start_time', 'end_time', 'duration', 'price', 'service_id', 'client_id', 'appointment_note']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for appt in parsed_appointments:
            writer.writerow(appt)

    print no_clients
    print no_service

def process_clients(clients):
    # Operator	Location	Service	Date	Start Time	End Time	Duration (Mins)	Client Name	Contact No	Price	Status	Booking Type	Comments
    clients_arr = []
    rownum, max_rows = 0, 0
    data  = open('clients.csv', 'rU')
    reader = csv.reader(data, delimiter=',', quotechar='"')
    for row in reader:

        if rownum == 0:
            header = row
        else:
            colnum = 0
            full_name = row[0].split()
            first_name = full_name[0].strip()
            last_name = ' '.join(full_name[1:].strip())
            mobile = row[5]
            email = row[6]
            client = {'first_name': first_name, 'last_name': last_name, 'mobile': mobile, 'email': email}

            client_id = False
            for c in clients:
                if c['first_name'].upper() +' '+ c['last_name'].upper() == client['first_name'].upper() +' '+ client['last_name'].upper():
                    client_id = True
                    break

            if not client_id:
                clients_arr.append(client)
                # print client

        rownum += 1

    with open('export_clients.csv', 'wb') as csvfile:
        fieldnames = ['first_name', 'last_name', 'email', 'mobile']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for c in clients_arr:
            writer.writerow(c)

    return clients_arr

def process_client_appointments(clients, appt_map):

    with open('export_client_appointments.csv', 'wb') as csvfile:
        fieldnames = ['client_id', 'appointments']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        writer.writeheader()
        for c in clients:
            appts = ""
            if appt_map.has_key(c['id']):
                appts = appt_map[c['id']]

            writer.writerow({ 'client_id': c['id'], 'appointments': ' '.join(appts) })

def fetch_clients(file):
    with open(file, 'r') as clientsFile:
        content = clientsFile.read()

    clients = re.findall(r'\[([^]]*)\]', content)

    clients_arr = []
    count = 0
    for client in clients:
        count += 1
        # if count > 5:
        #     break
        try:
            strings = re.findall(r'"([^"]*)"', client)
            digits = re.findall('\d+', client)

            c = {}
            c['first_name'] = strings[0].strip()
            c['last_name'] = strings[1].strip()
            c['email'] = strings[2].strip()
            c['mobile'] = strings[3].strip()
            c['id'] = digits[-1].strip()
            clients_arr.append(c)
            # print c
            write_data(c['first_name'] + '|' + c['last_name'] + '|' + c['email'] + '|' + c['mobile'] + '|' + c['id'], "export_clients.txt")
        except:
            continue

    return clients_arr

def fetch_services(file):
    with open(file, 'r') as dataFile:
        content = dataFile.read()

    services = re.findall(r'\[([^]]*)\]', content)
    services_arr = []
    for service in services:
        try:
            name = re.findall(r'"([^"]*)"', service)
            remaining = service.replace(name[0], '')
            digits = re.findall('\d+', remaining)

            data = service.split('"')
            s = {}
            s['name'] = data[1].strip()
            # print data[2].strip().split(' ')
            s['duration'] = digits[0]
            s['price'] = digits[1]
            s['id'] = digits[-1].strip()
            services_arr.append(s)
            # print s
            services_data = "|".join(s.values())
            write_data(services_data, 'out_services.txt')
        except:
            continue

    return services_arr

def fetch_appointments(file):
    # Operator	Location	Service	Date	Start Time	End Time	Duration (Mins)	Client Name	Contact No	Price	Status	Booking Type	Comments
    appointments_arr = []
    rownum, max_rows = 0, 0
    data  = open(file, 'rU')
    reader = csv.reader(data, delimiter=',', quotechar='"')
    for row in reader:

        if rownum == 0:
            header = row
        else:
            colnum = 0
            appointment = {}
            appointment['operator'] = row[0]
            appointment['location'] = row[1]
            appointment['service'] = row[2]
            appointment['service_date'] = row[3]
            appointment['start_time'] = row[4]
            appointment['end_time'] = row[5]
            appointment['start'] = row[3] + ' ' + row[4]
            appointment['end'] = row[3] + ' ' + row[5]
            appointment['duration'] = row[6]
            appointment['client'] = row[7]
            appointment['phone'] = row[8]
            appointment['price'] = row[9]
            appointment['status'] = row[10]
            appointment['booking_type'] = row[11]
            appointment['booking_notes'] = row[12]
            appointments_arr.append(appointment)
        rownum += 1
    return appointments_arr


def write_data(string, file_name):
	venues = open(file_name, "a")
	venues.write(unicode(string) + '\n')
	venues.close()

    # with open('out.csv', 'w') as csvfile:
    #     fieldnames = ['first_name', 'last_name']
    #     writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    #
    #     writer.writeheader()
    #     writer.writerow({'first_name': 'Baked', 'last_name': 'Beans'})
    #     writer.writerow({'first_name': 'Lovely', 'last_name': 'Spam'})
    #     writer.writerow({'first_name': 'Wonderful', 'last_name': 'Spam'})


# Standard boilerplate to call the main() function to begin
# the program.
if __name__ == '__main__':
    main()
