import os
import sys
import supervisor

# Number of entries to display at once
visible_lines = 6

def path_basename(file_path):
    return file_path.split("/")[-1]

class Menu:
    def __init__(self, path, page_size=visible_lines):
        self.path = path
        self.page_size = page_size
        self.scripts = self.get_all_scripts()
        self.cursor = 0  # current highlighted index
        self.view_offset = 0  # topmost visible script

    def get_all_scripts(self):
        files = [f"{self.path}/{f}" for f in os.listdir(self.path) if f.endswith(".py")]
        return sorted(files)

    def show(self):
        print("\033[2J\033[H", end="")  # Clear screen
        end = self.view_offset + self.page_size
        visible_scripts = self.scripts[self.view_offset:end]

        for i, script in enumerate(visible_scripts):
            idx = self.view_offset + i
            marker = "→" if idx == self.cursor else " "
            print(f"{marker} {path_basename(script)}")

    def move_up(self):
        if self.cursor == 0:
            self.cursor = len(self.scripts) - 1
            self.view_offset = max(0, self.cursor - self.page_size + 1)
        else:
            self.cursor -= 1
            if self.cursor < self.view_offset:
                self.view_offset -= 1

    def move_down(self):
        if self.cursor == len(self.scripts) - 1:
            self.cursor = 0
            self.view_offset = 0
        else:
            self.cursor += 1
            if self.cursor >= self.view_offset + self.page_size:
                self.view_offset += 1

    def run_selected(self):
        script_to_run = self.scripts[self.cursor]
        print(f"\nRunning {path_basename(script_to_run)}...\n")
        supervisor.set_next_code_file(script_to_run)
        supervisor.reload()

# Create menu instance
menu = Menu("/scripts")

# Main loop
menu.show()
while True:
    char = sys.stdin.read(1)

    if char == "\x1b":
        next1 = sys.stdin.read(1)
        if next1 == "[":
            next2 = sys.stdin.read(1)
            if next2 == "A":      # Up arrow
                menu.move_up()
                menu.show()
            elif next2 == "B":    # Down arrow
                menu.move_down()
                menu.show()
    elif char in ("\r", "\n"):  # Enter key
        menu.run_selected()
