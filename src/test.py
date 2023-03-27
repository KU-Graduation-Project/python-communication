import asyncio
from bleak import BleakClient

address = "A69B7523-4CFB-77FA-3EED-B8626B9955C6"

# characteristic UUID
uuid1 = "0000ffa1-0000-1000-8000-00805f9b34fb"
uuid2 = "0000ffa2-0000-1000-8000-00805f9b34fb"
uuid3 = "0000ffa3-0000-1000-8000-00805f9b34fb"
uuid4 = "0000ffb1-0000-1000-8000-00805f9b34fb"
uuid5 = "0000ffb2-0000-1000-8000-00805f9b34fb"
uuid6 = "0000ffb3-0000-1000-8000-00805f9b34fb"

async def notification_handler(sender, sensordata):
    # accX, accY, accZ, gyroX, gyroY, gyroZ
    data = int.from_bytes(sensordata, byteorder='little',signed=True)

    #print(f"{str(sender)}/ Received: {data}")
    if str(sender) == '0000ffa1-0000-1000-8000-00805f9b34fb (Handle: 11): Vendor specific':
        print(f"accX/ Received: {data}")
    elif str(sender) == '0000ffa2-0000-1000-8000-00805f9b34fb (Handle: 14): Vendor specific':
        print(f"accY/ Received: {data}")
    elif str(sender) == '0000ffa3-0000-1000-8000-00805f9b34fb (Handle: 17): Vendor specific':
        print(f"accZ/ Received: {data}")
    elif str(sender) == '0000ffb1-0000-1000-8000-00805f9b34fb (Handle: 20): Vendor specific':
        print(f"gyroX/ Received: {data}")
    elif str(sender) == '0000ffb2-0000-1000-8000-00805f9b34fb (Handle: 23): Vendor specific':
        print(f"gyroY/ Received: {data}")
    elif str(sender) == '0000ffb3-0000-1000-8000-00805f9b34fb (Handle: 26): Vendor specific':
        print(f"gyroZ/ Received: {data}")

async def run():
    async with BleakClient(address) as client:
        await client.start_notify(uuid1, notification_handler)
        await client.start_notify(uuid2, notification_handler)
        await client.start_notify(uuid3, notification_handler)
        await client.start_notify(uuid4, notification_handler)
        await client.start_notify(uuid5, notification_handler)
        await client.start_notify(uuid6, notification_handler)
        # wait for notifications indefinitely
        await asyncio.sleep(3600)

loop = asyncio.get_event_loop()
loop.run_until_complete(run())

