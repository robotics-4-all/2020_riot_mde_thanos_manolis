#!/usr/bin/env python

"""parser.py"""

# textX imports
from textx.export import metamodel_export, model_export, PlantUmlRenderer
from textx import metamodel_from_file

# PlantUML Imports
import model_2_plantuml

# Jinja imports
import codecs
import jinja2

from os.path import join, dirname
from pathlib import Path
import os
import sys
import pydot

currentdir = os.path.dirname(os.path.realpath(__file__))
parentdir = os.path.dirname(currentdir)
sys.path.append(parentdir)

fsloader = jinja2.FileSystemLoader(currentdir)
env = jinja2.Environment(loader=fsloader)


def main():
    # The 2 given arguments are the configuration files for device and connection model
    args = sys.argv[1:]
    connection_conf = args[0]

    """ Parse info from connections meta-model """

    # Get meta-model from language description
    connections_mm = metamodel_from_file('meta-models/connections.tx')

    # Export meta-model to PlantUML (.pu) and then png
    # metamodel_export(connections_mm, 'meta-models/dotexport/connections_mm.pu', renderer=PlantUmlRenderer())
    # os.system('plantuml -DPLANTUML_LIMIT_SIZE=8192 meta-models/dotexport/connections_mm.pu')

    # Construct connection model from a specific file
    connection_model = connections_mm.model_from_file(
        'meta-models/example_confs/' + connection_conf + '.con')

    # Export model to PlantUML (.pu) and then png
    model_2_plantuml.generate_plantuml_connections(connection_model, 'meta-models/dotexport/' + connection_conf + '.pu')
    os.system('plantuml -DPLANTUML_LIMIT_SIZE=8192 meta-models/dotexport/' + connection_conf + '.pu')

    """ Parse info from device meta-model """

    # Get meta-model from language description
    devices_mm = metamodel_from_file('meta-models/devices.tx')

    # Export meta-model to PlantUML (.pu) and then png
    # metamodel_export(devices_mm, 'meta-models/dotexport/devices_mm.pu', renderer=PlantUmlRenderer())
    # os.system('plantuml -DPLANTUML_LIMIT_SIZE=8192 meta-models/dotexport/devices_mm.pu')

    device_models = {}

    # Create a model for each device used (board/peripheral)
    for device in connection_model.includes:

        # Construct device model from a specific file
        device_models[device.val] = devices_mm.model_from_file(
            'meta-models/example_confs/' + device.val + '.hwd')

        # Export model to dot and png
        # model_export(device_model, 'meta-models/dotexport/' + board_conf + '.dot')
        # (graph,) = pydot.graph_from_dot_file(
        #     'meta-models/dotexport/' + board_conf + '.dot')
        # graph.write_png('meta-models/dotexport/' + board_conf + '.png')

    """ Produce source code from templates """

    # Load C template
    template1 = env.get_template(
        'templates/base.c.tmpl')

    # Load Makefile template
    template2 = env.get_template(
        'templates/Makefile.tmpl')
    
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
        peripheral_type_tmp[peripheral_name_tmp[i]] = device_models[peripheral_name_tmp[i]].type.val
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
    all_exist = True
    for peripheral in peripheral_name_tmp.values():
        if os.path.isfile('templates/' + peripheral + '.c.tmpl') == False:
            print("No template for peripheral " + peripheral + " found!")
            all_exist = False
    
    if all_exist == False:
        sys.exit("You need to create template(s) for the peripherals mentioned above ...")

    # C template
    rt = template1.render(address=address_tmp,
                            id=id_tmp,
                            port=mqtt_port,
                            peripheral_name=peripheral_name_tmp,
                            peripheral_type=peripheral_type_tmp,
                            args=args_tmp,
                            topic=topic_tmp,
                            frequency=frequency_tmp,
                            num_of_peripherals = num_of_peripherals_tmp)        
    ofh = codecs.open("codegen/" + connection_conf + ".c", "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()

    # Makefile template
    rt = template2.render(connection_conf=connection_conf,
                          module=module_tmp,
                          board_name=board_name_tmp,
                          wifi_ssid=wifi_ssid_tmp,
                          wifi_passwd=wifi_passwd_tmp)
    ofh = codecs.open("codegen/Makefile", "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()


if __name__ == '__main__':
    main()
