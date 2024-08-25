from app.services.env_manager import get_env_variable
print("Expected: ")
print("Actural:" + get_env_variable("GOOGLE_API_KEY"))