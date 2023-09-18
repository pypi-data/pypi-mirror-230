# Usermapper #

Create a complex Guacamole manual authentication file, saved as */etc/guacamole/user-mapping.xml*, from a simple confuration file. This is an *opinionated* script designed to support training labs. It assumes every user will have access to the same set of devices in the lab.

## Installation ##

This is a Python program. Install from Github:

    $ pip install git+https://github.com/blinklet/usermapper.git@v0.3#egg=usermapper

## Usage ##

Create a configuration file that describes the users and devices in your lab. Then run the usermapper program. To see an example of the configuration file format, look at the *example-config.yaml* file in this repository, or see the next section.

The usermapper program accepts two optional arguments that allow the user to specify the input file and the output file. See the command syntax below:

    $ python3 -m usermapper [-i <input filename>] [-o <output filename>]

For example:

    $ python3 -m usermapper -i test.yaml -o /tmp/guac/map.xml

To use default filenames, where the configuration script is named *config.yaml* and the output file will be named *user-mapping.xml* and both files are in the current directory, run the script without arguments as follows:

    $ python3 -m usermapper

## Configuration file format 

The configuration file is written using the [YAML data file standard](https://rollout.io/blog/yaml-tutorial-everything-you-need-get-started/). The file name must end with the ".yaml" extension. 

The configuration file consists of two main blocks: a *users* block and a *devices* block. You may have one or more types of users and one or more types of devices. 

The <em>username_suffix</em>, device <em>name_suffix</em>, and device <em>hostname_suffix</em> must be a number with or without leading zeros, enclosed in quotes. We generate names by combining the corresponding name prefix and a different name suffix with a length equal to the length of the suffix string and starting at the number specified in the suffix. 

If a user type's <em>password</em> is "random", each user of the same type will be assigned a unique random password. If you specify a specific user password, each user in the same user type will have the same password.

You may also add additional device parameters from the <a href="https://guacamole.apache.org/doc/gug/configuring-guacamole.html" target="_blank">list of Guacamole configuration parameters</a>.

### Example config file

See the example below, which specifies *trainers* and *students* user types, and *servers* and *routers* device types:

```
users:

    trainers:
        quantity: 1
        username_prefix: trainer
        username_suffix: '01'
        password: s7T6yxOC100

    students:
        quantity: 8
        username_prefix: training
        username_suffix: '01'
        password: random

devices:

    servers:
        quantity: 11
        name_prefix: PC
        name_suffix: '09'
        hostname_prefix: '10.0.10.'
        hostname_suffix: '109'
        parameters:
            protocol: ssh
            hostname: ~
            port: 22
            username: root
            password: root
            color-scheme: white-black
            enable-sftp: 'true'
            sftp-root-directory: '/'

    routers:
        quantity: 4
        name_prefix: R
        name_suffix: '01'
        hostname_prefix: '10.0.10.'
        hostname_suffix: '1'
        parameters:
            protocol: ssh
            hostname: ~
            port: 22
            username: admin
            password: admin
            color-scheme: white-black
            enable-sftp: 'true'
            sftp-root-directory: '/files/'
```
