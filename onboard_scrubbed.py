from pip._vendor import requests
import warnings
import re
import time

#############FUNCTIONS################



#function to onboard a team to BP
def BP_onboard(shortname, name):

    #BP Onboard nonprod code
    if env == 1 or env == 3:
        #pull enrichment map COMPLETE AND VALIDATED
        url = "xxxxxxxxxxxxx"
        headers = {
            "accept": "application/json",
            "Authorization": "Bearer xxxxxxxxxxxxxx",
            "Content-Type": "application/json; charset=utf-8"
        }
        current_onboarded_map = requests.get(url, headers=headers)
        #print(current_onboarded_map.text)
        current_onboarded_map = current_onboarded_map.json()

        #search json object for current shortname COMPLETE AND VALIDATED
        previously_onboarded = False
        for data in current_onboarded_map['items']:
            match = re.search(shortname, data['shortname'])
            if match:
                print("Shortname " + shortname + " has already been onboarded to BigPanda.")

                #TEST AND NONPROD ONLY - Allows removal of shortname that has been added to map if test is equal to True
                if(test == True):
                    rem_sn = input("Would you like to remove this shortname from the enrichment map? (y/n)")
                    if(rem_sn == "y"):
                        payload = {"op":"delete","value":{'shortname': shortname,'onboarded':'TRUE'}}
                        response = requests.patch(url, headers=headers, json=payload)

                #skips onboarding steps since this shortname is previously onboarded
                previously_onboarded = True
            
        #if not previously onboarded, add new line to enrichment map and increase total_results by one for later check COMPLETE AND VALIDATED
        if previously_onboarded == False:
            total_results = current_onboarded_map["total_results"]
            total_results = total_results+1

            #post new enrichment map (enables assignment group tags for that shortname's assignment groups)
            payload = {"op":"create","value":{'shortname': shortname,'onboarded':'TRUE'}}
            response = requests.patch(url, headers=headers, json=payload)
            #print(response)
            
            #FUTURE STATE: Add DL for all severities, and Cherwell and xMatters assignment groups for selected severity for service (look up service by shortname, edit assignment groups map)

            #pulls enrichment map again and performs a check to ensure that the new shortname was added to the map. 
            time.sleep(5)
            new_map = requests.get(url, headers=headers)
            #print(new_map.text)
            new_map = new_map.json()
            new_total_results = new_map["total_results"]
            if new_total_results == total_results:
                print("Team " + name + "'s shortname " + shortname + " has been onboarded to BigPanda Non-production.")
            else: 
                print("Team " + name + "'s shortname " + shortname + " was not onboarded successfully in Big Panda Non-production, please try again.")



    #BP production code (currently disabled for change freeze)
    """
    if env == 2 or env == 3:
        #pull enrichment map COMPLETE AND VALIDATED
            url = "xxxxxxxxxxx" #this map needs to be created still
            headers = {
                "accept": "application/json",
                "Authorization": "Bearer xxxxxxxxxx"
            }
            onboarded_map = requests.get(url, headers=headers)
            onboarded_map = onboarded_map.json()

            #search json object for current shortname COMPLETE AND VALIDATED
            previously_onboarded = False
            for data in onboarded_map['items']:
                match = re.search(shortname, data['shortname'])
                if match:
                    print("Shortname " + shortname + " has already been onboarded to BigPanda.")

                    #skips onboarding steps since this shortname is previously onboarded
                    previously_onboarded = True
                
            #if not previously onboarded, add new line to enrichment map and increase total_results by one for later check COMPLETE AND VALIDATED
            if previously_onboarded == False:
                total_results = onboarded_map["total_results"]
                total_results = total_results+1

                #post new enrichment map (enables assignment group tags for that shortname's assignment groups)
                payload = {"op":"create","value":{'shortname': shortname,'onboarded':'TRUE'}}
                response = requests.patch(url, headers=headers, json=payload)

                #FUTURE STATE: Add DL for all severities, and Cherwell and xMatters assignment groups for selected severity for service (look up service by shortname, edit assignment groups map)

                #pulls enrichment map again and performs a check to ensure that the new shortname was added to the map. 
                time.sleep(5)
                new_map = requests.get(url, headers=headers)
                #print(new_map.text)
                new_map = new_map.json()
                new_total_results = new_map["total_results"]
                if new_total_results == total_results:
                    print("Team " + name + "'s shortname " + shortname + " has been onboarded to BigPanda Production.")
                else: 
                    print("Team " + name + "'s shortname " + shortname + " was not onboarded successfully in Big Panda Production, please try again.")

    """




