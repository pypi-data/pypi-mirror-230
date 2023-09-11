# 🐣 GPT Data Dictionary

## Introduction

As a Senior Staff Spreadsheet Engineer, you understand the challenges of dealing with ambiguously and poorly defined data. The GPT Data Dictionary aims to alleviate this pain point by automating the creation of comprehensive and understandable data dictionaries.

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Them: Can you just quickly pull this data for me?<br><br>Me: Sure, let me just: <br><br>SELECT * FROM some_ideal_clean_and_pristine.table_that_you_think_exists</p>&mdash; Seth Rosen (@sethrosen) <a href="https://twitter.com/sethrosen/status/1252291581320757249?ref_src=twsrc%5Etfw">April 20, 2020</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

## What is a Data Dictionary?

A data dictionary is a centralized resource that offers metadata about data elements within a system or project. It outlines key details such as data types, constraints, and definitions, thus facilitating data interpretation and quality assurance. Essentially, a data dictionary is your go-to guide for understanding and managing your data landscape.

## Features

- **Automated Metadata Extraction**: Quickly generate metadata for each column in your dataset, including data types, allowed values, and more.
- **Readable Variable Names**: Utilizes GPT-3.5 to automatically generate human-readable variable names.
- **Quality Indicators**: Provides metadata that can be useful for data quality checks.
- **Extensible**: Easily extendable to include more advanced statistics or custom metadata as required.

## How to Use

1. **Install Dependencies**: Make sure you've installed all required Python packages.
    ```bash
    poetry install
    ```
  
2. **Run the Script**: Execute the main Python script and provide the path to your CSV file.
    ```bash
    poetry run scripts/extract_gpt_data_dictionary.py --csv-file=/path/to/your/csv/file.csv
    ```

3. **Review and Edit**: The generated data dictionary will be saved as a CSV file. Open it to manually enter any domain-specific information that couldn't be automatically generated.

4. **Finalize**: Save your changes to the data dictionary CSV. You can now use this as a comprehensive guide for data understanding and manipulation.

## Example

Running this script for the all famous titanic dataset on Kaggle:

    ```bash
    poetry run scripts/extract_gpt_data_dictionary.py --csv-file=data/titanic_train.csv
    ```

And it will output `gpt_data_dictionary.csv`
![example](assets/Screenshot_2023-09-09_20-06-39.png)

## Contribution

We welcome contributions! Feel free to fork this repository and submit pull requests, or open an issue to discuss what you'd like to add.

## References
- [OSF: How to Make a Data Dictionary](https://help.osf.io/article/217-how-to-make-a-data-dictionary)
- [UC Merced: Data Dictionaries](https://library.ucmerced.edu/data-dictionaries)
- [USGS: Data Dictionaries](https://www.usgs.gov/data-management/data-dictionaries)
