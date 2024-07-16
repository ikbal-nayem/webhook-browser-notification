from functools import wraps
from firebase_admin import auth
from flask import redirect, url_for, request, jsonify


def authenticate(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        session_cookie = request.cookies.get('session')

        if not session_cookie:
            # Redirect to the login route if no session cookie is found
            # (This is for HTML-based applications)
            return redirect(url_for('authentication'))

        try:
            # Verify the session cookie
            decoded_claims = auth.verify_session_cookie(session_cookie)
            # ... (You can access user information from decoded_claims)
            return func(*args, **kwargs)

        except ValueError as e:
            # Return a JSON error response if the cookie is invalid
            # (This is for API-based applications)
            return jsonify({'error': str(e)}), 401

    return wrapper
