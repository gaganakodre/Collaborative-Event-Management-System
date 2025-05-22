# Collaborative-Event-Management-System
(A NeoFi Backend Challenge) - Curated by [Shreegowri HD]

### Run Locally
```bash
python -m api.app
```
(To access the deployed version on Render, please visit : https://collaborative-event-management-system.onrender.com/apidocs/ )

A Flask-based RESTful API that enables users to create, manage, and collaborate on events with full version control. Features include secure authentication, event sharing, permission control, and changelog tracking.

# Authentication APIs
- **Register**: Create a new user with secure password hashing.

- **Login**: Authenticate user and return a JWT token.

- **Refresh Token** : Generate a new access token using a valid refresh token.

- **Logout** : Invalidate the user's session.

# Event Management APIs
- **Create Event** : Add new events with title and start time.

- **Get Events** : Retrieve paginated events for the logged-in user.

- **Get Event by ID** : Fetch detailed event information.

- **Update Event** : Modify event details and track changes via versioning.

- **Bulk Create Events** : Add multiple events in a single request.

# Collaboration APIs
- **Share Event** : Grant access to another user with a specific role.

- **List Permissions** : View users and their roles for an event.

- **Update Permission** : Change the assigned role of a user.

- **Remove Permission** : Revoke a user's access to an event.

# Version History APIs
- **Get Version** : Fetch a specific version of an event.

- **Rollback Version** : Restore an event to a previous version.

- **Get Changelog** : View the changelog of event updates.

- **Get Version Diff** : Compare and highlight changes between versions.

