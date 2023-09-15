import os

from sipc_xethhung12.cmd import load_devices


def gen(in_file, out_dir):
    devices = load_devices(in_file)
    path = f"{out_dir}/scripts/servers"
    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
    with open(f"{path}/sourcing.sh", "w") as sourcing:
        for key in devices:
            script_str = gen_server_script(devices, key, devices[key])
            if not os.path.exists(path):
                os.makedirs(path, exist_ok=True)
            sourcing.write(f"source {key}_env.sh\n")
            with open(f"{path}/{key}_env.sh", "w") as f:
                f.write(script_str)


def gen_server_script(devices, key, device):
    server_name = key
    ip = device['ip']
    username = devices[key]['extra']['user-name'] if 'user-name' in devices[key]['extra'] else 'root'
    s = ""
    s += f'export ser_{server_name}_host={server_name}'
    s += '\n'
    s += f'export ser_{server_name}_ip={ip}'
    s += '\n'
    s += f'export ser_{server_name}_un={username}'
    s += '\n'
    s += f'alias ssh_{server_name}=\'ssh {username}@{ip}\''
    s += '\n'
    return s
