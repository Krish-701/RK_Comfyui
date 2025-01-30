import os
import sys
import random
import csv

class RK_CSV_File_State_Looper_v01:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {
                    "multiline": False,
                    "default": "path/to/your_file.csv"
                }),
                "orientation": (["horizontal", "vertical", "specific_column"],), # Added "specific_column" option
                "column_name": ("STRING", { # Added column_name input
                    "default": "C",
                    "multiline": False
                }),
                "loop_mode": (["disabled", "random", "increment"],),
                "start_index": ("INT", {
                    "default": 0,
                    "min": 0,
                    "max": 100000,
                    "step": 1
                }),
                "end_index": ("INT", {
                    "default": 10,
                    "min": 0,
                    "max": 100000,
                    "step": 1
                }),
                "step_size": ("INT", {
                    "default": 1,
                    "min": 1,
                    "max": 1000,
                    "step": 1
                }),
                "delimiter": ("STRING", {
                    "default": ",",
                    "multiline": False
                })
            }
        }

    # Only one return type now
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("row_text",)
    FUNCTION = "read_row"
    CATEGORY = "RK_tools_v02"

    # Cache variables
    file_data_cache = None
    file_path_cache = None

    def load_file(self, file_path, delimiter):
        """
        Loads a CSV file into a list of lists and caches it.
        """
        if RK_CSV_File_State_Looper_v01.file_path_cache != file_path:
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            _, ext = os.path.splitext(file_path)
            ext = ext.lower()

            if ext != ".csv":
                raise ValueError(f"Unsupported file extension: {ext}. Only .csv is supported.")

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=delimiter)
                data = list(reader)

            RK_CSV_File_State_Looper_v01.file_data_cache = data
            RK_CSV_File_State_Looper_v01.file_path_cache = file_path

        return RK_CSV_File_State_Looper_v01.file_data_cache

    def get_row_count(self, data):
        return len(data)

    def get_column_count(self, data):
        if not data:
            return 0
        return len(data[0]) if data[0] else 0 # Handle empty first row

    def get_state_file_path(self, file_path, start_index, end_index, step_size, loop_mode, orientation, column_name=""): # Added column_name
        base, ext = os.path.splitext(file_path)
        state_file = f"{base}_state_{orientation}_{column_name}_{loop_mode}_{start_index}_{end_index}_{step_size}.txt" # Added column_name to state file name
        return state_file

    def read_current_index(self, state_file, start_index):
        if os.path.isfile(state_file):
            try:
                with open(state_file, 'r', encoding='utf-8') as f:
                    val = f.read().strip()
                    return int(val)
            except:
                pass
        return start_index

    def write_current_index(self, state_file, index):
        with open(state_file, 'w', encoding='utf-8') as f:
            f.write(str(index))

    def column_letter_to_index(self, column_letter):
        index = 0
        for char in column_letter:
            if 'A' <= char <= 'Z':
                index = index * 26 + (ord(char) - ord('A') + 1)
            else:
                raise ValueError("Invalid column letter")
        return index - 1 # Adjust to 0-based index


    def read_row(self, file_path, orientation, loop_mode, start_index, end_index, step_size, delimiter, column_name): # Added column_name parameter
        try:
            data = self.load_file(file_path, delimiter)
            total_rows = self.get_row_count(data)
            total_cols = self.get_column_count(data)

            if orientation == "horizontal":
                # Adjust row indices if out of range
                if start_index < 0:
                    start_index = 0
                if end_index >= total_rows:
                    end_index = total_rows - 1
                if end_index < start_index:
                    start_index, end_index = end_index, start_index # Swap if end_index < start_index

                state_file = self.get_state_file_path(file_path, start_index, end_index, step_size, loop_mode, orientation)

                # Determine chosen_index (row index)
                if loop_mode == "disabled":
                    chosen_index = start_index

                elif loop_mode == "random":
                    chosen_index = random.randint(start_index, end_index)

                elif loop_mode == "increment":
                    current_index = self.read_current_index(state_file, start_index)
                    chosen_index = current_index
                    new_index = chosen_index + step_size
                    if new_index > end_index:
                        new_index = start_index
                    self.write_current_index(state_file, new_index)

                else:
                    chosen_index = start_index

                if 0 <= chosen_index < total_rows: # Check if chosen_index is valid row index
                    row_data = data[chosen_index]
                    row_text = delimiter.join(map(str, row_data))
                else:
                    row_text = "" # Handle out of bound index, return empty string or handle as needed

            elif orientation == "vertical":
                # Adjust column indices if out of range
                if start_index < 0:
                    start_index = 0
                if end_index >= total_cols:
                    end_index = total_cols - 1
                if end_index < start_index:
                    start_index, end_index = end_index, start_index # Swap if end_index < start_index

                state_file = self.get_state_file_path(file_path, start_index, end_index, step_size, loop_mode, orientation)

                # Determine chosen_index (column index)
                if loop_mode == "disabled":
                    chosen_index = start_index

                elif loop_mode == "random":
                    chosen_index = random.randint(start_index, end_index)

                elif loop_mode == "increment":
                    current_index = self.read_current_index(state_file, start_index)
                    chosen_index = current_index
                    new_index = chosen_index + step_size
                    if new_index > end_index:
                        new_index = start_index
                    self.write_current_index(state_file, new_index)

                else:
                    chosen_index = start_index

                if 0 <= chosen_index < total_cols: # Check if chosen_index is valid column index
                    col_data = [row[chosen_index] if len(row) > chosen_index else "" for row in data] # Extract data from chosen column, handle shorter rows
                    row_text = delimiter.join(map(str, col_data)) # Join column data with delimiter
                else:
                    row_text = "" # Handle out of bound index, return empty string or handle as needed

            elif orientation == "specific_column": # New "specific_column" mode
                try:
                    col_index = self.column_letter_to_index(column_name.upper()) # Convert column letter to index
                except ValueError:
                    print(f"Error: Invalid column name: {column_name}. Please use letters like A, B, C, etc.")
                    return ("",)

                if col_index < 0:
                    print(f"Error: Column index out of range.")
                    return ("",)

                state_file = self.get_state_file_path(file_path, start_index, end_index, step_size, loop_mode, orientation, column_name) # Include column name in state file

                # Determine chosen_index (row index for looping within the column) - still use row indices for loop modes
                if loop_mode == "disabled":
                    chosen_index = start_index

                elif loop_mode == "random":
                    chosen_index = random.randint(start_index, end_index)

                elif loop_mode == "increment":
                    current_index = self.read_current_index(state_file, start_index)
                    chosen_index = current_index
                    new_index = chosen_index + step_size
                    if new_index > end_index:
                        new_index = start_index
                    self.write_current_index(state_file, new_index)

                else:
                    chosen_index = start_index

                if 0 <= chosen_index < total_rows: # Check if chosen_index is valid row index
                    if total_cols > col_index: # Check if column exists in the row
                        row_data = data[chosen_index][col_index] # Get data from specific column and chosen row
                        row_text = str(row_data) # No need to join, it's a single cell value
                    else:
                        row_text = "" # Column index out of range for this row
                else:
                    row_text = "" # Row index out of range


            else:
                row_text = "" # Default case, should not happen

            # Remove leading/trailing quotes (standard and fancy quotes)
            row_text = row_text.strip(' "“”')

            print(f"[DEBUG] Mode: {loop_mode}, Orientation: {orientation}, Chosen Index: {chosen_index}, Column: {column_name}") # Added column name to debug print
            print(f"[DEBUG] Raw Row Text: {repr(row_text)}")

            # Return only the row_text
            return (row_text,)

        except Exception as e:
            print(f"Error in RK_CSV_File_State_Looper_v01: {str(e)}")
            return ("",)

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "RK_CSV_File_State_Looper_v01": RK_CSV_File_State_Looper_v01
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "RK_CSV_File_State_Looper_v01": "📜 RK CSV File State Looper_v01"
}