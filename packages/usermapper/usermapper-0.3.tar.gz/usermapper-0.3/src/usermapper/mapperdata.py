#!/usr/bin/env python3
import yaml, secrets, string

def get_user_passwords(pass_value,length=8):
    if pass_value == "random":
        alphabet = string.ascii_letters + string.digits
        passwd = ''.join(secrets.choice(alphabet) for i in range(length))
    else:
        passwd = pass_value
    return passwd

def get_devices(dictionary):
    devices_dictionary = {}
    for device_type in dictionary['devices']:
        device = dictionary['devices'][device_type]
        device_suffix = int(device['name_suffix'])
        device_suffix_length = len(device['name_suffix'])
        host_suffix = int(device['hostname_suffix'])
        host_suffix_length = len(device['hostname_suffix'])

        for _ in range(int(device['quantity'])):
            device_name = device['name_prefix'] + str(device_suffix).zfill(device_suffix_length)
            device_suffix += 1
            devices_dictionary[device_name] = dict(device['parameters'])

            hostname = device['hostname_prefix'] + str(host_suffix).zfill(host_suffix_length)
            host_suffix += 1
            devices_dictionary[device_name]['hostname'] = hostname
            
    return(devices_dictionary)


def get_users(dictionary):
    user_list=[]

    for user_type in dictionary['users']:
        user_values = dictionary['users'][user_type]
        suffix = int(user_values['username_suffix'])
        length = len(user_values['username_suffix'])

        for _ in range(int(user_values['quantity'])):
            string = str(suffix).zfill(length)
            name = user_values['username_prefix'] + string
            suffix += 1
            passwd = get_user_passwords(user_values['password'])
            next_user = dict(
                username = name,
                password = passwd,
                devices = dict(get_devices(dictionary))
            )
            user_list.append(next_user)
    return(user_list)


if __name__ == "__main__":

    stream = open('config.yaml', 'r')
    configuration = yaml.safe_load(stream)

    for user_type in configuration['users']:
        output = user_type + ": "
        for _ in range(configuration['users'][user_type]["quantity"]):
            password = configuration['users'][user_type]["password"]
            output = output + get_user_passwords(password) + " "
        print(output)

    print()
    print('Input from YAML converted to dictionary:')
    print(configuration)
    print()

    print('Devices dictionary:')
    dev = get_devices(configuration)
    print(dev)
    print()

    print('Users dictionary:')
    users = get_users(configuration)
    print(users)
    print()
