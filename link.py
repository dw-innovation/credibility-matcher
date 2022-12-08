import pandas as pd
from argparse import ArgumentParser
from tqdm import tqdm
from thefuzz import process, fuzz
import tldextract


def link_publishers(input_publishers: str, input_mbfc, output_file: str):
    input_publishers = pd.read_csv(input_publishers, sep=',')
    input_publishers['domain_name'] = input_publishers['domain'].apply(lambda x: tldextract.extract(x).domain)
    mbfc_publishers = pd.read_csv(input_mbfc, sep=',').dropna(subset=['domain'])

    publisher_mbfc_linking = []
    for _, row in tqdm(input_publishers.iterrows(), total=input_publishers.shape[0]):
        candidate_match, score = process.extract(row['domain_name'], mbfc_publishers['domain'].tolist(), scorer=fuzz.token_set_ratio, limit=1)[0]
        if score == 100:
            mbfc_data = mbfc_publishers[mbfc_publishers['domain']==candidate_match]
            publisher_mbfc_linking.append(
                {'name':mbfc_data['name'].values[0],
                 'domain':row['domain'],
                 'label': mbfc_data['label'].values[0]
                 })
    pd.DataFrame(publisher_mbfc_linking).to_csv(output_file, sep=',', index=False)


if __name__ == '__main__':
    argparse = ArgumentParser()
    argparse.add_argument('--input_publishers', default='publishers.csv')
    argparse.add_argument('--input_mbfc', default='mbfc_labels.csv')
    argparse.add_argument('--output', type=str)

    args = argparse.parse_args()

    link_publishers(input_publishers=args.input_publishers, input_mbfc=args.input_mbfc, output_file=args.output)
