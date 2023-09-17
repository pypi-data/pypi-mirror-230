# Table of Content
- Jira Helper Module
- Prerequisites
- Getting Started
  - Connectivity to Atlassian Jira
  - Create a Jira ticket
  - Delete a Jira ticket
  - Transition a Jira ticket
  - If exist a Jira ticket
- Data Privacy Note
- Future Developments
- Release Notes
  - Release 0.1.2
  - Release 0.1.1
  - Release 0.1

# Jira Helper Module

This Python module provides easy and concise methods to interact with Atlassian Jira. With this module, you can:

1. Connectivity to Atlassian Jira
2. Create a Jira ticket
3. Delete a Jira ticket
4. Transition a Jira ticket
5. If exist a Jira ticket

# Prerequisites
```python
from atlassian_modules import JiraHelper
```

# Getting Started

## Connectivity to Atlassian Jira

To initialize a connection to Jira, instantiate the `JiraHelper` class with your Jira URL, email, and API token:

```python
jira_helper = JiraHelper(JIRA_URL, EMAIL, API_TOKEN)
```

## 1. Create a Jira Ticket

- You can create a new Jira ticket using the `create_ticket` method:

```python
jira_helper.create_ticket("XX", "Test Issue", "This is a test issue created from main.py", "Task")
```

Parameters:
- `project_key`: The key of the project in which the ticket should be created.
- `summary`: A brief summary of the issue.
- `description`: A detailed description of the issue.
- `issue_type`: The type of the issue (e.g., "Task", "Bug", etc.).

## 2. Delete a Jira Ticket

- To delete a ticket, use the `delete_ticket` method:

```python
jira_helper.delete_ticket("XX-1234")
```

Parameter:
- `ticket_key`: The unique key of the ticket you want to delete.

## 3. Transition a Jira Ticket

- To transition a ticket to a different status, use the `transition_ticket` method:

```python
jira_helper.transition_ticket("XX-1234", "In Progress")
# or
jira_helper.transition_ticket("XX-1234", 31)
```

Parameters:
- `ticket_key`: The unique key of the ticket you want to transition.
- `transition_name`: The name of the transition you want to apply. This is not a case sensitive when you apply the transtion name.

## 4. If exist a Jira Ticket

- To check if a ticket exist, use the `if_exist_ticket` method:

```python
jira_helper.if_exist_ticket("XX-1234")
```

Parameters:
- `ticket_key`: The unique key of the ticket you want to check that exist.

# Data Privacy Note

🔒 **We respect your privacy**: This module does **not** store any of your data anywhere. It simply interacts with the Atlassian Jira API to perform the requested operations. Ensure you manage your connection details securely.

# Future Developments

In upcoming releases, I am working to add below functions...

- `jql_ticket`
- `comment_ticket`

Please keep an eye on the repository's release notes for the latest updates and feature rollouts.

# Release Notes
## Release 0.1.2.1 (16 Sep 2023)
-- Updated the `README.md` format

## Release 0.1.2 (16 Sep 2023)
- Check Jira ticket exist `if_exist_ticket` added
- Updated the `README.md` format

## Release 0.1.1 (16 Sep 2023)
- Transition a Jira ticket (Can pass transition ID too) `transition_ticket`
- Modified `README.md` for clarity use of this module

## Release 0.1 (16 Sep 2023)
- Create a Jira ticket `create_ticket`
- Delete a Jira ticket `delete_ticket`
- Transition a Jira ticket (Strict to Transition Name) `transition_ticket`