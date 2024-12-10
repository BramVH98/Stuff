import pandas as pd
import pynetbox
import logging

# --- Configuration ---
NETBOX_URL = 'http://<ip-address>:8000'  # Replace with your NetBox URL
API_TOKEN = 'd6f4e314a5b5fefd164995169f28ae32d987704f'  # Replace with your API token
EXCEL_FILE = 'environment_data.xlsx'  # Replace with your Excel file path

# --- Logging Configuration ---
logging.basicConfig(filename="import.log", level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialize NetBox API ---
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)

# --- Load Data from Excel ---
df = pd.read_excel(EXCEL_FILE)

# --- Function to Fetch Related Object IDs ---
def get_object_id(resource, name):
    """
    Fetches the ID of an object in NetBox by name.
    Args:
        resource: NetBox API resource (e.g., nb.dcim.device_types)
        name: Name of the object to find
    Returns:
        The object ID if found, otherwise None
    """
    obj = resource.get(name=name)
    if obj:
        return obj.id
    else:
        logging.warning(f"{resource.name.capitalize()} '{name}' not found.")
        return None

# --- Add Devices to NetBox ---
def add_devices(dataframe):
    """
    Adds devices to NetBox from a pandas DataFrame.
    Args:
        dataframe: DataFrame containing device information
    """
    for _, row in dataframe.iterrows():
        try:
            # Fetch related object IDs
            device_type_id = get_object_id(nb.dcim.device_types, row["device_type"])
            site_id = get_object_id(nb.dcim.sites, row["site"])
            device_role_id = get_object_id(nb.dcim.device_roles, row["device_role"])

            # Skip if any required IDs are missing
            if not all([device_type_id, site_id, device_role_id]):
                logging.error(f"Skipping device {row['hostname']} due to missing IDs.")
                continue

            # Prepare payload
            payload = {
                "name": row["hostname"],
                "device_type": device_type_id,
                "device_role": device_role_id,
                "site": site_id,
                "status": "active",  # Default status
                "custom_fields": {
                    "memory": row.get("memory_gb", None),
                    "cpu": row.get("cpu_cores", None),
                },
            }

            # Add device to NetBox
            device = nb.dcim.devices.create(payload)
            if device:
                logging.info(f"Successfully added device: {row['hostname']}")
            else:
                logging.error(f"Failed to add device: {row['hostname']}")
        except Exception as e:
            logging.error(f"Error adding device {row['hostname']}: {e}")

# --- Execute the Import ---
add_devices(df)

print("Import completed. Check 'import.log' for details.")
