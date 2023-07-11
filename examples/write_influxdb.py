#!/usr/bin/env python3
"""
Example code on how to print ~all info about your router, you can try it by running:
python3 data_dump.py http://admin:PASSWORD@192.168.8.1/
"""
from argparse import ArgumentParser
import os.path
import re
import pprint
import sys
from typing import Any, Callable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), os.path.pardir))

from huawei_lte_api.Client import Client  # noqa: E402
from huawei_lte_api.Connection import Connection  # noqa: E402

from influxdb import InfluxDBClient


influx_client = InfluxDBClient(host='localhost', port=8086)
influx_client.switch_database('mydb') 


parser = ArgumentParser()
parser.add_argument('url', type=str)
parser.add_argument('--username', type=str)
parser.add_argument('--password', type=str)
args = parser.parse_args()
keys_to_convert = ['CurrentConnectTime', 'CurrentUpload', 'CurrentDownload', 'CurrentDownloadRate', 'CurrentUploadRate', 'TotalUpload', 'TotalDownload', 'TotalConnectTime', 'showtraffic', 'MaxUploadRate', 'MaxDownloadRate','ConnectionStatus','CurrentNetworkType','CurrentNetworkTypeEx','CurrentServiceDomain','CurrentWifiUser','RoamingStatus','ServiceStatus','SignalIcon','cellroam' ]


with Connection(args.url, username=args.username, password=args.password) as connection:
    client = Client(connection)
    
    device_info = client.monitoring.traffic_statistics()
    device_info.update(client.monitoring.status())
    device_info.update(client.device.signal())
    
    device_tags = client.device.information()
    device_signal = client.device.signal()
    
    rsrp = re.findall(r'-\d+', device_signal.get('rsrp')).pop(0)
    rsrq = re.findall(r'-\d+.\d+', device_signal.get('rsrq')).pop(0)
    
    rssi = re.findall(r'-\d+', device_signal.get('rssi')).pop(0)
    sinr = re.findall(r'\d+', device_signal.get('sinr')).pop(0)
    
    for key in keys_to_convert:
        if key in device_info:
            device_info[key] = int(device_info[key])
    # Convert data into a format suitable for InfluxDB

    json_body_traffic = [
        {
            "measurement": "hueawei_router_traffic",
            "tags": device_tags
            ,
            "fields": device_info
        }
    ]
    influx_client.write_points(json_body_traffic)

    json_body_signal = [
        {
            "measurement": "hueawei_signal",
            "tags": device_tags
            ,
            "fields": {
            "rsrp":float(rsrp),
            "rsrq":float(rsrq),
            "rssi":float(rssi),
            "sinr":float(sinr),
            }
        }
    ]
    influx_client.write_points(json_body_signal)

    pprint.pprint( json_body_traffic)
    pprint.pprint( json_body_signal)
   
