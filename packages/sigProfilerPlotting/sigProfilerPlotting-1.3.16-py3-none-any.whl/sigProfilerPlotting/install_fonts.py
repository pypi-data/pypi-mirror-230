import os
import shutil

import matplotlib
import pkg_resources


"""
Code for installing custom fonts for matplotlib.
"""


# Set up the machinery to install custom fonts.  Subclass the setup tools install
# class in order to run custom commands during installation.
class FontInstaller:
    def run(self):
        """
        Install the fonts in the matplotlib font directory.
        """

        # try:
        # Find where matplotlib stores its True Type fonts
        mpl_data_dir = os.path.dirname(matplotlib.matplotlib_fname())
        mpl_ttf_dir = os.path.join(mpl_data_dir, "fonts", "ttf")
        cp_ttf_dir = pkg_resources.resource_filename("sigProfilerPlotting", "fonts")

        file_names = [
            "Times New Roman.ttf",
            "Arial.ttf",
            "Courier New.ttf",
            "Courier New Bold.ttf",
            "Arial Bold.ttf",
            "Times New Roman Bold.ttf",
        ]
        for file in file_names:
            old_path = os.path.join(cp_ttf_dir, file)
            new_path = os.path.join(mpl_ttf_dir, file)
            shutil.copyfile(old_path, new_path)

        print("Fonts installed successfully.")

        # except:
        #     print("WARNING: An issue occured while installing the fonts.")
