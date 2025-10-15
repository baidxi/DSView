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
    id = 'smbus'
    name = 'SMBus'
    longname = 'System Management Bus'
    desc = 'System Management Bus protocol.'
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
        ('addr-read', 'Addr R'),
        ('addr-write', 'Addr W'),
        ('reg', 'Register'),
        ('data-read', 'Data R'),
        ('data-write', 'Data W'),
        ('transaction', 'Transaction'),
    )

    annotation_rows = (
        ('bus', 'Bus', (10,)),
        ('signals', 'Signals', (0, 1, 3, 4, 5, 6, 7, 8, 9)),
        ('bits', 'Bits', (2,)),
    )

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
        rw = 'R' if self.address & 1 else 'W'
        addr_str = 'Addr:%02X(%s)' % (addr_val, rw)

        reg_str = ' Reg:%02X' % self.command_reg if self.command_reg is not None else ''

        data_str = ''
        if self.data_w:
            data_str = ' W:' + ' '.join(['%02X' % b for b in self.data_w])
        elif self.data_r:
            data_str = ' R:' + ' '.join(['%02X' % b for b in self.data_r])

        output_str = addr_str + reg_str + data_str
        
        self.put_ann(self.transaction_ss, end_sample, 10, [output_str])
        self.reset_transaction_data()

    def handle_start(self):
        if self.address is not None:
            self.output_bus_data(self.ss)

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
            self.rw = 'R' if self.byte & 1 else 'W'
            ann_type = 5 if self.rw == 'R' else 6
            self.put_ann(self.byte_ss, byte_es, ann_type, ['%02X' % addr_val])
            self.state = 'COMMAND'
        elif self.transaction_type == 'COMMAND':
            self.command_reg = self.byte
            self.put_ann(self.byte_ss, byte_es, 7, ['%02X' % self.byte])
            self.state = 'DATA'
        elif self.transaction_type == 'DATA':
            if self.rw == 'W':
                self.data_w.append(self.byte)
            else:
                self.data_r.append(self.byte)
            ann_type = 8 if self.rw == 'R' else 9
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