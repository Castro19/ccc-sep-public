
import pandas as pd
import re
from collections import defaultdict
import pickle
import numpy as np
from pdfExtract import clean_class_list

# Examples are based on this PDF Agreement: https://assist.org/transfer/report/26298705

# Purpose: Takes in a clean list of classes where each class is a requirement to take. Categorizes each class into a dictionary where the key is the subject name and the value is a list of corresponding classes. Class Lists are also organized by prerequisite depth, so classes with no prereqs are first in the list. 
# EX of clean List: ['BIOL11A', 'CHEM1A', 'CHEM1B', 'CHEM28A', 'CHEM28B', 'CHEM29A', 'ENGL1B', 'ENGL1BH', 'ENGL1A', 'ENGL1AH', 'MATH5A', 'MATH5B', 'MATH6', 'MATH17', 'PHYS4A', 'PHYS4B', 'PHYS4C', 'MATH4B', 'MATH4A']
def createSubjects(classList):
# Create subjects and sort classes based on their prereq depth
    print(f"CLASSLIST in SUBJECT: {classList}")
    subject_dict = defaultdict(list)
    
    # Check if every item in the classList is a valid course by using our class_dict
    for class_id in classList:
        if class_id in class_dict.keys():
            # Find the subject of the class
            subject = class_dict[class_id]["Subject"]
            # Create a list of classes for their corresponding subject
            subject_dict[subject].append(class_id)

    # Sort each list value by its prereq depth
    for subject, class_ids in subject_dict.items():
        subject_dict[subject] = sorted(class_ids, key=lambda x: class_dict[x]['prereq_depth'])
        # Add units to each class in the list value for subject_dict
        subject_dict[subject] = add_units_to_class_ids(subject_dict[subject])
    
    return subject_dict

# Purpose: Use a disorganized list extracted from ASSIST PDF and clean it by uaing the logic of the conjuctions "AND" & "OR" in the agreement correctly to find what classes are required.
# EX of disorganized list from ASSIST PDF: ['BIOL11A(5.00)', 'CHEM1A(5.00) & CHEM1B(5.00) OR ', 'CHEM28A(3.00) & CHEM28B(3.00)', 'CHEM29A(2.00)', 'ENGL1B(3.00) / ENGL1BH(3.00)', 'ENGL1A(4.00) / ENGL1AH(4.00)', 'MATH5A(5.00)', 'MATH5B(4.00)', 'MATH6(5.00)', 'MATH17(5.00) OR ', '', 'PHYS4A(4.00) & PHYS4B(4.00) & PHYS4C(4.00)']
# Also find the Prerequisite of classes and add them to our clean list b4 creating our subject_dict
def createSchedule(classList):
    print(f"CLASSLIST in Schedule: {classList}")
    cleaned_list = clean_class_list(classList)
    class_list_with_no_units = removeUnits(cleaned_list)
    class_list_with_no_units_and_prereqs = find_all_prerequisites(class_list_with_no_units)
    subject_dict = createSubjects(class_list_with_no_units_and_prereqs)
    return subject_dict

# The following functions are dictionaries used in every user session. I was not provided this data and I had to scrape throught the course catalog and degree catalog to create these dictionaries. 

# Dictionary for CSU-GE & IGETCRequirements where keys are the Areas and values are sub-dictionaries where the keys are subjects and the values are list of classes to the corresponding subject
def createCSU_GE():
    with open('file_dictionaries/CSU_GE.pkl', 'rb') as f:
        CSU_GE = pickle.load(f) 
    return CSU_GE
def createIGETC():
    with open('file_dictionaries/IGETC.pkl', 'rb') as f:
        IGETC = pickle.load(f) 
    return IGETC

# Most important Dictionary where the key is the class ID and the attributes include subject, units, prereq depth, and prerequisites formatted as strings, tuples, and lists
def createCourses():
    with open('file_dictionaries/class_dict.pkl', 'rb') as f:
        course_dictionary = pickle.load(f) 
    return course_dictionary
class_dict = createCourses()

# Dictionary that maps out the requirements to earn each degree CCC has available by listing the required classes, optional classes, and the units/# of classes required from the optional classes
# Also has special characters for some degrees that are not consistent with the majority of other degrees 
def createDegreeDictionary():
    with open('file_dictionaries/degree_dict.pkl', 'rb') as f:
        degree_dict = pickle.load(f)
    return degree_dict

