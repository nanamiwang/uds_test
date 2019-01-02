from __future__ import print_function
import sys
from panda import Panda
from uds import UdsClient
from uds import ACCESS_TYPE, SESSION_TYPE, SERVICE_TYPE
import struct

# The tx address of the camera
TX_ADDRESS = 0x5A

# access key
# unsigned short format, 2 bytes.
KEY = struct.pack('H', 20103)
# Uncomment line below to use unsigned short format, 4 bytes.
#KEY = struct.pack('I', 20103)


if __name__ == "__main__":
	try:
		print("Trying to connect to Panda over USB...")
		p = Panda()
	except:
		print("Connect to panda failed")
		sys.exit(0)

	uds_client = UdsClient(p, TX_ADDRESS, rx_addr=TX_ADDRESS, bus=0, timeout=10, debug=True)
	# Step 1: Init diagnostic session
	result = uds_client._uds_request(SERVICE_TYPE.DIAGNOSTIC_SESSION_CONTROL, subfunction=SESSION_TYPE.EXTENDED_DIAGNOSTIC)
	print('Init diagnostic session return:', result)
	# Step 2: Request a seed
	security_seed = uds_client.security_access(ACCESS_TYPE.REQUEST_SEED)
	if not security_seed:
		print("Request security seed failed.")
		text = raw_input("Request security seed failed. Input \'y\' to continue, other to exit:")
		if text == 'y':
			sys.exit(0)
	print('the seed is', security_seed)
	# Step 3: Send the access key
	result = uds_client.security_access(ACCESS_TYPE.SEND_KEY, security_key=KEY)
	print('security_access return', result)
	# Step 4: Read memory, read ERAY_GTUC05 register
	result = uds_client.read_memory_by_address(0xF0010098, 4)
	print('read_memory_by_address return', result)