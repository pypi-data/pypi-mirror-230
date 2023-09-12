# perun.proxygui

Pages used by microservices
in [satosacontrib.perun](https://gitlab.ics.muni.cz/perun-proxy-aai/python/satosacontrib-perun).

## Installation

The recommended way to install is via pip:

```
pip3 install perun.proxygui
```

Alternatively, you can clone the repository and run:

```
pip3 install .
```

You also need to install the appropriate sqlalchemy driver. For PostgreSQL, you can include the `postgresql` extra, which will install [psycopg2-binary](https://pypi.org/project/psycopg2-binary/):

```
pip3 install perun.proxygui[postgresql]
```

## Configuration

### General

Copy `perun.proxygui.yaml` from config_templates to `/etc/` (it needs to reside at `/etc/perun.proxygui.yaml`) and
adjust to your needs.

The `global_cfg_filepath` option needs to point to the location of the global microservice config from
the [satosacontrib.perun](https://gitlab.ics.muni.cz/perun-proxy-aai/python/satosacontrib-perun) module. You also need
to set the attribute map config.

At the very least, you need to copy the config templates:

```
cp config_templates/perun.proxygui.yaml /etc/perun.proxygui.yaml
cp ../satosacontrib-perun/satosacontrib/perun/config_templates/attribute_typing.yaml /etc/
cp ../satosacontrib-perun/satosacontrib/perun/config_templates/microservices_global.yaml /etc/
```

Then change the following line in `/etc/perun.proxygui.yaml`:

```
global_cfg_filepath: /etc/microservices_global.yaml
```

And the following line in `/etc/microservices_global.yaml`:

```
attrs_cfg_path: /etc/attribute_typing.yaml
```

### Backchannel logout

Analogous to general configuration. Copy `backchannel-logout.yaml` from config_templates to `/etc/` so the resulting
filepath is `/etc/backchannel-logout.yaml` and adjust to your needs.

This configuration is necessary for using `/backchannel-logout` endpoint. It
performs [OIDC Back-Channel Logout 1.0](https://openid.net/specs/openid-connect-backchannel-1_0.html) using
the [idpy-oidc](https://github.com/IdentityPython/idpy-oidc) library.

OIDC builds upon OAuth 2.0. Config options `issuer`, `client_id` and `client_secret` are terms explained
in [OAuth 2.0 [RFC6749]](https://datatracker.ietf.org/doc/html/rfc6749#section-2.2).

The endpoint accepts
an [OIDC Logout Token](https://openid.net/specs/openid-connect-backchannel-1_0.html#LogoutToken)
which is a JWT with the necessary information for performing back-channel logout. Therefore, the `key_conf` setting must
contain paths to the key pair configured between an OP (our endpoint) which decrypts the JWT and an RP (endpoint caller)
who encrypts the JWT. Options `private_path` and `public_path` represent filepaths to the private/public key.
Settings `key_defs` specify key types and `read_only` determines whether the keys are read-only. Both come from the
[idpy-oidc](https://github.com/IdentityPython/idpy-oidc) library.

## Run

### uWSGI

To run this Flask app with uWSGI, use the callable `perun.proxygui.app:get_app`, e.g.

```
mount = /proxygui=perun.proxygui.app:get_app
```

### local development

```
python3 perun/proxygui/app.py
```

Now the app is available at `http://localhost:5000/` (e.g. `http://localhost:5000/banned-users/`).

## Translations

### Babel

First you need to generate `.pot` file: `pybabel extract -F babel.cfg -o messages.pot .`

Next step is to generate `.po` file: `pybabel init -i messages.pot -d perun/proxygui/gui/translations -D messages -l <language_code>`

- replace <language code> with given language code (eg: fr)

Then you need to, manually or using a tool like [Poedit](https://poedit.net/), write your translations in the generated `.po` file and compile it: `pybabel compile -d perun/proxygui/gui/translations -D messages`

- note that if the `.pot` file is already created and you want to add new language ignore the first step

## API

### Consent

This API handles consents - checks if any consent was given by the user and asks him to give a new one if not. API is connected to GUI where user can choose which attributes are to be consented. This API is strongly based on [CMservice](https://github.com/its-dirg/CMservice). Some of the differences:

- GUI
- usage of MongoDB
- user_id and requester_name are sent from micro_service and are part of the consent stored in the database
- we can define attributes which are ignored (in the config)

### Back-channel logout

Performs [OIDC Back-Channel Logout 1.0](https://openid.net/specs/openid-connect-backchannel-1_0.html) in the role of RP.

**Endpoint:** `/backchannel-logout`

**Method:** `POST`

**Description**: The logout token **must** include an attribute `sub` containing
subject id
(id of the user to be logged out). It **may** also include `sid` containing an id of
a specific session of user identified by `sub`. In case the request contains `sid`
and the session with given `sid` exists and belongs to the user with provided `sub`, it
will be revoked, otherwise nothing happens. If **only** `sub` is provided, **all** the
sessions of the user with given `sub` will be revoked. If the user doesn't exist,
nothing happens.

Calling this endpoint revokes user's SSP sessions, Mitre tokens and SATOSA sessions.
Refresh tokens will stay intact as per [OIDC standard](https://openid.net/specs/openid-connect-backchannel-1_0.html#BCActions).

**Example logout token**:

```
{
  "iss": "https://server.example.com",
  "sub": "123456@user",
  "sid": "2d1a...5264be", # OPTIONAL
  "aud": "s6BhdRkqt3",
  "iat": 1471566154,
  "jti": "bWJq",
  "events": {
      "http://schemas.openid.net/event/backchannel-logout": {}
  }
}
```

**Input
arguments:** [OIDC Logout Token](https://openid.net/specs/openid-connect-backchannel-1_0.html#LogoutToken)
in the request body.

**Result:**

- `HTTP Bad Request [400]` and an error message in the response body if the logout wasn't performed successfully
- `HTTP No Content [204]` indicating a successful logout

### Ban

Provides management of Perun user bans. A banned user can not log in to the system.

<br></br>
**Endpoint:** `/banned-users`

**Method:** `PUT`

**Description:** This endpoint adds all user bans provided in the request input data to the database. This effectively
bans the Perun users from logging in to the system. If the user is already banned, their ban is replaced with the latest
one (the one currently provided in the request).

Calling this endpoint revokes user's SSP sessions, Mitre tokens, SATOSA sessions and
refresh tokens.

**Example ban:**

```
{
    "description": "Misuse of resources.",
    "facilityId": "1",
    "id": 1,
    "userId": "12345",
    "validityTo": "1670799600000",
}
```

Here, `id` is the ban ID and `validityTo` is the time when the ban expires represented as a UNIX timestamp.

**Input arguments:** List of users bans in JSON format.

**Result:**

- `HTTP No Content [204]` indicating a successful update of bans

<br></br>
**Endpoint:** `/banned-users-generic`

**Method:** `PUT`

**Description:** Generalized endpoint behaving in the same way as the `/banned-users` endpoint. The only difference is
that the input data is passed in binary form as `.tar` file in the request.

**Input arguments:** List of users to ban in `.tar` format in request data.

**Result:**

- `HTTP Request Entity too large [413]` if the data passed to the request was larger than the upper limit
- `HTTP Unprocessable Entity [422]` if the banned users data couldn't be parsed correctly or wasn't provided in the
  request at all
- `HTTP No Content [204]` indicating successful banning

<br></br>
**Endpoint:** `/ban/<ban_id>`

**Method:** `GET`

**Description:** Used for checking whether a ban with given `ban_id` exists.

**Input arguments:** ID of a potential ban in the URL parameter

**Result:**

- `HTTP OK [200]` indicating a successful operation, the body of the response includes either the ban information as a
  JSON if it exists or an empty JSON `{}` if a ban with given ID doesn't exist
