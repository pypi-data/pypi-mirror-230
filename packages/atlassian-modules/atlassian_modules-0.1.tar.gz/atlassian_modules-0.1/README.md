# Jira Helper Module

This Python module provides easy and concise methods to interact with Atlassian Jira. With this module, you can:

1. Create a Jira ticket.
2. Delete a Jira ticket.
3. Transition a Jira ticket.

## Getting Started

### Connectivity to Atlassian Jira

To initialize a connection to Jira, instantiate the `JiraHelper` class with your Jira URL, email, and API token:

```python
jira_helper = JiraHelper(JIRA_URL, EMAIL, API_TOKEN)
```
# Features

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
```

Parameters:
- `ticket_key`: The unique key of the ticket you want to transition.
- `transition_name`: The name of the transition you want to apply. This is not a case sensitive.

# Data Privacy Note

🔒 **We respect your privacy**: This module does **not** store any of your data anywhere. It simply interacts with the Atlassian Jira API to perform the requested operations. Ensure you manage your connection details securely.

# Future Developments

In upcoming releases, there are plans to enhance the `transition_ticket` method:

- The method will soon support both `transition_name` and `transition_ticket` parameters within the same function. Based on what you've provided, the module will be intelligent enough to understand and act accordingly.

Example:

```python
# This function call might be able to interpret both transition name and ticket in the future
jira_helper.transition_ticket("XX-1234", "In Progress")
# or
jira_helper.transition_ticket("XX-1234", "31")
```

Please keep an eye on the repository's release notes for the latest updates and feature rollouts.
