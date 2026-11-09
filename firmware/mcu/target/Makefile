CC = arm-none-eabi-gcc
OBJCOPY = arm-none-eabi-objcopy
SIZE = arm-none-eabi-size

CFLAGS = -mcpu=cortex-m0plus -mthumb -Os -g -std=c11 -Wall -Wextra \
         -ffunction-sections -fdata-sections -Icmsis -I../include
LDFLAGS = -Tlinker.ld -nostartfiles -Wl,--gc-sections -Wl,-Map=build/firmware.map

SRC = ../src/main.c ../src/power.c ../src/proto.c ../src/pir.c \
      startup.c system_stm32l0xx.c hal_stm32l0.c

all: build/firmware.bin

build:
	mkdir -p build

build/firmware.elf: $(SRC) linker.ld | build
	$(CC) $(CFLAGS) $(LDFLAGS) $(SRC) -o $@

build/firmware.bin: build/firmware.elf
	$(OBJCOPY) -O binary $< $@
	$(SIZE) $<

clean:
	rm -rf build
