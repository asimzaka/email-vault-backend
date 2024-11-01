from configration import Config
from werkzeug.security import generate_password_hash, check_password_hash
from common.models import User, BillingInfo
from common.repositories import UserRepository, BillingInfoRepository
from flask import Flask, request, jsonify
from flask_cors import CORS
from rococo.auth.tokens import generate_access_token, generate_confirmation_token, validate_confirmation_token

app = Flask(__name__)
CORS(app)
config_instance = Config(app)
config_instance.run_migrations()


def get_repositories(adapter):
    return UserRepository(config_instance, adapter, None, None), BillingInfoRepository(Config.get_db_connection(), None, None)

def get_user_repo():
    return UserRepository(config_instance, Config.get_db_connection(), None, None)

def error_response(message, status_code=400):
    return jsonify({'message': message}), status_code

def send_email(event, data, to_emails):
    message = {"event": event, "data": data, "to_emails": to_emails}
    with config_instance.get_rabbit_mq_connection() as conn:
        conn.send_message(Config.EMAIL_TRANSMITTER_QUEUE_NAME, message)


@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    required_fields = ["firstName", "lastName", "companyName", "email",
                       "password", "nameOnCard", "cardNumber", "expirationDate", "cvv"]

    # Validate required fields
    if not all(field in data for field in required_fields):
        return jsonify({'message': 'All fields are required!'}), 400

    password = generate_password_hash(data['password'])
    try:
        with config_instance.get_db_connection() as adapter:
            user_repo, billing_info_repo = get_repositories(adapter)

            # Check if user already exists
            if user_repo.find_by_email(data['email']):
                return jsonify({'message': 'User with this email already exists!'}), 400

            # Create and save user
            user = User(
                first_name=data['firstName'], last_name=data['lastName'],
                email=data['email'], password=password,
                referral_code=data.get('referralCode'), company_name=data['companyName']
            )
            print("user", user)
            user_first_name = user.first_name
            user.verification_token = generate_confirmation_token(
                user.email, Config.SECRET_KEY)
            user_repo.save(user)

            # Create and save billing info
            billing_info = BillingInfo(
                user=user.entity_id, name_on_card=data['nameOnCard'],
                card_number=data['cardNumber'], expiration_date=data['expirationDate'], cvv=data['cvv']
            )
            billing_info_repo.save(billing_info)

            confirmation_link = f"{Config.FRONTEND_BASE_URL}/sign-in?token={user.verification_token}"
            send_email("USER_CREATED", {
                       "verify_link": confirmation_link, "recipient_name": user_first_name}, [user.email])

        return jsonify({'message': 'User registered. Verify your email.'}), 201

    except Exception as e:
        print(f"Error in register: {e}")
        return jsonify({'message': 'An error occurred during registration.'}), 500


@app.route('/api/check-email', methods=['POST'])
def check_email():
    email = request.get_json().get('email')
    if not email:
        return jsonify({'message': 'Email is required!'}), 400

    try:
        user_repo = get_user_repo()
        exists = bool(user_repo.find_by_email(email))
        return jsonify({'exists': exists, 'message': 'Email check completed.'}), 200

    except Exception as e:
        print(f"Error in check_email: {e}")
        return jsonify({'message': 'An error occurred while checking email.'}), 500


@app.route('/api/resend-verification-email', methods=['POST'])
def resend_verification_email():
    email = request.get_json().get('email')
    if not email:
        return jsonify({'message': 'Email is required!'}), 400

    try:
        user_repo = get_user_repo()
        user = user_repo.find_by_email(email)

        if not user:
            return jsonify({'message': 'User with this email does not exist!'}), 400
        if user.is_verified:
            return jsonify({'message': 'Already verified! Go to login!'}), 400

        # Update verification token and send email
        user.verification_token = generate_confirmation_token(
            user.email, Config.SECRET_KEY)
        user_repo.update_user(user.as_dict())
        confirmation_link = f"{Config.FRONTEND_BASE_URL}/sign-in?verification={user.verification_token}"
        send_email("USER_CREATED", {
                   "verify_link": confirmation_link, "recipient_name": user.first_name}, [user.email])

        return jsonify({'message': 'Verification email has been resent. Please check your email.'}), 200

    except Exception as e:
        print(f"Error in resend_verification_email: {e}")
        return jsonify({'message': 'An error occurred while resending verification email.'}), 500


