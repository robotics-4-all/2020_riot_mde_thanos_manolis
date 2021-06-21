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

    # Load C template
    template1 = env.get_template(
        'templates/node.c.tmpl')
    
    # Load C header template
    template2 = env.get_template(
        'templates/mqtt_funcs.h.tmpl')

    # Load Makefile template
    template3 = env.get_template(
        'templates/Makefile.tmpl')

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
        'meta-models/example_confs/esp32_wroom_32.hwd')

    # Export model to dot and png
    model_export(device_model, 'meta-models/dotexport/esp32_wroom_32.dot')
    (graph,) = pydot.graph_from_dot_file(
        'meta-models/dotexport/esp32_wroom_32.dot')
    graph.write_png('meta-models/dotexport/esp32_wroom_32.png')

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
        'meta-models/example_confs/sonar_esp32.con')

    # Export model to dot and png
    model_export(connection_model, 'meta-models/dotexport/sonar_esp32.dot')
    (graph,) = pydot.graph_from_dot_file(
        'meta-models/dotexport/sonar_esp32.dot')
    graph.write_png('meta-models/dotexport/sonar_esp32.png')

    print(connection_model.connections[0].board.device)
    print(connection_model.connections[0].peripheral.device)

    """ Produce source code from templates """

    mqtt_port = connection_model.connections[0].com_endpoint.port
    echo_pin_tmp = (connection_model.connections[0].hw_conns[0].board_int).split("_",1)[1]
    trigger_pin_tmp = (connection_model.connections[0].hw_conns[1].board_int).split("_",1)[1]
    system_name = connection_model.connections[0].name
    peripheral_name_tmp = connection_model.connections[0].peripheral.device
    module_tmp = connection_model.includes[0].val

    # C template
    rt = template1.render(port=mqtt_port,
                         trigger_port=1,
                         trigger_pin=trigger_pin_tmp,
                         echo_port=1,
                         echo_pin=echo_pin_tmp,
                         perihperal_name=peripheral_name_tmp)
    ofh = codecs.open("codegen/src/output_node.c", "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()

    # C header template
    rt = template2.render(port=mqtt_port)
    ofh = codecs.open("codegen/inc/mqtt_funcs.h", "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()

    # Makefile template
    rt = template3.render(app_name=system_name,
                          module=peripheral_name_tmp)
    ofh = codecs.open("codegen/Makefile", "w", encoding="utf-8")
    ofh.write(rt)
    ofh.close()


if __name__ == '__main__':
    main()
