import pandas as pd
import pynetbox

# Configure NetBox API
NETBOX_URL = "http://your-netbox-instance.com"
NETBOX_TOKEN = "your-netbox-api-token"

# Connect to NetBox
nb = pynetbox.api(NETBOX_URL, token=NETBOX_TOKEN)

# Load Excel File
file_path = "path_to_your_excel_file.xlsx"
data = pd.read_excel(file_path)

# Iterate Over Each Row and Add to NetBox
for index, row in data.iterrows():
    try:
        # Extract data from the row
        hostname = row['Hostname']
        project = row['PROJECT']
        location = row['Location']
        os = row['OS']
        os_version = row['OS_Version']
        cpus = row['CPUs']
        memory_mb = row['Memory_MB']
        disk1_gb = row['DISK1_GB']

        # Create or retrieve the site (example)
        site = nb.dcim.sites.get(name=location)
        if not site:
            site = nb.dcim.sites.create(name=location, slug=location.lower().replace(" ", "-"))

        # Create or retrieve the device
        device = nb.dcim.devices.get(name=hostname)
        if not device:
            device = nb.dcim.devices.create(
                name=hostname,
                device_type={'name': 'Default'},  # Adjust device type as needed
                device_role={'name': 'Server'},  # Adjust device role as needed
                site=site.id,
            )

        # Add custom attributes or tags as needed
        device.custom_fields.update({
            'Project': project,
            'OS': os,
            'OS Version': os_version,
            'CPUs': cpus,
            'Memory (MB)': memory_mb,
            'Disk1 (GB)': disk1_gb,
        })
        device.save()
        
        print(f"Processed: {hostname}")

    except Exception as e:
        print(f"Error processing row {index + 1}: {e}")
