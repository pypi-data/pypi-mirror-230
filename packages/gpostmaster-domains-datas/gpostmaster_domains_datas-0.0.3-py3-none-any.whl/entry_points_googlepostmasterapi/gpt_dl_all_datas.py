#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2021 Mindbaz
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Downloads data for all domains from GPT
"""

import os;
import sys;
import argparse;
from datetime import datetime, timedelta;
from pprint import pprint;

sys.path.insert ( 0, os.path.dirname ( os.path.dirname ( os.path.abspath ( __file__ ) ) ) );
from googlepostmasterapi.gpt import GPostmaster;
from googlepostmasterapi import __version__;

def run ():
    parser = argparse.ArgumentParser ( prog = 'gpt_dl_all_datas' );
    
    ## All arguments
    parser.add_argument ( '--token', type = str, nargs = '?', help = 'GPT token' );
    parser.add_argument ( '--pool-size', type = int, nargs = '?', help = 'Number of parallel calls to GPT. Default : 2', default = 2 );
    parser.add_argument ( '--date', type = str, nargs = '?', help = 'Date to fetch datas from GPT. Format : YYYY-MM-DD. Default : D-2' );
    parser.add_argument ( '--verbose', action = 'store_true', help = 'Verbose mode' );
    parser.add_argument ( '--version', action = 'store_true', help = 'Display version' );
    args = parser.parse_args ();
    
    ## Display version
    
    if ( args.version == True ):
        print ( __version__ );
        exit ( 0 );
    
    ## Valid required argument
    
    if ( args.token == None or os.path.isfile ( args.token ) == False ):
        print ( 'Missing --token file. -h to show help' );
        exit ( 2 );
    
    if ( args.pool_size < 1 ):
        print ( 'Wrong number to --pool-size, must be positive' );
        exit ( 2 );
    elif ( args.pool_size > 8 ):
        args.pool_size = 8;
    
    if ( args.date != None ):
        try:
            args.datetime = datetime.strptime ( args.date, '%Y-%m-%d' );
            args.date = args.datetime.strftime ( '%Y%m%d' );
        except Exception as e:
            print ( 'Missing --date. -h to show help' );
            exit ( 2 );
    
    if ( args.date == None ):
        args.date = ( datetime.now () - timedelta ( 2 ) ).strftime ( '%Y%m%d' );
        args.datetime = datetime.strptime ( args.date, '%Y%m%d' );
    
    #
    # Print args to console
    #

    if ( args.verbose == True ):
        print ( 'v v v v v v v v v v v v v v v v v v v v v' );
        print ( 'Arguments list : ' );
        for arg in sorted ( vars ( args ) ):
            print ( '{} : {}'.format ( arg.rjust ( 30 ), getattr ( args, arg ) ) );
        print ( '^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^ ^' );
    
    ## Begin
    
    #
    # Init tool
    #
    
    g = GPostmaster (
        token = args.token,
        pool_size = args.pool_size,
        verbose = args.verbose,
    );
    
    """Exec exit code"""
    exit_code = 0;
    """Error message"""
    error_msg = '';
    
    try:
        """Download all GPT datas"""
        ret = g.get_all_domains_infos (
            input_date = args.date
        );
        
        print ( 'Datas : ' );
        print ( ret );
    except Exception as e:
        exit_code = 1;
        error_msg = str ( e );
    
    if ( exit_code != 0 ):
        print ( 'Exit code : {}'.format ( str ( exit_code ) ) );
        print ( 'Error message : {}'.format ( error_msg ) );
    
    exit ( exit_code );

if __name__ == '__main__':
    run ();
