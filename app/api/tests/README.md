# API Tests


**/submit-tool**

```json

{
  "user": {
    "id": "test123",
    "fullName": "YourName",
    "email": "test123@gmail.com"
  },
  "type": "chat",
  "tool_data": {
    "tool_id": 0,
    "inputs": [
        {
            "name": "topic",
            "value": "Linear Regression"
        },
        {
            "name": "num_questions",
            "value": 3
        },
        {
            "name": "files",
            "value": ["/Users/danieldacosta/Documents/RadicalAI/kai-ai-backend/app/api/tests/linear_regression.pdf"]
        }
    ]
  }
}
```