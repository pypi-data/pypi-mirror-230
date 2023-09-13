# AlphaFetcher

`AlphaFetcher` facilitates fetching and downloading protein metadata and related files from the 
[AlphaFold Protein Structure Database](https://alphafold.ebi.ac.uk/) 
using Uniprot access codes.

---

## 🌟 Features

- **Batch Import**: Input single or multiple Uniprot access codes seamlessly.
  
- **Parallel Processing**: Efficiently fetch metadata using multithreading.
  
- **Flexible Downloads**: Choose among various file types - PDB, CIF, BCIF, PAE image, and PAE data files.
  
- **Optimal Performance**: Easily adjust the number of workers for threaded tasks.

---

## 🔧 Installation

We recommend PyPI installation:

```bash
pip install alphafetcher
```

---

## 💡 Usage

```python
from alphafetcher import AlphaFetcher

# Instantiate the fetcher
fetcher = AlphaFetcher()

# Add desired Uniprot access codes
fetcher.add_proteins(["A1KXE4", "H0YL14", "B2RXH2", "A8MVW5"])

# Retrieve metadata
fetcher.fetch_metadata(multithread=True, workers=4)

# Commence download of specified files
fetcher.download_all_files(pdb=True, cif=True, multithread=True, workers=4)
```

---

## 📜 Documentation

### Methods

- **`add_proteins(proteins: Union[str, List[str]])`**
  - *Description*: Add the provided Uniprot access codes for fetching. A single string or a list of strings are 
    accepted. 

- **`fetch_metadata(multithread: bool = False, workers: int = 10)`**
  - *Description*: Extracts metadata corresponding to the supplied Uniprot access codes. This metadata is used to 
    download the relevant files and is stored in ```fetcher.metadata_dict```, assuming the notation of the example
    above is followed.
  
- **`download_all_files(uniprot_access: str, pdb: bool = False, cif: bool = False, bcif: bool = False, 
  pae_image:bool = False, pae_data: bool = False)`**
  - *Description*: Initiates download for the specified file types linked to the given Uniprot codes.
  - Specify the types of files to be downloaded by changing the values of their parameters to True.

*For a comprehensive guide, users are encouraged to view the docstrings incorporated within the source code.*

---

## ⚠️ Limitations

Always respect the AlphaFold Protein Structure Database terms of service, ensuring not to flood it with excessive 
concurrent requests. Consider adjusting the number of workers to reduce the requests density. 

---

## 🙌 Contributing

We welcome your contributions! To collaborate:
1. Fork this repository.
2. Commit your changes.
3. Open a pull request with your updates.

---

## 📖 Authors and Acknowledgment

- **Jose Gavalda-Garcia** - *Author* - [jose.gavalda.garcia@vub.be](mailto:jose.gavalda.garcia@vub.be)
- **Wim Vranken** - *Supervisor* - [wim.vranken@vub.be](mailto:wim.vranken@vub.be)

---

## 📄 License

This project is licensed under the [GNU General Public License v3 (GPLv3)](https://www.gnu.org/licenses/gpl-3.0.en.html).
