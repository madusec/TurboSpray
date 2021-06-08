# Modules

import os, os.path, sys, time, argparse, json, csv, subprocess, random, datetime, pyfiglet
import pandas as pd

from time import sleep
from termcolor import colored
from fake_useragent import UserAgent
from bs4 import BeautifulSoup as bs
from random import randrange
from email.utils import getaddresses
from collections import Counter

from stem import Signal
from stem.control import Controller

from helium import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import InvalidSessionIdException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

import requests
from requests import Session
from requests.auth import HTTPBasicAuth
from requests.exceptions import SSLError
from requests.exceptions import InvalidURL
from requests.exceptions import ConnectionError
from requests.exceptions import ReadTimeout
from requests.exceptions import ConnectTimeout
from requests.exceptions import ProxyError
from requests.exceptions import MissingSchema
from requests.exceptions import InvalidSchema

import urllib3
from urllib.parse import urlparse
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import warnings
warnings.filterwarnings("ignore")