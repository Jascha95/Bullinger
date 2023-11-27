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
sort_out = []

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
            #file_tree = ET.parse(full_path) # not parseable sheet == 19_2809_12858.xml 
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
                elif sentence.attrib.get("lang") != "de":
                    for i, child in enumerate(sentence):
                        # if the fl child tag is encountered:
                        #if child.tag == 'fl' and child.text.isdigit():
                        #sort_out.append(child.__repr__())
                        #sort_out.append(child.__str__())
                        sort_out.append(child.text)
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

print(f"sort_out: {sort_out}")

#______________________________________________________________________

def parse_xml_files(directory_path):
    
    """This functions takes the data directory, opens the xml file, parses the element tree, finds the sentences in German
    with the footnotes, checks if the footnote is marked with digit, finds the last word before the footnote (the one which is 
    marked with a footnote), goes down to the references and finds the corresponding reference (excluding those which contain the place names or person names ),
    those are added to the tuple in the list of references"""
    
    references_list = []
    for root, dirs, files in os.walk(directory_path):
        for filename in files:
            full_path = os.path.join(root, filename)
            if os.path.isfile(full_path):
                try:
                    file_tree = ET.parse(full_path)
                except (ET.ParseError, IOError) as e:
                    print(f"Error reading/parsing {full_path}: {e}")
                    continue  # Skip to the next file

                root_element = file_tree.getroot()
                file_tree = ET.parse(full_path)
                root_element = file_tree.getroot()
                for sentence in root_element.findall('.//s'):
                    if sentence.attrib.get('lang') == 'de':
                        for i, child in enumerate(sentence):
                            if child.tag == 'fl' and child.text.isdigit():
                                preceding_text = sentence.text.strip() if i == 0 and sentence.text else sentence[i - 1].tail.strip() if sentence[i - 1].tail else ""
                                words = preceding_text.split()
                                cleaned_words = [word.rstrip('.,:!?;/') for word in words]  # Clean each word
                                if cleaned_words:
                                    word_before_fl = cleaned_words[-1]
                                    number = child.text
                                    for reference in root_element.findall('.//fn'):
                                        for child in reference:
                                        # if the reference doesn't contain place names or person names: 
                                            if not (child.tag == 'placeName' or child.tag == 'persName'):
                                                if reference.attrib.get('ref') == number and reference.text:
                                                    references_list.append((word_before_fl, reference.text))

    return references_list

def filter_references(references_list):
    
    """This function filters the references list and is aimed at finding the lexical footnotes"""
    
    filtered_list = [element for element in references_list if len(element[1]) <= 45 and not re.search("[0-9]", element[1])]
    
    return filtered_list

def build_reference_dictionary(filtered_list):
    
    """This function builds a dictionary with all the unique lexical entities and all their footnotes"""
    
    reference_dictionary = {}
    for word, reference in filtered_list:
        if word not in reference_dictionary:
            reference_dictionary[word] = [reference]
        else:
            reference_dictionary[word].append(reference)
    # we need to filter the values which contain repetative meanings of the lexical items:
    for key in reference_dictionary:
        reference_dictionary[key] = list(set(reference_dictionary[key]))
            
    return reference_dictionary

    
def levenshteinDistance(reference_dictionary): 
        
    """this function will return the list of the words the Levenstein distance for which is smaller than 3"""
    
    list_of_similar_words = []
    
    # creating the list with the unique word pairs from the dictionary:
    word_pairs_list = [("map","cup")]
    
    keys = list(reference_dictionary.keys())
    
    
    for i in range(len(keys)):
        for j in range(i + 1, len(keys)):
            word_pairs_list.append((keys[i], keys[j]))

            
    for element in word_pairs_list:
        word1, word2 = element
        
        # the Levenstein distance dynamic algorithm that computes the distance between two words, taken from: https://www.youtube.com/watch?v=SqDjsZG3Mkc
        m=len(word1)
        n=len(word2)
        table= [[0]*(n+1) for _ in range(m+1)]
        
        for i in range(m+1):
            table[i][0] = i
        for j in range(n+1):
            table[0][j] = j
        
        for i in range (1,m+1):
            for j in range (1, n+1):
                if word1[i-1]== word2[j-1]:
                    table[i][j] = table[i-1][j-1]
                else:
                    table[i][j] = 1+min(table[i-1][j], table[i][j-1], table[i-1][j-1])
        distance = table[-1][-1]
         
        if distance < 3:
            similar_words_tuple = (word1,word2,distance)
            list_of_similar_words.append (similar_words_tuple)
            
        
    
    return list_of_similar_words

