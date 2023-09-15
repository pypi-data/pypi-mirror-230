import os

import pandas as pd

################################################################
# data_licenses

dir_name = os.path.dirname(__file__)
licenses = pd.read_csv(os.path.join(dir_name, "licenses.csv"))
licences_data_or_software = licenses[licenses["domain_data"] | licenses["domain_software"]]
licenses = licenses[["id", "title"]]
licenses = [(d[1]["id"].lower(), d[1]["title"]) for d in licenses.iterrows()]
licences_data_or_software = licences_data_or_software[["id", "title"]]
licences_data_or_software = [(d[1]["id"].lower(), d[1]["title"]) for d in licences_data_or_software.iterrows()]

################################################################
# languages

dir_name = os.path.dirname(__file__)
lang = pd.read_csv(os.path.join(dir_name, "languages-iso-639-2.csv"))
lang["ISO 639-1 Code"] = lang["ISO 639-1 Code"].apply(lambda x: x.strip())
lang = lang[lang["ISO 639-1 Code"] != ""]
lang = lang[["ISO 639-2 Code", "English name of Language"]]
lang = [(d[1]["ISO 639-2 Code"].lower(), d[1]["English name of Language"]) for d in lang.iterrows()]
################################################################
