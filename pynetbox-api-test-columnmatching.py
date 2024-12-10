import pandas as pd
import pynetbox
import logging

# --- Configuration ---
NETBOX_URL = 'http://<ip-address>:8000'  # Replace with your NetBox URL
API_TOKEN = 'd6f4e314a5b5fefd164995169f28ae32d987704f'  # Replace with your API token
EXCEL_FILE = 'your_excel_file.xlsx'  # Path to your existing Excel file

# --- Logging Configuration ---
logging.basicConfig(filename="import.log", level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialize NetBox API ---
nb = pynetbox.api(NETBOX_URL, token=API_TOKEN)

# --- Load Data from Excel ---
df = pd.read_excel(EXCEL_FILE)

# --- Define Column Mapping ---
COLUMN_MAPPING = {
    "Hostname": "name",
    "Compute_Profile": "device_type",
    "Environment": "device_role",
    "Location": "site",
    "CPUs": "cpu_count",
    "Memory_GB": "memory_gb",
    "DISK1_GB": "disk1_gb",
}

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
def add_devices(dataframe, column_mapping):
    """
    Adds devices to NetBox from a pandas DataFrame using column mapping.
    Args:
        dataframe: DataFrame containing device information
        column_mapping: Dictionary mapping Excel column names to NetBox fields
    """
    for _, row in dataframe.iterrows():
        try:
            # Fetch related object IDs
            device_type_id = get_object_id(nb.dcim.device_types, row[column_mapping["Compute_Profile"]])
            site_id = get_object_id(nb.dcim.sites, row[column_mapping["Location"]])
            device_role_id = get_object_id(nb.dcim.device_roles, row[column_mapping["Environment"]])

            # Skip if any required IDs are missing
            if not all([device_type_id, site_id, device_role_id]):
                logging.error(f"Skipping device {row[column_mapping['Hostname']]} due to missing IDs.")
                continue

            # Prepare payload
            payload = {
                "name": row[column_mapping["Hostname"]],
                "device_type": device_type_id,
                "device_role": device_role_id,
                "site": site_id,
                "status": "active",  # Default status
                "custom_fields": {
                    "cpu_count": row.get(column_mapping.get("CPUs", ""), None),
                    "memory_gb": row.get(column_mapping.get("Memory_GB", ""), None),
                    "disk1_gb": row.get(column_mapping.get("DISK1_GB", ""), None),
                    # Add other custom fields as needed
                },
            }

            # Add device to NetBox
            device = nb.dcim.devices.create(payload)
            if device:
                logging.info(f"Successfully added device: {row[column_mapping['Hostname']]}")
            else:
                logging.error(f"Failed to add device: {row[column_mapping['Hostname']]}")
        except Exception as e:
            logging.error(f"Error adding device {row[column_mapping['Hostname']]}: {e}")

# --- Execute the Import ---
add_devices(df, COLUMN_MAPPING)

print("Import completed. Check 'import.log' for details.")
