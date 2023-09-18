import argparse

# from jnpr.junos import Device


def run_healthcheck(device: str) -> str:
    # dev = Device(host=device, username="cristian", passwd="Juniper")
    # dev.open()
    # version = dev.rpc.get_software_information()
    # version = version.xpath("//comment")[0].text
    # dev.close()
    return f"12.3 installed on {device}"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device")
    arguments = parser.parse_args()
    if arguments.device:
        result = run_healthcheck(arguments.device)
        return result
    else:
        raise ValueError("Device hostname needs to be specified")
