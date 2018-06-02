#-*- coding: utf-8 -*-
import pynetdot
import csv
import netaddr
import datetime
import logging

"""
Insertion UPS devices into the netdot via API
source file in csv format
The header of the csv file must be like this:
site_name;name;snmp_target;snmp_version;snmp_community;snmp_managed;entity_id
pip install pynetdot
ip = str(netaddr.IPAddress(ip))
"""

logging.basicConfig(filename='main.log', level=logging.INFO)

# Connect to netdot server
pynetdot.setup(
    url='http://127.0.0.1/netdot',
    username='admin',
    password='pass')

with open('ups_file', 'r') as ibp:
    reader = csv.DictReader(ibp, delimiter=";")
    for row in reader:
        ups_name = row['name']
        snmp_ver = row['snmp_version']
        snmp_target =  row['snmp_target']
        snmp_target = snmp_target + '/32'
        snmp_com = row['snmp_community']
        snmp_manag = row['snmp_managed']
        site_name = row['site_name'].decode('utf-8')
        entity_id = row['entity_id']
        site = pynetdot.Site.get_first(name=site_name)
        site_id = site.id
        if not site_id:
            logging.info("netdot don't have site %s. Host with name %s will be created without site" % (site_name, ups_name))
        ip = pynetdot.Ipblock.get_first(address=snmp_target)
        if ip:
            ip_id = ip.id
        else:
            newip = pynetdot.Ipblock(name = ups_name)
            newip.address =  snmp_target #  need to be in x.x.x.x/32 format
            newip.description = ups_name
            newip.save()
            ip_id = newip.id
        if pynetdot.Device.get_first(snmp_target=ip_id):
            logging.info("host with ip address %s already exist" % snmp_target)
        else:        
            rname = pynetdot.RR(name = ups_name)
            rname.name = ups_name
            rname.zone = 9 #  zone == power
            rname.save()
            device = pynetdot.Device(name=ups_name)
            if snmp_manag == 'True':
                print "Условие сработало"
                print snmp_manag
                device.snmp_managed = 1
                device.community = snmp_com
                device.snmp_version = snmp_ver
                device.snmp_bulk = 1
                device.snmp_polling = 1
                device.canautoupdate = 1
            else:
                print "Условие не сработало"
                print snmp_manag
                device.snmp_managed = 0
                device.snmp_version = 2 #  Otherwise device will not be created
            device.name = rname.id
            device.snmp_target = ip_id
            device.owner = entity_id
            device.site = site_id
            device.save() #  сначала сохраняется с именем  3386.defaultdomain
            device.name = rname.id
            device.save() #  а вот теперь все норм


