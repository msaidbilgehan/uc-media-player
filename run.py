import libs
from structure_ui import init_and_run_UI
from constructor_ui import Player_UI
# from structure_system import System_Object

if __name__ == "__main__":
    """
    system_info = System_Object()
    system_info.thread_print_info()
    """
    app, ui = init_and_run_UI(
        "UART Player",
        Player_UI,
        UI_File_Path="player_v2_UI.ui"
    )
