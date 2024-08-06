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
            "value": [{"url": "https://proceedings.neurips.cc/paper_files/paper/2012/file/c399862d3b9d6b76c8436e924a68c45b-Paper.pdf"}]
        }
    ]
  }
}
```