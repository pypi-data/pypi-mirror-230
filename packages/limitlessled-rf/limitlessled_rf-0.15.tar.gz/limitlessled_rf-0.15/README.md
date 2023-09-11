# Python LimitlessLED via RF

Control LimitlessLED bulbs through a directly attached radio.  The radio object must have an interface with a "`transmit`" method that formats messages as an LT8900 would over the air.

## API

### Synopsis

    limitlessled_rf.Remote(radio, remote_type, remote_id, message_id = None, config = None) -> instance
    limitlessled_rf.Remote.raw_send_button(button_info) -> value
    limitlessled_rf.Remote.raw_read_button() -> dictionary
    limitlessled_rf.Remote.set_brightness(brightness, zone = None) -> boolean
    limitlessled_rf.Remote.set_color(rgb, zone = None) -> boolean
    limitlessled_rf.Remote.set_temperature(kelvins, zone = None) -> boolean
    limitlessled_rf.Remote.on(zone = None) -> boolean
    limitlessled_rf.Remote.off(zone = None, dim = True) -> boolean
    limitlessled_rf.Remote.max_brightness(zone = None) -> boolean
    limitlessled_rf.Remote.white(zone = None) -> boolean
    limitlessled_rf.Remote.pair(zone) -> boolean
    limitlessled_rf.Remote.unpair(zone) -> boolean
    limitlessled_rf.Remote.get_zone_ids() -> list of ints
    limitlessled_rf.Remote.get_type() -> string
    limitlessled_rf.Remote.get_id() -> int
    limitlessled_rf.Remote.get_message_id() -> int
    limitlessled_rf.Remote.get_brightness_range() -> list of ints
    limitlessled_rf.Remote.get_temperature_range() -> llist of ints

### Constructor

Construct a LimitlessLED object that uses the specified radio to act as a specific numeric remote for a specific type of LimitlessLED bulb system.

The "`radio`" object is an LT8900 compatible radio interface -- for example the "`lt8900_spi`" package.

The "`remote_type`" parameter is a string which refers to the type of LimitlessLED bulb this remote can control.  Valid values are: "rgbw" or "cct".

The "`message_id`" parameter allows you to set a default initial message\_id.  If this is not supplied a random value is generated.

The "`config`" parameter allows for overriding a bulbs configuration.  Valid keys can be found in the "`_remote_type_parameters_map`" map.

### instance.raw\_send\_button

Send a button event directly via the locally connected radio to a remote bulb.

The "`button_info`" dictionary contains at least the "`button`" key which identifies the button by name.  Additional keys may be needed depending on the particular button.

### instance.raw\_read\_button

Wait for a button to be pressed that the locally connected radio can read and then return that as a parsed "`button_info`" dictionary.

### instance\.set\_brightness

Set the brightness for the bulbs paired to the specified zone.  Brightness ranges from 0 (off) to 255 (maximum brightness).

If no zone is specified all bulbs attached to the remote are updated.

### instance.set\_color

Set the color for the bulbs paired to the specified zone.  The "`rgb`" parameter is a 16-bit true-color value ranging from 0x000000 (black) to 0xffffff (white).  Since LimitlessLED bulbs
are not actually true-color, this will get mapped to a nearby color before sending it to the bulb.  If the color sent is a shade of white, and the bulb supports white it will be
translated into a brightness.  Otherwise, brightness will not be altered.

If no zone is specified all bulbs attached to the remote are updated.

### instance.set\_temperature

Set the color temperature for the bulbs paired to the specified zone.  The "`kelvins`" parameter refers to the color temperature, in kelvins, that the bulb should be configured to display.
Since LimitlessLED bulbs do not support infinite color temperatures, it will clamped to the range supported and to the nearest color temperature supported before sending the command
to the bulb.

If no zone is specified all bulbs attached to the remote are updated.

### instance.on

Turn on bulbs in the specified zone.

If no zone is specified all bulbs attached to the remote are updated.

### instance.off

Turn off bulbs in the specified zone.

If no zone is specified all bulbs attached to the remote are updated.

### instance.white

Turn the bulbs in the specified zone to their white mode.

If no zone is specified all bulbs attached to the remote are updated.

### instance.pair

Issue the bulb-specific kind of pairing sequence to pair a newly powered-on bulb to this remote on the specified zone.

### instance.unpair

Issue the bulb-specific kind of unpairing sequence to unpair a newly powered-on bulb from this remote on the specified zone.  The bulb must already be paired with this remote and in
the zone before it can be unpaired.  Once a bulb is unpaired from a given remote, it is unpaired from all remotes.

## Example

    #! /usr/bin/env python3
    
    import random
    import time
   
    import gpiozero
    import limitlessled_rf
    import lt8900_spi
    
    def init_radio():
    	# Need to keep this attached to drive the line high -- if the object disappears then
    	# the GPIO port gets reconfigured as an input port
    	# Note: broadcom pin numbers are used
    	reset_gpio = gpiozero.LED(24)
    	reset_gpio.on()
    	def reset_module_via_gpio():
    		reset_gpio.off()
    		time.sleep(0.1)
    		reset_gpio.on()
    		time.sleep(0.1)
    
    	# LT8900 compatible radio
    	radio = lt8900_spi.Radio(0, 0, {
    		'reset_command': reset_module_via_gpio,
    		'reset_command_gpio': reset_gpio
    	})
    
    	if not radio.initialize():
    		return None
    
    	return radio
    
    radio = init_radio()
    remote = limitlessled_rf.Remote(radio, 'rgbw', 0x51F0)
    
    while True:
    	remote.set_color(random.randint(0, 0xffffff))
