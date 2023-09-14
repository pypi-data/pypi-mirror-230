import httpx
import typer

from .config import AUTH_PUBLIC_ENDPOINT, ZITRC_FILE, logger

auth_app = app = typer.Typer(name="auth", help="Auth commands")


def authenticate_r(token: str = None):
    if not token:
        if not ZITRC_FILE.exists():
            return False

        with ZITRC_FILE.open("r") as f:
            token = f.read()

    with httpx.Client() as client:
        try:
            r = client.get(
                f"{AUTH_PUBLIC_ENDPOINT}/whoami",
                headers={"Authorization": f"Bearer {token}"},
            )
        except httpx.ConnectError:
            return False

        if r.status_code != 200:
            return False

        user = r.json()
        return user


def verification_code_r(email: str):
    with httpx.Client() as client:
        try:
            r = client.get(
                f"{AUTH_PUBLIC_ENDPOINT}/verification/email?email={email}&expect_registered=false", timeout=20
            )
        except httpx.ConnectError:
            return False

        if r.status_code != 200:
            if r.status_code == 409:
                logger.warning(r.json().get("detail"))

            return False

        token = r.json().get("token")
        return token


def signup_r(email: str, password: str, code: str, token: str):
    with httpx.Client() as client:
        try:
            r = client.post(
                f"{AUTH_PUBLIC_ENDPOINT}/signup/email",
                data={"email": email, "password": password, "code": code, "token": token},
                timeout=20,
            )
        except httpx.ConnectError:
            return False

        if r.status_code != 200:
            if r.status_code == 409:
                logger.warning(r.json().get("detail"))

            return False

        token = r.json().get("access_token")
        return token


def login_r(email: str, password: str):
    with httpx.Client() as client:
        try:
            r = client.post(
                f"{AUTH_PUBLIC_ENDPOINT}/token/email",
                data={"email": email, "password": password},
                timeout=20,
            )
        except httpx.ConnectError:
            return False

        if r.status_code != 200:
            if r.status_code == 401:
                logger.warning(r.json().get("detail"))

            return False

        token = r.json().get("access_token")
        return token


@app.command(name="signup", help="Zit signup")
def signup():
    logger.info("Please go to https://zityspace.cn/signup for signing up. Then run 'zit auth login' to login.")

    # email = typer.prompt("Enter your email", hide_input=False)
    # password = typer.prompt("Enter your password", hide_input=True)

    # token = verification_code_r(email)
    # if not token:
    #     logger.info("Signup failed. Please check your email and try again.")
    #     return

    # code = typer.prompt("Please enter the verification code sent to your email", hide_input=False)

    # token = signup_r(email, password, code, token)
    # if not token:
    #     logger.info("Signup failed. Please check your email and try again.")
    #     return

    # # Store the token in the .zitrc file
    # with ZITRC_FILE.open("w") as f:
    #     f.write(token)

    # # Set the file permissions to be readable and writable only by the owner
    # ZITRC_FILE.chmod(0o600)

    # logger.info("Signup successfully.")


@app.command(name="login", help="Zit login")
def login():
    email = typer.prompt("Enter your email", hide_input=False)
    password = typer.prompt("Enter your password", hide_input=True)

    token = login_r(email, password)
    if not token:
        logger.info("Login failed. Please check your email and password.")
        return

    # Store the API key in the .zitrc file
    with ZITRC_FILE.open("w") as f:
        f.write(token)

    # Set the file permissions to be readable and writable only by the owner
    ZITRC_FILE.chmod(0o600)

    logger.info("Login successfully.")

    whoami()


@app.command(name="logout", help="Zit logout")
def logout():
    if ZITRC_FILE.exists():
        ZITRC_FILE.unlink()  # Delete the .zitrc file
        logger.info("Logout successful. Your API key has been removed.")
    else:
        logger.info("You are not currently logged in.")


@app.command(name="whoami", help="Zit whoami")
def whoami():
    if not ZITRC_FILE.exists():
        logger.info('You are not currently logged in. Please login first by "zit auth login"')
        return

    user = authenticate_r()
    if not user:
        logger.info('Token expired or invalid. Please login by "zit auth login"')
        return

    logger.info({"username": user["username"], "email": user["email"]})

    if not user["username_confirmed"]:
        logger.info(
            "Your username is auto-generated during signup. Please go to https://zityspace.cn/set-username to set your"
            " username."
        )
