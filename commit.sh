#!/usr/bin/env bash

#**********************************************************************************************************************#
#                                        PYTOOLBOX - TOOLBOX FOR PYTHON SCRIPTS
#
#  Main Developer : David Fischer (david.fischer.ch@gmail.com)
#  Copyright      : Copyright (c) 2012-2015 David Fischer. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of David Fischer's pytoolbox Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/davidfischer-ch/pytoolbox.git

warning()
{
    echo "[WARNING] $1" 1>&2
    echo 'press enter to continue or ctrl+c to exit ...'
    read a
}

sudo python2 setup.py test || warning 'Python 2 unit-test of pytoolbox failed'
sudo python3 setup.py test || warning 'Python 3 unit-test of pytoolbox failed'
python3 setup.py docs || warning 'Sphinx is not fully happy with our docstrings'
cd ..
git commit
