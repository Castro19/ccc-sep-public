import time
import urllib.request
import json
import requests
import pickle
with open('u_map.pkl', 'rb') as f:
    u_map_unpickled = pickle.load(f)
    
def generate_universities():
    """
    Generate a list of dictionaries for every item in the u_map_unpickled.
    Each dictionary has the format:
    'id': u_map_unpickled key
    'code': value['code']
    'name': value['institutionName']
    """
    # Will be a List of Dictionaries that detail each University
    institution_dicts = []
    
    for key, value in u_map_unpickled.items():
        institution_dict = {
            'id': key,
            'code': value['code'],
            'name': value['institutionName']
        }
        institution_dicts.append(institution_dict)
    
    return institution_dicts

# Class for the agreements between CCC and the Transfer University the user chose
class PDFOutput:
    # Constructor that depends on transfer university_id
    def __init__(self, university_id, school_year_id=None, delay=0.3):
        self.university_id = university_id
        self.school_year_id = school_year_id
        self.community_college_id = 150
        self.delay = delay

    # Fetches every agreement data CCC has with other Universities
    def get_agreements(self):
        try:
            # Introduce delay
            time.sleep(self.delay)
            
            # Requesting the agreements data from the API
            response = requests.get(f'https://assist.org/api/institutions/{self.community_college_id}/agreements')
            response.raise_for_status()  # Check if response contains a 4xx or 5xx status code

            agreements = response.json()

            # Filtering out the most recent agreements
            recent_agreements = [agreement for agreement in agreements if 'receivingYearIds' in agreement and agreement['institutionParentId'] == self.university_id]
            
            return recent_agreements

        except requests.RequestException as e:
            print(f"Error fetching agreements: {e}")
            return []
        
    # This function returns the URL of the PDF for the given major & transfer university 
    def get_pdf_url(self, major_name, school_year_id=None, button_clicked=None):
        agreements = self.get_agreements()
        for agreement in agreements:
            time.sleep(self.delay)  # Delay to prevent spamming the server with requests
            university_id = agreement['institutionParentId']
            school_year_id = agreement['receivingYearIds'][-1]
            if school_year_id > 73: # Disregard agreements that are 74 as they are 2023-2024 agreements and do NOT have any PDF agreements yet
                school_year_id = 73

            # Requesting the major data from the API
            url = f'https://assist.org/api/agreements?receivingInstitutionId={university_id}&sendingInstitutionId={self.community_college_id}&academicYearId={school_year_id}&categoryCode=major'

            # Open the url: 
            with urllib.request.urlopen(f'https://assist.org/api/agreements?receivingInstitutionId={university_id}&sendingInstitutionId={self.community_college_id}&academicYearId={school_year_id}&categoryCode=major') as url:
                # Store data in reports
                reports = json.loads(url.read().decode())['reports']

            # Go through each major in report: 
            for report in reports:
                # Checking if the major name matches the user input
                if report['label'] == major_name:

                    if button_clicked == 'get-pdf-button': 
                        # Return PDF Link
                        return f"https://assist.org/transfer/report/{report['key']}"
                    elif button_clicked == 'get-schedule':
                        # Return PDF Download where my back-end function will extract the necessary class data from it
                        return f"https://assist.org/api/artifacts/{report['key']}"
        # If no matching major is found, return None
        return None
    
     # Old function that used to fetch all the majors available for the university of interest from the ASSIST API. Replaced by storing the information to save response time which increased user experience 
    # def get_majors(self, agreements):
    #     majors = set()  # Use a set instead of a list
    #     for agreement in agreements:
    #         time.sleep(self.delay)  # Delay to prevent spamming the server with requests
    #         university_id = agreement['institutionParentId']
    #         school_year_id = agreement['receivingYearIds'][-1]
    #         if school_year_id == 74:
    #             school_year_id = 73
    #         # Requesting the major data from the API
    #         print(school_year_id)
    #         with urllib.request.urlopen(f'https://assist.org/api/agreements?receivingInstitutionId={university_id}&sendingInstitutionId={self.community_college_id}&academicYearId={school_year_id}&categoryCode=major') as url:
    #             reports = json.loads(url.read().decode())['reports']
    #         for report in reports:
    #             majors.add(report['label'])  # Add the major to the set of majors
    #     return sorted(majors) # Return the list of majors in alphabetical order

    
# print(generate_universities())
