from micropython import const

MAX31856_CONST_THERM_LSB = 2**-7
MAX31856_CONST_THERM_BITS = const(19)
MAX31856_CONST_CJ_LSB = 2**-6
MAX31856_CONST_CJ_BITS = const(14)
MAX31856_REG_READ_CR0 = const(0x00)
MAX31856_REG_READ_CR1 = const(0x01)
MAX31856_REG_READ_MASK = const(0x02)
MAX31856_REG_READ_CJHF = const(0x03)
MAX31856_REG_READ_CJLF = const(0x04)
MAX31856_REG_READ_LTHFTH = const(0x05)
MAX31856_REG_READ_LTHFTL = const(0x06)
MAX31856_REG_READ_LTLFTH = const(0x07)
MAX31856_REG_READ_LTLFTL = const(0x08)
MAX31856_REG_READ_CJTO = const(0x09)
MAX31856_REG_READ_CJTH = const(0x0A)  # Cold-Junction Temperature Register, MSB
MAX31856_REG_READ_CJTL = const(0x0B)  # Cold-Junction Temperature Register, LSB
MAX31856_REG_READ_LTCBH = const(0x0C) # Linearized TC Temperature, Byte 2
MAX31856_REG_READ_LTCBM = const(0x0D) # Linearized TC Temperature, Byte 1
MAX31856_REG_READ_LTCBL = const(0x0E) # Linearized TC Temperature, Byte 0
MAX31856_REG_READ_FAULT = const(0x0F) 
MAX31856_REG_WRITE_CR0 = const(0x80)
MAX31856_REG_WRITE_CR1 = const(0x81)
MAX31856_REG_WRITE_MASK = const(0x82)
MAX31856_REG_WRITE_CJHF = const(0x83)
MAX31856_REG_WRITE_CJLF = const(0x84)
MAX31856_REG_WRITE_LTHFTH = const(0x85)
MAX31856_REG_WRITE_LTHFTL = const(0x86)
MAX31856_REG_WRITE_LTLFTH = const(0x87)
MAX31856_REG_WRITE_LTLFTL = const(0x88)
MAX31856_REG_WRITE_CJTO = const(0x89)
MAX31856_REG_WRITE_CJTH = const(0x8A)  # Cold-Junction Temperature Register, MSB
MAX31856_REG_WRITE_CJTL = const(0x8B)  # Cold-Junction Temperature Register, LSB
MAX31856_CR0_READ_ONE = const(0x40) # One shot reading, delay approx. 200ms then read temp registers
MAX31856_CR0_READ_CONT = const(0x80) # Continuous reading, delay approx. 100ms between readings
MAX31856_CR1_AVGSEL_01 = const(0x0) # 1 sample averaging
MAX31856_CR1_AVGSEL_02 = const(0x1) # 2 sample averaging
MAX31856_CR1_AVGSEL_04 = const(0x2) # 4 sample averaging
MAX31856_CR1_AVGSEL_08 = const(0x3) # 8 sample averaging
MAX31856_CR1_AVGSEL_16 = const(0x4) # 16 sample averaging
MAX31856_B_TYPE = const(0x0)
MAX31856_E_TYPE = const(0x1)
MAX31856_J_TYPE = const(0x2)
MAX31856_K_TYPE = const(0x3)
MAX31856_N_TYPE = const(0x4)
MAX31856_R_TYPE = const(0x5)
MAX31856_S_TYPE = const(0x6)
MAX31856_T_TYPE = const(0x7)

class MAX31856:
    def __init__(self, spi, cs, tc_type=MAX31856_K_TYPE, conv_mode=MAX31856_CR0_READ_CONT, avgsel=MAX31856_CR1_AVGSEL_16):
        """SPI Example: SPI(1, baudrate=5000000, polarity=0, phase=1)"""
        self._a = bytearray(1)
        self._b1 = bytearray(1)
        self._b2 = bytearray(2)
        self._b3 = bytearray(3)
        self._spi = spi
        self._cs = cs
        self.write_register(MAX31856_REG_WRITE_CR0, conv_mode)
        self.write_register(MAX31856_REG_WRITE_CR1, (avgsel << 4) + tc_type)

    def _cj_temp_from_bytes(self, b):
        v = (((b[0] & 0x7F) << 8) + b[1]) >> 2
        if b[0] & 0x80:
            v -= 2 ** (MAX31856_CONST_CJ_BITS - 1)
        v = v * MAX31856_CONST_CJ_LSB
        return v

    def _thermocouple_temp_from_bytes(self, b):
        v = (((b[0] & 0x7F) << 16) + (b[1] << 8) + b[2])
        v = v >> 5
        if b[0] & 0x80:
            v -= 2 ** (MAX31856_CONST_THERM_BITS - 1)
        v = v * MAX31856_CONST_THERM_LSB
        return v

    def read_registers(self, addr, buf):
        self._a[0] = addr
        self._cs.off()
        self._spi.write(self._a)
        self._spi.readinto(buf)
        self._cs.on()
        return buf

    def write_register(self, addr, val):
        self._b2[0] = addr
        self._b2[1] = val
        self._cs.off()
        r = self._spi.write(self._b2)
        self._cs.on()
        return r

    def read_internal_temp_c(self):
        self.read_registers(MAX31856_REG_READ_CJTH, self._b2)
        return self._cj_temp_from_bytes(self._b2)

    def read_temp_c(self):
        self.read_registers(MAX31856_REG_READ_LTCBH, self._b3)
        return self._thermocouple_temp_from_bytes(self._b3)

    def read_fault(self):
        return self.read_registers(MAX31856_REG_READ_FAULT, self._b1)
