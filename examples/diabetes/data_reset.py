############################################################################

## Licensed under the Apache License, Version 2.0 (the "License"); you may

## not use this file except in compliance with the License. You may obtain

## a copy of the License at

##

##    http://www.apache.org/licenses/LICENSE-2.0

##

## Unless required by applicable law or agreed to in writing, software

## distributed under the License is distributed on an "AS IS" BASIS, WITHOUT

## WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the

## License for the specific language governing permissions and limitations

## under the License.

############################################################################
import os
import shutil

# Clears data splits directory
def clear_data(path):
	dirs = []

	for i in os.listdir(path):
		if(not os.path.isfile(os.path.join(path,i))):
			dirs.append(os.path.join(path,i))

	for i in dirs:
		shutil.rmtree(i)

# main 
def main():
	path = "app-data/"
	clear_data(path)

if __name__ == "__main__":
	main()