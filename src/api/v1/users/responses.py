from src.api.schemas import ErrorResponse

UNPROCESSABLE_CONTENT_STATUS = 422

EMAIL_VALIDATION_ERROR_RESPONSE = {
    "description": "Request validation failed",
    "content": {
        "application/json": {
            "example": {
                "detail": [
                    {
                        "type": "value_error",
                        "loc": ["body", "email"],
                        "msg": "value is not a valid email address",
                    }
                ]
            }
        }
    },
}

QUERY_VALIDATION_ERROR_RESPONSE = {
    "description": "Request validation failed",
    "content": {
        "application/json": {
            "example": {
                "detail": [
                    {
                        "type": "greater_than_equal",
                        "loc": ["query", "skip"],
                        "msg": "Input should be greater than or equal to 0",
                    }
                ]
            }
        }
    },
}

UUID_VALIDATION_ERROR_RESPONSE = {
    "description": "Request validation failed",
    "content": {
        "application/json": {
            "example": {
                "detail": [
                    {
                        "type": "uuid_parsing",
                        "loc": ["path", "user_id"],
                        "msg": "Input should be a valid UUID",
                    }
                ]
            }
        }
    },
}

PATCH_VALIDATION_ERROR_RESPONSE = {
    "description": "Request validation failed",
    "content": {
        "application/json": {
            "examples": {
                "empty_body": {
                    "summary": "Empty update body",
                    "value": {
                        "detail": [
                            {
                                "type": "value_error",
                                "loc": ["body"],
                                "msg": "At least one field must be provided for update",
                            }
                        ]
                    },
                },
                "invalid_user_id": {
                    "summary": "Invalid user_id path parameter",
                    "value": {
                        "detail": [
                            {
                                "type": "uuid_parsing",
                                "loc": ["path", "user_id"],
                                "msg": "Input should be a valid UUID",
                            }
                        ]
                    },
                },
                "extra_field": {
                    "summary": "Unknown request body field",
                    "value": {
                        "detail": [
                            {
                                "type": "extra_forbidden",
                                "loc": ["body", "frist_name"],
                                "msg": "Extra inputs are not permitted",
                            }
                        ]
                    },
                },
            }
        }
    },
}

NOT_FOUND_RESPONSE = {"model": ErrorResponse, "description": "User was not found"}
CONFLICT_RESPONSE = {"model": ErrorResponse, "description": "Username or email already exists"}
