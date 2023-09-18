#!/usr/bin/env python3
from .mapperdata import get_users
import yaml, sys, os
  
def write_params(filename,parameters,indent):
    indent = indent + (" " *4)
    for name in parameters:
        if name == 'protocol':
            filename.write(f'{indent}<protocol>{parameters[name]}</protocol>\n')
        else:
            filename.write(f"{indent}<param name=\"{name}\">{parameters[name]}</param>\n")
    indent = indent[:-4]
    return indent

def write_dev(filename,lab,indent):
    indent = indent + (" " * 4)
    for device in lab:
        filename.write(f"{indent}<connection name=\"{device}\">\n")	    
        write_params(filename,lab[device],indent)       
        filename.write(f"{indent}</connection>\n")	
    indent = indent[:-4]

def write_student(filename,students_dir):
    indent = " " * 4
    for student in students_dir:
        username=student["username"]
        password=student["password"]
        filename.write(f"{indent}<authorize username=\"{username}\" password=\"{password}\">\n")
		
        write_dev(filename,student["devices"],indent)
        
        filename.write(f"{indent}</authorize>\n")

def xmlwriter(students_dir, output_file):
    usermapping = open(output_file, 'w')
    usermapping.write(f"<user-mapping>\n")
    write_student(usermapping,students_dir)
    usermapping.write(f"</user-mapping>\n")
    usermapping.close()

help_text = '''
Usermapper usage:

    usermapper -i|--input <input filename> -o|--output <output filename>

    Or, use no arguments if you wish to use one, or both of the default
    filenames, listed below:

        input default = config.yaml
        output default = user-mapping.xml'''

def main():
    #set default file names
    config_file = 'config.yaml'
    output_file = 'user-mapping.xml'

    # Expect a maximum of five arguments
    if len(sys.argv) > 5:
        print('Too many arguments!')
        print(help_text)
        sys.exit(2)

    # Make a copy of the argument list with the program name removed
    args = sys.argv[1:]

    while args:
        argument = args.pop(0)
        if argument == '-i' or argument == '--input':
            config_file = args.pop(0)
            if not os.path.exists(config_file):
                print('Input file not found')
                sys.exit(2)
        elif argument == '-o' or argument == '--output':
            output_file = args.pop(0)
            output_dir = os.path.dirname(output_file)
            if output_dir:
                if not os.path.exists(output_dir):
                    print('Output file directory does not exist!')
                    sys.exit(2)
        elif argument == '-h' or argument == '--help':
            print(help_text)
            sys.exit(0)
        else:
            print('Invalid arguments!')
            print(help_text)
            sys.exit(2)

    stream = open(config_file, 'r')
    configuration = yaml.safe_load(stream)
    structure = get_users(configuration)
    xmlwriter(structure, output_file)

if __name__ == "__main__":
    main()
    

        
