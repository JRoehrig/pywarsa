import os
import sys
import argparse
import subprocess
import ConfigParser
from cryptography.fernet import Fernet


def create_config(**kwargs):
    """

    :param kwargs:
        :key grp_dir:
        :key dem_dir:
        :key gpm_usr:
        :key gpm_pwd:
        :key earthdata_usr:
        :key earthdata_pwd:
    :return:
    """

    if 'WARSA_KEY' not in os.environ:
        warsa_key = create_warsa_key()
    else:
        warsa_key = os.environ['WARSA_KEY']

    grp_dir = kwargs.pop('grp', None)
    dem_dir = kwargs.pop('dem', None)
    gpm_usr = kwargs.pop('gpm_usr', None)
    gpm_pwd = kwargs.pop('gpm_pwd', None)
    earthdata_usr = kwargs.pop('earthdata_usr', None)
    earthdata_pwd = kwargs.pop('earthdata_pwd', None)

    config = ConfigParser.RawConfigParser()

    home = os.path.expanduser("~")

    # =========================================================================
    # Extract data from existing config file and use as default
    # =========================================================================
    filename = os.path.join(home, '.configs', '.warsa.cfg')
    if os.path.isfile(filename):
        config1 = read_config()
        if not grp_dir:
            grp_dir = config1.get('grp', 'dir')
        if not dem_dir:
            dem_dir = config1.get('dem', 'dir')
        if not gpm_usr and not gpm_pwd and config1.has_section('gpm'):
            gpm_usr = config1.get('gpm', 'usr')
            gpm_pwd = config1.get('gpm', 'pwd')
        if not earthdata_usr and not earthdata_pwd and config1.has_section('earthdata'):
            earthdata_usr = config1.get('earthdata', 'usr')
            earthdata_pwd = config1.get('earthdata', 'pwd')

    # =========================================================================
    # Encrypt user names and passwords
    # =========================================================================
    f = Fernet(warsa_key)
    if earthdata_usr and earthdata_pwd:
        earthdata_usr = f.encrypt(earthdata_usr)
        earthdata_pwd = f.encrypt(earthdata_pwd)
    if gpm_usr and gpm_pwd:
        gpm_usr = f.encrypt(gpm_usr)
        gpm_pwd = f.encrypt(gpm_pwd)

    # =========================================================================
    # Satellite precipitation products
    # =========================================================================
    config.add_section('grp')
    config.set('grp', 'dir', os.path.normpath(grp_dir))

    config.add_section('gpm')
    config.set('gpm', 'usr', gpm_usr)
    config.set('gpm', 'pwd', gpm_pwd)

    # =========================================================================
    # DEM
    # =========================================================================
    config.add_section('dem')
    config.set('dem', 'dir', os.path.normpath(dem_dir))
    config.set('dem', '1arcsec_usr', earthdata_usr)
    config.set('dem', '1arcsec_pwd', earthdata_pwd)

    with open(os.path.join(home, '.configs', '.warsa.cfg'), 'wb') as configfile:
        config.write(configfile)


def read_config():
    home = os.path.expanduser("~")
    config = ConfigParser.RawConfigParser()
    filename = os.path.join(home, '.configs', '.warsa.cfg')
    if not os.path.isfile(filename):
        create_config()
    config.read(filename)
    return config


def decrypt(usr, pwd):
    f = Fernet(os.environ['WARSA_KEY'])
    return f.decrypt(usr), f.decrypt(pwd)


def create_warsa_key():
    key = Fernet.generate_key()
    if sys == 'Windows':
        print subprocess.check_call("setx WARSA_KEY " + key)
    os.environ['WARSA_KEY'] = key
    return key


if __name__ == '__main__':
    """Usage example:
    config.py -grp G:/sarp -dem G:/dem -gpm_usr my_gpm_username -gpm_pwd my_gpm_password -earthdata_usr my_earthdata_username -earthdata_pwd my_earthdata_password
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-grp", type=str)
    parser.add_argument("-dem", type=str)
    parser.add_argument("-gpm_usr", type=str)
    parser.add_argument("-gpm_pwd", type=str)
    parser.add_argument("-earthdata_usr", type=str)
    parser.add_argument("-earthdata_pwd", type=str)
    args = parser.parse_args(sys.argv[1:])
    create_config(**vars(args))
