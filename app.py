import requests
import getpass
import rich

from rich.pretty import pprint as pp

class NordVPN(object):
    def __init__(self):
        self.session = requests.Session()

        self.scheme: str = 'https'
        self.domain: str = 'nordvpn.com'

    def _url(self, *endpoints: str):
        endpoint = '/'.join(endpoints)
        
        return f'{self.scheme}://{self.domain}/{endpoint}'
        
    def _action(self, action: str, **filters):
        return self.session.get \
        (
            self._url('wp-admin/admin-ajax.php'),
            params = \
            {
                'action':  action,
                'filters': filters,  
            },
        ).json()

    def get_user_info_data(self):
        return self._action('get_user_info_data')

    def servers_countries(self):
        return self._action('servers_countries')

    def servers_groups(self):
        return self._action('servers_groups')

    def servers_technologies(self):
        return self._action('servers_technologies')

    def servers_recommendations(self, *, country_id: int = None, servers_groups: list = None, servers_technologies: list = None):
        filters = {'country_id': country_id} if country_id else {}
        
        return self._action('servers_recommendations', **filters)

    def ovpn_config_file(self, hostname: str, protocol: str):
        return self.session.get(f'https://downloads.nordcdn.com/configs/files/ovpn_{protocol}/servers/{hostname}.{protocol}.ovpn'.lower()).text

# rich.print('[green]Please enter your Nord OpenVPN login details.')

# username = input('Username: ')
# password = getpass.getpass('Password: ')

# print(username, password)

nord = NordVPN()

technologies = nord.servers_technologies()

technology_name = 'OpenVPN UDP'
group_name      = 'Standard VPN'
protocol        = 'UDP'

for technology in technologies:
    if technology['name'] == technology_name:
        break

for group in technology['groups']:
    if group['name'] == group_name:
        break

countries = group['countries']

for country in countries:
    country_id   = country['id']
    country_name = country['name']
    country_code = country['code']

    print(country_id, country_name, country_code)

    servers = nord.servers_recommendations \
    (
        country_id           = country['id'],
        servers_groups       = [group['id']],
        servers_technologies = [technology['id']],
    )

    server = servers[0]

    ovpn_file = nord.ovpn_config_file \
    (
        hostname = server['hostname'],
        protocol = protocol,
    )

    print(ovpn_file)

    break
