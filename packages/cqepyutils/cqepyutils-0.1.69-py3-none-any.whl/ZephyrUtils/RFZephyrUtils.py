import requests
import json

# Zephyr API endpoint and bearer token
zephyr_base_url = 'https://your-jira-instance/rest/zapi/latest'
bearer_token = 'your_bearer_token'


# Create a new test case
def create_test_case(project_id, summary, description, issue_type_id):
    create_test_case_url = f"{zephyr_base_url}/teststep/{project_id}/"

    payload = {
        "fields": {
            "project": {
                "id": project_id
            },
            "summary": summary,
            "description": description,
            "issuetype": {
                "id": issue_type_id
            }
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bearer_token}'
    }

    response = requests.post(create_test_case_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 201:
        print("Test case created successfully.")
    else:
        print("Failed to create test case.")
        print(response.text)


# Update an existing test case
def update_test_case(test_case_id, new_summary):
    update_test_case_url = f"{zephyr_base_url}/teststep/{test_case_id}/"

    payload = {
        "fields": {
            "summary": new_summary
        }
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bearer_token}'
    }

    response = requests.put(update_test_case_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("Test case updated successfully.")
    else:
        print("Failed to update test case.")
        print(response.text)


# Update execution results for a test case
def update_execution_results(execution_id, status):
    update_execution_url = f"{zephyr_base_url}/execution/{execution_id}/execute"

    payload = {
        "status": status
    }

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bearer_token}'
    }

    response = requests.put(update_execution_url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print("Execution results updated successfully.")
    else:
        print("Failed to update execution results.")
        print(response.text)


# Get project ID by project name
def get_project_id_by_name(project_name):
    get_project_url = f"{zephyr_base_url}/project"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bearer_token}'
    }

    response = requests.get(get_project_url, headers=headers)

    if response.status_code == 200:
        projects = response.json()
        for project in projects:
            if project["name"] == project_name:
                return project["id"]
        print(f"Project with name '{project_name}' not found.")
        return None
    else:
        print("Failed to fetch projects.")
        print(response.text)
        return None


# Get test case ID by test case name and folder name
def get_test_case_id_by_name(test_case_name, folder_name=None):
    get_test_cases_url = f"{zephyr_base_url}/teststep"

    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {bearer_token}'
    }

    response = requests.get(get_test_cases_url, headers=headers)

    if response.status_code == 200:
        test_cases = response.json()
        for test_case in test_cases:
            if test_case["fields"]["summary"] == test_case_name:
                if folder_name:
                    if "folder" in test_case["fields"] and test_case["fields"]["folder"]:
                        if folder_name == test_case["fields"]["folder"]["folderName"]:
                            return test_case["id"]
                    continue
                else:
                    return test_case["id"]

        print(f"Test case with name '{test_case_name}' not found.")
        return None
    else:
        print("Failed to fetch test cases.")
        print(response.text)
        return None


if __name__ == "__main__":
    # Replace these values with your own
    project_name = "Your_Project_Name"
    test_case_name = "Your_Test_Case_Name"
    folder_name = "Your_Folder_Name"  # Optional, remove or set to None if not using folders

    # Get project ID by project name
    project_id = get_project_id_by_name(project_name)
    if project_id:
        print(f"Project ID for '{project_name}': {project_id}")

    # Get test case ID by test case name (with optional folder name)
    test_case_id = get_test_case_id_by_name(test_case_name, folder_name)
    if test_case_id:
        print(f"Test Case ID for '{test_case_name}': {test_case_id}")
