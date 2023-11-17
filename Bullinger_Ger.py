# ET.fromstring(String) --> element 
# ET.tostring(Element) --> string
# ET.parse(File) --> string
# to get the attribute call get method on the element

#language = s.get('lang')
#if language == 'de' 



import os
import xml.etree.ElementTree as ET
import re

# list with the words and their footnotes:
references_list = []
filtered_dictionary = {}

# the directory where the files are located
directory_path = r"/Users/yasardemirelli/cmd_code/Uni_UZH/WS23:24/Sprachtechnologische_Webapplikationen/Project Bullinger/Bullinger_Letter_Examples"

# iterate through directory and subdirectories
for root, dirs, files in os.walk(directory_path):
    for filename in files:
        # the full file path
        full_path = os.path.join(root, filename)

        # if the file if in the directory
        if os.path.isfile(full_path):
            # the XML file parsing
            try:
                file_tree = ET.parse(full_path)
            except (ET.ParseError, IOError) as e:
                print(f"Error reading/parsing {full_path}: {e}")
                continue  # Skip to the next file

            root_element = file_tree.getroot()

            # iterating over the sentences
            print(full_path)
            for sentence in root_element.findall('.//s'):
                # if the language is German, we are considering those sentences, otherwise --> ignore those:
                if sentence.attrib.get('lang') == 'de':

                    # iterate over the child elements of the sentence
                    for i, child in enumerate(sentence):
                        # if the fl child tag is encountered:
                        if child.tag == 'fl' and child.text.isdigit():
                            # determine the preceding text if this is the first child tag in the sentence
                            if i == 0:
                                preceding_text = sentence.text.strip() if sentence.text else ""
                            # if this is not the first child tag in the sentence, the word before fl tag will be the
                            # last word in the text of the preceding tag
                            else:
                                preceding_text = sentence[i - 1].tail.strip() if sentence[i - 1].tail else ""

                            # the text is split, and the last word is taken
                            words = preceding_text.split()
                            if words:
                                word_before_fl = words[-1]

                            # Extract the number inside <fl>
                            number = child.text

                            # the matching reference gets stored in a table
                            for reference in root_element.findall('.//fn'):
                                if reference.attrib.get('ref') == number and reference.text is not None:
                                    references_list.append((word_before_fl, reference.text, len(reference.text)))

# filtered out the elements where the length of the references is >45:
filtered_references_list = [element for element in references_list if len(element[1]) <= 45]
print(len(filtered_references_list))

# filtered out the references which have many numbers:
filtered_references_list_2 = [element for element in filtered_references_list if not re.search("[0-9]", element[1])]

print(len(filtered_references_list_2))

for element in filtered_references_list_2:
    if element[0] not in filtered_dictionary:
        filtered_dictionary[element[0]] = [element[1]]
    else:
        filtered_dictionary[element[0]].append(element[1])

print(len(filtered_dictionary), filtered_dictionary)
