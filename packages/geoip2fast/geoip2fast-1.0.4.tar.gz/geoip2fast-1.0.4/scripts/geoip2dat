#!/usr/bin/env python3
# encoding: utf-8
# -*- coding: utf-8 -*-
"""GeoIP2Dat - DAT file update for GeoIP2Fast"""
"""
GeoIP2Dat - Version: v1.0.4 - 13/Sep/2023

Author: Ricardo Abuchaim - ricardoabuchaim@gmail.com
        https://github.com/rabuchaim/geoip2fast/

License: MIT

"""
__appid__   = "GeoIP2Dat"
__version__ = "1.0.4"

import sys, os, gzip, pickle, io, inspect, socket, struct, json, hashlib
from datetime import datetime as dt
from geoip2fast import CIDRDetail
from argparse import ArgumentParser, HelpFormatter, SUPPRESS
from contextlib import contextmanager
from timeit import default_timer
from pprint import pprint as pp

##──── URL TO DOWNLOAD CSV FILES FROM MAXMIND (FOR FUTURE VERSIONS) ───────────────────────────────────────────────────────────────────────────────────
MM_URL_COUNTRY  = "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-Country-CSV&license_key=YOUR_LICENSE_KEY&suffix=zip"
MM_URL_CITY     = "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City-CSV&license_key=YOUR_LICENSE_KEY&suffix=zip"
MM_URL_ASN      = "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-ASN-CSV&license_key=YOUR_LICENSE_KEY&suffix=zip"
MM_URL_COUNTRY_SHA256 = "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-Country-CSV&license_key=YOUR_LICENSE_KEY&suffix=zip.sha256"
MM_URL_CITY_SHA256    = "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City-CSV&license_key=YOUR_LICENSE_KEY&suffix=zip.sha256"
MM_URL_ASN_SHA256     = "https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-ASN-CSV&license_key=YOUR_LICENSE_KEY&suffix=zip.sha256"
##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
##──── MAXMIND STANDARD FILENAMES ────────────────────────────────────────────────────────────────────────────────────────────────
MM_COUNTRY_LOCATIONS_FILENAME   = "GeoLite2-Country-Locations-XX.csv"
MM_COUNTRY_BLOCKS_FILENAME      = "GeoLite2-Country-Blocks-IPv4.csv"
MM_CITY_LOCATIONS_FILENAME      = "GeoLite2-City-Locations-XX.csv"
MM_CITY_BLOCKS_FILENAME         = "GeoLite2-City-Blocks-IPv4.csv"
MM_ASN_BLOCKS_FILENAME          = "GeoLite2-ASN-Blocks-IPv4.csv"
##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
##──── GEOIP2FAST FILENAME ───────────────────────────────────────────────────────────────────────────────────────────────────────
GEOIP2FAST_DAT_FILENAME_GZ      = "geoip2fast.dat.gz"
GEOIP2FAST_REDIS_DAT_FILENAME_GZ= "geoip2fastredis.dat.gz"
GEOIP2FAST_ASN_DAT_FILENAME_GZ  = GEOIP2FAST_DAT_FILENAME_GZ

GEOIP2FAST_CITY_DAT_FILENAME_GZ = "geoip2fastcity.dat.gz"
GEOIP2FAST_FULL_DAT_FILENAME_GZ = "geoip2fastfull.dat.gz"

DEFAULT_COUNTRY_SOURCE_INFO     = "MAXMIND:GeoLite2-Country-CSV_"
DEFAULT_ASN_SOURCE_INFO         = "MAXMIND:GeoLite2-ASN-CSV_"
DEFAULT_CITY_SOURCE_INFO        = "MAXMIND:GeoLite2-CITY-CSV_"
DEFAULT_FULL_SOURCE_INFO        = "MAXMIND:GeoLite2-CountryASN-CSV_"

LIST_SLICE_SIZE                 = 5000
REDIS_LIST_SLICE_SIZE           = 5000
##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
AVAILABLE_LANGUAGES     = ['de','en','es','fr','ja','pt-BR','ru','zh-CN']

__DAT_VERSION__         = 104
terminalWidth           = 100

