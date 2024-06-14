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
            "value": [{"url": "https://drive.google.com/file/d/1i86ZEygL4i2ZHvVD9akzt8O48Rr4cxw0/view?usp=sharing", "filePath": "/Users/danieldacosta/Documents/RadicalAI/kai-ai-backend/app/api/tests/linear_regression.pdf"}]
        }
    ]
  }
}
```