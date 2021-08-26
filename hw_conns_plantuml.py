#!/usr/bin/env python

"""
model_2_plantuml.py
Script that generates PlantUML text from textX models
"""

# PlantUML generation for connection model
def generate_plantuml_connections(model, filename):

    f = open(filename, "w")

    tmp = '@startuml\n' + \
        '\nskinparam componentStyle rectangle' + \
        '\nskinparam linetype ortho' + \
        '\nskinparam NoteFontSize 15' + \
        '\nskinparam NoteFontStyle italics' + \
        '\nskinparam RectangleFontSize 16\n' + \
        '\n!define T2 \\t\\t' + \
        '\n!define T5 \\t\\t\\t\\t\\t' + \
        '\n!define NL2 \\n\\n' + \
        '\n!define NL4 \\n\\n\\n\\n\n\n'
    f.write(tmp)    

    tmp = 'component [NL4 T5 **' + str(model.connections[0].board.device) + \
        '** T5 NL4] as ' + str(model.connections[0].board.device) + ' #FFF9C2\n'
    f.write(tmp)

    for i in range(len(model.connections)):
        tmp = 'component [' + (i%4 < 2)*'NL4 T2' + (i%4 >= 2)*'NL2 T5' + \
            ' **' + str(model.connections[i].peripheral.device) + \
            '** ' +  (i%4 < 2)*'T2 NL4' + (i%4 >= 2)*'T5 NL2' + \
            '] as ' + str(model.connections[i].peripheral.device) + \
            ' #CAE2C8\n'
        f.write(tmp)
    f.write('\n')

    note_directions = ['top', 'bottom', 'right', 'left']
    for i in range(len(model.connections)):
        tmp = 'note ' + note_directions[i%4] + ' of ' + \
            str(model.connections[i].peripheral.device) + \
            ' : topic - "' + str(model.connections[i].com_endpoint.topic[:-1]) + '"\n'
        f.write(tmp)
    f.write('\n')

    pin_directions = ['le', 'ri', 'up', 'down']
    for i in range(len(model.connections)):

        for j in range(len(model.connections[i].hw_conns)):
            if model.connections[i].hw_conns[j].type == 'gpio':
                tmp = str(model.connections[i].board.device) + \
                    ' "**' + str(model.connections[i].hw_conns[j].peripheral_int) + \
                    '**" #--' + str(pin_directions[i]) + '--# "**' + \
                    str(model.connections[i].hw_conns[j].board_int) + \
                    '**" ' + str(model.connections[i].peripheral.device) + \
                    (i%4 < 2) * ' : \\t\\t\\t\\t' + '\n'
            elif model.connections[i].hw_conns[j].type == 'i2c':
                tmp = ''
                for k in range(2):
                    tmp = tmp + str(model.connections[i].board.device) + \
                        ' "**' + str(model.connections[i].hw_conns[j].peripheral_int[k]) + \
                        '**" #--' + str(pin_directions[i]) + '--# "**' + \
                        str(model.connections[i].hw_conns[j].board_int[k]) + \
                        '**" ' + str(model.connections[i].peripheral.device) + \
                        (i%4 < 2) * ' : \\t\\t\\t\\t' + '\n'
            f.write(tmp)
        
        for j in range(len(model.connections[i].power_conns)):
            tmp = str(model.connections[i].board.device) + \
                ' "**' + str(model.connections[i].power_conns[j].peripheral_power) + \
                '**" #--' + str(pin_directions[i]) + '--# "**' + \
                str(model.connections[i].power_conns[j].board_power) + \
                '**" ' + str(model.connections[i].peripheral.device) + \
                (i%4 < 2) * ' : \\t\\t\\t\\t' + '\n'
            f.write(tmp)

        f.write('\n')


    f.write('\nhide @unlinked\n@enduml')

    f.close()