sys.tracebacklimit      = 0
doubleLine              = "═"
singleLine              = "─"
middot                  = "\xb7"

##──── To enable DEBUG flag just export an environment variable GEOIP2DAT_DEBUG with any value ──────────────────────────────────
##──── Ex: export GEOIP2DAT_DEBUG=1 ─────────────────────────────────────────────────────────────────────────────────────────────
_DEBUG = bool(os.environ.get("GEOIP2DAT_DEBUG",False))

os.environ["PYTHONWARNINGS"]    = "ignore"
os.environ["PYTHONIOENCODING"]  = "UTF-8"        

reservedNetworks = {
    "0.0.0.0/8":         {"01":"Reserved for self identification"},
    "10.0.0.0/8":        {"02":"Private Network Class A"},
    "100.64.0.0/10":     {"03":"Reserved for Shared Address Space"},
    "127.0.0.0/8":       {"04":"Localhost"},
    "169.254.0.0/16":    {"05":"APIPA Automatic Priv.IP Addressing"},
    "172.16.0.0/12":     {"06":"Private Network Class B"},
    "192.0.0.0/29":      {"07":"Reserved IANA"},
    "192.0.2.0/24":      {"08":"Reserved for TEST-NET"},
    "192.88.99.0/24":    {"09":"Reserved for 6to4 Relay Anycast"},
    "192.168.0.0/16":    {"10":"Private Network Class C"},
    "198.18.0.0/15":     {"11":"Reserved for Network Benchmark"},
    "224.0.0.0/4":       {"12":"Reserved Multicast Networks"},
    "240.0.0.0/4":       {"13":"Reserved for future use"},
    "255.255.255.255/32":{"14":"Reserved for broadcast"}
    }

##──── Number os possible IPs in a network range. (/0, /1 .. /8 .. /24 .. /30, /31, /32) ─────────────────────────────────────
##──── Call the index of a list. Ex. numIPs[24] (is the number os IPs of a network range class C /24) ──────────────────────
numIPs = sorted([2**num for num in range(0,33)],reverse=True) # from 0 to 32
##──── numHosts is the numIPs - 2 ────────────────────────────────────────────────────────────────────────────────────────────────
numHosts = sorted([(2**num)-2 for num in range(0,33)],reverse=True) # from 0 to 32

##──── Function to check the memory use ────────────────────────────────────────────────────────────────────────────────────────
def get_mem_usage()->float:
    ''' Memory usage in MiB '''
    with open('/proc/self/status') as f:
        memusage = f.read().split('VmRSS:')[1].split('\n')[0][:-3]
    return float(memusage.strip()) / 1024

def int2ip(addr)->str:
    try:
        return socket.inet_ntoa(struct.pack("!I", addr))
    except:
        return ""

def ip2int(ipaddr)->int:
    try: 
        return struct.unpack("!I", socket.inet_aton(ipaddr))[0]
    except: 
        return 0

def is_inside_network(cidrIp,cidrNetwork):
    import ipaddress
    try:
        if cidrIp == "" or cidrNetwork == "":
            return False
        checkNET = ipaddress.ip_network(cidrNetwork)
        checkIP = ipaddress.ip_network(cidrIp)
        return (checkIP.subnet_of(checkNET))
    except Exception as ERR:
        print("ERROR is_inside_network %s / %s: %s"%(cidrIp,cidrNetwork,str(ERR)))
    return False    

def json_default_formatter(o):
    import datetime
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.__str__

##──── RETURN A MD5SUM HASH OF A STRING ────────────────────────────────────────────────────────────────────────────────────────
def get_md5(stringToHash=""):
    stringToHash = f"{str(stringToHash)}".encode()
    resultMd5 = hashlib.md5(stringToHash)
    return resultMd5.hexdigest()

##──── Function to retrieve the name of a var in string ────────────────────────────────────────────────────────────────────────────────────────
def retrieve_var_name(var):
    callers_local_vars = inspect.currentframe().f_back.f_locals.items()
    return [var_name for var_name, var_val in callers_local_vars if var_val is var]

