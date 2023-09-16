# Fixme: this demo is still work in progress
import imgui_bundle
from imgui_bundle import imgui, hello_imgui, immapp
from imgui_bundle.demos_python import demo_utils
import sdl2  # type: ignore # always import sdl2 *after* imgui_bundle


def show_gui():
    imgui.text("Hello, _World_")

    if imgui.button("Test SDL call"):
        # Fixme: the pointers returned by imgui_bundle.sdl_utils do not work.
        # This button should move and rename the window, but it fails silently
        win = imgui_bundle.sdl_utils.sdl2_window_hello_imgui()
        sdl2.SDL_SetWindowTitle(win, b"Changed title via  SDL!!!")
        sdl2.SDL_SetWindowSize(win, 100, 100)

    if imgui.button("Bye"):
        hello_imgui.get_runner_params().app_shall_exit = True


def main():
    hello_imgui.set_assets_folder(demo_utils.demos_assets_folder())

    runner_params = immapp.RunnerParams()
    runner_params.backend_type = hello_imgui.BackendType.sdl

    runner_params.callbacks.show_gui = show_gui

    immapp.run(runner_params)


if __name__ == "__main__":
    main()
