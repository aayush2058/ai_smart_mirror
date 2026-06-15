from database.schema import create_database_schema
from services.auth_service import AuthService
from paths import ensure_directories


def main():
    ensure_directories()
    create_database_schema()

    username = input("Admin username: ").strip()
    password = input("Admin password: ")

    service = AuthService()

    try:
        admin_id = service.create_admin(
            username,
            password
        )

        print(
            f"Admin created successfully. ID: {admin_id}"
        )

    except Exception as error:
        print(f"Could not create admin: {error}")


if __name__ == "__main__":
    main()