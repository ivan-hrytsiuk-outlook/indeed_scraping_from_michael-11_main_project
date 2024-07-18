keywords = ["police officer lateral", "police officer basic", "sheriffs deputy", "police recruit", "police officer recruit",
            "sheriffs deputy", "sheriff", "police officer lateral", "police lateral", "deputy sheriff",
            "border patrol", "customs agent", "police officer", "patrol officer", "police officer lateral"]
txt = "["
for keyword in keywords:
    txt += "{"
    txt += '"position": "' + keyword + '",'
    txt += '"datasetId": ""},\n'
txt+="]"
print(txt)
