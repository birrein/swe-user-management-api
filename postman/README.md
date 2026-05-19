# Postman

This folder contains everything needed to test the SWE User Management API from Postman.

## Files

- `swe-user-management-api.postman_collection.json`: collection with health, CRUD, duplicate, and validation checks.
- `local.postman_environment.json`: environment for `http://localhost:8000`.
- `cloud-run.postman_environment.json`: environment for the deployed Cloud Run URL.

## How to Use

1. Open Postman.
2. Import the collection JSON.
3. Import one of the environment JSON files.
4. Select the imported environment.
5. Run the `Smoke CRUD Flow` folder from top to bottom.

The `Create User` request generates a unique username/email and stores the created `user_id` as a collection variable. Later requests reuse that id for get, update, delete, and soft-delete verification.

## Optional CLI Run

If Newman is available:

```bash
npx newman run postman/swe-user-management-api.postman_collection.json \
  -e postman/cloud-run.postman_environment.json
```
