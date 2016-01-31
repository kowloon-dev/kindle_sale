#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from os import pardir
from os.path import dirname
from os.path import sep
import configparser
import logging
import traceback

# Construct config_file path & read config file
try:
    pardir_path = dirname(__file__) + sep + pardir
    config_file = pardir_path + "/config/kindle_sale.ini"
    config = configparser.ConfigParser()
    config.read(config_file)
except:
    logging.error(traceback.format_exc())
    raise

# ------------  Import parameters from config file  ------------

# [ItemSearch]
access_key_id = config.get('ItemSearch', 'access_key_id')
secret_key =    config.get('ItemSearch', 'secret_key')
associate_tag = config.get('ItemSearch', 'associate_tag')
search_index =  config.get('ItemSearch', 'search_index')
item_page =     int(config.get('ItemSearch', 'item_page'))
region =        config.get('ItemSearch', 'region')

# [GetPrice]
price_tag =       config.get('GetPrice', 'price_tag')
price_class =     config.get('GetPrice', 'price_class')
retry_sleep_min = int(config.get('GetPrice', 'retry_sleep_min'))
retry_sleep_max = int(config.get('GetPrice', 'retry_sleep_max'))
retry_max =       int(config.get('GetPrice', 'retry_max'))
currency_symbol = config.get('GetPrice', 'currency_symbol')

# [Global]
base_url = config.get('Global', 'base_url')

# [Logging]
logging_level = config.get('Logging', 'logging_level')
log_dir = pardir_path + "/log/"
log_filename = log_dir + config.get('Logging', 'log_filename')

# [MailSend]
smtp_host =     config.get('MailSend', 'smtp_host')
smtp_port =     config.get('MailSend', 'smtp_port')
local_host =    config.get('MailSend', 'local_host')
smtpauth_id =   config.get('MailSend', 'smtpauth_id')
smtpauth_pass = config.get('MailSend', 'smtpauth_pass')
from_addr =     config.get('MailSend', 'from_addr')
to_addr =       config.get('MailSend', 'to_addr')
mail_title =    config.get('MailSend', 'mail_title')

# [SQL]
db =         pardir_path + "/db/" + config.get('SQL', 'db_filename')
item_table = config.get('SQL', 'item_table')


# ------------  Construct Flask Parameters  ------------

flask_static_path = pardir_path + "/static"
flask_templates_path = pardir_path + "/templates"
