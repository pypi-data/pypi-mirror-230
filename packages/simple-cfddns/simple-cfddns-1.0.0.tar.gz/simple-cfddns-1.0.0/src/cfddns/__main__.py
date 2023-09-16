import argparse
from . import iptools
from . import CloudflareAPI
import os
import sys

SERVICE_TEMPLATE = """
[Unit]
Description=Cloudflare Dynamic DNS
After=network.target
StartLimitIntervalSec=0

[Service]
Type=simple
Restart=always
RestartSec={restart_sec}
User=root
ExecStart={python} -m cfddns -n {name} -z {zone_id} -t {token} -m {method} update

[Install]
WantedBy=multi-user.target
"""


class CFDDNS:
    def __init__(self) -> None:
        pass

    def execute(self):
        parser = argparse.ArgumentParser()
        parser.add_argument( '-n', "--name", help="domain name")
        parser.add_argument('-z', "--zone", help="zone id for your domain")
        parser.add_argument('-t', "--token", help="api token, refer to " +
                            "https://developers.cloudflare.com/fundamentals/api/get-started/")
        parser.add_argument("--ttl", help="ttl", default=60)
        parser.add_argument("-m", "--method", help="method to get ip address, select from iptools.py", 
                            default="get_all_inet_ip")

        action_parser = parser.add_subparsers(title="action", dest="action", required=True)

        # update, delete, list
        action_parser.add_parser("update", help="update record")
        del_parser = action_parser.add_parser("delete", help="delete record")
        del_parser.add_argument("-y", "--yes", help="skip confirmation", action="store_true")
        action_parser.add_parser("list", help="list records")

        # install
        install_parser = action_parser.add_parser("install", help="install as a service")
        install_parser.add_argument("service_name", help="service name")
        install_parser.add_argument("-s", "--restart-sec", help="restart interval in seconds", default=60, type=int)
        install_parser.add_argument("-y", "--yes", help="skip confirmation", action="store_true")
        install_parser.add_argument("--python", help="python interpreter path", default=sys.executable)

        # uninstall
        uninstall_parser = action_parser.add_parser("uninstall", help="uninstall service")
        uninstall_parser.add_argument("service_name", help="service name")
        uninstall_parser.add_argument("-y", "--yes", help="skip confirmation", action="store_true")

        # all services
        services_parser = action_parser.add_parser("services", help="list all services")
        
        args = parser.parse_args()
        self.args = args

        if args.action == "list":
            self.list()
        elif args.action == "update":
            self.update()
        elif args.action == "delete":
            self.delete()
        elif args.action == "install":
            self.install()
        elif args.action == "uninstall":
            self.uninstall()
        elif args.action == "services":
            self.services()

    def _check_api_args(self):
        args = self.args
        self.token = args.token or input("Token: ")
        self.zone_id = args.zone or input("Zone ID: ")
        self.name = args.name or input("Domain name: ")

        if self.token is None:
            print("-t or --token is required")
            sys.exit(1)
        if self.zone_id is None:
            print("-z or --zone is required")
            sys.exit(1)
        if self.name is None:
            print("-n or --name is required")
            sys.exit(1)

    
    def list(self):
        self._check_api_args()

        api = CloudflareAPI(self.zone_id, self.token)
        records = api.list_records(self.name, "A")
        records += api.list_records(self.name, "AAAA")
        print(f"Found {len(records)} records:")
        for record in records:
            print(f"{record['name']} -> {record['content']}")
        
    
    def update(self):
        self._check_api_args()

        api = CloudflareAPI(self.zone_id, self.token, self.args.ttl)

        method = getattr(iptools, self.args.method, None)
        if method is None:
            print(f"Method {self.args.method} not found")
            sys.exit(1)

        addrs = method()
        if isinstance(addrs, str):
            addrs = [addrs]

        if len(addrs) == 0:
            print("No ip address found")
            sys.exit(0)
    
        for addr in addrs:
            print(f"Updating record {self.name} -> {addr}")
            try:
                api.smart_update(self.name, addr)
            except Exception as e:
                print(f"error: {e}")


    def delete(self):
        """
        list all records with name and delete them
        """
        self._check_api_args()

        api = CloudflareAPI(self.zone_id, self.token)
        records = api.list_records(self.name, "A")
        records += api.list_records(self.name, "AAAA")

        if len(records) == 0:
            print("No records to delete")
            sys.exit(0)

        print("The following records will be deleted:")
        for record in records:
            print(f"  {record['name']} -> {record['content']}")

        if not self.args.yes:
            if input("Are you sure? [y/N] ").lower() != "y":
                print("Aborted")
                sys.exit(0)

        for record in records:
            print(f"Deleting record {record['name']} -> {record['content']}")
            try:
                api.delete_record(record['id'])
            except Exception as e:
                print(f"error: {e}")

    def _compose_name(self, input_name):
        service_name = input_name
        if not service_name.startswith("cfddns-"):
            service_name = "cfddns-" + service_name
        if not service_name.endswith(".service"):
            service_name += ".service"
        return service_name

    
    def _check_systemd(self):
        # check if systemd is available
        if not os.path.exists("/bin/systemctl"):
            print("systemd is not available on this system")
            sys.exit(1)
    
    def _check_root(self):
        # check if in sudo mode
        if os.getuid() != 0:
            print("Please run this script as root")
            sys.exit(1)


    def install(self):
        """
        install this program as a service.
        only support systemd for now.
        """
        self._check_api_args()
        self._check_systemd()
        self._check_root()

        location = "/etc/systemd/system"
        service_name = self._compose_name(self.args.service_name)
        service_path = os.path.join(location, service_name)

        # check if service file exists
        if os.path.exists(service_path):
            print("Service file already exists")
            sys.exit(1)

        restart_sec = self.args.restart_sec
        python = self.args.python
        method = self.args.method

        # confirm
        print(f"Service name: {service_name}")
        print(f"Service file will be created at: {service_path}")
        print(f"Restart interval: {restart_sec} seconds")
        print(f"Python interpreter: {python}")
        print(f"Method to get ip address: {method}")

        service_str = SERVICE_TEMPLATE.format(
            restart_sec=restart_sec,
            name=self.name,
            zone_id=self.zone_id,
            token=self.token,
            python=python,
            method=method
        )

        if not self.args.yes:
            if input("Are you sure? [y/N] ").lower() != "y":
                print("Aborted")
                sys.exit(0)
        
        # write service file
        with open(service_path, "w") as f:
            f.write(service_str)
        
        import stat
        os.chmod(service_path, stat.S_IWUSR | stat.S_IRUSR)
        
    def uninstall(self):
        """
        uninstall service
        """
        self._check_systemd()
        self._check_root()

        location = "/etc/systemd/system"
        service_name = self._compose_name(self.args.service_name)
        service_path = os.path.join(location, service_name)

        # check if service file exists
        if not os.path.exists(service_path):
            print("Service file not found")
            sys.exit(1)

        # confirm
        print(f"Service name: {service_name}")
        print(f"Service file here will be deleted: {service_path}")

        if not self.args.yes:
            if input("Are you sure? [y/N] ").lower() != "y":
                print("Aborted")
                sys.exit(0)

        # stop and disable service
        os.system(f"systemctl stop {service_name}")
        os.system(f"systemctl disable {service_name}")

        # delete service file
        os.remove(service_path)

    def services(self):
        """
        list all services
        """
        self._check_systemd()

        location = "/etc/systemd/system"
        services = os.listdir(location)
        services = [s for s in services if s.startswith("cfddns-") and s.endswith(".service")]

        print(f"Found {len(services)} services:")
        for service in services:
            print(f"  {service}")


def main():
    CFDDNS().execute()


if __name__ == "__main__":
    main()