def simiar_words_detection (list_of_similar_words):
    
    """Since the lemmatizer for the early German words doesn't exist we apply Levenstein Distance to detect the lexical items which might have the same lemma"""
    #TODO: filter the words which are similar from the list of the similar words
    how_manywords = 0
    similar_in = []
    not_similar = []
    print(f"{120*"#"}")
    for word_pairs in reference_dictionary:#enumerate for editing index 
        how_manywords += 1
        #print(f"{120*"#"}")

        print(word_pairs)
    for similar in reference_dictionary:
        if similar in reference_dictionary:
            similar_in.append(similar)


        elif similar not in reference_dictionary:
            not_similar.append(similar)
        else:
            return f"\n\n\nTheses words {similar} are not in {similar_in} and {not_similar}()\n\n\n"


    print(f"\nThere are {how_manywords} word pairs from reference_dictionary\n")
    print(f"{120*"#"}")
    return list_of_similar_words

    
# 2cnd filter for lexical 
#lexical more than 4 words or reference
# concerne if not online one word is annotatated 
# footnotes are not contain in the files 

#############################################################

"""
to write the script to add the footnotes to words in the documents which were not annotated 
in the same format as the ones we are extracting
then we will have a solid draft for Early German by that time."""

#adding to to the existing files 
def add_footnotes(list_of_similar_words):
    # comparing for footnotes in german for 
    # https://www.bullinger-digital.ch/letter/11256 == 09_1213_11256.xml
    #check existing footnotes 
    #format 
    #write an lookup table for that 
    # <letter lang="de" edition="HBBW" vol="9" fk_bibliography="11" nr="1213" page="30">
    #     <div ref_regest="1">
    #         <p>
    #             <s n="1" lang="de" state="auto">Zuͦ<fl>b</fl> <placeName ref="1115">Überlingen</placeName> hatt einer an die kilchthür einen rymen angeschlagen, welcher abgnommen und ussgangen ist<fl>1</fl>.</s>
    #             <s n="2" lang="de" state="auto">Von dem hatt mir der stattschryber<fl>2</fl> des<fl>c</fl> ein abgschrifft von wunders wägen zuͦ gestelt.</s>
    #             <s n="3" lang="de" state="auto">Lutet also:<pb_edition start_of="31"/> Ich fragen hie on allen list, worum so vil tüfel und nun<fl>3</fl> ein gott ist?</s>
    #         </p>

    # 1.sentence <s> 2 footlote <fl>  
    store_fn =[]
    words_found = []
    n = 1
    for footnotes_found in list_of_similar_words: #root.iter("fl"):
        if footnotes_found in reference_dictionary:
            words_found.append(footnotes_found)
            n += 1 
        elif footnotes_found not in reference_dictionary:
            #add footnote on the write side with context 
            new_footnote = s.text[footnotes_found]
            new_footnote.set("updated","yes")
            # adding new footnote to xml 
# merge instanly in the looked file 
# set a placholder at the point where the footnote should be in 
    # check it twice and annotate it later 
    # return store_fn,words_found,n-1
    tree = ET.parse(full_path)
    root = tree.getroot()
    print(root)
    for note in root.findall('letter'):
        # using root.findall() to avoid removal during traversal
        letter_of = repr((note.find('s'))) #letter_of = (note.find('s').text) ERRor
        if note == store_fn:
            root.remove(note)

    tree.write('output.xml')

    return store_fn,words_found,n-1


    

directory_path = r"/Users/yasardemirelli/cmd_code/Uni_UZH/WS23:24/Sprachtechnologische_Webapplikationen/Project Bullinger/Bullinger_Letter_Examples"
references_list = parse_xml_files(directory_path)
filtered_list = filter_references(references_list)
reference_dictionary = build_reference_dictionary(filtered_list)
print(len(reference_dictionary), reference_dictionary)
print(levenshteinDistance(reference_dictionary))
simiar_words_detection(reference_dictionary)
print(add_footnotes(reference_dictionary))

print(type(root))


# if 2 words have the same form but one has - ge at the beginning -same lemma?
# if s at the end is the only difference -- same lemma?
# if 2 words are in similar words list and start from the same letter, have the same meaning
# meaning;s. -- definitely the same meaning?
# a lot of Vgl in the values: didn't capture the whole reference? a lot of Paraphrase von - also didn't capture the whole meaning?
# if the value is only Vgl --? delete the value and the key?
