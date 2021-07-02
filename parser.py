#!/usr/bin/env python

"""parser.py"""

# textX imports
from textx.export import metamodel_export, model_export
from textx import metamodel_from_file

# Jinja imports
import codecs
import jinja2

from os.path import join, dirname
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
    board_conf = args[0]
    connection_conf = args[1]

    """ Parse info from device meta-model """

    # Get meta-model from language description
    devices_mm = metamodel_from_file('meta-models/devices.tx')

    # Export meta-model to dot and png
    metamodel_export(devices_mm, 'meta-models/dotexport/devices_mm.dot')
    (graph,) = pydot.graph_from_dot_file(
        'meta-models/dotexport/devices_mm.dot')
    graph.write_png('meta-models/dotexport/devices_mm.png')

    # Construct device model from a specific file
    device_model = devices_mm.model_from_file(
        'meta-models/example_confs/' + board_conf + '.hwd')

    # Export model to dot and png
    model_export(device_model, 'meta-models/dotexport/' + board_conf + '.dot')
    (graph,) = pydot.graph_from_dot_file(
        'meta-models/dotexport/' + board_conf + '.dot')
    graph.write_png('meta-models/dotexport/' + board_conf + '.png')

    """ Parse info from connections meta-model """

    # Get meta-model from language description
    connections_mm = metamodel_from_file('meta-models/connections.tx')

    # Export meta-model to dot and png
    metamodel_export(connections_mm, 'meta-models/dotexport/connections_mm.dot')
    (graph,) = pydot.graph_from_dot_file(
        'meta-models/dotexport/connections_mm.dot')
    graph.write_png('meta-models/dotexport/connections_mm.png')

    # Construct connection model from a specific file
    connection_model = connections_mm.model_from_file(
        'meta-models/example_confs/' + connection_conf + '.con')

    # Export model to dot and png
    model_export(connection_model, 'meta-models/dotexport/' + connection_conf + '.dot')
    (graph,) = pydot.graph_from_dot_file(
        'meta-models/dotexport/' + connection_conf + '.dot')
    graph.write_png('meta-models/dotexport/' + connection_conf + '.png')

    print(connection_model.connections[0].board.device)
    print(connection_model.connections[0].peripheral.device)

    """ Produce source code from templates """

    # Load C template
    template1 = env.get_template(
        'templates/base.c.tmpl')

    # Load Makefile template
    template2 = env.get_template(
        'templates/Makefile.tmpl')
    
    address_tmp = connection_model.connections[0].com_endpoint.addr
    id_tmp = 1
    num_of_msgs_tmp = 10
    mqtt_port = connection_model.connections[0].com_endpoint.port
    system_name = connection_model.connections[0].name
    peripheral_name_tmp = connection_model.connections[0].peripheral.device

    # Hardware connection args
    args_tmp = {}

    for hw_conn in connection_model.connections:
        if (connection_model.connections[0].hw_conns[0].type == 'gpio'):
            args_tmp["echo_pin"] = (connection_model.connections[0].hw_conns[0].board_int).split("_",1)[1]
            args_tmp["trigger_pin"] = (connection_model.connections[0].hw_conns[1].board_int).split("_",1)[1]
        elif (connection_model.connections[0].hw_conns[0].type == 'i2c'):
            args_tmp["slave_address"] = '0x76'
            peripheral_name_tmp = peripheral_name_tmp + '_i2c'

    # C template
    rt = template1.render(address=address_tmp,
                          id=id_tmp,
                          num_of_msgs=num_of_msgs_tmp,
                          port=mqtt_port,
                          peripheral_name=peripheral_name_tmp,
                          args=args_tmp)
    ofh = codecs.open("codegen/output_node.c", "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()

    # Makefile template
    rt = template2.render(app_name=system_name,
                          module=peripheral_name_tmp)
    ofh = codecs.open("codegen/Makefile", "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()


if __name__ == '__main__':
    main()
