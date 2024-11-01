from rococo.repositories.mysql import MySqlRepository
from common.models import User

class UserRepository(MySqlRepository):
    def __init__(self, config, adapter=None, message_adapter=None, message_queue_name=None):
        """Initializes UserRepository with a given config for database connection."""
        super().__init__(adapter, User, message_adapter, message_queue_name)
        self.config = config

    def find_by_email(self, email: str):
        conditions = {"email": email}
        return self.get_one(conditions)

    def update_user(self, user_data: dict):
        """Updates user data using a fresh adapter connection from the provided config."""
        with self.config.get_db_connection() as adapter:
            try:
                adapter.save(self.table_name, user_data)
            except Exception as e:
                print(f"Error updating user: {e}")
                adapter.rollback()
                raise
