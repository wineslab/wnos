# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


# This program is used to simpflify experiment management
# Start a session by starting the nodes one by one with each node using a separate terminal window
import os
import time

#os.system("gnome-terminal -e 'bash -c \"python print(n in range(10000)); exec bash\"'")


#os.system("gnome-terminal 'python print(n in range(10000))'")
print 'Starting nodes...'
print 'dst2, rly25, rly24, rly23, rly22'

os.system("gnome-terminal -e 'bash -c \"python mynd.py -i dst2 ; exec bash\"'")
time.sleep(1)
os.system("gnome-terminal -e 'bash -c \"python mynd.py -i rly25; exec bash\"'")
time.sleep(1)
os.system("gnome-terminal -e 'bash -c \"python mynd.py -i rly24; exec bash\"'")
time.sleep(1)
os.system("gnome-terminal -e 'bash -c \"python mynd.py -i rly23; exec bash\"'")
time.sleep(1)
os.system("gnome-terminal -e 'bash -c \"python mynd.py -i rly22; exec bash\"'")
