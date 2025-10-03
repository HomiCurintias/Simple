import os
import requests

variables = {}
functions = {}

file = input("File name: ")

with open(file, "r", encoding="utf-8") as Code:
    lines = [l.strip() for l in Code]

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
            print(f"[OK] Arquivo '{filename}' criado.")
            i += 3
        else:
            break

    # --- READ FILE ---
    elif lines[i] == "read file:":
        if i + 1 < len(lines):
            filename2 = lines[i + 1]
            try:
                with open(filename2, "r", encoding="utf-8") as f2:
                    content2 = f2.read()
                with open("Output.txt", "a", encoding="utf-8") as out:
                    out.write(content2 + "\n")
                print(f"[OK] Conteúdo de '{filename2}' adicionado ao Output.txt")
            except FileNotFoundError:
                print(f"[ERRO] Arquivo '{filename2}' não encontrado.")
            i += 2
        else:
            break

    # --- INPUT ---
    elif lines[i] == "input:":
        if i + 1 < len(lines):
            PromptName = lines[i + 1]
            newContent = input(PromptName + ": ")
            variables[PromptName] = newContent
            with open("Output.txt", "a", encoding="utf-8") as out:
                out.write(newContent + "\n")
            print(f"[OK] Entrada '{PromptName}' salva em Output.txt")
            i += 2
        else:
            break

    # --- PRINT ---
    elif lines[i] == "print:":
        if i + 1 < len(lines):
            printContent = lines[i + 1]
            if printContent in variables:
                printContent = variables[printContent]
            with open("Output.txt", "a", encoding="utf-8") as out:
                out.write(str(printContent) + "\n")
            print(f"[OK] Texto '{printContent}' salvo em Output.txt")
            i += 2
        else:
            break

    # --- MATH ---
    elif lines[i] == "math:":
        if i + 3 < len(lines):
            try:
                x = lines[i + 1]
                op = lines[i + 2].strip()
                y = lines[i + 3]

                x = variables.get(x, x)
                y = variables.get(y, y)

                x = int(x)
                y = int(y)

                if op == "+":
                    z = x + y
                elif op == "-":
                    z = x - y
                elif op == "*":
                    z = x * y
                elif op == "/":
                    z = x / y if y != 0 else "Erro: divisão por zero"
                else:
                    z = f"Operador inválido: {op}"

                with open("Output.txt", "a", encoding="utf-8") as out:
                    out.write(str(z) + "\n")

                print(f"[OK] {x} {op} {y} = {z}")
            except ValueError:
                print("[ERRO] Valor inválido para operação matemática")
            i += 4
        else:
            break

    # --- DELETE FILE ---
    elif lines[i] == "delete:":
        if i + 1 < len(lines):
            DeletedFileName = lines[i + 1]
            try:
                os.remove(DeletedFileName)
                print(f"[OK] Arquivo '{DeletedFileName}' deletado.")
            except FileNotFoundError:
                print(f"[ERRO] Arquivo '{DeletedFileName}' não encontrado.")
            i += 2
        else:
            break

    # --- GET (HTTP) ---
    elif lines[i] == "get:":
        if i + 1 < len(lines):
            URL = lines[i + 1]
            try:
                response = requests.get(URL)
                if response.status_code == 200:
                    with open("Output.txt", "a", encoding="utf-8") as out:
                        out.write(response.text + "\n")
                    print(f"[OK] Conteúdo de {URL} salvo em Output.txt")
                else:
                    print(f"[ERRO] Falha ao acessar {URL} (status {response.status_code})")
            except requests.RequestException as e:
                print(f"[ERRO] Erro ao acessar {URL}: {e}")
            i += 2
        else:
            break

    # --- IF ---
    elif lines[i] == "if:":
        if i + 4 < len(lines):
            Data = lines[i + 1]
            Comparative = lines[i + 2]
            SecondData = lines[i + 3]
            Action = lines[i + 4]

            Data = variables.get(Data, Data)
            SecondData = variables.get(SecondData, SecondData)

            condition = False
            if Comparative == "==":
                condition = (str(Data) == str(SecondData))
            elif Comparative == "!=":
                condition = (str(Data) != str(SecondData))
            elif Comparative == ">":
                condition = (str(Data) > str(SecondData))
            elif Comparative == "<":
                condition = (str(Data) < str(SecondData))

            if condition:
                print(f"[OK] Condição ({Data} {Comparative} {SecondData}) verdadeira, executando '{Action}'")
            else:
                print(f"[INFO] Condição ({Data} {Comparative} {SecondData}) falsa, pulando")
            i += 5
        else:
            break

    # --- VARIABLE ---
    elif lines[i] == "variable:":
        if i + 2 < len(lines):
            VarName = lines[i + 1]
            VarVal = lines[i + 2]
            try:
                VarVal = int(VarVal)
            except ValueError:
                pass
            variables[VarName] = VarVal
            print(f"[OK] Variável '{VarName}' definida como {VarVal}")
            i += 3
        else:
            break

    # --- FUNCTION ---
    elif lines[i] == "function:":
        if i + 1 < len(lines):
            header = lines[i + 1].split()
            func_name = header[0]
            params = header[1:]
            func_body = []
            i += 2
            while i < len(lines) and lines[i] != "endfunction":
                func_body.append(lines[i])
                i += 1
            functions[func_name] = {"params": params, "body": func_body}
            print(f"[OK] Função '{func_name}' definida com parâmetros {params}")
            i += 1
        else:
            break

    # --- CALL FUNCTION ---
    elif lines[i] == "call:":
        if i + 1 < len(lines):
            parts = lines[i + 1].split()
            func_name = parts[0]
            args = parts[1:]
            if func_name in functions:
                func = functions[func_name]
                params = func["params"]
                body = func["body"]

                local_vars = dict(variables)
                for p, a in zip(params, args):
                    try:
                        a = int(a)
                    except ValueError:
                        pass
                    local_vars[p] = a

                print(f"[OK] Chamando função '{func_name}' com {args}")

                for j, line in enumerate(reversed(body)):
                    lines.insert(i + 2, line)

                variables.update(local_vars)

            else:
                print(f"[ERRO] Função '{func_name}' não definida")
            i += 2
        else:
            break

    # --- LOOP ---
    elif lines[i] == "loop:":
        if i + 1 < len(lines):
            try:
                times = int(lines[i + 1])
                loop_body = []
                i += 2
                while i < len(lines) and lines[i] != "endloop":
                    loop_body.append(lines[i])
                    i += 1
                print(f"[OK] Loop de {times} vezes")
                for _ in range(times):
                    for cmd in reversed(loop_body):
                        lines.insert(i + 1, cmd)
                i += 1
            except ValueError:
                print("[ERRO] Valor inválido no loop")
        else:
            break

    else:
        i += 1
