# name of your application
APPLICATION = example1

# If no BOARD is found in the environment, use this default:
BOARD ?= esp32-wroom-32

# This has to be the absolute path to the RIOT base directory:
RIOTBASE ?= $(HOME)/RIOT

# Include Peripheral and FMT module
USEMODULE += srf04
USEMODULE += bme680_i2c
USEMODULE += ws281x

USEMODULE += fmt
USEMODULE += xtimer

# Comment this out to disable code in RIOT that does safety checking
# which is not needed in a production environment but helps in the
# development process:
DEVELHELP ?= 1

# Change this to 0 show compiler invocation lines by default:
QUIET ?= 1

# Include packages that pull up and auto-init the link layer.
# NOTE: 6LoWPAN will be included if IEEE802.15.4 devices are present
USEMODULE += gnrc_netdev_default
USEMODULE += auto_init_gnrc_netif
# Specify the mandatory networking modules for IPv6
USEMODULE += gnrc_ipv6_default
# Include MQTT-SN
USEMODULE += emcute
# Add also the shell, some shell commands
USEMODULE += shell
USEMODULE += shell_commands
USEMODULE += ps
# For testing we also include the ping6 command and some stats
USEMODULE += gnrc_icmpv6_echo
# Optimize network stack to for use with a single network interface
USEMODULE += gnrc_netif_single

# Connect board to wifi
USEMODULE += esp_wifi
CFLAGS += -DESP_WIFI_SSID=\"Wifi_2.4GHz\"
CFLAGS += -DESP_WIFI_PASS=\"okodikos?\"

# Give specific ID to this MQTT node
CFLAGS += -DEMCUTE_ID=\"example1\"

include $(RIOTBASE)/Makefile.include