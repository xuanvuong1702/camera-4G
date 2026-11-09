CC ?= clang
CFLAGS ?= -std=c11 -Wall -Wextra -O1
INC = -Iinclude

SRC = src/power.c src/proto.c src/pir.c
TEST_SRC = $(SRC) host/hal_mock.c host/test_mcu.c

.PHONY: test clean target

test:
	mkdir -p build
	$(CC) $(CFLAGS) $(INC) $(TEST_SRC) -o build/test_mcu
	./build/test_mcu

# Target build requires arm-none-eabi-gcc + STM32CubeL0 (CMSIS + HAL).
# Not verified on this machine.
target:
	@echo "Need arm-none-eabi-gcc and Drivers/ from STM32CubeL0"
	$(MAKE) -C target

clean:
	rm -rf build
