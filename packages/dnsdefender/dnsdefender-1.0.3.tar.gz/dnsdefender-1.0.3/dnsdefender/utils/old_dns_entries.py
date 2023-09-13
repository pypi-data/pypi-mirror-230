def update_old_dns_entries(filename, dns_records):
  with open(filename, 'w') as file:
      for entry in dns_records:
          line = f"type: {entry['type']}, name: {entry['name']}, records: {', '.join(entry['records'])}, source: {entry['source']}, zone_name: {entry['zone_name']}\n"
          file.write(line)

def get_old_dns_entries(filename):
  entries = []
  with open(filename, 'r') as file:
      for line in file:
          entry = {}
          line = line.strip()
          line = line.split(",")
          for field in line:
            field = field.strip()
            field = field.split(":")
            entry[field[0].strip()] = ':'.join(field[1:]).strip()
          entry["records"] = [entry["records"]]
          entries.append(entry)
  return entries