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
print 'dst1, rly15, rly14, rly13, rly12'

os.system("gnome-terminal -e 'bash -c \"python mynd.py -i dst1 ; exec bash\"'")
time.sleep(1)
os.system("gnome-terminal -e 'bash -c \"python mynd.py -i rly15; exec bash\"'")
time.sleep(1)
os.system("gnome-terminal -e 'bash -c \"python mynd.py -i rly14; exec bash\"'")
time.sleep(1)
os.system("gnome-terminal -e 'bash -c \"python mynd.py -i rly13; exec bash\"'")
time.sleep(1)
os.system("gnome-terminal -e 'bash -c \"python mynd.py -i rly12; exec bash\"'")
