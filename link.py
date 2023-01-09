import pandas as pd
from argparse import ArgumentParser
from tqdm import tqdm
from thefuzz import process, fuzz
import tldextract
from loguru import logger

logger.add("out.log", rotation="500 MB")


def link_mbfc(input_publishers: str, input_mbfc, output_file: str):
    input_publishers = pd.read_csv(input_publishers, sep=',')
    mbfc_publishers = pd.read_csv(input_mbfc, sep=',').dropna(subset=['website'])

    publisher_mbfc_linking = []
    for _, row in tqdm(input_publishers.iterrows(), total=input_publishers.shape[0]):
        candidate_match, score = \
            process.extract(row['source_name'], mbfc_publishers['website'].tolist(), scorer=fuzz.token_set_ratio,
                            limit=1)[
                0]
        if score > 90:
            mbfc_data = mbfc_publishers[mbfc_publishers['website'] == candidate_match]
            publisher_mbfc_linking.append(
                {'name': mbfc_data['name'].values[0],
                 'source_name': row['source_name'],
                 'label': mbfc_data['label'].values[0]
                 })
        else:
            logger.warning(f"{row['source_name']} could not link with MBFC.")

    pd.DataFrame(publisher_mbfc_linking).to_csv(output_file, sep=',', index=False)


if __name__ == '__main__':
    argparse = ArgumentParser()
    argparse.add_argument('--input_data', default='publishers.csv', help="input data that will be processed")
    argparse.add_argument('--input_ref', default='mbfc_labels.csv', help="reference input")
    argparse.add_argument('--link', choices=['mbfc'])
    argparse.add_argument('--output', type=str)

    args = argparse.parse_args()

    if args.link == "mbfc":
        link_mbfc(input_publishers=args.input_data, input_mbfc=args.input_ref, output_file=args.output)
