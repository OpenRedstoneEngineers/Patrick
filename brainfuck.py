class Memory:
    def __init__(self, input):
        self.counter = 0
        self.pointer = 0
        self.cells = [0] * 30000
        self.input = input
        self.input_index = 0
        self.output = ""
        self.loops_counter = 0

def process_brainfuck(code: str, input: str):
    memory = Memory(input)
    memory.counter = 0
    while memory.counter < len(code):
        match code[memory.counter]:
            case ">":
                memory.pointer += 1
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
                    open_brackets = 1
                    starting_position = memory.counter
                    while open_brackets > 0:
                        memory.counter += 1
                        if memory.counter > len(code) - 1:
                            return f"error: unmatched '[' at character {starting_position}"
                        if code[memory.counter] == "[":
                            open_brackets += 1
                        elif code[memory.counter] == "]":
                            open_brackets -= 1
            case "]":
                if memory.cells[memory.pointer] != 0:
                    close_brackets = 1
                    starting_position = memory.counter
                    starting_pointer = memory.pointer
                    starting_value = memory.cells[memory.pointer]
                    while close_brackets > 0:
                        memory.counter -= 1
                        if memory.counter < 0:
                            return f"error: unmatched ']' at character {starting_position}"
                        if code[memory.counter] == "]":
                            close_brackets += 1
                        elif code[memory.counter] == "[":
                            close_brackets -= 1
                        if close_brackets == 0 and memory.pointer == starting_pointer and memory.cells[memory.pointer] == starting_value:
                            memory.loops_counter += 1
                            if memory.loops_counter > 50:
                                return f"error: infinite loop detected at character {starting_position}"
                        else:
                            memory.loops_counter = 0

        memory.counter += 1
    return memory.output
