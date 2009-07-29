#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""This loads the user's _config.py file and provides a standardized interface
into it."""

__author__ = "Ryan McGuire (ryan@enigmacurry.com)"
__date__   = "Tue Jul 28 20:40:29 2009"

import os

__config_file_path = None
__config_locals = {}
__config_loaded = False

class UnknownConfigSectionException(Exception):
    pass
class ConfigNotFoundException(Exception):
    pass

def __load_config():
    execfile("_config.py", globals(), __config_locals)

def init(config_file_path):
    if not os.path.isfile(config_file_path):
        raise ConfigNotFoundException
    __config_file_path = config_file_path

def has_section(section_name):
    try:
        __get_section(section_name)
        return True
    except UnknownConfigSectionException:
        return False
    
def __get_section(section_name):
    if not __config_loaded:
        __load_config()
    #Don't care whether or not section names use dashes or underscores:
    section_name = section_name.replace("-","_")
    try:
        section = __config_locals["{0}_config".format(section_name)]
    except KeyError:
        raise UnknownConfigSectionException, "Unknown config section : {0}".format(section_name)
    return section

def get(section_name, key):
    """Get a specific value from a specific section of the config"""
    section = __get_section(section_name)
    return section[key]

def do_pre_build():
    try:
        __config_locals['pre_build']()
    except KeyError:
        pass

def do_post_build():
    try:
        __config_locals['post_build']()
    except KeyError:
        pass
    