##──── CLASS TO INTERCEPT INIT, ENTER and EXIT ───────────────────────────────────────────────────────────────────────────────────
class geoip2dat():
    def __init__(self):
        terminal_adjust()
        log(letter_repeat(">",terminalWidth))
        log(f">>>>> STARTING {__appid__} v{__version__}")
        log(letter_repeat(">",terminalWidth))
    def __enter__(self):
        pass        
    def __exit__(self,type,value,traceback):
        terminal_adjust()
        log(letter_repeat("<",terminalWidth))
        log(f"<<<<< EXITING {__appid__} PROCESS")
        log(letter_repeat("<",terminalWidth))
    def __run__(self,args):
        run()

##──── CLASS FOR ARGUMENT PARSER ─────────────────────────────────────────────────────────────────────────────────────────────────
class class_argparse_formatter(HelpFormatter):
    my_max_help_position = 30
    ttyRows, ttyCols = os.popen('stty size', 'r').read().split()
    ttyRows = int(ttyRows)
    ttyCols = (int(ttyCols) // 4) * 3
    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = 'Sintax: '
        return super(class_argparse_formatter, self).add_usage(usage, actions, groups, prefix)
    def _format_usage(self, usage, actions, groups, prefix):
        return super(class_argparse_formatter, self)._format_usage(usage, actions, groups, prefix)
    def add_text(self, text):
        if text is not SUPPRESS and text is not None:
            if text.startswith('1|'):   # 1| antes do texto dá espaço de 2 linhas
                text = str(text[2:]+"\n\n")
            return super()._add_item(self._format_text, [text])
    def _split_lines(self, text, width): # 0| antes do texto não dá espaço entre linhas
        if text.startswith('0|'):
            return text[2:].splitlines()
        return super()._split_lines(text, width=class_argparse_formatter.ttyCols-class_argparse_formatter.my_max_help_position-5) + ['']
    def _format_action(self, action):
        self._max_help_position = class_argparse_formatter.my_max_help_position
        self._indent_increment = 2
        self._width = class_argparse_formatter.ttyCols
        return super(class_argparse_formatter, self)._format_action(action)
    
class GeoIP2DatError(Exception):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

def letter_repeat(letter,times)->str:
    letter1=''
    for N in range (times):
        letter1 = letter1 + letter
    return letter1

def terminal_adjust()->None:
    global terminalWidth, ttyCols, ttyRows
    try:
        ttyRows, ttyCols        = os.popen('stty size', 'r').read().split()
        ttyRows, ttyCols        = int(ttyRows), int(ttyCols)
        
        terminalWidth = ttyCols-1 if ttyCols-1 < terminalWidth else terminalWidth
    except Exception as ERR:
        terminalWidth = 100

##──── Function to check the memory use ────────────────────────────────────────────────────────────────────────────────────────
def get_mem_usage()->float:
    ''' Memory usage in MiB '''
    with open('/proc/self/status') as f:
        memusage = f.read().split('VmRSS:')[1].split('\n')[0][:-3]
    return float(memusage.strip()) / 1024

##──── Functions to print to stdout ─────────────────────────────────────────────────────────────────────────────────────────────────
def _log_empty(msg,end=""):return
def log(msg,end="\n"):
    print(msg,end=end,flush=True)
def logVerbose(msg,end="\n"):
    print(msg,end=end,flush=True)
def logDebug(msg,end="\n"):
    print("[DEBUG] "+msg,end=end,flush=True)
def logError(msg,end="\n"):
    print(cRed("[ERROR] "+msg),end=end,flush=True)
##──── Return date with no spaces to use with filenames ──────────────────────────────────────────────────────────────────────────
def get_date():
    A='%Y%m%d%H%M%S'
    B=dt.now()
    return B.strftime(A)

##──── ANSI colors ───────────────────────────────────────────────────────────────────────────────────────────────────────────────
def cRed(msg):return '\033[91m'+msg+'\033[0m'
def cYellow(msg):return '\033[93m'+msg+'\033[0m'
def cGrey(msg): return '\033[90m'+msg+'\033[0m'
def cBlue(msg): return '\033[94m'+msg+'\033[0m'


########################################################################################################################
# CLOCK ELAPSED TIME
@contextmanager
def elapsed_timer():
    start = default_timer()
    elapsed = lambda: default_timer() - start
    yield lambda: elapsed()
    end = default_timer()
    elapsed = lambda: end-start

def timer(elapsed_timer_name): 
    try:
        return "[%.6f sec]"%elapsed_timer_name
    except:
        try:
            return "[%.6f sec]"%elapsed_timer_name()
        except:
            return "[error sec]"

########################################################################################################################
## SPLIT A LIST OR A DICT
def split_list(lista, n):
    for i in range(0, len(lista), n):
        yield lista[i:i + n]

def take(iterable, start, stop):
    from itertools import islice
    return islice(iterable, start, stop)
#################################################################################################################################


##################################################################################################################################
##################################################################################################################################

                         ########     ##     ##    ##    ## 
                         ##     ##    ##     ##    ###   ## 
                         ##     ##    ##     ##    ####  ## 
                         ########     ##     ##    ## ## ## 
                         ##   ##      ##     ##    ##  #### 
                         ##    ##     ##     ##    ##   ### 
                         ##     ##     #######     ##    ## 
 
##################################################################################################################################
##################################################################################################################################
#defrun
def run(country_dir,output_dir,language="en",source_info=""):
    global geoip, dictCountryByID, asnByCIDR, asnByID
    with elapsed_timer() as elapsed_total:
        if language not in AVAILABLE_LANGUAGES:
            raise GeoIP2DatError(F"Invalid language. Valid options are {str(AVAILABLE_LANGUAGES)[1:-1]}")
        ##──── Check the directories and filenames ───────────────────────────────────────────────────────────────────────────────────────
        try:
            with elapsed_timer() as elapsed:
                if not os.path.isdir(country_dir):
                    raise GeoIP2DatError("Invalid country CSV files directory. %s"%(country_dir))
                if not os.path.isfile(os.path.join(country_dir,MM_COUNTRY_BLOCKS_FILENAME)):
                    raise GeoIP2DatError("Unable to access the file %s in directory %s"%(MM_COUNTRY_BLOCKS_FILENAME,country_dir))
                if not os.path.isfile(os.path.join(country_dir,MM_COUNTRY_LOCATIONS_FILENAME.replace("XX",args.language))):
                    raise GeoIP2DatError("Unable to access the file %s in directory %s"%(MM_COUNTRY_LOCATIONS_FILENAME.replace("XX",args.language),country_dir))
                if not os.path.isdir(output_dir):
                    raise GeoIP2DatError("Invalid output directory. %s"%(output_dir))
                log(f"- Checking directories... done! {timer(elapsed())}")
        except Exception as ERR:
            logError("Failed at directories check. %s"%(str(ERR)))
            return 1
        try:
            with elapsed_timer() as elapsed:
                if os.path.isfile(os.path.join(output_dir,GEOIP2FAST_DAT_FILENAME_GZ)):
                    oldFile = os.path.join(output_dir,GEOIP2FAST_DAT_FILENAME_GZ)
                    newFile = os.path.join(output_dir,GEOIP2FAST_DAT_FILENAME_GZ.split(".")[0]+"-"+get_date()+"."+(".".join(GEOIP2FAST_DAT_FILENAME_GZ.split(".")[1:])))
                    logDebug(f"OldFile: {oldFile} - NewFile: {newFile}")
                    try:
                        ##──── If the process of creation fails, the rename will be rolled back ──────────────────────────────────────────────────────────
                        os.rename(oldFile,newFile)
                        log(f"- Renaming file {oldFile} to {newFile}... done! {timer(elapsed())}")
                    except Exception as ERR:
                        raise GeoIP2DatError(f"Failed to rename existing file {GEOIP2FAST_DAT_FILENAME_GZ}. %s"%(str(ERR)))
        except Exception as ERR:
            logError("%s"%(str(ERR)))
            return 1
        ##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        log(f"- Starting read lines from CSV file {MM_COUNTRY_LOCATIONS_FILENAME}")
        with elapsed_timer() as elapsed:
            try:
                dictCountryByCode = {}
                dictCountryByID = {}
                counter = 0
                with io.open(os.path.join(country_dir,MM_COUNTRY_LOCATIONS_FILENAME.replace("XX",args.language)), mode="rt",encoding="utf-8",) as f:
                    next(f)  # skip the first line (the CSV's header)
                    while True:
                        line = f.readline()
                        if not line:
                            break
                        else:
                            try:
                                counter += 1
                                linha = line.replace("\"","").replace("\n","").split(",")
                                geoname_id = linha[0]
                                continent_code = linha[2]
                                continent_name = linha[3]
                                country_iso_code = linha[4]
                                country_name = linha[5]
                                if country_iso_code != "":
                                    dictCountryByID[geoname_id] = country_iso_code
                                    dictCountryByCode[country_iso_code] = country_name
                                else:
                                    dictCountryByID[geoname_id] = continent_code
                                    dictCountryByCode[continent_code] = continent_name                        
                            except Exception as ERR:
                                logError(f"Failed to process line {line} - {str(ERR)}")
                                continue
                log(f"- Read {counter} lines from file {MM_COUNTRY_LOCATIONS_FILENAME.replace('XX',args.language)}... done! {timer(elapsed())}")
            except Exception as ERR:
                logError(f"Failed at country location read file %s"%(str(ERR)))
                return 1
        try:
            with elapsed_timer() as elapsed:
                for k,v in reservedNetworks.items():
                    for code,desc in v.items():
                        dictCountryByCode[code] = desc
                        logDebug(f"{code}: {desc}")
            log(f"- Added {len(reservedNetworks.keys())} private/reserved networks... done! {timer(elapsed())}")
            dictCountryByCode["XX"] = '<unknown>'
            dictCountryByCode["99"] = '<network not found in database>'
            log(f"- Added 1 location '99':'<network not found in database>' for future use... done! {timer(elapsed())}")
        except Exception as ERR:
            logError(f"Failed at country location add new networks %s"%(str(ERR)))
            return 1                        
        ##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        log(f"- Starting read lines from CSV file {MM_COUNTRY_BLOCKS_FILENAME}")
        geoip = {}
        counter = 0
        with elapsed_timer() as elapsed:
            try:
                with io.open(os.path.join(country_dir,MM_COUNTRY_BLOCKS_FILENAME.replace("XX",args.language)), mode="rt",encoding="utf-8") as f:
                    next(f)  # skip the first line (the CSV's header)
                    while True:
                        try:
                            counter += 1
                            line = f.readline()
                            if not line:
                                break
                            else:
                                try:
                                    LINE = line.split(",")
                                    cidr = LINE[0]
                                    CIDRInfo = CIDRDetail(cidr)
                                    geoname_id = LINE[1]
                                    registered_country_id = LINE[2]
                                    represented_country_id = LINE[3]
                                    is_anonymous_proxy = LINE[4]
                                    is_satellite_provider = LINE[5]
                                    if registered_country_id == "":
                                        registered_country_id = geoname_id
                                    if geoname_id == "":    
                                        geoname_id = registered_country_id
                                    if geoname_id == "":
                                        country_code = "XX"
                                    else:
                                        country_code = dictCountryByID[geoname_id]
                                    if country_code == "":
                                        country_code = "XX"
                                    firstIP = CIDRInfo.first_ip2int
                                    lastIP = CIDRInfo.last_ip2int
                                    geoip[firstIP] = {'cidr':cidr,'country_code':country_code,
                                                    'last_ip':lastIP }
                                                #    'geoname_id':geoname_id,
                                                #    'registered_country_id':registered_country_id, 
                                                #    'represented_country_id':represented_country_id,
                                                #    'is_anonymous_proxy':bool(int(is_anonymous_proxy)),
                                                #    'is_satellite_provider': bool(int(is_satellite_provider)),
                                    # logDebug(str(firstIP)+" "+str(geoip[firstIP]))
                                except Exception as ERR:
                                    print("Error at \""+LINE+"\" - "+str(ERR))                                    
                                if counter % 50000 == 0:
                                    # break
                                    log(f"\r> Lines read: {counter}",end="")
                        except Exception as ERR:
                            logError("Falied at country blocks look %s"%(str(ERR)))
                            continue
                log(f"\r- Lines read: {counter} done! {timer(elapsed())}")
            except Exception as ERR:
                logError("Failed country cidr readline %s"%(str(ERR)))
                return 1 
        # ##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        with elapsed_timer() as elapsed:
            try:
                for cidr,v in reservedNetworks.items():
                    CIDRInfo = CIDRDetail(cidr)
                    for key,value in v.items():
                        country_code = key
                        first_ip2int = CIDRInfo.first_ip2int
                        geoip[first_ip2int] = {'cidr':cidr,'country_code':country_code,
                                                'last_ip':CIDRInfo.last_ip2int}
                        if country_code == '14':
                            continue
                        logDebug(str(first_ip2int)+" "+str(geoip[first_ip2int]))
                log(f"- Added {len(reservedNetworks.keys())} private/reserved networks... done! {timer(elapsed())}")
            except Exception as ERR:
                logError("%s"%(str(ERR)))
                return 1
        ##────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        with elapsed_timer() as elapsed:
            try:
                dictCountryByCode = dict(sorted(dictCountryByCode.items(),key=lambda x:x[0], reverse=False))
                listLocation = [f"{key}:{val}" for key,val in dictCountryByCode.items()]
                log(f"- Locations list language {args.language} with {len(listLocation)} items... done! {timer(elapsed())}")
                logDebug(str(listLocation))
            except Exception as ERR:
                logError(f"Failed to create Locations list %s"%(str(ERR)))
                return 1
        with elapsed_timer() as elapsed:
            try:
                geoip = dict(sorted(geoip.items(),key=lambda x:int(x[0]), reverse=False))
                _listFirstIP = [int(key) for key in geoip.keys()]
                listFirstIP = [item for item in _listFirstIP]
                log(f"- First IP list with {len(listFirstIP)} networks... done! {timer(elapsed())}")
                logDebug(str(listFirstIP))
            except Exception as ERR:
                logError(f"Failed to create FirstIP list %s"%(str(ERR)))
                return 1
        with elapsed_timer() as elapsed:
            try:
                _listCIDR = [int(val['cidr'].split('/')[1]) for key,val in geoip.items()]
                listCIDR = [item for item in _listCIDR]
                log(f"- listCIDR list with {len(listCIDR)} networks... done! {timer(elapsed())}")
                logDebug(str(listCIDR))
            except Exception as ERR:
                logError(f"Failed to create listCIDR list %s"%(str(ERR)))
                return 1
        with elapsed_timer() as elapsed:
            try:
                _listCountryCode = [int(f"{list(dictCountryByCode.keys()).index(val['country_code'])}") for key,val in geoip.items()]
                listCountryCode = [item for item in _listCountryCode]
                log(f"- listCountryCode list with {len(listCountryCode)} networks... done! {timer(elapsed())}")
                logDebug(str(listCountryCode))
            except Exception as ERR:
                logError(f"Failed to create listCountryCode list %s"%(str(ERR)))
                return 1
        #────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
        _SOURCE_INFO = source_info
        mainList = list(split_list(listFirstIP,LIST_SLICE_SIZE))
        mainListCodes = list(split_list(listCountryCode,LIST_SLICE_SIZE))
        mainListNetLength = list(split_list(listCIDR,LIST_SLICE_SIZE))
        sliceInfo = {'num_keys':len(mainList),
                    'total_networks':len(listFirstIP),
                    'slice_size':LIST_SLICE_SIZE,
                    'length_last_list':len(mainList[-1]) }
        mainIndex = []
        for item in mainList:
            mainIndex.append(item[0])
        log(f"- Using an index with {len(mainIndex)} chunks for COUNTRY lookups...")
        geoipList = [mainIndex, mainList, mainListCodes, mainListNetLength]
        stringToHash = str(mainIndex)+":"+str(len(listFirstIP))
        hashMD5 = get_md5(stringToHash)
        with elapsed_timer() as elapsed:
            database = [__DAT_VERSION__,    # integer
                        listLocation,       # list      "country_code:country_name"
                        geoipList,          # geoipList = [mainIndex (4Kb), mainList (668Kb), mainListCodes (1004Kb), mainListNetLength (908Kb)]
                        hashMD5,            # hashmd5 = mainIndex + ":" + lenght of all records
                        str(sliceInfo),     # string (dict = 'num_keys','total_networks','slice_size''length_last_list')
                        _SOURCE_INFO]       # string 
            log(f"- Preparing database {GEOIP2FAST_DAT_FILENAME_GZ}... {timer(elapsed())}")
        with elapsed_timer() as elapsed_save_gzip:
            with gzip.GzipFile(filename=os.path.join(output_dir,GEOIP2FAST_DAT_FILENAME_GZ), mode='wb', compresslevel=9) as f:
                pickle.dump(database,f,pickle.HIGHEST_PROTOCOL)
            f.close()
        log(f"- Saved file {os.path.join(output_dir,GEOIP2FAST_DAT_FILENAME_GZ)} {timer(elapsed_save_gzip())}")

    log(cYellow(f">>> ALL DONE!!! {timer(elapsed_total())}"))
    
##################################################################################################################################
##################################################################################################################################

                             ##     ##    ###    #### ##    ##                 
                             ###   ###   ## ##    ##  ###   ##                 
                             #### ####  ##   ##   ##  ####  ##                 
                             ## ### ## ##     ##  ##  ## ## ##                 
                             ##     ## #########  ##  ##  ####                 
                             ##     ## ##     ##  ##  ##   ###                 
             ####### ####### ##     ## ##     ## #### ##    ## ####### ####### 
 
##################################################################################################################################
##################################################################################################################################
#defmain
if __name__ == "__main__":
    if _DEBUG == False:
        logDebug = _log_empty
    if '-v' not in sys.argv:
        logVerbose = _log_empty


    parser = ArgumentParser(formatter_class=class_argparse_formatter,
                               description=__doc__,
                               allow_abbrev=True,
                               epilog="",
                               add_help=False
                               )

    fileimport = parser.add_argument_group("Import options")
    fileimport.add_argument("--country-dir",dest='country_dir',action="store",metavar="<directory>",help="Provide the full path of the CSV files GeoLite2-Country-Blocks-IPv4.csv and GeoLite2-Country-Locations-XX.csv files. Only the path of directory. Mandatory.")
    fileimport.add_argument("--output-dir",dest='output_dir',action="store",default="",metavar="<directory>",help="Define the output directory to save the file geoip2fast.dat.gz. Any file with the same name will be renamed. Mandatory.")
    fileimport.add_argument("--language",dest='language',action="store",default="en",choices=AVAILABLE_LANGUAGES,help="Choose the language of locations that you want to use. Default: en.")
    fileimport.add_argument("--source-info",dest='sourceinfo',action="store",metavar="<text>",default="",help="Provide data source information to be written in the dat file. Default: "+DEFAULT_COUNTRY_SOURCE_INFO+"YYYYMMDD")
    optional = parser.add_argument_group("More options")
    optional.add_argument('-v',dest="verbose",action='store_true',default=False,help='0|Show useful messages for debugging.')
    optional.add_argument('-h','--help',action='help',help='0|Show a help message about the allowed commands.')
    optional.add_argument('--version','-version',action='version',help='0|Show the application version.',version="%s v%s"%(__appid__,__version__))
    # HIDDEN
    optional.add_argument('--debug',dest="debug",action='store_true',default=False,help=SUPPRESS)

    ##────── do the parse ───────────────────────────────────────────────────────────────────────────────────────────────────
    args = parser.parse_args()
    ##────── Se não houve subcomando, exiba o help ─────────────────────────────────────────────────────────────────────────

    if (args.country_dir != "") + (args.output_dir != "") != 2:
        parser.print_help()
        print("")
        sys.exit(0)
    
    with geoip2dat():
        if args.sourceinfo == "":
            args.sourceinfo = DEFAULT_COUNTRY_SOURCE_INFO+get_date()[:8]
        sys.exit(run(args.country_dir,args.output_dir,args.language,args.sourceinfo))
    