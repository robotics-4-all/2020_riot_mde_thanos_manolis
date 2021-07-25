#!/usr/bin/env python

"""
model_2_plantuml.py
Script that generates PlantUML text from textX models
"""

# PlantUML generation for connection model
def generate_plantuml_connections(model, filename):

    f = open(filename, "w")

    f.write('@startuml\nset namespaceSeparator .\n\n\n')

    f.write('class connections.SYSTEM  {\n}\n\n\n')

    for i in range(len(model.includes)):
        tmp = 'class connections.INCLUDE_' + str(i) + \
            '  {\n  val: str=\'' + model.includes[i].val + \
            '\'\n}\n\n\n'
        f.write(tmp)

    for i in range(len(model.connections)):
        tmp = 'class connections.CONNECTION_' + str(i) + \
            '  {\n  name: ' + model.connections[i].name + \
            '\n}\n\n\n'
        f.write(tmp)

        tmp = 'class connections.BOARD_' + str(i) + \
            '  {\n  device: str=\'' + model.connections[i].board.device + '\'\n' + \
            '  number: int=' + str(model.connections[i].board.number) + '\n}\n\n\n'
        f.write(tmp)

        tmp = 'class connections.PERIPHERAL_' + str(i) + \
            '  {\n  device: str=\'' + model.connections[i].peripheral.device + '\'\n' + \
            '  number: int=' + str(model.connections[i].peripheral.number) + '\n}\n\n\n'
        f.write(tmp)

        for j in range(len(model.connections[i].power_conns)):
            tmp = 'class connections.POWER_CONNECTION_' + str(i) + '_' + str(j) + \
                '  {\n  board_power: str=\'' + model.connections[i].power_conns[j].board_power + '\'\n' + \
                '  peripheral_power: str=\'' + str(model.connections[i].power_conns[j].peripheral_power) + \
                '\'\n}\n\n\n'
            f.write(tmp)
        
        for j in range(len(model.connections[i].hw_conns)):

            if model.connections[i].hw_conns[j].type == 'gpio':
                tmp = 'class connections.GPIO_' + str(i) + '_' + str(j) + \
                    '  {\n  type: str=\'' + model.connections[i].hw_conns[j].type + '\'\n' + \
                    '  board_int: str=\'' + model.connections[i].hw_conns[j].board_int + '\'\n' + \
                    '  peripheral_int: str=\'' + str(model.connections[i].hw_conns[j].peripheral_int) + \
                    '\'\n}\n\n\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'i2c':
                tmp = 'class connections.I2C_' + str(i) + \
                    '  {\n  type: str=\'' + model.connections[i].hw_conns[j].type + '\'\n' + \
                    '  board_int: list=[\'' + \
                        model.connections[i].hw_conns[j].board_int[0] + '\',\'' + \
                        model.connections[i].hw_conns[j].board_int[1]+ '\']\n' + \
                    '  peripheral_int: list=[\'' + \
                        model.connections[i].hw_conns[j].peripheral_int[0] + '\',\'' + \
                        model.connections[i].hw_conns[j].peripheral_int[1]+ '\']\n' + \
                    '  slave_addr: int=' + str(model.connections[i].hw_conns[j].slave_addr) + \
                    '\n}\n\n\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'pwm':
                tmp = 'class connections.PWM_' + str(i) + '_' + str(j) + \
                    '  {\n  type: str=\'' + model.connections[i].hw_conns[j].type + '\'\n' + \
                    '  board_int: str=\'' + model.connections[i].hw_conns[j].board_int + '\'\n' + \
                    '  peripheral_int: str=\'' + str(model.connections[i].hw_conns[j].peripheral_int) + \
                    '\'\n}\n\n\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'spi':
                tmp = 'class connections.SPI_' + str(i) + '_' + str(j) + \
                    '  {\n  type: str=\'' + model.connections[i].hw_conns[j].type + '\'\n' + \
                    '  board_int: str=\'' + model.connections[i].hw_conns[j].board_int + '\'\n' + \
                    '  peripheral_int: str=\'' + str(model.connections[i].hw_conns[j].peripheral_int) + \
                    '\'\n}\n\n\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'uart':
                tmp = 'class connections.UART_' + str(i) + '_' + str(j) + \
                    '  {\n  type: str=\'' + model.connections[i].hw_conns[j].type + '\'\n' + \
                    '  board_int: str=\'' + model.connections[i].hw_conns[j].board_int + '\'\n' + \
                    '  peripheral_int: str=\'' + str(model.connections[i].hw_conns[j].peripheral_int) + '\'\n' + \
                    '  baudrate: int=' + str(model.connections[i].hw_conns[j].baudrate) + '\n}\n\n\n'
                f.write(tmp)

        tmp = 'class connections.COM_ENDPOINT_' + str(i) + \
            '  {\n  topic: str=\'' + model.connections[i].com_endpoint.topic[:-1] + '\'\n' + \
            '  addr: str=\'' + model.connections[i].com_endpoint.addr + '\'\n' + \
            '  port: int=' + str(model.connections[i].com_endpoint.port) + '\n}\n\n\n'
        f.write(tmp)

        msg_entries = ''
        for j in range(len(model.connections[i].com_endpoint.msg.msg_entries)):
            msg_entries += '\'' + model.connections[i].com_endpoint.msg.msg_entries[j] + '\','
        msg_entries = msg_entries[:-1]

        tmp = 'class connections.MSG_ENTRIES_' + str(i) + \
            '  {\n  msg_entries: list=[' + msg_entries + ']' + '\n}\n\n\n'
        f.write(tmp)

        if( hasattr(model.connections[i].com_endpoint.freq, 'val') ):
            tmp = 'class connections.FREQUENCY_' + str(i) + \
                '  {\n  val: int=' + str(model.connections[i].com_endpoint.freq.val) + '\n' + \
                '  unit: str=\'' + model.connections[i].com_endpoint.freq.unit + \
                '\'\n}\n\n\n'
            f.write(tmp)

    # Relations 

    for i in range(len(model.includes)):
        tmp = 'connections.SYSTEM *-- "includes:' + str(i) + \
            '" connections.INCLUDE_' + str(i) + '\n'
        f.write(tmp)
    
    for i in range(len(model.connections)):
        tmp = 'connections.SYSTEM *-- "connections:' + str(i) + \
            '" connections.CONNECTION_' + str(i) + '\n'
        f.write(tmp)

        tmp = 'connections.CONNECTION_' + str(i) + \
            ' *-- "board" connections.BOARD_' + str(i) + '\n'
        f.write(tmp)

        tmp = 'connections.CONNECTION_' + str(i) + \
            ' *-- "peripheral" connections.PERIPHERAL_' + str(i) + '\n'
        f.write(tmp)

        for j in range(len(model.connections[i].power_conns)):
            tmp = 'connections.CONNECTION_' + str(i) + ' *-- "power_conns:' + str(j) + \
                '" connections.POWER_CONNECTION_' + str(i) + '_' + str(j) + '\n'
            f.write(tmp)

        for j in range(len(model.connections[i].hw_conns)):

            if model.connections[i].hw_conns[j].type == 'gpio':
                tmp = 'connections.CONNECTION_' + str(i) + ' *-- "hw_conns:' + str(j) + \
                    '" connections.GPIO_' + str(i) + '_' + str(j) + '\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'i2c':
                tmp = 'connections.CONNECTION_' + str(i) + ' *-- "hw_conns:' + str(j) + \
                    '" connections.I2C_' + str(i) + '\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'pwm':
                tmp = 'connections.CONNECTION_' + str(i) + ' *-- "hw_conns:' + str(j) + \
                    '" connections.PWM_' + str(i) + '_' + str(j) + '\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'spi':
                tmp = 'connections.CONNECTION_' + str(i) + ' *-- "hw_conns:' + str(j) + \
                    '" connections.SPI_' + str(i) + '_' + str(j) + '\n'
                f.write(tmp)
            elif model.connections[i].hw_conns[j].type == 'uart':
                tmp = 'connections.CONNECTION_' + str(i) + ' *-- "hw_conns:' + str(j) + \
                    '" connections.UART_' + str(i) + '_' + str(j) + '\n'
                f.write(tmp)

        tmp = 'connections.CONNECTION_' + str(i) + \
            ' *-- "com_endpoint" connections.COM_ENDPOINT_' + str(i) + '\n'
        f.write(tmp)

        tmp = 'connections.COM_ENDPOINT_' + str(i) + \
            ' *-- "msg" connections.MSG_ENTRIES_' + str(i) + '\n'
        f.write(tmp)

        if( hasattr(model.connections[i].com_endpoint.freq, 'val') ):
            tmp = 'connections.COM_ENDPOINT_' + str(i) + \
                ' *-- "freq" connections.FREQUENCY_' + str(i) + '\n'
            f.write(tmp)

    f.write('\n@enduml')

    f.close()