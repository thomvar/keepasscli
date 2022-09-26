from argparse import ArgumentParser, Namespace
from getpass import getpass
from os.path import dirname, isfile
from time import sleep
from pykeepass import PyKeePass, create_database
from pykeepass.exceptions import CredentialsError
from pykeepass.group import Group
from pykeepass.entry import Entry


def get_arguments() -> Namespace:
    """Parse the user input."""

    def validate_arguments(parser: ArgumentParser) -> Namespace:
        """Try to ensure that we can work with the user input."""

        def test_path(file_name):
            return arguments.new or isfile(file_name) or isfile(dirname(__file__) + file_name)

        def ask_for_file():
            file_name = input("What file do you want to open? ")
            if not test_path(file_name):
                return file_name

        arguments = parser.parse_args()
        while not arguments.file:
            parser.parse_args(args=["--file", ask_for_file()], namespace=arguments)
        while not test_path(arguments.file):
            print(f"{arguments.file} not found on the system")
            parser.parse_args(args=["--file", ask_for_file()], namespace=arguments)
        return arguments

    parser = ArgumentParser(description="Read KeePassX databases")
    parser.add_argument("-f", "--file", type=str, help="File to open")
    parser.add_argument("-n", "--new", action="store_true")
    return validate_arguments(parser)


def load_databases(file_name: str, new: bool=False) -> PyKeePass:
    """Create or open a database."""
    try_again = 0
    while try_again < 3:
        password = getpass("Database password: ")
        if new:
            return create_database(file_name, password=password)
        try:
            return PyKeePass(file_name, password=password)
        except CredentialsError:
            try_again += 1


def make_selection(options, quit: bool=True, back: bool=False):
    """Use a list to make a selection. Add `quit` to give the user the option to exit the
    application. Use `back` to move back to a previous selection (if applicable)."""
    number_of_selections = len(options)
    last_option = number_of_selections
    for index, option in enumerate(options):
        print(index + 1, option, sep=". ")
    if back:
        number_of_selections += 1
        print(number_of_selections, "Back", sep=". ")
    if quit:
        last_option = number_of_selections + 1
        print(number_of_selections + 1, "Quit", sep=". ")
    selection = None
    while not isinstance(selection, int) or 0 > selection > number_of_selections:
        try:
            selection = int(input(f"Select option [1-{last_option}]:"))
        except ValueError:
            pass
        else:
            try:
                # This is just to prevent negative numbers. Allowing it is a nice Easter egg
                # but it might confuse non technical users.
                if selection < 1:
                    raise IndentationError
                return options[selection-1]
            except IndexError:
                if back and selection == number_of_selections:
                    return None
                elif quit and selection == last_option:
                    exit()


def get_group(database: PyKeePass) -> Group:
    """List all groups and help the user select one of them."""
    print("Select a group:")
    return make_selection(database.groups)


def get_entry(group: Group) -> Entry:
    """List all entries in `group` and help the user select one."""
    print("Select an entry:")
    return make_selection(group.entries, back=True)


def get_entry_data(entry: Entry):
    """Naively print some of the entry data."""
    print(f"Data for {entry.title}")
    print(entry.url, entry.password, sep="\n")
    print("-"*10)
    return make_selection([], back=True)


def workflow() -> bool:
    """Basic actions to perform on the database."""
    group = get_group(dbx)
    entry = get_entry(group)
    while not entry:
        group = get_group(dbx)
        entry = get_entry(group)
    return not get_entry_data(entry)


if __name__ == "__main__":
    arguments = get_arguments()
    dbx = load_databases(arguments.file, arguments.new)
    while workflow():
        pass
