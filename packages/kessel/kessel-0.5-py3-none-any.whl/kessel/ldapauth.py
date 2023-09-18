import logging
import ldap3
from ldap3 import Server, Connection, ALL

def authenticate_search_bind(username, password):
    """
    Custom authenticator function, actually just a wrapper
    around ldap3's usual methods for search & bind.

    Args:
        username (str): Username of the user to bind (the field specified
                        as LDAP_BIND_LOGIN_ATTR)
        password (str): User's password to bind with when we find their dn.

    Returns:
        Boolean

    """

    # hardcode the server
    server = Server('ad.lfap.ph2.uni-koeln.de', get_info=ALL)
    # open anonymous connection
    connection = Connection(server, auto_bind=True)

    # hardcode the search base
    search_base = 'cn=Users,dc=lfap,dc=ph2,dc=uni-koeln,dc=de'

    # filter: is ad user
    search_filter = (
            '(&(objectClass=user)(objectCategory=person)'
            '(!(userAccountControl:1.2.840.113556.1.4.803:=2))'
            f'(uid={username}))'
    )

    # search for the user dn
    isUser = connection.search(search_base=search_base
            , search_filter=search_filter
            , attributes='uid')

    response = dict()
    result = []
    if isUser:
        result = connection.response

    if len(result) == 0:
        logging.warning(f"Authentication was not successful for user '{username}'")

    else:
        for user in result:
            # Attempt to bind with each user we find until we can find
            # one that works.

            if 'type' not in user or user.get('type') != 'searchResEntry':
                # Issue #13 - Don't return non-entry results.
                continue

            user_connection = Connection(server,
                                         user=user['dn'],
                                         password=password
                                        )

            logging.info(
                "Directly binding a connection to a server with "
                f"user:'{user['dn']}'"
                )
            try:
                bind_return_code = user_connection.bind()
                # print(f'Bind returnes: {bind_return_code}')
                logging.info(
                    f"Authentication was successful for user '{username}'"
                    )
                response['status'] = True

                # Populate User Data
                user['attributes']['dn'] = user['dn']
                response['user_info'] = user['attributes']
                response['user_id'] = username
                response['user_dn'] = user['dn']
                break

            except ldap3.core.exceptions.LDAPInvalidCredentialsResult:
                logging.info(
                    "Authentication was not successful for "
                    f"user '{username}'"
                    )
                response['status'] = False
            except Exception as e:  # pragma: no cover
                # This should never happen, however in case ldap3 does ever
                # throw an error here, we catch it and log it
                logging.error(e)
                response['status'] = False
            user_connection.unbind()
    connection.unbind()
    return response


# def validateLdap(ldapForm):
#         logging.debug('Validating LDAPLoginForm against LDAP')
#         'Validate the username/password data against ldap directory'
#         ldapManager = current_app.ldap3_login_manager
#         username = ldapForm.username.data
#         password = ldapForm.password.data

#         result = authenticate_search_bind(username, password)

#         if result.status == AuthenticationResponseStatus.success:
#             ldapForm.user = ldapManager._save_user(
#                 result.user_dn,
#                 result.user_id,
#                 result.user_info,
#                 result.user_groups
#             )
#             return True

#         else:
#             ldapForm.user = None
#             ldapForm.username.errors.append('Invalid Username/Password.')
#             ldapForm.password.errors.append('Invalid Username/Password.')
#             return False
