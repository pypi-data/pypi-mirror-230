import requests


class JiraHelper:
    def __init__(self, server_url, email, api_token):
        """
        Initialize the Jira helper.

        :param server_url: URL of the Jira server.
        :param email: Email associated with Jira account.
        :param api_token: Jira API token.
        """
        self.server_url = server_url.rstrip('/')
        self.auth = (email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_ticket(self, project_key, summary, description, issue_type):
        """
        Create a Jira ticket.

        :param project_key: Key of the Jira project.
        :param summary: Ticket summary.
        :param description: Ticket description.
        :param issue_type: Type of the issue (e.g., Bug, Task). Default is "Bug".
        :return: Created Jira issue object or None if failed.
        """
        issue_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
            }
        }

        print("Creating ticket, please wait...")

        response = requests.post(
            f"{self.server_url}/rest/api/2/issue",
            json=issue_data,
            headers=self.headers,
            auth=self.auth
        )

        if response.status_code == 201:  # HTTP 201 Created
            ticket_data = response.json()
            ticket_key = ticket_data["key"]
            ticket_url = f"{self.server_url}/browse/{ticket_key}"

            # Print success message with ticket details
            print(f"Ticket created successfully!")
            print(f"Ticket Key: {ticket_key}")
            print(f"Ticket URL: {ticket_url}")

            return ticket_data
        else:
            print(f"Failed to create ticket. Status code: {response.status_code}, Response: {response.text}")
            return None

    def delete_ticket(self, ticket_key):
        """
        Delete a Jira ticket based on the provided ticket key.

        :param ticket_key: The key of the Jira ticket to delete (e.g., "PROJ-123").
        :return: True if successfully deleted, False otherwise.
        """

        print("Deleting ticket, please wait...")

        response = requests.delete(
            f"{self.server_url}/rest/api/2/issue/{ticket_key}",
            headers=self.headers,
            auth=self.auth
        )

        if response.status_code == 204:  # HTTP 204 No Content, indicates success.
            print(f"Ticket created successfully!")
            return True
        else:
            print(
                f"Failed to delete ticket {ticket_key}. Status code: {response.status_code}, Response: {response.text}")
            return False

    def get_transitions(self, ticket_key, transition_to):
        """
        Get all available transitions for a Jira ticket based on the provided ticket key.

        :param ticket_key: The key of the Jira ticket (e.g., "PROJ-123").
        :return: List of available transitions or None if there's an error.
        """
        print(f"Fetching available transitions for ticket {ticket_key}...")
        response = requests.get(
            f"{self.server_url}/rest/api/2/issue/{ticket_key}/transitions",
            headers=self.headers,
            auth=self.auth
        )

        if response.status_code == 200:  # HTTP 200 OK
            print(f"Successfully fetched transitions for ticket {ticket_key}.")
            transitions = response.json().get("transitions", [])
            for transition in transitions:
                if str(transition["name"]).lower() == transition_to:
                    return transition["id"]
            print(f"Transition '{transition_to}' not found for ticket {ticket_key}.")
            return None
        else:
            print(
                f"Failed to get transitions for ticket {ticket_key}. Status code: {response.status_code}, Response: {response.text}")
            return None

    def transition_ticket(self, ticket_key, transition_name):
        """
        Transition a Jira ticket using the provided transition name.

        :param ticket_key: The key of the Jira ticket (e.g., "PROJ-123").
        :param transition_name: The name of the transition to perform.
        :return: A message indicating the result.
        """
        print(f"Initiating transition '{transition_name}' for ticket {ticket_key}...")
        transition_id = self.get_transitions(ticket_key, str(transition_name).lower())
        if not transition_id:
            return f"Failed to get available transitions for ticket {ticket_key}. Case sensitivity is not a problem."

        print(f"Found transition ID for '{transition_name}'. Proceeding to apply transition...")

        # Perform the transition
        payload = {
            "transition": {
                "id": transition_id
            }
        }

        response = requests.post(
            f"{self.server_url}/rest/api/2/issue/{ticket_key}/transitions",
            headers=self.headers,
            auth=self.auth,
            json=payload
        )

        if response.status_code == 204:  # HTTP 204 No Content, indicates success.
            print(f"Transition '{transition_name}' successfully applied to ticket {ticket_key}.")
            return f"Ticket {ticket_key} successfully transitioned using '{transition_name}'."
        else:
            print(f"Failed to transition ticket {ticket_key} using '{transition_name}'.")
            return f"Failed to transition ticket {ticket_key} using '{transition_name}'. Status code: {response.status_code}, Response: {response.text}"