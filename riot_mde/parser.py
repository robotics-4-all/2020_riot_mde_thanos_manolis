#!/usr/bin/env python

"""parser.py"""

# textX imports
from textx.export import metamodel_export, model_export, PlantUmlRenderer
from textx import metamodel_from_file

# PlantUML Imports
from riot_mde import model_2_plantuml
from riot_mde import hw_conns_plantuml

# Jinja imports
import codecs
import jinja2

from os.path import join, dirname
from pathlib import Path
import os
import sys
import argparse
import pydot
import shutil

from riot_mde.definitions import *

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

fsloader = jinja2.FileSystemLoader(TEMPLATES)
env = jinja2.Environment(loader=fsloader)

def parse_args() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()

    # Add arguments
    parser.add_argument("--connections",
                        help="Filename of a connection specification.")

    return parser.parse_args()

def main():
    cl_args = parse_args()
    connection_conf_filename = cl_args.connections
    if connection_conf_filename.endswith(".con"): 
        connection_conf = connection_conf_filename.removesuffix('.con')
    else:
        sys.exit("Connection file should end with '.con'")

    # Create a list of supported boards
    supported_boards = []
    directory = os.fsencode(SUPPORTED_DEVICES + 'boards')        
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".hwd"): 
            supported_boards.append(filename[:-4])
            continue
        else:
            continue

    # Create a list of supported peripherals
    supported_peripherals = []
    directory = os.fsencode(SUPPORTED_DEVICES + 'peripherals')        
    for file in os.listdir(directory):
        filename = os.fsdecode(file)
        if filename.endswith(".hwd"): 
            supported_peripherals.append(filename[:-4])
            continue
        else:
            continue


    """ Parse info from connections meta-model """

    # Get meta-model from language description
    connections_mm = metamodel_from_file(META_MODELS + '/connections.tx')

    # Export meta-model to PlantUML (.pu) and then png
    # metamodel_export(connections_mm, IMG_EXPORT + 'connections_mm.pu', renderer=PlantUmlRenderer())
    # os.system('plantuml -DPLANTUML_LIMIT_SIZE=8192 ' + IMG_EXPORT + 'connections_mm.pu')

    # Construct connection model from a specific file
    connection_model = connections_mm.model_from_file(
        'test_connections/' + connection_conf_filename)

    # Export model to PlantUML (.pu) and then png
    hw_conns_plantuml.generate_plantuml_connections(connection_model, IMG_EXPORT + connection_conf + 'a.pu')
    os.system('plantuml -DPLANTUML_LIMIT_SIZE=8192 ' + IMG_EXPORT + connection_conf + 'a.pu')

    model_2_plantuml.generate_plantuml_connections(connection_model, IMG_EXPORT + connection_conf + 'b.pu')
    os.system('plantuml -DPLANTUML_LIMIT_SIZE=8192 ' + IMG_EXPORT + connection_conf + 'b.pu')

    """ Parse info from device meta-model """

    # Get meta-model from language description
    devices_mm = metamodel_from_file(META_MODELS + '/devices.tx')

    # Export meta-model to PlantUML (.pu) and then png
    # metamodel_export(devices_mm, IMG_EXPORT + 'devices_mm.pu', renderer=PlantUmlRenderer())
    # os.system('plantuml -DPLANTUML_LIMIT_SIZE=8192 ' + IMG_EXPORT + 'devices_mm.pu')

    # Check if a hardware configuration file exists for each given board/peripheral
    all_hwd_exist = True
    for device in connection_model.includes:
        # Construct device model from a specific file
        if device.name in supported_boards:
            continue
        elif device.name in supported_peripherals:
            continue
        else:
            print("No configuration file for device " + device.name + " found!")
            all_hwd_exist = False
    
    if all_hwd_exist == False:
        sys.exit("You need to create configuration (.hwd) file(s) for the devices(s) mentioned above ...")

    device_models = {}

    # Create a model for each device used (board/peripheral)
    for device in connection_model.includes:

        # Construct device model from a specific file
        if device.name in supported_boards:
            device_models[device.name] = devices_mm.model_from_file(
                SUPPORTED_DEVICES + '/boards/' + device.name + '.hwd')
        elif device.name in supported_peripherals:
            device_models[device.name] = devices_mm.model_from_file(
                SUPPORTED_DEVICES + '/peripherals/' + device.name + '.hwd')

        # Export model to dot and png
        # model_export(device_models[device.name], IMG_EXPORT + device.name + '.dot')
        # (graph,) = pydot.graph_from_dot_file(
        #     IMG_EXPORT + device.name + '.dot')
        # graph.write_png(IMG_EXPORT + device.name + '.png')

    """ Produce source code from templates """

    # Load C template
    template1 = env.get_template(
        'base.c.tmpl')

    # Load Makefile template
    template2 = env.get_template(
        'Makefile.tmpl')
    
    peripheral_name_tmp = {}
    peripheral_type_tmp = {}
    id_tmp = {}
    frequency_tmp = {}
    module_tmp = {}
    args_tmp = {}
    topic_tmp = {}
    num_of_peripherals_tmp = len(connection_model.connections)
    
    # Name of board
    board_name_tmp = connection_model.connections[0].board.device
    if board_name_tmp == 'esp32_wroom_32':
        board_name_tmp = 'esp32-wroom-32'
    elif board_name_tmp == 'wemos_d1_mini':
        board_name_tmp = 'esp8266-esp-12x'

    # Wifi credentials
    wifi_ssid_tmp = connection_model.connections[0].com_endpoint.wifi_ssid[:-1]
    wifi_passwd_tmp = connection_model.connections[0].com_endpoint.wifi_passwd[:-1]

    for i in range(len(connection_model.connections)):

        # Parse info from the created models
        address_tmp = connection_model.connections[i].com_endpoint.addr
        id_tmp[i] = i + 1
        mqtt_port = connection_model.connections[i].com_endpoint.port
        peripheral_name_tmp[i] = connection_model.connections[i].peripheral.device
        peripheral_type_tmp[peripheral_name_tmp[i]] = device_models[peripheral_name_tmp[i]].type
        module_tmp[i] = connection_model.connections[i].peripheral.device
        topic_tmp[i] = connection_model.connections[i].com_endpoint.topic[:-1]

        # Publishing frequency (always convert to Hz) 
        # If not given, default value is 1Hz
        if( hasattr(connection_model.connections[i].com_endpoint.freq, 'val') ):
            frequency_tmp[i] = connection_model.connections[i].com_endpoint.freq.val
            frequency_unit = connection_model.connections[i].com_endpoint.freq.unit
            if (frequency_unit == "khz"):
                frequency_tmp[i] = (10**3) * frequency_tmp[i]
            elif (frequency_unit == "mhz"):
                frequency_tmp[i] = (10**6) * frequency_tmp[i]
            elif (frequency_unit == "ghz"):
                frequency_tmp[i] = (10**9) * frequency_tmp[i]
        else:
            frequency_tmp[i] = 1

        # Hardware connection args
        args_tmp[i] = {}

        if (connection_model.connections[i].hw_conns[0].type == 'gpio'):
            for hw_conn in connection_model.connections[i].hw_conns:
                args_tmp[i][hw_conn.peripheral_int] = (hw_conn.board_int).split("_",1)[1]
        elif (connection_model.connections[i].hw_conns[0].type == 'i2c'):
            args_tmp[i]["sda"] = (connection_model.connections[i].hw_conns[0].board_int[0]).split("_",1)[1]
            args_tmp[i]["scl"] = (connection_model.connections[i].hw_conns[0].board_int[1]).split("_",1)[1]
            args_tmp[i]["slave_address"] = connection_model.connections[i].hw_conns[0].slave_addr
            if(connection_model.connections[i].peripheral.device == 'bme680'):
                module_tmp[i] = module_tmp[i] + '_i2c'

    # Check if a template exists for each given peripheral
    all_tmpl_exist = True
    for peripheral in peripheral_name_tmp.values():
        file = TEMPLATES + peripheral + '.c.tmpl'
        if os.path.isfile(file) == False:
            print("No template for peripheral " + peripheral + " found!")
            all_tmpl_exist = False
            if peripheral_type_tmp[peripheral] == 'sensor':
                shutil.copyfile(TEMPLATES + 'unsupported_sensor.txt', file)
            elif peripheral_type_tmp[peripheral] == 'actuator':
                shutil.copyfile(TEMPLATES + 'unsupported_actuator.txt', file)
    
    if all_tmpl_exist == False:
        sys.exit('\nA template for each one of the peripheral(s) mentioned above' + \
                 '\nwas created. You need to fill it with appropriate code ...')

    # C template
    rt = template1.render(address=address_tmp,
                            id=id_tmp,
                            port=mqtt_port,
                            peripheral_name=peripheral_name_tmp,
                            peripheral_type=peripheral_type_tmp,
                            args=args_tmp,
                            topic=topic_tmp,
                            frequency=frequency_tmp,
                            num_of_peripherals = num_of_peripherals_tmp,
                            templates = TEMPLATES)        
    ofh = codecs.open(CODEGEN + connection_conf + ".c", "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()

    # Makefile template
    rt = template2.render(connection_conf=connection_conf,
                          module=module_tmp,
                          board_name=board_name_tmp,
                          wifi_ssid=wifi_ssid_tmp,
                          wifi_passwd=wifi_passwd_tmp)
    ofh = codecs.open(CODEGEN + 'Makefile', "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()


if __name__ == '__main__':
    main()
