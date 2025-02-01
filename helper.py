with open("data.json", "rb") as f:
    raw_data = f.read()

with open("data_fixed.json", "w", encoding="utf-8") as f:
    f.write(raw_data.decode("utf-8", errors="ignore"))
