import os
import sys
import random
import csv

class RK_CSV_File_State_Looper_v02: # Renamed class to v02
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path": ("STRING", {
                    "multiline": False,
                    "default": "path/to/your_file.csv"
                }),
                "orientation": (["horizontal_row", "vertical_column", "specific_columns"],),
                "column_name_1": ("STRING", {
                    "default": "B",
                    "multiline": False
                }),
                "column_name_2": ("STRING", {
                    "default": "D",
                    "multiline": False
                }),
                "column_name_3": ("STRING", { # Added column_name_3 input
                    "default": "A",
                    "multiline": False
                }),
                "column_name_4": ("STRING", { # Added column_name_4 input
                    "default": "E",
                    "multiline": False
                }),
                "column_name_5": ("STRING", { # Added column_name_5 input
                    "default": "F",
                    "multiline": False
                }),
                "loop_mode": (["disabled", "random", "increment"],),
                "start_index": ("INT", {
                    "default": 2,
                    "min": 0,
                    "max": 100000,
                    "step": 1
                }),
                "end_index": ("INT", {
                    "default": 999999,
                    "min": 0,
                    "max": 999999,
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

    # Now five return types
    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING",) # Added two more return types
    RETURN_NAMES = ("column_1_text", "column_2_text", "column_3_text", "column_4_text", "column_5_text",) # Added two more return names
    FUNCTION = "read_row"
    CATEGORY = "RK_tools_v02"

    # Cache variables
    file_data_cache = None
    file_path_cache = None

    def load_file(self, file_path, delimiter):
        """
        Loads a CSV file into a list of lists and caches it.
        """
        if RK_CSV_File_State_Looper_v02.file_path_cache != file_path: # Updated class name
            if not os.path.isfile(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            _, ext = os.path.splitext(file_path)
            ext = ext.lower()

            if ext != ".csv":
                raise ValueError(f"Unsupported file extension: {ext}. Only .csv is supported.")

            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f, delimiter=delimiter)
                data = list(reader)

            RK_CSV_File_State_Looper_v02.file_data_cache = data # Updated class name
            RK_CSV_File_State_Looper_v02.file_path_cache = file_path # Updated class name

        return RK_CSV_File_State_Looper_v02.file_data_cache # Updated class name

    def get_row_count(self, data):
        return len(data)

    def get_column_count(self, data):
        if not data:
            return 0
        return len(data[0]) if data[0] else 0 # Handle empty first row

    def get_state_file_path(self, file_path, start_index, end_index, step_size, loop_mode, orientation, column_name_1="", column_name_2="", column_name_3="", column_name_4="", column_name_5=""): # Added column_name_4 and column_name_5
        base, ext = os.path.splitext(file_path)
        state_file = f"{base}_state_{orientation}_{column_name_1}_{column_name_2}_{column_name_3}_{column_name_4}_{column_name_5}_{loop_mode}_{start_index}_{end_index}_{step_size}.txt" # Added column_name_4 and column_name_5 to state file name
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


    def read_row(self, file_path, orientation, loop_mode, start_index, end_index, step_size, delimiter, column_name_1, column_name_2, column_name_3, column_name_4, column_name_5): # Added column_name_4 and column_name_5 parameter
        try:
            data = self.load_file(file_path, delimiter)
            total_rows = self.get_row_count(data)
            total_cols = self.get_column_count(data)
            column_1_text = ""
            column_2_text = ""
            column_3_text = "" # Initialize column_3_text
            column_4_text = "" # Initialize column_4_text
            column_5_text = "" # Initialize column_5_text

            if orientation == "horizontal_row":
                # ... (Horizontal row logic - no changes needed here) ...
                if start_index < 0:
                    start_index = 0
                if end_index >= total_rows:
                    end_index = total_rows - 1
                if end_index < start_index:
                    start_index, end_index = end_index, start_index

                state_file = self.get_state_file_path(file_path, start_index, end_index, step_size, loop_mode, orientation)

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

                if 0 <= chosen_index < total_rows:
                    row_data = data[chosen_index]
                    row_text = delimiter.join(map(str, row_data))
                    column_1_text = row_text
                    column_2_text = ""
                    column_3_text = "" # column_3_text is empty in horizontal mode
                    column_4_text = "" # column_4_text is empty in horizontal mode
                    column_5_text = "" # column_5_text is empty in horizontal mode
                else:
                    column_1_text = ""
                    column_2_text = ""
                    column_3_text = ""
                    column_4_text = ""
                    column_5_text = ""


            elif orientation == "vertical_column":
                # ... (Vertical column logic - no changes needed here) ...
                if start_index < 0:
                    start_index = 0
                if end_index >= total_cols:
                    end_index = total_cols - 1
                if end_index < start_index:
                    start_index, end_index = end_index, start_index

                state_file = self.get_state_file_path(file_path, start_index, end_index, step_size, loop_mode, orientation)

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

                if 0 <= chosen_index < total_cols:
                    col_data = [row[chosen_index] if len(row) > chosen_index else "" for row in data]
                    row_text = delimiter.join(map(str, col_data))
                    column_1_text = row_text
                    column_2_text = ""
                    column_3_text = "" # column_3_text is empty in vertical mode
                    column_4_text = "" # column_4_text is empty in vertical mode
                    column_5_text = "" # column_5_text is empty in vertical mode
                else:
                    column_1_text = ""
                    column_2_text = ""
                    column_3_text = ""
                    column_4_text = ""
                    column_5_text = ""


            elif orientation == "specific_columns":
                col_index_1 = -1
                col_index_2 = -1
                col_index_3 = -1 # Initialize col_index_3
                col_index_4 = -1 # Initialize col_index_4
                col_index_5 = -1 # Initialize col_index_5
                try:
                    col_index_1 = self.column_letter_to_index(column_name_1.upper())
                except ValueError:
                    print(f"Error: Invalid column name for Column 1: {column_name_1}. Please use letters like A, B, C, etc.")
                    return ("", "", "", "", "") # Return five empty strings on error

                try:
                    col_index_2 = self.column_letter_to_index(column_name_2.upper())
                except ValueError:
                    print(f"Error: Invalid column name for Column 2: {column_name_2}. Please use letters like A, B, C, etc.")
                    return ("", "", "", "", "") # Return five empty strings on error

                try:
                    col_index_3 = self.column_letter_to_index(column_name_3.upper()) # Get index for column 3
                except ValueError:
                    print(f"Error: Invalid column name for Column 3: {column_name_3}. Please use letters like A, B, C, etc.")
                    return ("", "", "", "", "") # Return five empty strings on error

                try:
                    col_index_4 = self.column_letter_to_index(column_name_4.upper()) # Get index for column 4
                except ValueError:
                    print(f"Error: Invalid column name for Column 4: {column_name_4}. Please use letters like A, B, C, etc.")
                    return ("", "", "", "", "") # Return five empty strings on error

                try:
                    col_index_5 = self.column_letter_to_index(column_name_5.upper()) # Get index for column 5
                except ValueError:
                    print(f"Error: Invalid column name for Column 5: {column_name_5}. Please use letters like A, B, C, etc.")
                    return ("", "", "", "", "") # Return five empty strings on error


                if col_index_1 < 0 or col_index_2 < 0 or col_index_3 < 0 or col_index_4 < 0 or col_index_5 < 0: # Check for col_index_3, 4 and 5 as well
                    print(f"Error: Column index out of range.")
                    return ("", "", "", "", "") # Return five empty strings on error

                state_file = self.get_state_file_path(file_path, start_index, end_index, step_size, loop_mode, orientation, column_name_1, column_name_2, column_name_3, column_name_4, column_name_5) # Include column_name_3, 4 and 5 in state file

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

                if 0 <= chosen_index < total_rows:
                    if total_cols > col_index_1:
                        column_1_text = str(data[chosen_index][col_index_1])
                    else:
                        column_1_text = ""

                    if total_cols > col_index_2:
                        column_2_text = str(data[chosen_index][col_index_2])
                    else:
                        column_2_text = ""

                    if total_cols > col_index_3: # Get data for column 3
                        column_3_text = str(data[chosen_index][col_index_3])
                    else:
                        column_3_text = ""

                    if total_cols > col_index_4: # Get data for column 4
                        column_4_text = str(data[chosen_index][col_index_4])
                    else:
                        column_4_text = ""

                    if total_cols > col_index_5: # Get data for column 5
                        column_5_text = str(data[chosen_index][col_index_5])
                    else:
                        column_5_text = ""
                else:
                    column_1_text = ""
                    column_2_text = ""
                    column_3_text = "" # Row index out of range, set column_3_text to empty
                    column_4_text = "" # Row index out of range, set column_4_text to empty
                    column_5_text = "" # Row index out of range, set column_5_text to empty


            else:
                column_1_text = ""
                column_2_text = ""
                column_3_text = "" # Default case, initialize column_3_text
                column_4_text = "" # Default case, initialize column_4_text
                column_5_text = "" # Default case, initialize column_5_text

            column_1_text = column_1_text.strip(' "“”')
            column_2_text = column_2_text.strip(' "“”')
            column_3_text = column_3_text.strip(' "“”') # Strip quotes from column_3_text
            column_4_text = column_4_text.strip(' "“”') # Strip quotes from column_4_text
            column_5_text = column_5_text.strip(' "“”') # Strip quotes from column_5_text

            print(f"[DEBUG] Mode: {loop_mode}, Orientation: {orientation}, Chosen Index: {chosen_index}, Column 1: {column_name_1}, Column 2: {column_name_2}, Column 3: {column_name_3}, Column 4: {column_name_4}, Column 5: {column_name_5}") # Debug print for five columns
            print(f"[DEBUG] Raw Column 1 Text: {repr(column_1_text)}")
            print(f"[DEBUG] Raw Column 2 Text: {repr(column_2_text)}")
            print(f"[DEBUG] Raw Column 3 Text: {repr(column_3_text)}") # Debug print for column_3_text
            print(f"[DEBUG] Raw Column 4 Text: {repr(column_4_text)}") # Debug print for column_4_text
            print(f"[DEBUG] Raw Column 5 Text: {repr(column_5_text)}") # Debug print for column_5_text


            # Return all five column texts
            return (column_1_text, column_2_text, column_3_text, column_4_text, column_5_text,) # Return column_3_text, column_4_text, column_5_text

        except Exception as e:
            print(f"Error in RK_CSV_File_State_Looper_v02: {str(e)}") # Updated error message to v02
            return ("", "", "", "", "") # Return five empty strings on error

# Node class mappings
NODE_CLASS_MAPPINGS = {
    "RK_CSV_File_State_Looper_v02": RK_CSV_File_State_Looper_v02 # Updated class name in mappings
}

# Node display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    "RK_CSV_File_State_Looper_v02": "📜 RK CSV File State Looper_v02" # Updated display name in mappings
}