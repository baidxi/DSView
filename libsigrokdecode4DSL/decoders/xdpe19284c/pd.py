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
    id = 'xdpe19284c'
    name = 'XDPE19284C'
    longname = 'Infineon XDPE19284C'
    desc = 'Infineon XDPE19284C PMBus protocol.'
    license = 'gplv2+'
    inputs = ['logic']
    outputs = ['smbus']
    tags = ['Embedded/industrial']

    channels = (
        {'id': 'scl', 'name': 'SCL', 'desc': 'Serial Clock Line'},
        {'id': 'sda', 'name': 'SDA', 'desc': 'Serial Data Line'},
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
        0x01: ('OPERATION', 'operation'),
        0x02: ('ON_OFF_CONFIG', 'on_off_config'),
        0x03: ('CLEAR_FAULTS', None),
        0x10: ('WRITE_PROTECT', 'write_protect'),
        0x19: ('CAPABILITY', 'capability'),
        0x20: ('VOUT_MODE', None),
        0x21: ('VOUT_COMMAND', 'vout'),
        0x22: ('VOUT_TRIM', 'vout'),
        0x23: ('VOUT_CAL_OFFSET', 'vout'),
        0x24: ('VOUT_MAX', 'vout'),
        0x25: ('VOUT_MARGIN_HIGH', 'vout'),
        0x26: ('VOUT_MARGIN_LOW', 'vout'),
        0x27: ('VOUT_TRANSITION_RATE', 'vout'),
        0x29: ('VOUT_SCALE_LOOP', 'vout'),
        0x33: ('FREQUENCY_SWITCH', 'linear'),
        0x34: ('VOUT_SCALE_MONITOR', 'vout'),
        0x35: ('VIN_ON', 'vout'),
        0x36: ('VIN_OFF', 'vout'),
        0x3A: ('IOUT_CAL_GAIN', 'linear'),
        0x3B: ('IOUT_CAL_OFFSET', 'linear'),
        0x40: ('VIN_OV_FAULT_LIMIT', 'vout'),
        0x42: ('VIN_UV_FAULT_LIMIT', 'vout'),
        0x44: ('VIN_UV_WARN_LIMIT', 'vout'),
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
        0x78: ('STATUS_BYTE', 'status_byte'),
        0x79: ('STATUS_WORD', 'status_word'),
        0x7A: ('STATUS_VOUT', 'status_vout'),
        0x7B: ('STATUS_IOUT', 'status_iout'),
        0x7C: ('STATUS_INPUT', 'status_input'),
        0x7D: ('STATUS_TEMPERATURE', 'status_temp'),
        0x7E: ('STATUS_CML', 'status_cml'),
        0x7F: ('STATUS_OTHER', 'status_other'),
        0x80: ('STATUS_MFR_SPECIFIC', 'status_mfr'),
        0x81: ('STATUS_FANS_1_2', None),
        0x82: ('STATUS_FANS_3_4', None),
        0x88: ('READ_VIN', 'vout'),
        0x89: ('READ_IIN', 'linear'),
        0x8B: ('READ_VOUT', 'vout'),
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
        # Add all MFR commands from datasheet
        0xA0: ('MFR_VOUT_TRIM_UP_RATE', 'vout'),
        0xA1: ('MFR_VOUT_TRIM_DOWN_RATE', 'vout'),
        0xA2: ('MFR_VOUT_TRIM_UP_STEP', 'vout'),
        0xA3: ('MFR_VOUT_TRIM_DOWN_STEP', 'vout'),
        0xA4: ('MFR_VOUT_TRIM_UP_MAX', 'vout'),
        0xA5: ('MFR_VOUT_TRIM_DOWN_MIN', 'vout'),
        0xA6: ('MFR_VOUT_TRIM_DELAY', None),
        0xA7: ('MFR_VOUT_TRIM_DECAY', None),
        0xA8: ('MFR_VOUT_CMD_MIN', 'vout'),
        0xA9: ('MFR_VOUT_CMD_MAX', 'vout'),
        0xAA: ('MFR_VOUT_CMD_STEP', 'vout'),
        0xAB: ('MFR_VOUT_OFFSET', 'vout'),
        0xAC: ('MFR_VOUT_SCALE', 'vout'),
        0xAD: ('MFR_IC_DEVICE_ID', None),
        0xAE: ('MFR_IC_DEVICE_REV', None),
        0xB0: ('MFR_IOUT_OC_FAST_FAULT_RESPONSE', None),
        0xB1: ('MFR_IOUT_OC_FAST_FAULT_LIMIT', 'linear'),
        0xB2: ('MFR_IOUT_OC_SLOW_FAULT_RESPONSE', None),
        0xB3: ('MFR_IOUT_OC_SLOW_FAULT_LIMIT', 'linear'),
        0xB4: ('MFR_IOUT_OC_WARN_LIMIT_LOOP', 'linear'),
        0xB5: ('MFR_IOUT_UC_FAULT_RESPONSE_LOOP', None),
        0xB6: ('MFR_IOUT_UC_FAULT_LIMIT_LOOP', 'linear'),
        0xB7: ('MFR_IOUT_OFFSET', 'linear'),
        0xB8: ('MFR_IOUT_SCALE', 'linear'),
        0xB9: ('MFR_IOUT_CAL_OFFSET_ADC', 'linear'),
        0xBA: ('MFR_IOUT_CAL_GAIN_ADC', 'linear'),
        0xBB: ('MFR_IOUT_TEMP_COEFF', 'linear'),
        0xBC: ('MFR_IOUT_TEMP_COMP', None),
        0xC0: ('MFR_LOOP_POLE_ZERO_CONFIG', None),
        0xC1: ('MFR_LOOP_GAIN_CONFIG', None),
        0xC2: ('MFR_LOOP_PID_CONFIG', None),
        0xC3: ('MFR_LOOP_MISC_CONFIG', None),
        0xC4: ('MFR_LOOP_VOUT_CONFIG', None),
        0xC5: ('MFR_LOOP_IOUT_CONFIG', None),
        0xC6: ('MFR_LOOP_IIN_CONFIG', None),
        0xC7: ('MFR_LOOP_VIN_CONFIG', None),
        0xC8: ('MFR_LOOP_TELEMETRY_CONFIG', None),
        0xC9: ('MFR_LOOP_STATUS_CONFIG', None),
        0xCA: ('MFR_LOOP_FAULT_CONFIG', None),
        0xCB: ('MFR_LOOP_PIN_CONFIG', None),
        0xCC: ('MFR_LOOP_FAN_CONFIG', None),
        0xCD: ('MFR_LOOP_PMBUS_CONFIG', None),
        0xCE: ('MFR_REGISTER_POINTER', None),
        0xCF: ('MFR_LOOP_USER_CONFIG', None),
        0xD0: ('MFR_VOUT_PEAK', 'vout'),
        0xD1: ('MFR_IOUT_PEAK', 'linear'),
        0xD2: ('MFR_VIN_PEAK', 'vout'),
        0xD3: ('MFR_IIN_PEAK', 'linear'),
        0xD4: ('MFR_PIN_PEAK', 'linear'),
        0xD5: ('MFR_POUT_PEAK', 'linear'),
        0xD6: ('MFR_TEMPERATURE_PEAK', 'linear'),
        0xD7: ('MFR_DUTY_CYCLE_PEAK', 'linear'),
        0xD8: ('MFR_FREQUENCY_PEAK', 'linear'),
        0xD9: ('MFR_FW_VERSION', None),
        0xDA: ('MFR_TRIM_CONTROL', None),
        0xDB: ('MFR_TRIM_SELECT', None),
        0xDC: ('MFR_TRIM_VALUE', None),
        0xDD: ('MFR_TRIM_STATUS', None),
        0xDE: ('MFR_REG_WRITE', None),
        0xDF: ('MFR_REG_READ', None),
        0xE0: ('MFR_SPECIFIC_00', None),
        0xE1: ('MFR_SPECIFIC_01', None),
        0xE2: ('MFR_SPECIFIC_02', None),
        0xE3: ('MFR_SPECIFIC_03', None),
        0xE4: ('MFR_SPECIFIC_04', None),
        0xE5: ('MFR_SPECIFIC_05', None),
        0xE6: ('MFR_SPECIFIC_06', None),
        0xE7: ('MFR_SPECIFIC_07', None),
        0xE8: ('MFR_SPECIFIC_08', None),
        0xE9: ('MFR_SPECIFIC_09', None),
        0xEA: ('MFR_SPECIFIC_0A', None),
        0xEB: ('MFR_SPECIFIC_0B', None),
        0xEC: ('MFR_SPECIFIC_0C', None),
        0xED: ('MFR_SPECIFIC_0D', None),
        0xEE: ('MFR_SPECIFIC_0E', None),
        0xEF: ('MFR_COMMON', None),
        0xF0: ('MFR_QUERY', None),
        0xF1: ('MFR_DEVICE_ID', None),
        0xF2: ('MFR_DEVICE_INFO', None),
        0xF3: ('MFR_RESET', None),
        0xF4: ('MFR_STORE', None),
        0xF5: ('MFR_RESTORE', None),
        0xF6: ('MFR_CRC', None),
        0xF7: ('MFR_PASSWORD', None),
        0xF8: ('MFR_CONFIG_ALL', None),
        0xF9: ('MFR_CONFIG_CRC', None),
        0xFA: ('MFR_PAGE_ALL', None),
        0xFB: ('MFR_OTP_CTRL', None),
        0xFC: ('MFR_OTP_STATUS', None),
        0xFD: ('MFR_FW_COMMAND_DATA', None),
        0xFE: ('MFR_FW_COMMAND', None),
    }

    def __init__(self):
        self.reset()

    def reset(self):
        self.state = 'IDLE'
        self.bitcount = 0
        self.byte = 0
        self.rw = 'Write'
        self.transaction_type = None
        
        self.last_scl = -1
        self.last_sda = -1
        
        self.ss = 0
        self.byte_ss = 0
        self.last_samplenum = 0
        
        self.reset_transaction_data()
        self.vout_mode = 0x00

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

        # Update vout_mode on write to VOUT_MODE register
        if self.command_reg == 0x20 and self.data_w:
            self.vout_mode = self.data_w[0]

        data_str = ''
        data_bytes = None
        if self.data_w:
            data_str = ' Write:' + ' '.join(['%02X' % b for b in self.data_w])
            data_bytes = self.data_w
        elif self.data_r:
            data_str = ' Read:' + ' '.join(['%02X' % b for b in self.data_r])
            data_bytes = self.data_r

        if cmd_info and data_bytes:
            format_type = cmd_info[1]
            
            decoded_str = None
            if format_type == 'linear' and len(data_bytes) == 2:
                val = (data_bytes[1] << 8) | data_bytes[0]
                decoded_val = self.decode_linear_format(val)
                decoded_str = ' (%.4f)' % decoded_val
            elif format_type == 'vout' and len(data_bytes) == 2:
                mode = (self.vout_mode >> 5) & 0x7
                if mode == 0b000:  # Linear format based on VOUT_MODE
                    y = (data_bytes[1] << 8) | data_bytes[0]
                    n_comp = self.vout_mode & 0x1F
                    n = (n_comp - 32) if n_comp > 15 else n_comp
                    decoded_val = y * (2.0 ** n)
                    decoded_str = ' (%.4f)' % decoded_val
                else:
                    formats = {1: 'VID', 2: 'Direct', 3: 'IEEE-754 HP', 4: 'IEEE-754 SP'}
                    mode_name = formats.get(mode, 'Unknown')
                    decoded_str = ' (%s format)' % mode_name
            else:
                # Bitfield decoders
                decoders = {
                    'operation': self.decode_operation,
                    'on_off_config': self.decode_on_off_config,
                    'write_protect': self.decode_write_protect,
                    'capability': self.decode_capability,
                    'status_byte': self.decode_status_byte,
                    'status_word': self.decode_status_word,
                    'status_vout': self.decode_status_vout,
                    'status_iout': self.decode_status_iout,
                    'status_input': self.decode_status_input,
                    'status_temp': self.decode_status_temp,
                    'status_cml': self.decode_status_cml,
                    'status_other': self.decode_status_other,
                    'status_mfr': self.decode_status_mfr,
                }
                if format_type in decoders and data_bytes:
                    val = 0
                    if len(data_bytes) == 1:
                        val = data_bytes[0]
                    elif len(data_bytes) == 2:
                        val = (data_bytes[1] << 8) | data_bytes[0]
                    
                    decoded_bits = decoders[format_type](val)
                    if decoded_bits:
                        decoded_str = ' (%s)' % ', '.join(decoded_bits)

            if decoded_str:
                data_str += decoded_str

        output_str = addr_str + reg_str + data_str
        
        self.put_ann(self.transaction_ss, end_sample, 10, [output_str])
        self.reset_transaction_data()

    def decode_linear_format(self, data):
        y = data & 0x7FF
        n_comp = (data >> 11) & 0x1F
        n = (n_comp - 16) if n_comp > 15 else n_comp
        return y * (2.0 ** n)

    def decode_bitfield(self, data, bits_map):
        parts = []
        for bit, name in bits_map.items():
            if data & (1 << bit):
                parts.append(name)
        return parts

    def decode_operation(self, data):
        parts = []
        if data & 0x80:
            parts.append('On')
        else:
            parts.append('Off')
        
        if (data & 0x60) == 0x40:
            parts.append('Margin High')
        elif (data & 0x60) == 0x20:
            parts.append('Margin Low')
        else:
            parts.append('No Margin')
        return parts

    def decode_on_off_config(self, data):
        return self.decode_bitfield(data, {
            4: 'CMD', 3: 'CPI', 2: 'POL', 1: 'PU', 0: 'EN'
        })

    def decode_write_protect(self, data):
        return self.decode_bitfield(data, {
            7: 'DISABLE_ALL', 2: 'PAGE_2', 1: 'PAGE_1', 0: 'PAGE_0'
        })

    def decode_capability(self, data):
        parts = []
        if data & 0x80: parts.append('PEC')
        if data & 0x40: parts.append('ALERT#')
        if data & 0x20: parts.append('SMBus')
        return parts

    def decode_status_byte(self, data):
        return self.decode_bitfield(data, {
            7: 'VOUT', 6: 'IOUT/POUT', 5: 'INPUT', 4: 'MFR',
            3: 'POWER_GOOD#', 2: 'FANS', 1: 'OTHER', 0: 'UNKNOWN'
        })

    def decode_status_word(self, data):
        low_byte = data & 0xFF
        high_byte = (data >> 8) & 0xFF
        parts = self.decode_status_byte(low_byte)
        
        high_bits = {
            7: 'VOUT_OV_FAULT', 6: 'IOUT_OC_FAULT', 5: 'VIN_UV_FAULT',
            4: 'OT_FAULT', 3: 'TON_MAX_FAULT', 2: 'CML', 1: 'NONE', 0: 'BUSY'
        }
        parts.extend(self.decode_bitfield(high_byte, high_bits))
        return parts

    def decode_status_vout(self, data):
        return self.decode_bitfield(data, {
            7: 'OV_FAULT', 6: 'OV_WARN', 5: 'UV_WARN', 4: 'UV_FAULT',
            3: 'MAX', 2: 'TON_MAX', 1: 'TOFF_MAX', 0: 'VOUT_TRACK'
        })

    def decode_status_iout(self, data):
        return self.decode_bitfield(data, {
            7: 'OC_FAULT', 6: 'OC_WARN', 5: 'UC_FAULT', 4: 'CURRENT_SHARE',
            3: 'PWR_LIMIT', 2: 'POUT_OP_FAULT', 1: 'POUT_OP_WARN', 0: 'IN_PWR_LIMIT'
        })

    def decode_status_input(self, data):
        return self.decode_bitfield(data, {
            7: 'VIN_OV_FAULT', 6: 'VIN_OV_WARN', 5: 'VIN_UV_WARN', 4: 'VIN_UV_FAULT',
            3: 'IIN_OC_FAULT', 2: 'IIN_OC_WARN', 1: 'PIN_OP_WARN', 0: 'UNIT_OFF'
        })

    def decode_status_temp(self, data):
        return self.decode_bitfield(data, {
            7: 'OT_FAULT', 6: 'OT_WARN', 5: 'UT_WARN', 4: 'UT_FAULT'
        })

    def decode_status_cml(self, data):
        return self.decode_bitfield(data, {
            7: 'INVALID_CMD', 6: 'INVALID_DATA', 5: 'PEC_FAIL', 4: 'MEM_FAULT',
            3: 'PROC_FAULT', 1: 'COMM_OTHER', 0: 'OTHER'
        })

    def decode_status_other(self, data):
        return self.decode_bitfield(data, {
            7: 'MFR_SPEC', 6: 'INPUT_A', 5: 'INPUT_B', 4: 'INPUT_C',
            3: 'FANS_3_4', 2: 'FANS_1_2', 1: 'OTP', 0: 'ORING'
        })

    def decode_status_mfr(self, data):
        return self.decode_bitfield(data, {
            7: 'TRIM_FAIL', 6: 'VMON_FAIL', 5: 'CRC_FAIL', 4: 'NVM_FAIL',
            3: 'VDR_FAIL', 2: 'VREF_FAIL', 1: 'TSEN_FAIL', 0: 'DRV_FAIL'
        })

    def handle_start(self):
        if self.state != 'IDLE':
            # Repeated start. Finalize previous transaction.
            if self.address is not None:
                self.output_bus_data(self.ss)
            self.reset_transaction_data()
            self.transaction_ss = self.ss
        else:
            # Normal start.
            self.reset_transaction_data()
            self.transaction_ss = self.ss

        self.put_ann(self.samplenum, self.samplenum, 0, ['S'])
        self.state = 'ADDRESS'
        self.bitcount = 0
        self.byte = 0

    def handle_stop(self):
        self.put_ann(self.samplenum, self.samplenum, 1, ['P'])
        if self.address is not None:
            self.output_bus_data(self.samplenum)
        self.state = 'IDLE'

    def process_bit(self, sda):
        if self.bitcount == 0:
            self.byte_ss = self.ss
        
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
            ann_str = 'Addr:%02X' % (addr_val)
            self.put_ann(self.byte_ss, byte_es, ann_type, [ann_str])
            self.state = 'COMMAND'
        elif self.transaction_type == 'COMMAND':
            self.command_reg = self.byte
            cmd_str = 'Reg:%02X' % self.byte
            if self.command_reg in self.pmbus_commands:
                cmd_info = self.pmbus_commands[self.command_reg]
                cmd_name = cmd_info[0]
                if cmd_name:
                    cmd_str += ' (%s)' % cmd_name
            self.put_ann(self.byte_ss, byte_es, 7, [cmd_str])
            self.state = 'DATA'
        elif self.transaction_type == 'DATA':
            if self.rw == 'Write':
                self.data_w.append(self.byte)
            else:
                self.data_r.append(self.byte)
            ann_type = 8 if self.rw == 'Read' else 9
            data_str = '%s:%02X' % (self.rw, self.byte)
            self.put_ann(self.byte_ss, byte_es, ann_type, [data_str])
            self.state = 'DATA'
        
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