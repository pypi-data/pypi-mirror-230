import requests


class JiraHelper:
    def __init__(self, server_url, email, api_token):
        self.server_url = server_url.rstrip('/')
        self.auth = (email, api_token)
        self.headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def create_ticket(self, project_key, summary, description, issue_type):
        issue_data = {
            "fields": {
                "project": {"key": project_key},
                "summary": summary,
                "description": description,
                "issuetype": {"name": issue_type},
            }
        }

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

            return ticket_url
        else:
            return False

    def delete_ticket(self, ticket_key):
        if not self.if_exist_ticket(ticket_key):
            return False

        response = requests.delete(
            f"{self.server_url}/rest/api/2/issue/{ticket_key}",
            headers=self.headers,
            auth=self.auth
        )

        if response.status_code == 204:  # HTTP 204 No Content, indicates success.
            return True
        else:
            return False

    def get_transitions(self, ticket_key, transition_to):
        response = requests.get(
            f"{self.server_url}/rest/api/2/issue/{ticket_key}/transitions",
            headers=self.headers,
            auth=self.auth
        )

        if response.status_code == 200:  # HTTP 200 OK
            transitions = response.json().get("transitions", [])
            for transition in transitions:
                if str(transition["name"]).lower() == transition_to:
                    return transition["id"]
            return False
        else:
            return False

    def transition_ticket(self, ticket_key, transition_input):
        if str(transition_input).isdigit():
            transition_id = transition_input
        else:
            transition_id = self.get_transitions(ticket_key, str(transition_input).lower())
            if not transition_id:
                return False

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
            return True
        else:
            return False

    def if_exist_ticket(self, ticket_key):

        response = requests.get(
            f"{self.server_url}/rest/api/2/issue/{ticket_key}",
            headers=self.headers,
            auth=self.auth
        )

        if response.status_code == 200:  # HTTP 200 OK, indicates the ticket exists.
            return True
        elif response.status_code == 404:  # HTTP 404 Not Found, indicates the ticket does not exist.
            return False
        else:
            return False

    def comment_ticket(self, ticket_key, comment_text):
        if not self.if_exist_ticket(ticket_key):
            return False

        payload = {
            "body": comment_text
        }

        response = requests.post(
            f"{self.server_url}/rest/api/2/issue/{ticket_key}/comment",
            headers=self.headers,
            auth=self.auth,
            json=payload
        )

        if response.status_code == 201:  # HTTP 201 Created, indicates success.
            comment_id = response.json().get("id")
            comment_url = f"{self.server_url}/browse/{ticket_key}?focusedCommentId={comment_id}#comment-{comment_id}"
            return comment_url
        else:
            # print(f"Failed to add comment to ticket {ticket_key}. Status code: {response.status_code}, Response: {response.text}")
            return False

    def jql_ticket(self, jql_query, max_results=None):
        all_ticket_keys = []

        start_at = 0
        batch_size = 50  # This number can be adjusted based on your preference

        while True:
            payload = {
                "jql": jql_query,
                "fields": ["key"],  # We only need the ticket key
                "maxResults": batch_size,
                "startAt": start_at
            }

            response = requests.post(
                f"{self.server_url}/rest/api/2/search",
                headers=self.headers,
                auth=self.auth,
                json=payload
            )

            if response.status_code == 200:  # HTTP 200 OK, indicates success.
                issues = response.json().get("issues", [])
                ticket_keys = [issue["key"] for issue in issues]
                all_ticket_keys.extend(ticket_keys)

                # Check if we need to fetch more results or if we've reached the limit if one was set
                if not max_results:
                    if len(issues) < batch_size:
                        break
                    else:
                        start_at += batch_size
                else:
                    if len(all_ticket_keys) >= max_results:
                        all_ticket_keys = all_ticket_keys[:max_results]
                        break
                    elif len(issues) < batch_size:
                        break
                    else:
                        start_at += batch_size
            else:
                return False

        # print(f"Found {len(all_ticket_keys)} tickets.")
        return all_ticket_keys
