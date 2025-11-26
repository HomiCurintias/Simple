import os
import requests

def run_simple_script(file):
    variables = {}
    functions = {}

    if not isinstance(file, str):
        raise TypeError(f"run_simple_script expected filename (str), got: {type(file)}")

    with open(file, "r", encoding="utf-8") as Code:
        lines = [l.strip() for l in Code]

    i = 0
    while i < len(lines):
        if lines[i] == "include:":
            if i + 1 < len(lines):
                filename = lines[i + 1].strip()
                print(f"[COMPILER] Including file '{filename}'")

                with open(filename, "r", encoding="utf-8") as inc:
                    included_lines = [l.strip() for l in inc.readlines()]

                lines = lines[:i] + included_lines + lines[i+2:]
                continue
            else:
                print("[COMPILER ERROR] 'include:' sem arquivo!")
                break
        i += 1

    i = 0
    while i < len(lines):

        # --- CREATE FILE ---
        if lines[i] == "create file:":
            if i + 1 < len(lines):
                filename = lines[i + 1]
                with open(filename, "w", encoding="utf-8") as output:
                    if i + 2 < len(lines):
                        content = lines[i + 2]
                        output.write(content)
                print(f"[OK] File '{filename}' created.")
                i += 3
                continue

        # --- READ FILE ---
        if lines[i] == "read file:":
            filename2 = lines[i + 1]
            try:
                with open(filename2, "r", encoding="utf-8") as f2:
                    content2 = f2.read()
                with open("Output.txt", "a", encoding="utf-8") as out:
                    out.write(content2 + "\n")
                print(f"[OK] Content of '{filename2}' added to Output.txt")
            except FileNotFoundError:
                print(f"[ERROR] File '{filename2}' not found.")
            i += 2
            continue

        # --- INPUT ---
        if lines[i] == "input:":
            PromptName = lines[i + 1]
            newContent = input(PromptName + ": ")
            variables[PromptName] = newContent
            with open("Output.txt", "a", encoding="utf-8") as out:
                out.write(newContent + "\n")
            print(f"[OK] Input '{PromptName}' saved to Output.txt")
            i += 2
            continue

        # --- PRINT ---
        if lines[i] == "print:":
            printContent = lines[i + 1]
            if printContent in variables:
                printContent = variables[printContent]
            with open("Output.txt", "a", encoding="utf-8") as out:
                out.write(str(printContent) + "\n")
            print(f"[OK] Text '{printContent}' saved to Output.txt")
            i += 2
            continue

        # --- MATH ---
        if lines[i] == "math:":
            try:
                x = lines[i + 1]
                op = lines[i + 2].strip()
                y = lines[i + 3]

                x = variables.get(x, x)
                y = variables.get(y, y)

                x = int(x)
                y = int(y)

                match op:
                    case "+": z = x + y
                    case "-": z = x - y
                    case "*": z = x * y
                    case "/": z = x / y if y != 0 else "Error: division by zero"
                    case _: z = f"Invalid operator: {op}"

                with open("Output.txt", "a", encoding="utf-8") as out:
                    out.write(str(z) + "\n")

                print(f"[OK] {x} {op} {y} = {z}")
            except ValueError:
                print("[ERROR] Invalid value for math operation")
            i += 4
            continue

        # --- DELETE FILE ---
        if lines[i] == "delete:":
            DeletedFileName = lines[i + 1]
            try:
                os.remove(DeletedFileName)
                print(f"[OK] File '{DeletedFileName}' deleted.")
            except FileNotFoundError:
                print(f"[ERROR] File '{DeletedFileName}' not found.")
            i += 2
            continue

        # --- GET ---
        if lines[i] == "get:":
            URL = lines[i + 1]
            try:
                response = requests.get(URL)
                if response.status_code == 200:
                    with open("Output.txt", "a", encoding="utf-8") as out:
                        out.write(response.text + "\n")
                    print(f"[OK] Content from {URL} saved to Output.txt")
                else:
                    print(f"[ERROR] Failed to access {URL}")
            except requests.RequestException as e:
                print(f"[ERROR] Error accessing {URL}: {e}")
            i += 2
            continue

        # --- IF ---
        if lines[i] == "if:":
            Data = variables.get(lines[i + 1], lines[i + 1])
            Comp = lines[i + 2]
            Second = variables.get(lines[i + 3], lines[i + 3])
            Action = lines[i + 4]

            condition = (
                (Comp == "==" and Data == Second) or
                (Comp == "!=" and Data != Second) or
                (Comp == ">" and Data > Second) or
                (Comp == "<" and Data < Second)
            )

            print(f"[OK] IF → {condition}")

            i += 5
            continue

        # --- VARIABLE ---
        if lines[i] == "variable:":
            VarName = lines[i + 1]
            VarVal = lines[i + 2]
            try: VarVal = int(VarVal)
            except: pass
            variables[VarName] = VarVal
            print(f"[OK] Variable '{VarName}' set to {VarVal}")
            i += 3
            continue

        # --- FUNCTION ---
        if lines[i] == "function:":
            header = lines[i + 1].split()
            func_name = header[0]
            params = header[1:]
            func_body = []
            i += 2
            while lines[i] != "endfunction":
                func_body.append(lines[i])
                i += 1
            functions[func_name] = {"params": params, "body": func_body}
            print(f"[OK] Function '{func_name}' defined")
            i += 1
            continue

        # --- CALL ---
        if lines[i] == "call:":
            parts = lines[i + 1].split()
            func_name = parts[0]
            args = parts[1:]

            if func_name not in functions:
                print(f"[ERROR] Function '{func_name}' not defined")
                i += 2
                continue

            func = functions[func_name]
            params = func["params"]
            body = func["body"]

            local_vars = dict(variables)
            for p, a in zip(params, args):
                try: a = int(a)
                except: pass
                local_vars[p] = a

            print(f"[OK] Calling '{func_name}'")

            for cmd in reversed(body):
                lines.insert(i + 2, cmd)

            variables.update(local_vars)
            i += 2
            continue

        i += 1
