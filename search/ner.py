import nltk
import csv
from database import load_people


def extract_keywords(text):
    keywords = []
    tokens = nltk.word_tokenize(text)
    pos_tags = nltk.pos_tag(tokens)
    chunks = nltk.ne_chunk(pos_tags, binary=True)
    for chunk in chunks:
        if isinstance(chunk, nltk.tree.Tree):
            if chunk.label() == 'NE':
                keyword = ' '.join(word for word, _ in chunk.leaves())
                keywords.append(keyword)
    return keywords

if __name__ == '__main__':

    from progressbar import ProgressBar, Bar, ETA, Percentage, Counter
    from itertools import islice
    with open("keywords.tsv", "wb") as fp:
        writer = csv.writer(fp, delimiter='\t')
        people = load_people()
        bar = ProgressBar(widgets=[Counter(), ' ', Percentage(), ' ', Bar(), ' ', ETA()], maxval=len(people))
        bar.start()
        for index, person in enumerate(islice(people, 0, None)):
            xeac_id = person.xeac_id
            for fact in person.facts:
                keywords = []
                keywords = extract_keywords(fact)
                for keyword in keywords:
                    try:
                        writer.writerow((xeac_id, keyword))
                    except UnicodeEncodeError:
                        continue
            bar.update(index)
        bar.finish()
