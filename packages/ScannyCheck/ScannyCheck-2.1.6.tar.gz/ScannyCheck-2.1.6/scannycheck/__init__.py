from scannycheck.checker import check_user, kill_user
from scannycheck.checker import CheckerUserManager

from scannycheck.checker.ovpn import OpenVPNManager
from scannycheck.checker.ssh import SSHManager

from scannycheck.web import Server, ServerManager

from scannycheck.utils import base_cli

__version__ = '2.1.6'
__author__ = 'security virtual'
__email__ = 'templodefogoc@gmail.com'

base_cli.description = 'Checker for OpenVPN and SSH'
base_cli.prog = 'checker v' + __version__

base_cli.add_argument(
    '-v',
    '--version',
    action='version',
    version='%(prog)s',
)
