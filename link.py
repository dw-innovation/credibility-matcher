import pandas as pd
from argparse import ArgumentParser
from tqdm import tqdm
from thefuzz import process, fuzz
import tldextract
from loguru import logger
from external_apis import entity_linker

logger.add("out.log", rotation="500 MB")


def link_mbfc(input_data: str, input_ref, output_file: str):
    input_data = pd.read_csv(input_data, sep=',')
    mbfc_publishers = pd.read_csv(input_ref, sep=',').dropna(subset=['website'])

    publisher_mbfc_linking = []
    for _, row in tqdm(input_data.iterrows(), total=input_data.shape[0]):
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


def link_wiki_like(input_data: str, output_file: str):
    '''
    it links to the knowledge graphs: Wikidata, wikipedia and dbpedia if they have an entity
    '''
    input_data = pd.read_csv(input_data, sep=',')
    publisher_kg_matches = []
    for _, row in tqdm(input_data.iterrows(), total=input_data.shape[0]):
        linked_doc = entity_linker(row['source_name'])
        publisher_kg_matches.append({
            "source_name": row['source_name'],
            "dp": linked_doc.get("dp", None) if linked_doc else None,
            "wd": linked_doc.get("wd", None) if linked_doc else None,
            "wp": linked_doc.get("wp", None) if linked_doc else None,
            "name": linked_doc.get("label", None) if linked_doc else None,

        })

    pd.DataFrame(publisher_kg_matches).to_csv(output_file, sep=',', index=False)


if __name__ == '__main__':
    argparse = ArgumentParser()
    argparse.add_argument('--input_data', default='publishers.csv', help="input data that will be processed")
    argparse.add_argument('--input_ref', default='mbfc_labels.csv', help="reference input")
    argparse.add_argument('--type', choices=['mbfc', 'wiki-like'])
    argparse.add_argument('--output', type=str)

    args = argparse.parse_args()

    if args.type == "mbfc":
        link_mbfc(input_data=args.input_data, input_ref=args.input_ref, output_file=args.output)

    if args.type == "wiki-like":
        link_wiki_like(input_data=args.input_data, output_file=args.output)
