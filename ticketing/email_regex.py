import email
import re

class GetEmailDetails:
    def __init__(self, email_body):
        self.email = email_body
        self.first_name_regex = re.compile("first name:\s(\w+\s\w+)", re.IGNORECASE)
        self.last_name_regex = re.compile("last name:\s(\w+\s\w+)", re.IGNORECASE)
        self.email_regex = re.compile(
            "[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}"
        )
        self.phone_number = re.compile("(263|0)(\d{9})")
        self.issue_section = re.compile("Section:\s([a-zA-Z]+\s?)([a-zA-Z]+\s?)?([a-zA-Z]+\s?)?", re.IGNORECASE)
        self.issue_description = re.compile(
            "Issue:", re.IGNORECASE)
        
    def get_details(self):
        self.get_first_name()
        self.get_last_name()
        self.get_email()
        self.get_phone_number()
        self.get_issue_section()
        self.get_issue_description()
        
    
    def get_first_name(self):
        firstname = self.first_name_regex.search(self.email).group(1)
        print("First Name: ", firstname)
        if firstname:
            return firstname
        return None
    
    def get_last_name(self):
        lastname = self.last_name_regex.search(self.email).group(1)
        print("Last Name: ", lastname)
        if lastname:
            return lastname
        return None

    def get_email(self):
        email_address = self.email_regex.findall(self.email)
        print("Email Address: ", email_address)
        if email_address:
            return email_address[0]
        return None
    
    def get_phone_number(self):
        phone_number = self.phone_number.findall(self.email)
        print("Phone Number: ", phone_number)
        if phone_number:
            return phone_number[0][1]
        return None
    
    def get_issue_section(self):
        words = ['Client', 'Consultant', 'Admin', 'Infrastructure Specialist', 'Database Administrator']
        for word in words:
            if word.lower() in self.email.lower():
                 section = word
                 break
            if section:
                return section
            return None
        
    
    def get_issue_description(self):
        description = self.issue_description.search(self.email).end()
        issue_description = self.email[description:]
        print("Description: ", issue_description)

        if issue_description:
            return issue_description
        return None
    

    def process_section(self, section):
        counter = 0
        for sec in section:
            if sec.endswith("\n"):
                break
            counter += 1
        
        if counter == 0:
            return re.sub("\n", "", section[0])
        
        else:
            return " ".join(section[:counter+1])
            



            

    
    
        
    
