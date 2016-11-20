import glob
import re
from xml.etree import ElementTree

NAMESPACES = {'xeac': 'urn:isbn:1-931666-33-4'}


class Expedition(object):

    def __init__(self, xeac_id, name, purpose, history, place, date, note):
        self.xeac_id = xeac_id
        self.name = name
        self.purpose = purpose
        self.history = history
        self.place = place
        self.date = date
        self.note = note

    @staticmethod
    def build(xeac_id, content):
        identity = content.find('xeac:identity', NAMESPACES)
        name = identity.find('xeac:nameEntry', NAMESPACES)[0].text
        description = content.find('xeac:description', NAMESPACES)
        purpose = None
        history = None
        place = None
        date = None
        note = None
        if description is not None:
            history = description.find('xeac:biogHist', NAMESPACES)
            history = [fact.text for fact in history]
            purpose = history[0]
            history.pop(0)
            place = description.find('xeac:place', NAMESPACES)
            if place is not None:
                place = place.find('xeac:placeEntry', NAMESPACES).text
            period = description.find('xeac:existDates', NAMESPACES)
            date = period.find('xeac:date', NAMESPACES)
            if date is not None:
                date = date.text
            date_range = period.find('xeac:dateRange', NAMESPACES)
            if date_range is not None:
                start = date_range.find('xeac:fromDate', NAMESPACES).text
                end = date_range.find('xeac:toDate', NAMESPACES).text
                date = '{} - {}'.format(start, end)
            date_set = period.find('xeac:dateSet', NAMESPACES)
            if date_set is not None:
                dates = [date.text for date in date_set if date.text.isdigit()]
                date = ', '.join(dates)
            note = period.find('xeac:descriptiveNote', NAMESPACES)
            if note is not None:
                note = note.text
        return Expedition(xeac_id, name, purpose, history, place, date, note)


