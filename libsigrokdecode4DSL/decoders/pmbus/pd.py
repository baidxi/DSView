##
## This file is part of the libsigrokdecode project.
##
## Copyright (C) 2023 Your Name <your.email@example.com>
## Copyright (C) 2022 DreamSourceLab <support@dreamsourcelab.com>
##
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, see <http://www.gnu.org/licenses/>.
##

import sigrokdecode as srd

class Decoder(srd.Decoder):
    api_version = 3
    id = 'pmbus'
    name = 'PMBus'
    longname = 'Power Management Bus'
    desc = 'Power Management Bus protocol.'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = ['smbus']
    tags = ['Embedded/industrial']

    channels = (
        {'id': 'scl', 'name': 'SCL', 'desc': 'Serial Clock Line'},
        {'id': 'sda', 'name': 'SDA', 'desc': 'Serial Data Line'},
    )

    options = (
        {'id': 'show_bits', 'desc': 'Show bits', 'default': 'yes',
            'values': ('yes', 'no')},
    )

    annotations = (
        ('start', 'Start'),
        ('stop', 'Stop'),
        ('bit', 'Bit'),
        ('ack', 'ACK'),
        ('nack', 'NACK'),
        ('addr-read', 'Addr Read'),
        ('addr-write', 'Addr Write'),
        ('reg', 'Register'),
        ('data-read', 'Data Read'),
        ('data-write', 'Data Write'),
        ('transaction', 'Transaction'),
    )

    annotation_rows = (
        ('bus', 'Bus', (10,)),
        ('signals', 'Signals', (0, 1, 3, 4, 5, 6, 7, 8, 9)),
        ('bits', 'Bits', (2,)),
    )

    pmbus_commands = {
        0x00: ('PAGE', None),
        0x01: ('OPERATION', None),
        0x02: ('ON_OFF_CONFIG', None),
        0x03: ('CLEAR_FAULTS', None),
        0x10: ('WRITE_PROTECT', None),
        0x19: ('CAPABILITY', None),
        0x20: ('VOUT_MODE', None),
        0x21: ('VOUT_COMMAND', 'linear'),
        0x22: ('VOUT_TRIM', 'linear'),
        0x23: ('VOUT_CAL_OFFSET', 'linear'),
        0x24: ('VOUT_MAX', 'linear'),
        0x25: ('VOUT_MARGIN_HIGH', 'linear'),
        0x26: ('VOUT_MARGIN_LOW', 'linear'),
        0x27: ('VOUT_TRANSITION_RATE', 'linear'),
        0x29: ('VOUT_SCALE_LOOP', 'linear'),
        0x33: ('FREQUENCY_SWITCH', 'linear'),
        0x35: ('VIN_ON', 'linear'),
        0x36: ('VIN_OFF', 'linear'),
        0x3A: ('IOUT_CAL_GAIN', 'linear'),
        0x3B: ('IOUT_CAL_OFFSET', 'linear'),
        0x40: ('VIN_OV_FAULT_LIMIT', 'linear'),
        0x42: ('VIN_UV_FAULT_LIMIT', 'linear'),
        0x44: ('VIN_UV_WARN_LIMIT', 'linear'),
        0x46: ('IOUT_OC_FAULT_LIMIT', 'linear'),
        0x4A: ('IOUT_UC_FAULT_LIMIT', 'linear'),
        0x4F: ('OT_FAULT_LIMIT', 'linear'),
        0x50: ('OT_FAULT_RESPONSE', None),
        0x51: ('OT_WARN_LIMIT', 'linear'),
        0x55: ('IIN_OC_FAULT_LIMIT', 'linear'),
        0x57: ('IIN_OC_WARN_LIMIT', 'linear'),
        0x5D: ('FAN_CONFIG_1_2', None),
        0x5E: ('FAN_CONFIG_3_4', None),
        0x5F: ('FAN_COMMAND_1', 'linear'),
        0x60: ('FAN_COMMAND_2', 'linear'),
        0x61: ('FAN_COMMAND_3', 'linear'),
        0x62: ('FAN_COMMAND_4', 'linear'),
        0x78: ('STATUS_BYTE', None),
        0x79: ('STATUS_WORD', None),
        0x7A: ('STATUS_VOUT', None),
        0x7B: ('STATUS_IOUT', None),
        0x7C: ('STATUS_INPUT', None),
        0x7D: ('STATUS_TEMPERATURE', None),
        0x7E: ('STATUS_CML', None),
        0x7F: ('STATUS_OTHER', None),
        0x80: ('STATUS_MFR_SPECIFIC', None),
        0x81: ('STATUS_FANS_1_2', None),
        0x82: ('STATUS_FANS_3_4', None),
        0x88: ('READ_VIN', 'linear'),
        0x89: ('READ_IIN', 'linear'),
        0x8B: ('READ_VOUT', 'linear'),
        0x8C: ('READ_IOUT', 'linear'),
        0x8D: ('READ_TEMPERATURE_1', 'linear'),
        0x8E: ('READ_TEMPERATURE_2', 'linear'),
        0x8F: ('READ_TEMPERATURE_3', 'linear'),
        0x90: ('READ_FAN_SPEED_1', 'linear'),
        0x91: ('READ_FAN_SPEED_2', 'linear'),
        0x92: ('READ_FAN_SPEED_3', 'linear'),
        0x93: ('READ_FAN_SPEED_4', 'linear'),
        0x96: ('READ_POUT', 'linear'),
        0x97: ('READ_PIN', 'linear'),
        0x98: ('PMBUS_REVISION', None),
        0x99: ('MFR_ID', None),
        0x9A: ('MFR_MODEL', None),
        0x9B: ('MFR_REVISION', None),
        0x9C: ('MFR_LOCATION', None),
        0x9D: ('MFR_DATE', None),
        0x9E: ('MFR_SERIAL', None),
    }

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = 'IDLE'
        self.bitcount = 0
        self.byte = 0
        self.rw = 'W'
        self.transaction_type = None
        
        self.last_scl = -1
        self.last_sda = -1
        
        self.ss = 0
        self.byte_ss = 0
        self.last_samplenum = 0
        
        self.reset_transaction_data()

    def reset_transaction_data(self):
        self.transaction_ss = 0
        self.address = None
        self.command_reg = None
        self.data_w = []
        self.data_r = []

    def start(self):
        self.out_ann = self.register(srd.OUTPUT_ANN)

    def put_ann(self, start, end, ann_type, data):
        self.put(start, end, self.out_ann, [ann_type, data])

    def output_bus_data(self, end_sample):
        if self.address is None:
            return

        addr_val = self.address >> 1
        rw = 'Read' if self.address & 1 else 'Write'
        addr_str = 'Addr:%02X(%s)' % (addr_val, rw)

        reg_str = ''
        cmd_info = None
        if self.command_reg is not None:
            reg_str = ' Reg:%02X' % self.command_reg
            if self.command_reg in self.pmbus_commands:
                cmd_info = self.pmbus_commands[self.command_reg]
                reg_str += ' (%s)' % cmd_info[0]

        data_str = ''
        if self.data_w:
            data_str = ' Write:' + ' '.join(['%02X' % b for b in self.data_w])
            if cmd_info and cmd_info[1] == 'linear' and len(self.data_w) == 2:
                val = (self.data_w[1] << 8) | self.data_w[0]
                decoded_val = self.decode_linear_format(val)
                data_str += ' (%.4f)' % decoded_val
        elif self.data_r:
            data_str = ' Read:' + ' '.join(['%02X' % b for b in self.data_r])
            if cmd_info and cmd_info[1] == 'linear' and len(self.data_r) == 2:
                val = (self.data_r[1] << 8) | self.data_r[0]
                decoded_val = self.decode_linear_format(val)
                data_str += ' (%.4f)' % decoded_val

        output_str = addr_str + reg_str + data_str
        
        self.put_ann(self.transaction_ss, end_sample, 10, [output_str])
        self.reset_transaction_data()

    def decode_linear_format(self, data):
        y = data & 0x7FF
        n_comp = (data >> 11) & 0x1F
        n = (n_comp - 16) if n_comp > 15 else n_comp
        return y * (2.0 ** n)

    def handle_start(self):
        # This is a repeated start.
        if self.state != 'IDLE':
            # If there is no command, it's a normal I2C read.
            if self.command_reg is None:
                self.output_bus_data(self.ss)
                self.reset_transaction_data()
                self.transaction_ss = self.ss
            # Otherwise it's a PMBus read. Don't reset transaction data.
        else:
            self.reset_transaction_data()
            self.transaction_ss = self.ss

        self.put_ann(self.ss, self.samplenum, 0, ['Start'])
        self.state = 'ADDRESS'
        self.bitcount = 0
        self.byte = 0

    def handle_stop(self):
        self.put_ann(self.ss, self.samplenum, 1, ['Stop'])
        self.output_bus_data(self.samplenum)
        self.state = 'IDLE'

    def process_bit(self, sda):
        if self.bitcount == 0:
            self.byte_ss = self.ss
        
        if self.options['show_bits'] == 'yes':
            self.put_ann(self.ss, self.samplenum, 2, [str(sda)])
        
        self.byte = (self.byte << 1) | sda
        self.bitcount += 1

        if self.bitcount < 8:
            return

        if self.state == 'ADDRESS':
            self.transaction_type = 'ADDRESS'
        elif self.state == 'COMMAND':
            self.transaction_type = 'COMMAND'
        elif self.state == 'DATA':
            self.transaction_type = 'DATA'
        
        self.state = 'ACK'

    def handle_ack(self, sda):
        byte_es = self.ss

        if self.transaction_type == 'ADDRESS':
            self.address = self.byte
            addr_val = self.byte >> 1
            self.rw = 'Read' if self.byte & 1 else 'Write'
            ann_type = 5 if self.rw == 'Read' else 6
            self.put_ann(self.byte_ss, byte_es, ann_type, ['%02X' % addr_val])
            if self.rw == 'Read':
                self.state = 'DATA'
            else:
                self.state = 'COMMAND'
        elif self.transaction_type == 'COMMAND':
            self.command_reg = self.byte
            self.put_ann(self.byte_ss, byte_es, 7, ['%02X' % self.byte])
            self.state = 'DATA'
        elif self.transaction_type == 'DATA':
            if self.rw == 'Write':
                self.data_w.append(self.byte)
            else:
                self.data_r.append(self.byte)
            ann_type = 8 if self.rw == 'Read' else 9
            self.put_ann(self.byte_ss, byte_es, ann_type, ['%02X' % self.byte])
            self.state = 'DATA'

        if self.options['show_bits'] == 'yes':
            ack_ann_type = 3 if sda == 0 else 4
            self.put_ann(self.ss, self.samplenum, ack_ann_type, ['ACK' if sda == 0 else 'NACK'])
        
        self.bitcount = 0
        self.byte = 0

    def decode(self):
        while True:
            scl, sda = self.wait([{0: 'e'}, {1: 'e'}])
            
            if self.last_scl == -1:
                self.last_scl, self.last_sda = scl, sda
                self.last_samplenum = self.samplenum
                continue

            self.ss = self.last_samplenum

            if self.last_scl == 1 and scl == 1 and self.last_sda == 1 and sda == 0:
                self.handle_start()
            elif self.last_scl == 1 and scl == 1 and self.last_sda == 0 and sda == 1:
                self.handle_stop()
            elif self.last_scl == 0 and scl == 1:
                if self.state in ('ADDRESS', 'COMMAND', 'DATA'):
                    self.process_bit(sda)
                elif self.state == 'ACK':
                    self.handle_ack(sda)
            
            self.last_scl, self.last_sda = scl, sda
            self.last_samplenum = self.samplenum