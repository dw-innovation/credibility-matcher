import re

import pandas as pd
from dataclasses import dataclass
from argparse import ArgumentParser
from pathlib import Path
from bs4 import BeautifulSoup

REGEX_MATCH = r"(\S+\.\S+)"


@dataclass
class Publisher:
    name: str
    website:str = None
    label: str = None


def export_labels(input_folder: str, output_file: str):
    input_folder = Path(input_folder)

    publishers = []
    for fpath in input_folder.rglob('*.html'):
        table = BeautifulSoup(open(fpath, 'r').read()).find('table').find("tbody").find_all("tr")

        label = str(fpath.name).replace('- Media Bias_Fact Check.html', '').strip().lower()

        for row in table:
            cells = row.find_all("td")
            cell_data = cells[0].get_text().strip()

            if not cell_data:
                continue
            matches = re.findall(REGEX_MATCH, cell_data, re.MULTILINE)

            if len(matches) < 1:
                print(f"There is no match for {cell_data}")
                publishers.append(
                    Publisher(name=cell_data, label=label))
            else:
                website = matches[0].replace('(', '').replace(')', '')
                name = cell_data.replace(f'{matches[0]}', '').strip()

                publishers.append(
                    Publisher(name=name,
                              website=website,
                              label=label))

    pd.DataFrame(publishers).to_csv(output_file, index=False)


if __name__ == '__main__':
    argparse = ArgumentParser()
    argparse.add_argument('--input', default='html_files')
    argparse.add_argument('--output', type=str)

    args = argparse.parse_args()

    export_labels(input_folder=args.input, output_file=args.output)
