# -*- coding: utf-8 -*-
# @Author: Jason Y. Wu
# @Date:   2023-07-03 22:44:39
# @Last Modified by:   Jason Y. Wu
# @Last Modified time: 2023-08-10 18:47:17

import setuptools

if __name__ == "__main__":
    setuptools.setup(license_files=["LICENSE"],
                     packages=setuptools.find_packages(where="src"),
                     package_dir={"": "src"},
                     include_package_data=True)
    
