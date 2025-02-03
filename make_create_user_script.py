import os.path
import sys
from os import getenv

# Function to print error messages to standard error
def print_stderr(output: str):
    print(output, file=sys.stderr)

# Class to represent user information in the CSV file
class CsvFileUserInfo:
    def __init__(self, lastname, firstname, group, extension):
        self.firstname = firstname  # User's first name
        self.lastname = lastname    # User's last name
        self.group = group          # User's group name
        self.extension = extension  # User's extension

# Main function to handle user information processing
def main(argv):

    # Ensure the script is run with the correct number of arguments
    if len(argv) != 2:
        print_stderr(f"Usage: python3 {argv[0]} csv_filename")
        return

    file_name = argv[1]  # CSV file name from the arguments
    # Check if the file exists
    if not os.path.exists(file_name):
        print_stderr(f"ERROR: {file_name} doesn't exist")
        return

    # List to store user data parsed from the CSV
    csv_file_users = []
    with open(file_name, "r") as file:
        line = file.readline().strip()

        # Check if the first line matches the expected CSV header format
        if line == "lastname,firstname,group,extension":
            # Process each line in the CSV file
            for line in file:
                try:
                    # Split the CSV line into fields
                    lastname, firstname, group, extension =  line.strip().split(",")
                    # Create an instance of CsvFileUserInfo for each user
                    user = CsvFileUserInfo(lastname, firstname, group, extension)
                    csv_file_users.append(user)
                except:
                    # Print error if the line cannot be parsed
                    print_stderr(f"Unable to parse line \"{line}\"")
        else:
            # Error if the CSV file is not in the correct format
            print_stderr(f"ERROR: {file_name} is not in the proper format")
            return

    # Output the number of user records found in the CSV
    print_stderr(f"Found {len(csv_file_users)} user records in {file_name}")

    # Sets to store existing system users and groups
    existing_user_names = set()
    existing_group_names = set()
    system_user_file = '/etc/passwd'  # Default system user file
    system_group_file = '/etc/group'  # Default system group file

    # Check if we're in a test environment and modify file names accordingly
    if getenv("TEST_MAKE_USERS"):
        print_stderr("TEST_MAKE_USERS is set, going to read system files for users and groups")
        system_user_file = 'passwd'  # Use test files
        system_group_file = 'group'

    # Read system users from '/etc/passwd'
    with open(system_user_file, "r") as file:
        for line in file:
            try:
                # Extract the username from the line
                name =  line.split(":")[0]
                existing_user_names.add(name)
            except:
                # Print error if the line cannot be parsed
                print_stderr(f"Unable to parse line \"{line}\"")

    # Read system groups from '/etc/group'
    with open(system_group_file, "r") as file:
        for line in file:
            try:
                # Extract the group name from the line
                name =  line.split(":")[0]
                existing_group_names.add(name)
            except:
                # Print error if the line cannot be parsed
                print_stderr(f"Unable to parse line \"{line}\"")

    # Output the existing system users and groups
    print_stderr(f"Found system users {existing_user_names}")
    print_stderr(f"Found system group {existing_group_names}")

    # Set to store unique group names found in the CSV file
    groups_in_csv_file = set()
    for user in csv_file_users:
        groups_in_csv_file.add(user.group.lower().replace(" ", "_"))

    # Print the bash script header
    print("#!/bin/bash")
    print("")
    # Print groupadd commands for groups not already existing in the system
    for group_name in groups_in_csv_file - existing_group_names:
        print(f"groupadd {group_name}")

    usernames_taken = existing_user_names  # Set to track already taken usernames

    # Create system user accounts based on CSV data
    for user in csv_file_users:
        # Generate a unique username based on the user's name
        initial_system_username = f"{user.lastname}.{user.firstname[0]}".lower().replace(" ", "_")
        suffix = ""
        n = 1
        # Ensure the username is unique by adding a numeric suffix if necessary
        while initial_system_username + suffix in usernames_taken:
            n += 1
            suffix = str(n)

        system_username = initial_system_username + suffix
        usernames_taken.add(system_username)

        # Group name and password generation
        system_group_name = user.group.lower().replace(" ", "_")
        password = f"{user.firstname}123".replace(" ", "_")
        comment = f"{user.firstname} {user.lastname} - {user.extension}"

        # Print user creation and password setting commands
        print(f"useradd {system_username} -g {system_group_name} -c \"{comment}\"")
        print(f"echo \"{password}\" | passwd --stdin {system_username}")
        print(f"passwd -e {system_username}")
        print(f"passwd -x 120 {system_username}")

# Entry point to the script
main(sys.argv)
