from datetime import datetime

# Aktuelle Zeit im gewünschten Format
timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")

# Beispiel für einen Dateinamen
filename = f"report_{timestamp}.txt"

print(filename)


print()