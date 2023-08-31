import os
import glob
import xml.etree.ElementTree as ET
import math

def prepare_obj():
    return {"Title": None, "UserName": None, "Password": None, "LastModified": None, "CustomKeys": []}

def print_new_entry(entry):
    print(f"UserName: {entry['UserName']}")
    print(f"Password: {entry['Password']}")
    print(f"LastModified: {entry['LastModified']}")
    if len(entry['CustomKeys']) > 0:
        print("CustomKeys:")
        for custom_key in entry['CustomKeys']:
            key_name = custom_key[0]
            value = custom_key[1]
            print(f"  {key_name}: {value}")
    print("\n")

def extract_entries_from_file(file_n):
    try:    
        if file_n == 1:
            folder_path = './xml_data/first/'
        elif file_n == 2:
            folder_path = './xml_data/second/'
        else:
            raise ValueError("Value must indicate what file to analyze (1-2)")
    
        xml_files = glob.glob(os.path.join(folder_path, '*.xml'))
        entry_arr = []

        for xml_file in xml_files:
            filename = os.path.basename(xml_file)
            tree = ET.parse(xml_file)
            root = tree.getroot()
            groups = root.findall(".//Root/Group/Group")
            for group in groups:
                if group.find("Name").text == "Recycle Bin":
                    continue
                entries = group.findall("Entry")

                # entry
                for entry in entries:
                    entry_obj = prepare_obj()

                    # string
                    for string in entry.findall("./String"):
                        key = string.find("Key").text
                        value = string.find("Value").text
                        if value is None:
                            continue

                        if key == "Title":
                            entry_obj["Title"] = value
                        elif key == "UserName":
                            entry_obj["UserName"] = value
                        elif key == "Password":
                            entry_obj["Password"] = value
                        elif key != "History":
                            entry_obj["CustomKeys"].append((key, value))

                    # LastModificationTime
                    times = entry.find("Times")
                    if times is not None:
                        entry_obj["LastModified"] = times.find("LastModificationTime").text
                    entry_arr.append(entry_obj)
        return (entry_arr, filename)
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit..")

def compare_lists(list1, list2, filename1, filename2):
    list1_copy = list1.copy()
    list2_copy = list2.copy()

    for item1 in list1_copy:
        for item2 in list2_copy:
            if item1["Title"] == item2["Title"]:
                changes = []
                for key in item1.keys():
                    # custom keys
                    if key == "CustomKeys":
                        for tuple1 in item1[key]:
                            if tuple1 not in item2[key]:
                                changes.append(f'{key}: [{tuple1[0]}: {tuple1[1]}] not in {filename2}')
                        for tuple2 in item2[key]:
                            if tuple2 not in item1[key]:
                                changes.append(f'{key}: [{tuple2[0]}: {tuple2[1]}] not in {filename1}')
                    # other keys
                    elif item1[key] != item2[key]:
                        changes.append(f'{key}: {item1[key]} --> {item2[key]}')

                if changes:
                    print(f'{filename1}___________{item1["Title"]}___________{filename2}')
                    for change in changes:
                        print(change)
                    print("\n")

                # matched entries are removed, remaning new/unmatched ones are printed below
                list1.remove(item1)
                list2.remove(item2)
                break

    # print new/unmatched entries
    for item in list1:
        print(f'{filename1}(new)___________{item["Title"]}___________{filename2}')
        print_new_entry(item)

    for item in list2:
        print(f'{filename2}(new)___________{item["Title"]}___________{filename1}')
        print_new_entry(item)

def get_entropy(password):
    # char sets
    lowercase = 'abcdefghijklmnopqrstuvwxyz'
    uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    digits = '0123456789'
    symbols = '!@#$%^&*()-_=+[]{}|;:,.<>?/\\`~'

    # pool of characters used in the password
    pool = 0
    if any(c in lowercase for c in password):
        pool += len(lowercase)
    if any(c in uppercase for c in password):
        pool += len(uppercase)
    if any(c in digits for c in password):
        pool += len(digits)
    if any(c in symbols for c in password):
        pool += len(symbols)
    # entropy
    entropy = math.log2(pool**len(password))
    return entropy

def entropy_or_compare(first_list, second_list):
    try:
        print("1. Calculate entropy (first file).\n2. Compare XMLs.")
        choice = input("Choice: ")
        if choice == "1":
            print("Sorting by entropy...")
            sorted_data = sorted(first_list[0], key=lambda x: get_entropy(x['Password']))
            for password in sorted_data:
                print("----------------------------------------------------")
                print(f"{password['Title']}: {password['Password']}")
        elif choice == "2": 
            compare_lists(first_list[0], second_list[0], first_list[1], second_list[1])
    except Exception as e:
        print(f"Error: {e}")
        input("Press Enter to exit..")

first_list = extract_entries_from_file(1)
second_list = extract_entries_from_file(2)       
entropy_or_compare(first_list, second_list)
input("Press Enter to exit...")
