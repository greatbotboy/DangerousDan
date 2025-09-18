#!/usr/bin/env python3
import os
import stat
import subprocess
import time
import logging
import re

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

CONFIG = {
    "SHRED_PASSES": 3,
    "POLL_INTERVAL_SECONDS": 2,
    "EXCLUDED_DEVICES": ["sda"], # Example: prevent wiping the OS drive
}

def get_block_devices():
    """
    Parses /proc/partitions to get a list of block devices.
    Filters out partition names (e.g., sda1) and loop devices.
    """
    devices = []
    try:
        with open('/proc/partitions', 'r') as f:
            lines = f.readlines()[2:] # Skip header
            for line in lines:
                parts = line.strip().split()
                if not parts:
                    continue
                device_name = parts[3]
                # We want whole disks (e.g., 'sda'), not partitions ('sda1') or loop devices
                if re.match(r'^[sh]d[a-z]+$', device_name):
                    if device_name not in CONFIG["EXCLUDED_DEVICES"]:
                        devices.append(os.path.join('/dev', device_name))
    except FileNotFoundError:
        logging.error("/proc/partitions not found. This script is likely not running on Linux.")
    except Exception as e:
        logging.error(f"Error reading /proc/partitions: {e}")
    return devices

def wipe_device(device_path):
    """
    Wipes a given block device. Uses blkdiscard for SSDs and shred for HDDs.
    """
    try:
        # Check if the device is a rotational disk (HDD) or not (SSD/NVMe)
        is_rotational_path = f'/sys/block/{os.path.basename(device_path)}/queue/rotational'
        with open(is_rotational_path, 'r') as f:
            is_rotational = f.read().strip() == '1'

        # Unmount any mounted partitions on the device before wiping
        logging.info(f"Unmounting all partitions on {device_path}...")
        # Using a glob pattern to unmount all partitions, e.g., /dev/sdb*
        subprocess.run(["umount", f"{device_path}*"], check=False, stderr=subprocess.DEVNULL)

        if not is_rotational:
            logging.info(f"Detected SSD ({device_path}). Wiping with blkdiscard...")
            # Use blkdiscard for SSDs as it's faster and better for the drive's health
            command = ['blkdiscard', '-f', device_path]
            process = subprocess.run(command, check=True, capture_output=True, text=True)
            logging.info(f"Successfully wiped {device_path}.")
        else:
            logging.info(f"Detected HDD ({device_path}). Wiping with shred...")
            # Use shred for HDDs
            command = ['shred', '-v', '-n', str(CONFIG["SHRED_PASSES"]), '-z', device_path]
            process = subprocess.run(command, check=True, capture_output=True, text=True)
            logging.info(f"Successfully wiped {device_path}.")

    except FileNotFoundError:
        logging.warning(f"Could not determine disk type for {device_path}. It may have been disconnected.")
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to wipe {device_path}. Return code: {e.returncode}")
        logging.error(f"Stderr: {e.stderr}")
    except Exception as e:
        logging.error(f"An unexpected error occurred while wiping {device_path}: {e}")

def main():
    """
    Main loop to monitor for and wipe new block devices.
    """
    logging.info("DangerousDan drive wiper started. Monitoring for new devices...")
    logging.warning("This script is DESTRUCTIVE. Use with extreme caution.")
    if CONFIG["EXCLUDED_DEVICES"]:
        logging.info(f"Excluding devices: {', '.join(CONFIG['EXCLUDED_DEVICES'])}")

    known_devices = set(get_block_devices())
    logging.info(f"Initial devices detected: {', '.join(known_devices) or 'None'}")

    while True:
        current_devices = set(get_block_devices())
        new_devices = current_devices - known_devices

        for device in new_devices:
            logging.info(f"New device detected: {device}")
            wipe_device(device)

        known_devices = current_devices
        time.sleep(CONFIG["POLL_INTERVAL_SECONDS"])

if __name__ == "__main__":
    main()
