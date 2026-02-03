import asyncio
from bleak import BleakClient
from pylsl import StreamInfo, StreamOutlet

ADDRESS = "A0:9E:1A:A8:B4:7E"
HR_CHAR_UUID = "00002a37-0000-1000-8000-00805f9b34fb"

info = StreamInfo("physio_metrics", "metrics", 1, 0, "float32", "polar-verity-001")
outlet = StreamOutlet(info)

def notification_handler(sender, data):
    flags = data[0]
    hr_16bit = flags & 0x01

    if hr_16bit:
        hr = int.from_bytes(data[1:3], "little")
    else:
        hr = data[1]

    print("HR:", hr)
    outlet.push_sample([float(hr)])

async def main():
    async with BleakClient(ADDRESS) as client:
        print("Connected:", client.is_connected)
        await client.start_notify(HR_CHAR_UUID, notification_handler)
        while True:
            await asyncio.sleep(1)

asyncio.run(main())