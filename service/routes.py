"""
Account Service - REST API
"""

from flask import jsonify, request, make_response, abort, url_for
from service.models import Account
from service.common import status
from . import app


# ============================================================
# Health
# ============================================================

@app.route("/health")
def health():
    return jsonify(status="OK"), status.HTTP_200_OK


# ============================================================
# Index
# ============================================================

@app.route("/")
def index():
    return jsonify(
        name="Account REST API Service",
        version="1.0"
    ), status.HTTP_200_OK


# ============================================================
# Create Account
# ============================================================

@app.route("/accounts", methods=["POST"])
def create_accounts():

    app.logger.info("Request to create an Account")

    check_content_type("application/json")

    account = Account()
    account.deserialize(request.get_json())
    account.create()

    response = make_response(
        jsonify(account.serialize()),
        status.HTTP_201_CREATED
    )

    response.headers["Location"] = url_for(
        "get_accounts",
        account_id=account.id,
        _external=True
    )

    return response


# ============================================================
# List Accounts
# ============================================================

@app.route("/accounts", methods=["GET"])
def list_accounts():

    app.logger.info("Request to list all accounts")

    accounts = Account.all()
    return jsonify([a.serialize() for a in accounts]), 200


# ============================================================
# Get Account
# ============================================================

@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):

    account = Account.find(account_id)

    if not account:
        abort(404, "Account not found")

    return jsonify(account.serialize()), 200


# ============================================================
# Update Account
# ============================================================

@app.route("/accounts/<int:account_id>", methods=["PUT"])
def update_account(account_id):

    app.logger.info("Update account %s", account_id)

    account = Account.find(account_id)

    if not account:
        abort(404, f"Account {account_id} not found")

    data = request.get_json()

    account.name = data.get("name", account.name)
    account.email = data.get("email", account.email)
    account.address = data.get("address", account.address)

    account.update()

    return jsonify(account.serialize()), 200


# ============================================================
# Delete Account
# ============================================================

@app.route("/accounts/<int:account_id>", methods=["DELETE"])
def delete_account(account_id):

    app.logger.info("Delete account %s", account_id)

    account = Account.find(account_id)

    if not account:
        abort(404, f"Account {account_id} not found")

    account.delete()

    return "", 204


# ============================================================
# Utility
# ============================================================

def check_content_type(media_type):

    content_type = request.headers.get("Content-Type")

    if content_type != media_type:
        app.logger.error("Invalid Content-Type: %s", content_type)
        abort(
            status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            f"Content-Type must be {media_type}"
        )
