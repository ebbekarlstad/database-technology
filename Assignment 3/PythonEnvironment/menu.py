# Print the header
def print_header(title):
    header_width = 66  # Width of the header lines including stars
    title_string = f"****{title.center(header_width - 8)}****"
    print("*" * header_width)
    print("*" + " " * (header_width - 2) + "*")
    print(title_string)
    print("*" + " " * (header_width - 2) + "*")
    print("*" * header_width)

def print_options(options):
    for i in range(len(options)):
        print(f"{i+1}. {options[i]}")

# Check_choice function
def check_choice(maxOptions):
    selectedOption = None
    
    while selectedOption is None:
        choice = input("Enter choice: ")
        try:
            choice_int = int(choice)  # Convert to integer
            if choice_int in range(1, maxOptions + 1):
                selectedOption = choice_int  # Use integer for comparison
            else:
                print("Invalid input: Please select the available options.")
        except ValueError:  # More specific exception
            print("Invalid input: Should be a number.")
    return selectedOption