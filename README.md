# Media Bias/Fact Check 

Media Bias/Fact Check ([MBFC](https://mediabiasfactcheck.com)) is a website by editor Dave M. Van Zandt for scoring publishers in terms of bias and factuality.

This repository contains a script for constucting a dataset of publisher-MBFC labels. The user should save the html files from the website, and then execute the script.

Set up a python environment and install the required libraries: 

``` shell
pip install -r requirements.txt
``` 

Execute the following command to get the labels: 

``` shell
python -m export_labels --output mbfc_labels.csv --input html_files >> result.out
``` 