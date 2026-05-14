"""
Account Service

This microservice handles the lifecycle of Accounts
"""

from flask import jsonify, request, make_response, abort, url_for
from service.models import Account
from service.common import status
from . import app


# ============================================================
# Health Endpoint
# ============================================================

@app.route("/health")
def health():
    """Health Status"""
    return jsonify(dict(status="OK")), status.HTTP_200_OK


# ============================================================
# GET INDEX
# ============================================================

@app.route("/")
def index():
    """Root URL response"""
    return jsonify(
        name="Account REST API Service",
        version="1.0"
    ), status.HTTP_200_OK


# ============================================================
# CREATE ACCOUNT
# ============================================================

@app.route("/accounts", methods=["POST"])
def create_accounts():
    """Creates an Account"""
    app.logger.info("Request to create an Account")

    check_content_type("application/json")

    account = Account()
    account.deserialize(request.get_json())
    account.create()

    message = account.serialize()

    location_url = url_for(
        "get_accounts",
        account_id=account.id,
        _external=True
    )

    response = make_response(
        jsonify(message),
        status.HTTP_201_CREATED
    )
    response.headers["Location"] = location_url

    return response


# ============================================================
# LIST ACCOUNTS
# ============================================================

@app.route("/accounts", methods=["GET"])
def list_accounts():
    """List all accounts"""
    app.logger.info("Request to list all accounts")

    accounts = Account.all()
    return [a.serialize() for a in accounts], 200


# ============================================================
# READ ACCOUNT
# ============================================================

@app.route("/accounts/<int:account_id>", methods=["GET"])
def get_accounts(account_id):

    account = Account.find(account_id)

    if not account:
        abort(404, "Account not found")

    return account.serialize(), 200


# ============================================================
# UPDATE ACCOUNT
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

    return account.serialize(), 200


# ============================================================
# DELETE ACCOUNT
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
# UTILITY
# ============================================================

def check_content_type(media_type):
    """Validate request Content-Type"""
    content_type = request.headers.get("Content-Type")

    if content_type == media_type:
        return

    app.logger.error("Invalid Content-Type: %s", content_type)

    abort(
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        f"Content-Type must be {media_type}"
    )