class Person(object):

    def __init__(self, xeac_id, name, gender, facts, birth, death, occupations, languages, relevant_places, links):
        self.xeac_id = xeac_id
        self.name = name
        self.gender = gender
        self.facts = facts
        self.birth = birth
        self.death = death
        self.occupations = occupations
        self.languages = languages
        self.relevant_places = relevant_places
        self.links = links

    def __repr__(self):
        return self.name

    def json(self):
        return {
            'xeac_id': self.xeac_id,
            'name': self.name,
            'gender': self.gender,
            'facts': self.facts,
            'birth': self.birth,
            'death': self.death,
            'occupations': self.occupations,
            'languages': self.languages,
            'places': self.relevant_places
        }

    @staticmethod
    def build(xeac_id, content):
        identity = content.find('xeac:identity', NAMESPACES)
        description = content.find('xeac:description', NAMESPACES)
        description = Person.parse_description(description)
        relations = content.find('xeac:relations', NAMESPACES)
        links = []
        if relations is not None:
            for relation in relations:
                link = relation.attrib.get('{http://www.w3.org/1999/xlink}href', '')
                if link.startswith('amnh'):
                    links.append(link)
        # Name
        name = Person.build_name(identity)
        # Gender
        gender = None
        if 'localDescription' in description:
            gender = description['localDescription'].find('xeac:term', NAMESPACES).text
        # Facts
        facts = []
        if 'biogHist' in description:
            facts = [' '.join(fact.text.split()).strip() for fact in description['biogHist'] if fact.text is not None]
        # Dates
        birth, death = None, None
        if 'existDates' in description:
            dates = description['existDates'].find('xeac:dateRange', NAMESPACES)
            if dates is not None:
	        birth = re.match("\d*", dates.find('xeac:fromDate', NAMESPACES).text).group(0)
                death = re.match("\d*", dates.find('xeac:toDate', NAMESPACES).text).group(0)
        # Occupations
        occupations = []
        if 'occupations' in description:
            for occupation in description['occupations']:
                occupation_title = occupation.find('xeac:term')
                if occupation_title is not None:
                    occupation_title = occupation_title.text
                start = None
                end = None
                date_range = occupation.find('dateRange')
                if date_range is not None:
                    start = date_range.find('xeac:fromDate', NAMESPACES).text
                    end = date_range.find('xeac:toDate', NAMESPACES).text
                occupations.append((occupation_title, start, end))
        # Languages
        languages = []
        if 'languagesUsed' in description:
            for language in description['languagesUsed']:
                languages.append(language.find('xeac:language', NAMESPACES).text)
        # Places
        relevant_places = []
        if 'places' in description:
            places = description['places']
            for place in places:
                parsed_place = {}
                for place_info in place:
                    tag = place_info.tag.replace('{urn:isbn:1-931666-33-4}', '')
                    parsed_place[tag] = place_info
                if len(parsed_place) > 0:
                    place_role = parsed_place.get('placeRole', None)
                    if place_role is not None:
                        place_role = place_role.text
                    place_name = ' '.join(parsed_place['placeEntry'].text.split())
                    place_note = parsed_place.get('descriptiveNote')
                    if place_note is not None:
                        place_note = ' '.join(place_note.find('xeac:p', NAMESPACES).text.split())
                    place_date = parsed_place.get('date', None)
                    if place_date is not None:
                        place_date = place_date.text
                    place_range = parsed_place.get('dateRange', None)
                    place_start = None
                    place_end = None
                    if place_range is not None:
                        place_start = place_range.find('xeac:fromDate', NAMESPACES).text
                        place_end = place_range.find('xeac:toDate', NAMESPACES).text
                    relevant_places.append((place_role, place_name, place_note, place_date, place_start, place_end))
        return Person(xeac_id, name, gender, facts, birth, death, occupations, languages, relevant_places, links)

    @staticmethod
    def parse_description(description):
        data = {}
        for part in description:
            key = part.tag.replace('{urn:isbn:1-931666-33-4}', '')
            data[key] = part
        return data

    # noinspection PyUnresolvedReferences
    @staticmethod
    def build_name(identity):
        names = identity.findall('xeac:nameEntry', NAMESPACES)
        chosen_name = None
        for name in names:
            name_info = {'parts': []}
            for chunk in name:
                if chunk.tag == '{urn:isbn:1-931666-33-4}part':
                    if 'localType' in chunk.attrib:
                        name_info[chunk.attrib['localType']] = chunk.text
                    else:
                        name_info['parts'].append(chunk.text)
                elif chunk.tag == '{urn:isbn:1-931666-33-4}authorizedForm':
                    name_info['standard'] = chunk.text
            if 'forename' in name_info and 'surname' in name_info:
                forename = name_info['forename']
                surname = name_info['surname']
                expansion = None
                if 'nameExpansion' in name_info:
                    expansion = name_info['nameExpansion']
                candidate = '{} {}'.format(forename, surname).replace(',', '').strip()
                if expansion is not None:
                    expanded = expansion.strip('( )')
                    surname = candidate.split(' ')[-1]
                    candidate = '{} {}'.format(expanded, surname)
                chosen_name = candidate.title()
            elif name_info.get('standard', None) == 'amnhopac':
                if len(name_info['parts']) > 0:
                    parts = name_info['parts']
                    parts = map(Person.parse_name, parts)
                    draft = parts[0]
                    expansion = None
                    for part in parts:
                        if '(' in part:
                            expansion = part
                    if expansion is not None:
                        expanded = expansion.strip('( )')
                        surname = draft.split(' ')[-1]
                        chosen_name = '{} {}'.format(expanded, surname)
                    else:
                        chosen_name = draft
            elif 'name' in name_info:
                chosen_name = name_info['name'].strip(', ')
            else:
                chunks = name_info['parts'][0].split(',')
                chunks.reverse()
                chunks = map(lambda c: c.strip(), chunks)
                chosen_name = ' '.join(chunks).strip()
        return chosen_name

    @staticmethod
    def parse_name(name):
        return ' '.join(reversed(map(lambda n: n.strip(), name.split(',')))).strip()


def load_keywords():
    import csv
    from collections import defaultdict
    keywords = defaultdict(set)
    with open("keywords.tsv") as fp:
        reader = csv.reader(fp, delimiter='\t')
        for xeac_id, keyword in reader:
            keywords[keyword].add(xeac_id)
    return keywords


def load_people():
    people = {}
    for index, filename in enumerate(glob.glob('data/*.xml')):
        with open(filename) as fp:
            tree = ElementTree.fromstring(fp.read())
            xeac_id = tree.find('xeac:control', NAMESPACES).find('xeac:recordId', NAMESPACES).text
            content = tree.find('xeac:cpfDescription', NAMESPACES)
	    entity_type = content.find('xeac:identity', NAMESPACES).find('xeac:entityType', NAMESPACES).text
            if entity_type == 'person':
		person = Person.build(xeac_id, content)
		people[xeac_id] = person
    return people


def load_expeditions():
    expeditions = {}
    for index, filename in enumerate(glob.glob('data/amnhc_2*.xml')):
        with open(filename) as fp:
            tree = ElementTree.fromstring(fp.read())
            xeac_id = tree.find('xeac:control', NAMESPACES).find('xeac:recordId', NAMESPACES).text
            content = tree.find('xeac:cpfDescription', NAMESPACES)
            entity_type = content.find('xeac:identity', NAMESPACES).find('xeac:entityType', NAMESPACES).text
            if entity_type == 'corporateBody':
                expedition = Expedition.build(xeac_id, content)
                expeditions[xeac_id] = expedition
    return expeditions


if __name__ == '__main__':
    load_people()
