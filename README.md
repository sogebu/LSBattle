# Light Speed Battle

[日本語版](./README-ja.md)

This is a FPS game where you can experience special relativity.

![SS1](./play_screenshot_1.png)
![SS2](./play_screenshot_2.png)

## Usage

dependency

* Python3
* OpenGL
* SDL2

How to build

1. Install Python3
2. Install OpenGL
    * At macOS `brew install glfw`
3. If it doesn't work with the SDL2 included in this repository, install SDL2 on your own.
    * At macOS `brew install sdl2`
4. Install Python lib

    ```
    pip install pipenv
    pipenv install -d
    ```
5. Built by Cython

    ```
    python cython_setup.py build_ext --inplace
    ```
6. Let's play!

    ```
    pipenv run python LSBattle3D.py
    ```

## License

### Source Code

This project is licensed under the **zlib License**.

### Assets

The assets used in this project are **licensed separately** from the source code.
Please check the individual licenses before redistribution or modification.

| Asset | Source | License |
|--------|-----------------------------------------------|-------------|
| **3D Models** | http://www.geocities.jp/oirahakobito2/sozai/sozai.html (site closed, see web archive) | **CC BY 4.0** |
| **Milky Way Image** | https://www.eso.org/public/images/eso0932a/ | **CC BY 4.0** |
| **Earth & Moon Images** | https://visibleearth.nasa.gov/ | **NASA Licensed** (Public Domain) |
| **Kiloji Font** | http://www.ez0.net/distribution/font/kiloji/ (site closed, see web archive) | **BSD 3-Clause (NewBSD License)** |
| **Einstein Image** | http://www.courseweb.uottawa.ca/Mat4183/ (site closed, see web archive) | **Public Domain** |
| **Yukkuri Marisa/Reimu** | 2ch & Niconico | **Public Domain** |

For assets licensed under **CC BY 4.0**, you must provide proper attribution when using them. See [Creative Commons Attribution 4.0 International](https://creativecommons.org/licenses/by/4.0/) for details.

If you have any questions regarding licensing, please check the original sources linked above or contact the respective copyright holders.
