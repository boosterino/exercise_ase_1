from flakon import JsonBlueprint
from flask import abort, jsonify, request

from bedrock_a_party.classes.party import CannotPartyAloneError, Party

parties = JsonBlueprint('parties', __name__)

_LOADED_PARTIES = {}  # dict of available parties
_PARTY_NUMBER = 0  # index of the last created party


@parties.route("/parties", methods=['GET', 'POST'])
def all_parties():
    result = ""
    if request.method == 'POST':
        try:
            result = create_party(request)
        except:
            abort(400)


    elif request.method == 'GET':
        result = get_all_parties()

    return result


@parties.route("/parties/loaded")
def loaded_parties():
    return jsonify({'loaded_parties': _PARTY_NUMBER })


@parties.route("/party/<id>",methods=['GET', 'DELETE'])
def single_party(id):
    global _LOADED_PARTIES,_PARTY_NUMBER
    result = ""

    exists_party(id)

    if 'GET' == request.method:
       return jsonify( _LOADED_PARTIES[id].serialize())

    elif 'DELETE' == request.method:
        _LOADED_PARTIES.pop(id)
        _PARTY_NUMBER -= 1

    return result


@parties.route("/party/<id>/foodlist", methods=['GET'])
def get_foodlist(id):
    global _LOADED_PARTIES
    result = ""

    exists_party(id)

    if 'GET' == request.method:

        appo = Party.get_food_list(_LOADED_PARTIES[id])

        return jsonify({"foodlist":appo.serialize()})

    return result


@parties.route("/party/<id>/foodlist/<user>/<item>", methods=['POST', 'DELETE'])
def edit_foodlist(id, user, item):
    global _LOADED_PARTIES

    exists_party(id)

    result = ""

    if 'POST' == request.method:

        try:

            Party.add_to_food_list(_LOADED_PARTIES[id],item,user)
            appo = Party.get_food_list(_LOADED_PARTIES[id])
            return appo.serialize()[0]

        except:
            abort(401)


    if 'DELETE' == request.method:

        try:
            Party.remove_from_food_list(_LOADED_PARTIES[id],item,user)
            return jsonify({"msg" : "Food deleted!"})
        except:
             abort(400)


    return result

#
# These are utility functions. Use them, DON'T CHANGE THEM!!
#

def create_party(req):
    global _LOADED_PARTIES, _PARTY_NUMBER

    # get data from request
    json_data = req.get_json()


    # list of guests
    try:
        guests = json_data['guests']
    except:
        raise CannotPartyAloneError("you cannot party alone!")

    # add party to the loaded parties lists
    _LOADED_PARTIES[str(_PARTY_NUMBER)] = Party(_PARTY_NUMBER, guests)
    _PARTY_NUMBER += 1

    return jsonify({'party_number': _PARTY_NUMBER - 1})


def get_all_parties():
    global _LOADED_PARTIES

    return jsonify(loaded_parties=[party.serialize() for party in _LOADED_PARTIES.values()])


def exists_party(_id):
    global _PARTY_NUMBER
    global _LOADED_PARTIES

    if int(_id) > _PARTY_NUMBER:
        abort(404)  # error 404: Not Found, i.e. wrong URL, resource does not exist
    elif not(_id in _LOADED_PARTIES):
        abort(410)  # error 410: Gone, i.e. it existed but it's not there anymore
