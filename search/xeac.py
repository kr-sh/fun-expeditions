import requests
import time
import re
import os
import glob
from xml.etree import ElementTree


NAMESPACES = {'xeac': 'http://www.w3.org/2005/Atom'}


def get_all_xeac_ids():
    url = 'http://data.library.amnh.org:8082/orbeon/xeac/feed/?q=*:*&start={}'
    for start in [0, 100]:
        response = requests.get(url.format(start)).content
        tree = ElementTree.fromstring(response)
        for entry in tree.findall('xeac:entry', NAMESPACES):
            yield entry.find('xeac:id', NAMESPACES).text


def is_downloaded(xeac_id):
    return os.path.exists('data/{}.xml'.format(xeac_id))


def get_outbound_links(xeac_id):
    with open('data/{}.xml'.format(xeac_id)) as fp:
        try:
            tree = ElementTree.fromstring(fp.read())
            namespace = {'xeac': re.match('\{.*\}', tree.tag).group(0).strip('{}')}
            description = tree.find('xeac:cpfDescription', namespace)
            for relation in description.find('xeac:relations', namespace):
                if '{http://www.w3.org/1999/xlink}href' in relation.attrib:
                    relation_id = relation.attrib['{http://www.w3.org/1999/xlink}href']
                    if relation_id.startswith('amnh'):
                        for chunk in relation_id.split(';'):
                            yield chunk.strip()
        except:
            pass


def download(xeac_id):
    url = 'http://data.library.amnh.org:8082/orbeon/xeac/id/{}.xml'.format(xeac_id)
    response = requests.get(url).content
    with open('data/{}.xml'.format(xeac_id), 'wb') as fp:
        fp.write(response)
    return response


def main():
    for index, xeac_id in enumerate(get_all_xeac_ids()):
        download(xeac_id)
        time.sleep(1)
        print index, xeac_id


def crawl(estimate=False):
    todo = set()
    for filename in glob.glob('data/*.xml'):
        xeac_id = filename.split('/')[-1].split('.')[0]
        for relation_id in get_outbound_links(xeac_id):
            if not is_downloaded(relation_id):
                todo.add(relation_id)
    print 'Downloading {} entries'.format(len(todo))
    if not estimate:
        for index, relation_id in enumerate(todo):
            download(relation_id)
            time.sleep(1)
            print index, relation_id


def clean():
    for filename in glob.glob('data/*.xml'):
        with open(filename) as fp:
            data = fp.read()
            if 'Page Not Found' in data:
                os.unlink(filename)


if __name__ == '__main__':
    clean()
