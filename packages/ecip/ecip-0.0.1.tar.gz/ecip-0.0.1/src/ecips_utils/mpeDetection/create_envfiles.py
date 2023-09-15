import subprocess
import re
import json


def main():
    mappings = standardize_mpe_info()
    mappings = extract_mpe_name(mappings)
    write_mpe_env_file(mappings)


def standardize_mpe_info():
    '''
    This function uses subprocess to harvest mapping information by checking the disk filesystem.
    Output:
        mappings - pandas data frame containing the mapping informaton referenced by the
        disk filesystem
    '''
    cmd = ["df", "-h"]
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
    data = []
    new = True
    for line in process.stdout:
        temp_all = list(line.decode('utf-8'))
        temp_condensed = []
        temper = ''
        for ele in temp_all:
            if new:
                if ele != ' ' and ele != '\n':
                    temper += ele
                elif ele == '\n':
                    temp_condensed.append(temper)
                else:
                    new = False
                    temp_condensed.append(temper)
            else:
                if ele != ' ':
                    new = True
                    temper = ele
                    if ele == temp_all[-1]:
                        temp_condensed.append(temper)
        data.append(temp_condensed)
    mappings = {}
    for i in range(len(data[0][:-1])):
        temp = []
        for a in range(1, len(data)):
            temp.append(data[a][i])
        index = [j for j in range(1, len(data))]
        mappings[data[0][i]] = dict(zip(index, temp))
    return mappings


def extract_mpe_name(mappings):
    '''
    This function extracts the mpe name associated with a known mount.
    Input:
        mappings - pandas data frame containing the mapping informaton referenced by the disk filesystem
    Output:
        mappings - With additional mpe name column
    '''
    mappings['MPE'] = {}
    i = -1
    for ele in mappings['Mounted'].values():
        i += 1
        ele = ele.split('/')[-1]
        # the PRLM feeds seem to have the same IPv4 address as the MPE noted in the mounted
        # field that doesn't have the PRLM suffix
        if 'PRLM' not in ele:
            mappings['MPE'][i] = ele
    return mappings


def write_mpe_env_file(mappings):
    '''
    This function writes the known mpes and associated IPv4 addresses to an .env file.
    Input:
        mappings - pandas data frame containing the mapping informaton referenced by the
        disk filesystem
    '''
    def construct_env_vars(mappings):
        env_vars = {}
        for mpe in mappings['MPE'].values():
            for (mount, filesystem) in zip(mappings['Mounted'].values(), mappings['Filesystem'].values()):
                if mpe in mount:
                    r = re.compile(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}')  # NOSONAR
                    # - processing local data only not externally inducted data.
                    ip = r.search(filesystem)
                    if ip is None:
                        break
                    if "LETTER" in mpe:
                        # We don't want to process data from Letter data on the test server
                        break
                    else:
                        ip = ip.group()
                        env_vars[str(mpe)] = str(ip)
        # to help with testing write mpe_landing_test to mpe_mappings.env
        # env_vars['mpe_landing_test'] = '10.0.0.1'
        env_vars = '{}'.format(env_vars)
        env_vars = env_vars.replace("'", '"')
        env_vars = 'ECIPS_MPE_INDEX' + '=' + env_vars
        return env_vars
    env_vars = construct_env_vars(mappings)
    path = '/ECIPs/Docker/mpe_mappings.env'
    File_object = open(path, "w+")
    File_object.writelines(env_vars)
    return env_vars


def write_device_env_file():
    '''
    This function writes the name and ip address of the device it is deployed to
    '''
    device_ip = subprocess.check_output("hostname -I | awk '{for (i=1;i<=NF;i++) print $i}' | grep 56.",
                                        shell=True).strip()
    device_name = subprocess.check_output('hostname', shell=True).strip()
    path = '/ECIPs/Docker/device_mappings.env'
    device_mappings = {'name': device_name.decode('utf-8'), 'ip': device_ip.decode('utf-8')}
    device_mappings = 'ECIPS_DEVICE_MAPPINGS=' + json.dumps(device_mappings, separators=(',', ':'))
    File_object = open(path, "w+")
    File_object.writelines(device_mappings)


if __name__ == 'main':
    main()
