from ds18b20 import DS18B20

sensor = DS18B20()
temperature_in_celsius = sensor.get_temperature()
temperature_in_fahrenheit = sensor.get_temperature(DS18B20.DEGREES_F)