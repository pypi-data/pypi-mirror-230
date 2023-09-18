import argparse
import json
from lxml import etree
from .netUtils import requestPost, requestGet


class GeneSetScraper:
    def __init__(self, base_url, search_url, gene_set_name, 
                 json_file_name='data.json',
                 ensembl_file_name='ensembl_texts.txt'):
        self.base_url = base_url
        self.search_url = search_url
        self.gene_set_name = gene_set_name
        self.json_file_name = json_file_name
        self.ensembl_file_name = ensembl_file_name

    def get_gene_set_links(self):
        data = {'geneSetName': self.gene_set_name, 'Search': "Search"}
        response = requestPost(self.search_url, Data=data)
        html_tree = etree.HTML(response.text)
        content_navs = html_tree.xpath(
            '//div[@id="contentwrapper"]/div[@id="content_navs"]')[0]
        td_table = content_navs.xpath(
            './/td[@class="body"]//table[@class="lists2 human"]')[0]
        tr_table = td_table.xpath('.//tr')
        return {link.text: f"{self.base_url}{link.get('href')}" for row in tr_table for cell in row.xpath('.//td') for link in cell.xpath('.//a')}

    def parse_gene_info(self, gene_set_links):
        data_list = []
        seen_ids = set()
        for GeneSetUrl in gene_set_links.values():
            response = requestGet(GeneSetUrl)
            html_tree = etree.HTML(response.text)
            rows = html_tree.xpath('//div[@id="geneListing"]//tr')[1:]
            for row in rows:
                if 'unmapped' in row.attrib.get('class', ''):
                    continue
                id_values = row.xpath('.//td[1]/text()')
                if not id_values:
                    continue
                id_value = id_values[0]
                if id_value in seen_ids:
                    continue
                seen_ids.add(id_value)
                row_data = {
                    'id': id_value,
                    'ncbi': {'link': row.xpath('./td[2]/a/@href')[0], 'text': row.xpath('./td[2]/a/text()')[0]},
                    'ensembl': {'link': row.xpath('./td[3]/a/@href')[0], 'text': row.xpath('./td[3]/a/text()')[0]},
                    'description': row.xpath('./td[4]/text()')[0]
                }
                data_list.append(row_data)
        return data_list

    def save_data_to_json(self, data_list):
        with open(self.json_file_name, 'w') as file:
            json.dump(data_list, file, indent=4)

    def extract_ensembl_texts(self, data_list):
        ensembl_texts = [item['ensembl']['text'] for item in data_list]
        ensembl_texts = list(set(ensembl_texts))
        return ensembl_texts

    def save_ensembl_texts(self, ensembl_texts):
        with open(self.ensembl_file_name, 'w') as file:
            file.write('\n'.join(ensembl_texts))

    def scrape(self):
        gene_set_links = self.get_gene_set_links()
        if len(gene_set_links) > 100:
            print(
                "查询到的相关基因集过多（>100）请前往https://www.gsea-msigdb.org/gsea/msigdb/human/genesets.jsp检测关键词手动查询后再尝试。")
        data_list = self.parse_gene_info(gene_set_links)
        self.save_data_to_json(data_list)
        ensembl_texts = self.extract_ensembl_texts(data_list)
        self.save_ensembl_texts(ensembl_texts)
        return data_list, ensembl_texts


def main():
    parser = argparse.ArgumentParser(description='Scrape gene sets.')
    parser.add_argument("-by", '--base_url', default="https://www.gsea-msigdb.org/gsea/",
                        help='Base URL for gene sets.')
    parser.add_argument("-su", '--search_url', default="https://www.gsea-msigdb.org/gsea/msigdb/human/genesets.jsp",
                        help='Search URL for gene sets.')
    parser.add_argument("-gsn", '--gene_set_name', required=True,
                        help='Name of the gene set to scrape.')
    parser.add_argument("-jfn", '--json_file_name', default='data.json',
                        help='Output file name for JSON data (default: data.json).')
    parser.add_argument("-efn", '--ensembl_file_name', default='ensembl_texts.txt',
                        help='Output file name for Ensembl texts (default: ensembl_texts.txt).')
    args = parser.parse_args()
    base_url = args.base_url
    search_url = args.search_url
    gene_set_name = args.gene_set_name
    json_file_name = args.json_file_name
    ensembl_file_name = args.ensembl_file_name
    scraper = GeneSetScraper(
        base_url, search_url, gene_set_name, json_file_name, ensembl_file_name)
    scraper.scrape()
