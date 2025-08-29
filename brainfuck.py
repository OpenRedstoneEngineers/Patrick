from collections import deque

class Memory:
    def __init__(self, input):
        self.counter = 0
        self.pointer = 0
        self.cells = [0] * 30000
        self.input = input
        self.input_index = 0
        self.output = ""
        self.loops_counter = 0
        self.brace_map = {}

def create_brace_map(code: str):
    brace_map = {}
    stack = deque()
    ptr = 0
    while ptr < len(code):
        if code[ptr] == "[":
            stack.append(ptr)
        elif code[ptr] == "]":
            if not stack:
                raise SyntaxError("Unmatched ']'")
            opening_brace = stack.pop()
            brace_map[opening_brace] = ptr
            brace_map[ptr] = opening_brace
        ptr += 1
    if stack:
        raise SyntaxError(stack.pop())
    return brace_map

def process_brainfuck(code: str, input: str):
    memory = Memory(input)
    try:
        memory.brace_map = create_brace_map(code)
    except SyntaxError as e:
        return f"error: unmatched '[' at character {e.args[0]}"
    memory.counter = 0
    while memory.counter < len(code):
        match code[memory.counter]:
            case ">":
                if memory.pointer < 29999:
                    memory.pointer += 1
                else:
                    return f"error: pointer moved above 29999 at character {memory.counter}"
            case "<":
                if memory.pointer > 0:
                    memory.pointer -= 1
                else:
                    return f"error: pointer moved below 0 at character {memory.counter}"
            case "+":
                memory.cells[memory.pointer] = (memory.cells[memory.pointer] + 1) % 256
            case "-":
                memory.cells[memory.pointer] = (memory.cells[memory.pointer] - 1) % 256
            case ".":
                memory.output += chr(memory.cells[memory.pointer])
            case ",":
                if memory.input_index < len(memory.input):
                    memory.cells[memory.pointer] = ord(memory.input[memory.input_index])
                    memory.input_index += 1
                else:
                    return f"error: input exhausted at character {memory.counter}"
            case "[":
                if memory.cells[memory.pointer] == 0:
                    memory.counter = memory.brace_map[memory.counter]
            case "]":
                if memory.cells[memory.pointer] != 0:
                    memory.counter = memory.brace_map[memory.counter]
                    memory.loops_counter += 1
                    if memory.loops_counter > 1000:
                        return f"error: infinite loop detected at character {memory.counter}"
                else:
                    memory.loops_counter = 0

        memory.counter += 1
    return memory.output