"""
Example of data to be written to influx

[{'fields': {'BatteryLevel': None,
             'BatteryPercent': None,
             'BatteryStatus': None,
             'ConnectionStatus': 901,
             'CurrentConnectTime': 16152,
             'CurrentDownload': 595291481,
             'CurrentDownloadRate': 9714,
             'CurrentNetworkType': 19,
             'CurrentNetworkTypeEx': 1011,
             'CurrentServiceDomain': 3,
             'CurrentUpload': 174116890,
             'CurrentUploadRate': 5273,
             'CurrentWifiUser': 0,
             'MaxDownloadRate': 8371358,
             'MaxUploadRate': 622425,
             'PrimaryDns': '41.1.240.29',
             'PrimaryIPv6Dns': None,
             'RoamingStatus': 0,
             'SecondaryDns': '41.1.239.253',
             'SecondaryIPv6Dns': None,
             'ServiceStatus': 2,
             'SignalIcon': 5,
             'SignalStrength': None,
             'SimStatus': '1',
             'TotalConnectTime': 1789048,
             'TotalDownload': 8011565266,
             'TotalUpload': 984422899,
             'TotalWifiUser': '64',
             'WifiConnectionStatus': None,
             'WifiStatus': '0',
             'WifiStatusExCustom': '0',
             'arfcn': None,
             'band': '3',
             'bsic': None,
             'cell_id': '29458206',
             'cellroam': 1,
             'classify': 'cpe',
             'cqi0': '12',
             'cqi1': '8',
             'currenttotalwifiuser': '0',
             'dl_mcs': 'mcsDownCarrier1Code0:15 mcsDownCarrier1Code1:16',
             'dlbandwidth': '10MHz',
             'dlfrequency': '1862600kHz',
             'earfcn': 'DL:1776 UL:19776',
             'ecio': None,
             'enodeb_id': '0115071',
             'flymode': '0',
             'hvdcp_online': '0',
             'ims': '0',
             'lac': None,
             'ltedlfreq': '18626',
             'lteulfreq': '17676',
             'maxsignal': '5',
             'mode': '7',
             'nei_cellid': None,
             'pci': '266',
             'plmn': '65501',
             'rac': None,
             'rrc_status': None,
             'rscp': None,
             'rsrp': '-79dBm',
             'rsrq': '-8.0dB',
             'rssi': '-57dBm',
             'rxlev': None,
             'sc': None,
             'showtraffic': 1,
             'simlockStatus': '0',
             'sinr': '7dB',
             'speedLimitStatus': '0',
             'tac': '20006',
             'tdd': None,
             'transmode': 'TM[4]',
             'txpower': 'PPusch:2dBm PPucch:-6dBm PSrs:0dBm PPrach:-7dBm',
             'ul_mcs': 'mcsUpCarrier1:23',
             'ulbandwidth': '10MHz',
             'ulfrequency': '1767600kHz',
             'usbup': '0',
             'wdlfreq': None,
             'wififrequence': '0',
             'wifiindooronly': '0',
             'wifiswitchstatus': '1'},
  'measurement': 'hueawei_router_traffic',
  'tags': {'Classify': 'cpe',
           'DeviceName': 'B535-932',
           'HardwareVersion': 'WL2B535M',
           'Iccid': '89330000000029032674',
           'Imei': '860415043074029',
           'ImeiSvn': '09',
           'Imsi': '655013302902967',
           'MacAddress1': '6C:06:D6:AB:D6:3A',
           'MacAddress2': None,
           'Mccmnc': '65501',
           'Msisdn': None,
           'ProductFamily': 'LTE',
           'SerialNumber': 'SHTUT20512000641',
           'SoftwareVersion': '10.0.5.1(H195SP2C983)',
           'WanIPAddress': '100.77.223.36',
           'WanIPv6Address': None,
           'WebUIVersion': 'WEBUI 10.0.5.1(W2SP2C7601)',
           'WifiMacAddrWl0': '6C:06:D6:AB:D6:3B',
           'WifiMacAddrWl1': '6C:06:D6:AB:D6:40',
           'iniversion': 'B535-932-CUST 10.0.2.2(C1232)',
           'spreadname_en': 'Huawei 4G Router 3 Pro',
           'spreadname_zh': '华为4G路由3 Pro',
           'submask': '255.255.255.255',
           'supportmode': 'LTE|WCDMA|GSM',
           'uptime': '16184',
           'wan_dns_address': '41.1.240.29,41.1.239.253',
           'wan_ipv6_dns_address': None,
           'workmode': 'LTE'}}]
[{'fields': {'rsrp': -79.0, 'rsrq': -8.0, 'rssi': -57.0, 'sinr': 7.0},
  'measurement': 'hueawei_signal',
  'tags': {'Classify': 'cpe',
           'DeviceName': 'B535-932',
           'HardwareVersion': 'WL2B535M',
           'Iccid': '89330000000029032674',
           'Imei': '860415043074029',
           'ImeiSvn': '09',
           'Imsi': '655013302902967',
           'MacAddress1': '6C:06:D6:AB:D6:3A',
           'MacAddress2': None,
           'Mccmnc': '65501',
           'Msisdn': None,
           'ProductFamily': 'LTE',
           'SerialNumber': 'SHTUT20512000641',
           'SoftwareVersion': '10.0.5.1(H195SP2C983)',
           'WanIPAddress': '100.77.223.36',
           'WanIPv6Address': None,
           'WebUIVersion': 'WEBUI 10.0.5.1(W2SP2C7601)',
           'WifiMacAddrWl0': '6C:06:D6:AB:D6:3B',
           'WifiMacAddrWl1': '6C:06:D6:AB:D6:40',
           'iniversion': 'B535-932-CUST 10.0.2.2(C1232)',
           'spreadname_en': 'Huawei 4G Router 3 Pro',
           'spreadname_zh': '华为4G路由3 Pro',
           'submask': '255.255.255.255',
           'supportmode': 'LTE|WCDMA|GSM',
           'uptime': '16184',
           'wan_dns_address': '41.1.240.29,41.1.239.253',
           'wan_ipv6_dns_address': None,
           'workmode': 'LTE'}}]
"""