@app.route('/api/verify-email/<token>', methods=['POST'])
def verify_email(token):
    try:
        email = validate_confirmation_token(
            token, Config.SECRET_KEY, expiration=86400)
        if not email:
            return jsonify({'message': 'Invalid or expired token!'}), 400

        user_repo = get_user_repo()
        user = user_repo.find_by_email(email)
        if not user or user.verification_token != token:
            return jsonify({'message': 'Invalid token!'}), 400

        user.is_verified = True
        user.verification_token = None
        user_repo.update_user(user.as_dict())

        return jsonify({'message': 'User verified successfully!'}), 200

    except Exception as e:
        print(f"Error in verify_email: {e}")
        return jsonify({'message': 'An error occurred during email verification.'}), 500


@app.route('/api/signin', methods=['POST'])
def signin():
    data = request.get_json()
    email, password = data.get('email'), data.get('password')

    try:
        user_repo = get_user_repo()
        user = user_repo.find_by_email(email)

        if user and check_password_hash(user.password, password):
            access_token = generate_access_token(
                user.entity_id, Config.SECRET_KEY, expiration=3600)
            return jsonify({'message': 'Login successful!', "is_verified": user.is_verified, "token": access_token}), 200

        return jsonify({'message': 'Invalid credentials'}), 401

    except Exception as e:
        print(f"Error in signin: {e}")
        return jsonify({'message': 'An error occurred during sign-in.'}), 500


@app.route('/api/password-reset/request', methods=['POST'])
def request_password_reset():
    data = request.get_json()
    email = data.get('email')

    if not email:
        return error_response('Email is required!')

    try:
        user_repo = get_user_repo()
        user = user_repo.find_by_email(email)

        if not user:
            return error_response('No user exists with this email!')

        # Generate and save reset token
        reset_token = generate_confirmation_token(
            user.email, Config.SECRET_KEY)
        user.reset_password_token = reset_token
        user_repo.update_user(user.as_dict())

        # Prepare and send reset link email
        reset_link = f"{Config.FRONTEND_BASE_URL}/create-password?token={reset_token}"
        send_email("RESET_PASSWORD", {
                       "verify_link": reset_link, "recipient_name": user.first_name}, [user.email])

        return jsonify({'message': 'Password reset link has been sent!'}), 200

    except Exception as e:
        print(f"Error in request_password_reset: {e}")
        return error_response('An error occurred while processing your request.', 500)


@app.route('/api/password-reset/<token>', methods=['POST'])
def reset_password(token):
    data = request.get_json()
    password = data.get('password')

    if not password:
        return error_response('Password is required!')

    expiration_time = 86400
    email = validate_confirmation_token(
        token, Config.SECRET_KEY, expiration_time)

    if not email:
        return error_response('Invalid or expired token!')

    try:
        user_repo = get_user_repo()
        user = user_repo.find_by_email(email)

        if not user:
            return error_response('User not found!')

        if user.reset_password_token != token:
            return error_response('Invalid token!')

        # Update password and clear reset token
        user.password = generate_password_hash(password)
        user.reset_password_token = None
        user_repo.update_user(user.as_dict())

        return jsonify({'message': 'User password updated successfully!'}), 200

    except Exception as e:
        print(f"Error in reset_password: {e}")
        return error_response('An error occurred while processing your request.', 500)


@app.route('/api/validate-token/<token>', methods=['GET'])
def validate_token(token):
    expiration_time = 86400
    email = validate_confirmation_token(
        token, Config.SECRET_KEY, expiration_time)

    if not email:
        return error_response('Invalid or expired token!')

    try:
        user_repo = get_user_repo()
        user = user_repo.find_by_email(email)

        if not user or user.reset_password_token != token:
            return error_response('Invalid token!')

        user_name = f"{user.first_name} {user.last_name}"
        return jsonify({
            'message': 'Token is verified!',
            "email": user.email,
            "userName": user_name,
            "company": user.company_name
        }), 200

    except Exception as e:
        print(f"Error in validate_token: {e}")
        return error_response('An error occurred while processing your request.', 500)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
