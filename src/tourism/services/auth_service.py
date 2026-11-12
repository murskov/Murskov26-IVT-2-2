from tourism.services.security import hash_password, verify_password

class AuthService:
    def __init__(self, client_repository, manager_repository, administrator_repository):
        self.clients = client_repository
        self.managers = manager_repository
        self.administrators = administrator_repository

    def _login_is_used(self, login):
        return bool(self.clients.get_by_login(login) or self.managers.get_by_login(login) or self.administrators.get_by_login(login))

    def register_client(self, full_name, phone, email, login, password):
        if not full_name.strip() or not phone.strip() or not login.strip() or len(password) < 6:
            raise ValueError("Заполните имя, телефон и логин; пароль должен быть не короче 6 символов")
        if self._login_is_used(login.strip()):
            raise ValueError("Такой логин уже занят")
        if self.clients.get_by_phone(phone.strip()):
            raise ValueError("Клиент с таким телефоном уже существует")
        return self.clients.create(full_name.strip(), phone.strip(), email.strip(), login.strip(), hash_password(password))

    def login(self, login, password):
        client = self.clients.get_by_login(login)
        if client and client.password_hash and verify_password(password, client.password_hash):
            return "Клиент", client
        manager = self.managers.get_by_login(login)
        if manager and verify_password(password, manager.password_hash):
            return "Менеджер", manager
        admin = self.administrators.get_by_login(login)
        if admin and verify_password(password, admin.password_hash):
            return "Администратор", admin
        return None

    def create_first_admin(self, full_name, login, password):
        if self.administrators.get_all():
            raise ValueError("Администратор уже существует")
        if not full_name.strip() or not login.strip() or len(password) < 6:
            raise ValueError("Имя и логин обязательны, пароль — минимум 6 символов")
        if self._login_is_used(login.strip()):
            raise ValueError("Такой логин уже занят")
        return self.administrators.create(full_name.strip(), login.strip(), hash_password(password))

    def create_manager(self, full_name, login, password):
        if not full_name.strip() or not login.strip() or len(password) < 6:
            raise ValueError("Имя и логин обязательны, пароль — минимум 6 символов")
        if self._login_is_used(login.strip()):
            raise ValueError("Такой логин уже занят")
        return self.managers.create(full_name.strip(), login.strip(), hash_password(password))