#function to offboard a team from Moogsoft (removes all text from team's description) COMPLETE AND VALIDATED
def Moo_offboard(name):
    warnings.filterwarnings("ignore")
    
    #nonprod or both
    if env == 1 or env == 3:

        #get Team ID from Team name
        url = "https://aa.moogsoft.qa/graze/v1/getTeam"
        auth = ('xxxxxxxxxxx', 'xxxxxxxxxx') #need to remove secrets before going to GH
        params = {'name': name}
        team_info = requests.get(url, auth=auth, params=params, verify=False)
        team_info = team_info.json()
        # print(team_info)
        try:
            team_id = team_info['team_id']
            print("Moogsoft team ID = ")
            print(team_id)
            print("Proceeding to update description using this ID.")

            #Use team ID to Update team
            url = "https://aa.moogsoft.qa/graze/v1/updateTeam"
            headers = {'Content-Type': 'application/json; charset=UTF-8'}
            json_data = {
                'team_id': team_id,
                'description': 'Description removed via offboarding script',
            }

            update = requests.post(url, headers=headers, json=json_data, verify=False, auth=auth)   
            print("Offboarding of team " + name + " in Moogsoft Nonprod is now complete")
                
        #if GET request for team ID fails, script fails (team name is incorrect)
        except KeyError:
            print("Could not find team " + name + " in Moogsoft Nonprod. Offboarding was not completed. Please try again.")

    #prod or both
    if env == 2 or env == 3:

        #get Team ID from Team name
        url = "https://aa.moogsoft.com/graze/v1/getTeam"
        auth = ('xxxxxxxxxxxx', 'xxxxxxxxxx') #need to remove secrets before going to GH
        params = {'name': name}
        team_info = requests.get(url, auth=auth, params=params, verify=False)
        team_info = team_info.json()
        try:
            team_id = team_info['team_id']
            print("Moogsoft team ID = ")
            print(team_id)
            print("Proceeding to update description using this ID.")

            #Use team ID to Update team
            url = "https://aa.moogsoft.com/graze/v1/updateTeam"
            headers = {'Content-Type': 'application/json; charset=UTF-8'}
            json_data = {
                'team_id': team_id,
                'description': 'Description removed via offboarding script',
            }

            update = requests.post(url, headers=headers, json=json_data, verify=False, auth=auth)   
            print("Offboarding of team " + name + " in Moogsoft Production is now complete")
        
        #if GET request for team ID fails, script fails (team name is incorrect)
        except KeyError:
            print("Could not find team " + name + " in Moogsoft Production. Offboarding was not completed. Please try again.")






###############BASE SCRIPT#################

#for testing: 
test = True
env = 1

#Test script with dummy answers so I don't have to keep answering the questions. VALIDATED AND COMPLETE
if test == True:
    name = "Situational Awareness Engineering - AIOps"
    cherwell_name = name
    xmatters_name = name.replace(" ", "_")
    int_check = "n"
    int_check = int_check.lower()
    rr_check = "n"
    rr_check = rr_check.lower()
    if int_check == "n" and rr_check == "n":     

        #infitely loops unless valid selection is made
        while True:
            choice = input("Which would you like to do? \n1. Onboard to BP \n2. Offboard from Moogsoft \n3. Both\n")
            if choice == "1":
                email = "xxxxxxxxxxx"
                shortname = "xxxxxxx"
                BP_onboard(shortname, name)
                break
            elif choice == "2": 
                Moo_offboard(name)
                break
            elif choice == "3":
                Moo_offboard(name)
                email = "xxxxxxxxxxx"
                shortname = "xxxxxx"
                BP_onboard(shortname, name)
                break
            else: 
                print("You made an invalid selection, please try again.")
    else:


#Live script (when test = False). VALIDATED AND COMPLETE
else:
    # input team name and generate xMatters and Cherwell team names from it (for future use in creating enrichment map).
    name = input("What is your team name in xMatters and Cherwell?\n")
    cherwell_name = name
    xmatters_name = name.replace(" ", "_")

    #performs checks to ensure people are not onboarded earlier than expected, then asks for number of shortnames being onboarded.
    int_check = input("Does your team use any of the following integrations: OEM, Cloudwatch, or Splunk? (y/n)\n")
    int_check = int_check.lower()
    rr_check = input("Does your team use any rate recipes, such as 0410, 0330, 05C0, etc.? This does not include U010, U020, etc. (y/n)\n")
    rr_check = rr_check.lower()
    if int_check == "n" and rr_check == "n": #customer cannot select yes for either question and proceed.

            #FUTURE STATE: Add code to loop through multiple shortnames?

            while True:
                env = input("Which environment would you like to make this change in? \n1. Non-production \n2. Production \n3. Both\n")
                env = int(env)
                if env > 0 and env < 4:
                    break;
                else:
                    print("Invalid environment selection, please try again.")

            #infitely loops unless valid selection is made
            while True:
                choice = input("Which would you like to do? \n1. Onboard to BP \n2. Offboard from Moogsoft \n3. Both\n")
                if choice == "1": #Onboard BP
                    email = input("What is your team's email distribution list?\n")
                    shortname = input("Enter your application's shortname (Case sensitive)\n")
                    BP_onboard(shortname, name)
                    break
                elif choice == "2":  #Offboard Moogsoft
                    Moo_offboard(name)
                    break
                elif choice == "3":   #Run both functions
                    Moo_offboard(name)
                    email = input("What is your team's email distribution list?\n")
                    shortname = input("Enter your application's shortname (Case sensitive)\n")  
                    BP_onboard(shortname, name)
                    break
                else:   #Made a selection that was not 1, 2, or 3
                    print("You made an invalid selection, please try again.")
    else:    #Customer selected an answer that was not "n" for either the rate recipe or integration question
        print("At this time your team is not eligible for onboarding to BigPanda. Please create a GitHub issue at xxxxxxxxxxxxxxxxxxxxx to join our standby list. You can contact the AIOps team via Slack at #help-sae-aiops with any questions.")