# Values were being stored as 'int64' so we need to reverse it
def replace_nan(obj):
    if isinstance(obj, dict):
        return {k: replace_nan(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nan(v) for v in obj]
    elif isinstance(obj, np.float64):
        return float(obj)
    elif isinstance(obj, (float, np.float32, np.float16)) and np.isnan(obj):
        return None
    else:
        return obj

# University Map to easily identify the name of the School based on their corresponding ASSIST API University ID
def createUniversityMap():

    university_map = {
    '1': 'California State University, Maritime Academy (CSUMA)',
    '7': 'University of California, San Diego (UCSD)',
    '11': 'California Polytechnic University, San Luis Obispo (CPSLO)',
    '12': 'California State University, Monterey Bay (CSUMB)',
    '21': 'California State University, East Bay (CSUEB)',
    '23': 'California State University, San Marcos (CSUSM)',
    '24': 'California State University, Stanislaus (CSUSTAN)',
    '29': 'California State University, Fresno (CSUFRES)',
    '39': 'San Jose State University (SJSU)',
    '42': 'California State University, Northridge (SUN)',
    '46': 'University of California, Riverside (UCR)',
    '50': 'California State University, Dominguez Hills (CSUDH)',
    '60': 'California State University, Sacramento (CUS)',
    '75': 'California Polytechnic University, Pomona (CPP)',
    '76': 'California State University, Los Angeles (CSULA)',
    '79': 'University of California, Berkeley (UCB)',
    '81': 'California State University, Long Beach (CSULB)',
    '85': 'California State University, San Bernardino (CSUSB)',
    '88': 'Sonoma State University (SSU)',
    '89': 'University of California, Davis (UCD)',
    '98': 'California State University, Bakersfield (CSUB)',
    '115': 'California Polytechnic University, Humboldt (HSU)',
    '116': 'San Francisco State University (SFSU)',
    '117': 'University of California, Los Angeles (UCLA)',
    '120': 'University of California, Irvine (UCI)',
    '128': 'University of California, Santa Barbara (UCSB)',
    '129': 'California State University, Fullerton (CSUFULL)',
    '132': 'University of California, Santa Cruz (UCSC)',
    '141': 'California State University, Chico (CSUC)',
    '143': 'California State University, Channel Islands (CSUCI)',
    '144': 'University of California, Merced (UCM)'
}
    return university_map
    
# Solved an edge case with the Assist Class Extraction where class items have nested conjuctions
def process_complex_class_item(class_item):
    if class_item.startswith('('):  # If it starts with '(', split the classes
        class_item = re.findall(r'\[.*?\]', class_item)  # Find all substrings enclosed in square brackets
        class_item = [re.sub(r'[&()]', '', item) for item in class_item]  # Remove '&', '(', and ')'
    return class_item

# Formatting the classes based on the conjugation logic from the ASSIST agreement, getting rid of any duplicates and invalid classes
def format_classes(classList):
    v4 = []  # List to maintain order
    seen = set()  # Set for quick lookup

    for item in classList:
        # If item is a list, iterate over its elements
        if isinstance(item, list):
            for sublist in item:
                sublist = sublist.split('/')[0]  # Select the text before the first '/'
                sublist = re.sub(r'[\[\]]', '', sublist)  # Remove all brackets
                if sublist in class_dict.keys() and sublist not in seen:
                    v4.append(sublist)
                    seen.add(sublist)
        # Condition 1: Starts with '[' and does not contain '&'
        elif item.startswith('[') and '&' not in item:
            item = item.split('/')[0]  # Select the text before the first '/'
            item = re.sub(r'[\[\]]', '', item)  # Remove all brackets
            if item in class_dict.keys() and item not in seen:
                v4.append(item)
                seen.add(item)
        # Condition 2: Starts with '[' and contains '&'
        elif item.startswith('[') and '&' in item:
            item = re.sub(r'[\[\]()]', '', item)  # Remove all brackets and parentheses
            groups = item.split('&')  # Split into groups by '&'
            for group in groups:
                classes = group.split('/')  # split into classes by '/'
                # If all classes in the group are already in the list, continue to next group
                if all(class_ in seen for class_ in classes):
                    continue
                else:
                    # Add classes to the list and seen set
                    for class_ in classes:
                        if class_ in class_dict.keys() and class_ not in seen:
                            v4.append(class_)
                            seen.add(class_)
                    break  # exit loop once we find a group that hasn't been added yet
        # If item doesn't start with '['
        else:
            if item in class_dict.keys() and item not in seen:
                v4.append(item)
                seen.add(item)
    return v4

# def clean_dict_ordered(subject_dict):
#     cleaned_dict = defaultdict(list)
#     for key, values in subject_dict.items():
#         cleaned_values = []
#         for value in values:
#             cleaned_value = re.sub(r'\(.*\)', '', value)
#             if cleaned_value not in cleaned_values:
#                 cleaned_values.append(cleaned_value)
#         cleaned_dict[key] = cleaned_values
#     return cleaned_dict

# def clean_and_filter_dict(subject_dict, prereq_dict):
#     # Clean the subject_dict
#     cleaned_dict = clean_dict_ordered(subject_dict)

#     # Flatten the prereq_dict values into a single list for easy checking
#     prereq_values = [item for sublist in prereq_dict.values() for item in sublist]

#     # Remove values from cleaned_dict if they are not in prereq_dict
#     for key in cleaned_dict.keys():
#         cleaned_dict[key] = [value for value in cleaned_dict[key] if value in prereq_values]

#     return cleaned_dict

# Recursively checks if a value or any of its elements (if iterable) are NaN.
def is_nan_value(val):
    if isinstance(val, (list, tuple)):
        return any(is_nan_value(element) for element in val)
    else:
        return pd.isna(val)
    
# Create the List of All the Required Classes using the data w/ the ASSIST agreements, PreRequisites of classes, and creating it based on the the  conjugation logic with "OR" & "AND". 
def clean_and_format_class_list(class_list):
    # print(f"v0: {class_list}")
    v1 = []
    # v1 removes units, spaces, and errors in formatting
    for class_item in class_list:
        # Remove all text within parentheses
        class_item = re.sub(r'\(.*?\)', '', class_item)
        # Remove all spaces
        class_item = class_item.replace(" ", "")
        # Remove trailing "AND", "OR", "/" and "&"
        class_item = re.sub(r'(AND|OR|/&)$', '', class_item)
        
        # Split into substrings by "OR"
        substrings = class_item.split("OR")
        for i, substring in enumerate(substrings):
            # Split each substring into groups by "AND"
            groups = substring.split("AND")
            for j, group in enumerate(groups):
                # Split each group into classes by "/"
                classes = group.split("/")
                # If a group contains more than one class, wrap it in "[...]"
                if len(classes) > 1:
                    groups[j] = "[" + "/".join(classes) + "]"
            # If a substring contains more than one group, wrap it in "(...)"
            if len(groups) > 1:
                substrings[i] = "(" + "&".join(groups) + ")"
            else:
                substrings[i] = groups[0]
        # If the original string contains more than one substring, wrap the entire string in "[...]"
        if len(substrings) > 1:
            class_item = "[" + "/".join(substrings) + "]"
        else:
            class_item = substrings[0]
        v1.append(class_item)
    # print(f"v1 list: {v1}")
    v2 = []
    seen = set()  # Keep track of seen items to eliminate duplicates
    seen_items = set()  # Keep track of seen class items
    # v2 removes duplicate classes and seperates the & classes 
    for item in v1:
        if item not in seen_items:  # check if class item has been seen before
            seen_items.add(item)
            if '/' in item:
                v2.append(item)
            elif '&' in item:
                item = item.replace('(', '').replace(')', '')  # remove parentheses
                for subitem in item.split('&'):
                    if subitem not in seen:
                        v2.append(subitem)
                        seen.add(subitem)
            else:
                if item not in seen:
                    v2.append(item)
                    seen.add(item)

    v3 = []
    # print(f"v2 list: {v2}")
    for item in v2:
        v3.append(process_complex_class_item(item)
)
    # print(f"v3 list: {v3}")
    v4 = format_classes(v3)
    # print(f"v4 list: {v4}")

    v5 = find_best_prerequisites(v4)
    # print(f"v5 list: {v5}")
    return v5

# Purpose: Create a dictionary and Assign each class in the list as the key and the value is the class's prerequisite depth 
def calculate_prereq_depths(class_list):
    result_dict = {}
    for class_name in class_list:
        if class_name in class_dict:
            result_dict[class_name] = class_dict[class_name]['prereq_depth']
            # print(f"{class_name}: {result_dict[class_name]}")
    return result_dict

# My favorite Function: An algorithm I created to create a schedule from the classes in the final cleaned classList. Algorithm places classes in semesters based on unit count, prereq depth, and priority to classes w/ same subject being taken in back to back semesters. 
# EX: IF a student is in MATH1 in their 1st semester then I want to prioritize MATH2 for the semester after
def unverifiedScheduleGenerator(classList):
    # print(f"unverified initial List {classList}")
    # If there is an empty classList
    if not classList:
        return {}
# Phase 1: Clean up the classList
    new_final_list = clean_and_format_class_list(classList)
    # print(f"NEW FINAL LIST: {new_final_list}")
    depths = calculate_prereq_depths(new_final_list)

# Phase 2: Create PreReq Depth
    prereq_dict = defaultdict(list)
    # Check each class in depths
    invalid_classes = []
    for class_name in depths.keys():
        if class_name not in class_dict.keys():
            invalid_classes.append(class_name)
        else:
            prereq_dict[depths[class_name]].append(class_name)
        
    # Remove invalid classes from depths
    for class_name in invalid_classes:
        del depths[class_name]

# Phase 3: Create the field_dict
    field_dict = {
    1: dict.fromkeys(['1_3', '1_4', '2_3', '2_4', '3_3', '3_4', '4_3', '4_4', '5_3', '5_4', '6_3', '6_4', '7_3', '7_4'], []),
    2: dict.fromkeys(['1_5', '1_6', '2_5', '2_6', '3_5', '3_6', '4_5', '4_6', '5_5', '5_6', '6_5', '6_6', '7_5', '7_6'], []),
    3: dict.fromkeys(['1_9', '1_10', '2_9', '2_10', '3_9', '3_10', '4_9', '4_10', '5_9', '5_10', '6_9', '6_10', '7_9', '7_10'], []),
    4: dict.fromkeys(['1_11', '1_12', '2_11', '2_12', '3_11', '3_12', '4_11', '4_12', '5_11', '5_12', '6_11', '6_12', '7_11', '7_12'], []),
    5: dict.fromkeys(['1_15', '1_16', '2_15', '2_16', '3_15', '3_16', '4_15', '4_16', '5_15', '5_16', '6_15', '6_16', '7_15', '7_16'], []),
    6: dict.fromkeys(['1_17', '1_18', '2_17', '2_18', '3_17', '3_18', '4_17', '4_18', '5_17', '5_18', '6_17', '6_18', '7_17', '7_18'], [])
    }
    # cleaned_list = clean_class_list(classList)

    # Start with an empty stack and @ the 1st semester
    stack = []
    i = 0
    subject_order = set()
    scheduled_classes = set()
    leftover_classes = []
    completed_classes = []
    max_units = 15.0 # This is my suggest max Unit Cap. However, students can take more units per semester if they choose. 
    for depth in range(7):
        i += 1 # Increase the Semester 
        if i > 6:
            # If semester exceeds the maximum, store the leftover classes and break
            leftover_classes.extend(stack)
            break
        # key iterator is how we know which semester to insert into based on our field_dict
        keys_iterator = iter(field_dict[i].keys())

        # At the beginning of every semester, we start @ 0.0 units
        semesterUnits = 0.0 
        
        # Add classes of the current depth to the stack
        stack.extend(prereq_dict[depth])
        invalid_classes = []
        # Sort the stack:
        # 1. By giving priority to classes with the lowest prereq_depth
        # 2. By giving priority to classes whose subjects are the same as the last classes inserted
        # print(f"SUBJECT ORDER for {i}: {subject_order}")
        stack.sort(key=lambda x: (depths[x], -1 * (class_dict[x]['Subject'] in subject_order)), reverse=True)

        subject_order = set()
        subject_depth_scheduled = {}  # reset for new semester

        # print(f"{i}: {stack}") # Debegging Statement
        # Go through each class in the Stack and try to insert it into our current semester.
        while stack:
            # Pop class off the stack
            classID = stack.pop()
            # Get the units of the corresponding class, so we can make sure not to exceed 15.0 units
            units = float(class_dict[classID]['Units'])
            # Get the Subject of the corresponding class, so we can prioritize a class with the same subject on the next semester
            subject = class_dict[classID]['Subject']
            # Get the depth of the class
            depth_of_class = depths[classID]
            
            # Check if the subject and depth are already scheduled
            already_scheduled = subject_depth_scheduled.get(subject, None) == depth_of_class
            # Check if the class has all there prereqs completed
            prereq_completion = check_prereq_completion(classID, completed_classes)
            # For the Last semester, increase the max_units so we can try and fit all classes in schedule 
            if i == 6:
                max_units = 18.0

# Conditions for class to be inserted to Semester:
    # 1.) Total Units <= max_units (15)
    # 2.) Class of the same subject & different prereq depth cannot be inserted into the same semester
    # 3.) The prereq depth of a class must be less than our semester (i)
    # 4.) The prerequisites for the class must be completed
    # 5.) No duplicate classes can be inserted
            if (semesterUnits + units <= max_units) and ((subject not in subject_depth_scheduled) or already_scheduled) and (i > depth_of_class or semesterUnits == 0) and prereq_completion and classID not in completed_classes:
                class_key = next(keys_iterator)
                units_key = next(keys_iterator)
                field_dict[i][class_key] = classID
                field_dict[i][units_key] = units
                semesterUnits += units
                scheduled_classes.add(classID)
                subject_order.add(subject)
                subject_depth_scheduled[subject] = depth_of_class
                completed_classes.append(classID)
            # Class did not meet conditions:
            else:
                invalid_classes.append(classID)
                # Go to next class on the stack if the stack is not empty
                if stack:
                    continue
                # Else: # Go to next semester
                stack.extend(invalid_classes)
                break 

    print(f"LEFTOVERS {leftover_classes} @ {i}") # Debug Statement to check for classes unable to fit in the schedule

    # Flatten out the sub dictionaries into 1 whole dictionary where the key is the textbox location and the values are the text for classes & units
    result_dict = {key: '' if not val else ', '.join(['{:.2f}'.format(i) if isinstance(i, float) else str(i) for i in val]) if isinstance(val, list) else '{:.2f}'.format(val) if isinstance(val, float) else val for sub_dict in field_dict.values() for key, val in sub_dict.items()}
    return result_dict

# Helper function to remove the units of each class in the list
def removeUnits(class_list):
    # Use regular expression to replace everything within parentheses with an empty string
    class_list_without_units = [re.sub(r'\(.*?\)', '', s) for s in class_list]
    
    return class_list_without_units

# Helper function to insert the units of each class in the correct format
def add_units_to_class_ids(classList):
    """Adds units to each class ID in the classList."""
    
    class_list_with_units = []
    
    for class_id in classList:
        if class_id in class_dict:
            units = class_dict[class_id]["Units"]
            class_list_with_units.append(class_id + '(' + units + ')')
        else:
            # If class_id not found in the dictionary, just append it as is
            class_list_with_units.append(class_id)
    
    return class_list_with_units

def find_all_prerequisites(classList):
    """Find all prerequisites (including prerequisites of prerequisites) for each class in the classList."""
    # Create a list to store the results
    result = classList.copy()

    # Initialize an index to go through the classList
    idx = 0

    # Go through each class in the result list
    while idx < len(result):
        classID = result[idx]
        
        # Check if the classID is in the class_dict
        if classID in class_dict:
            # Get the prerequisites for the current class
            prereqs = class_dict[classID]['PREREQUISITES']

            # If the prerequisites is a string, add it to the result list if not already present
            if isinstance(prereqs, str) and prereqs not in result:
                result.append(prereqs)
            
            # If the prerequisites is a tuple, go through each item and add it to the result list if not already present
            elif isinstance(prereqs, tuple):
                for item in prereqs:
                    # If the item is a list, go through each string in the list and add it to the result list if not already present
                    if isinstance(item, list):
                        for sub_item in item:
                            if isinstance(sub_item, str) and sub_item not in result:
                                result.append(sub_item)
                    # If the item is a string, add it to the result list if not already present
                    elif isinstance(item, str) and item not in result:
                        result.append(item)

            # If the prerequisites is a list, go through each item and add it to the result list if not already present
            elif isinstance(prereqs, list):
                for item in prereqs:
                    # If the item is a tuple, go through each string in the tuple and add it to the result list if not already present
                    if isinstance(item, tuple):
                        for sub_item in item:
                            if isinstance(sub_item, str) and sub_item not in result:
                                result.append(sub_item)
                    # If the item is a string, add it to the result list if not already present
                    elif isinstance(item, str) and item not in result:
                        result.append(item)
        
        # Move to the next index
        idx += 1
    return result

# Helper Function that is used to handle the conjugation logic and find the best prereqs to complete based on our classList and conjugations, then add them to our result list. THis logic is different than the ASSIST logic as I have set the types to be tuples, lists, and strings instead of parsing strings. 
def find_best_prerequisites(classList):
    result = classList.copy() # Make a copy of our list

    idx = 0 # Loop through result list
    while idx < len(result):
        classID = result[idx]
        
        if classID in class_dict:
            # Find the prerequisites for the class
            prereqs = class_dict[classID]['PREREQUISITES']
            
            # Skip if prereq is NaN (no prerequisites) 
            if isinstance(prereqs, float):
                idx += 1
                continue
            
            # Handling strings and tuples of strings
            if isinstance(prereqs, str) and prereqs not in result:
                result.append(prereqs)
            elif isinstance(prereqs, tuple) and all(isinstance(item, str) for item in prereqs):
                for item in prereqs:
                    if item not in result:
                        result.append(item)
            
            # Handling types involving lists
            else:
                items_to_check = []
                if isinstance(prereqs, list):
                    items_to_check.extend(prereqs)
                elif isinstance(prereqs, tuple):  # It's a tuple
                    items_to_check.extend(prereqs)
                
                # Sorting items to check based on type priority
                items_to_check.sort(key=lambda x: (
                    0 if isinstance(x, str) else 
                    1 if isinstance(x, tuple) and all(isinstance(i, str) for i in x) else 
                    2 if isinstance(x, list) and all(isinstance(i, str) for i in x) else 
                    3
                ))
                # Handle tuples of strings and lists or tuples containing lists
                for item in items_to_check:
                    # If the item is a standalone string, prioritize it
                    if isinstance(item, str) and item in class_dict:
                        if item not in result:
                            result.append(item)
                        
                        break
                    # For tuples, process them only if no standalone string was found
                    elif isinstance(item, tuple) and all(isinstance(sub_item, str) for sub_item in item):
                        for sub_item in item:
                            if sub_item not in result:
                                result.append(sub_item)
                    
                    if isinstance(item, list):
                        # Lists containing only strings
                        if all(isinstance(sub_item, str) for sub_item in item):
                            if not any(sub_item in result for sub_item in item):
                                best_prereq = min(item, key=lambda x: class_dict[x]['prereq_depth'])
                                if best_prereq not in result:
                                    result.append(best_prereq)
                                    break
                        # Lists containing tuples and strings
                        elif all(isinstance(sub_item, (str, tuple)) for sub_item in item):
                            strings = [sub_item for sub_item in item if isinstance(sub_item, str)]
                            tuples = [sub_item for sub_item in item if isinstance(sub_item, tuple)]
                            # Filter out strings that are present in any tuple
                            strings = [string for string in strings if not any(string in tuple_item for tuple_item in tuples)]
                            # Choose the string with the lowest prereq depth that is not in any tuple
                            if strings:
                                best_string = min(strings, key=lambda x: class_dict[x]['prereq_depth'])
                                if best_string not in result:
                                    result.append(best_string)
        idx += 1

    return result

# Return a Boolean Value that is depended on if a prerequisite has completed all the prerequisite classes. `class_list` acts as the list of completed classes. 
def check_prereq_completion(classID, class_list):
    # Get the prerequisites for the classID
    prereqs = class_dict[classID]['PREREQUISITES']
    
    # Check if prereq is NaN (float)
    if isinstance(prereqs, float):
        return True
    
    # Handle string prerequisites
    if isinstance(prereqs, str):
        return prereqs in class_list
    
    # Handle list of only strings
    if isinstance(prereqs, list) and all(isinstance(item, str) for item in prereqs):
        return any(item in class_list for item in prereqs)
    
    # Handle list of strings and tuples
    if isinstance(prereqs, list) and all(isinstance(item, (str, tuple)) for item in prereqs):
        for item in prereqs:
            if isinstance(item, str) and item in class_list:
                return True
            elif isinstance(item, tuple) and all(sub_item in class_list for sub_item in item):
                return True
        return False
    
    # Handle tuple of only strings
    if isinstance(prereqs, tuple) and all(isinstance(item, str) for item in prereqs):
        return all(item in class_list for item in prereqs)
    
    # Handle tuple of only lists
    if isinstance(prereqs, tuple) and all(isinstance(item, list) for item in prereqs):
        for item in prereqs:
            if not any(sub_item in class_list for sub_item in item):
                return False
        return True
    
    # Handle tuple of strings and lists
    if isinstance(prereqs, tuple) and all(isinstance(item, (str, list)) for item in prereqs):
        for item in prereqs:
            if isinstance(item, str) and item not in class_list:
                return False
            elif isinstance(item, list) and not any(sub_item in class_list for sub_item in item):
                return False
        return True
    
    return False
