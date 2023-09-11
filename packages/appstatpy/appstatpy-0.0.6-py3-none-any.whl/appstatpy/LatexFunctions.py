def to_latex(exer, value):
    main =  "\\newcommand{{}}"
    main = main.replace("{}", str(exer))
    main = main.replace("{", "{\\")
    second =  "{{}}"
    second = second.replace("{}", str(value))
    return "\n" + main + second


def remove_duplicate_commands(lines):
    unique_commands = {}
    new_lines = []

    for line in lines:
        if line.startswith("\\newcommand{"):
            command_name = line.split("{")[1].split("}")[0]
            if command_name not in unique_commands:
                unique_commands[command_name] = True
                new_lines.append(line)
        else:
            new_lines.append(line)

    return new_lines

def LatexTool(exer, value):
    file_path = "output.tex"
    
    with open(file_path, 'a') as file:
        file.write(to_latex(exer, value))

    with open(file_path, "r") as input_file:
        lines = input_file.readlines()

    lines = lines[::-1]

    new_lines = remove_duplicate_commands(lines)

    with open(file_path, "w") as output_file:
        output_file.writelines(new_lines)
