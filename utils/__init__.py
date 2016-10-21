import sys
import tty

male_names = {
    'Kendall', 'Antonio', 'Garry', 'Dewitt', 'Douglas', 'Wilford', 'Wiley',
    'Casey', 'Brian', 'Rocco', 'Michael', 'Gregg', 'Jesse', 'Darrick',
    'Derrick', 'Dong', 'Tim', 'Donovan', 'Man', 'Oswaldo', 'Steve', 'Kareem',
    'Abel', 'Stanley', 'Gustavo', 'Heriberto', 'Marcus', 'Darryl', 'Kerry',
    'Monty', 'Elliot', 'Brant', 'Perry', 'Leonardo', 'Lonny', 'Santos',
    'Delbert', 'Ahmed', 'Darron', 'Kendrick', 'Danial', 'Sam', 'Otto',
    'Lawrence', 'Gerard', 'Victor', 'Jimmie', 'Dorian', 'Alberto', 'Craig'
}
female_names = {
    'Tobi', 'Addie', 'Myriam', 'Danette', 'Jacquelin', 'Shawana', 'Erica',
    'Eleanore', 'Maire', 'Gabriella', 'Reva', 'Elaina', 'Margene', 'Kisha',
    'Leonor', 'Jada', 'Marsha', 'Chau', 'Krystle', 'Dorcas', 'Sofia', 'Kandis',
    'Lois', 'Rochel', 'Lavina', 'Esta', 'Slyvia', 'Nicola', 'Yoko', 'Kathrine',
    'Keira', 'Luisa', 'Gracie', 'Karlene', 'Heather', 'Katlyn', 'Piper',
    'Carita', 'Elenor', 'Izola', 'Myra', 'Jacquline', 'Shaunta', 'Florida',
    'Brandy', 'Nada', 'Jenell', 'Shawna', 'Becki', 'Marcelle'
}
all_names = male_names | female_names


def _find_getch():
    try:
        import termios
    except ImportError:
        # Non-POSIX. Return msvcrt's (Windows') getch.
        import msvcrt
        return msvcrt.getch

    # POSIX system. Create and return a getch that manipulates the tty.
    def _getch():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    return _getch

getch = _find_getch()
