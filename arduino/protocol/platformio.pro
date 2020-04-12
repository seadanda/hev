win32 {
    HOMEDIR += $$(USERPROFILE)
}
else {
    HOMEDIR += $$(HOME)
}
INCLUDEPATH += "$${_PRO_FILE_PWD_}/include"
INCLUDEPATH += "$${_PRO_FILE_PWD_}/src"
INCLUDEPATH += "$${_PRO_FILE_PWD_}/../common/lib/commsControl"
INCLUDEPATH += "$${_PRO_FILE_PWD_}/.pio/libdeps/uno/uCRC16Lib_ID5390/src"
INCLUDEPATH += "$${_PRO_FILE_PWD_}/.pio/libdeps/uno/RingBuffer_ID5418/src"
INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/framework-arduino-avr/cores/arduino"
INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/framework-arduino-avr/variants/standard"
INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/framework-arduino-avr/libraries/EEPROM/src"
INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/framework-arduino-avr/libraries/HID/src"
INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/framework-arduino-avr/libraries/SPI/src"
INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/framework-arduino-avr/libraries/SoftwareSerial/src"
INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/framework-arduino-avr/libraries/Wire/src"
INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/toolchain-atmelavr/avr/include"
INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/toolchain-atmelavr/lib/gcc/avr/5.4.0/include"
INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/toolchain-atmelavr/lib/gcc/avr/5.4.0/include-fixed"
INCLUDEPATH += "$${HOMEDIR}/.platformio/packages/tool-unity"

DEFINES += "PLATFORMIO=40301"
DEFINES += "ARDUINO_AVR_UNO"
DEFINES += "F_CPU=16000000L"
DEFINES += "ARDUINO_ARCH_AVR"
DEFINES += "ARDUINO=10808"
DEFINES += "__AVR_ATmega328P__"

OTHER_FILES += platformio.ini

SOURCES +=  src/protocol.cpp \
            ../common/lib/commsControl/commsControl.cpp \
            ../common/lib/commsControl/commsFormat.cpp

HEADERS +=  ../common/lib/commsControl/commsConstants.h \
            ../common/lib/commsControl/commsControl.h \
            ../common/lib/commsControl/commsFormat.h
