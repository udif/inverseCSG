import os, sys, subprocess
import readline, glob # For autocompleting file path.
import urllib.request
import shutil
import helper

# Logics behind this script: it tries to check if all necessary dependences are
# installed. If any of them is missing, it will attempt to download and install
# them, which may require adding new environment variables. To avoid polluting
# users' environment variables, we will save them into an ENVIRONMENT file and
# load them at the beginning of our scripts.

################################################################################
# Helpers.
################################################################################

# Credit:
# https://stackoverflow.com/questions/6656819/filepath-autocompletion-using-users-input
def AutoComplete(text, state):
  return (glob.glob(text + '*') + [None])[state]

def SaveCustomizedEnvironmentVariables(env_variables, file_path):
  f = open(file_path, 'w')
  f.write('# You can manually change the environment variables below:\n')
  for key, val in env_variables.items():
    f.write('%s: %s\n' % (key, val))

def CheckVersionNumber(version_number, target):
  major, minor, change = version_number.split('.')
  major = int(major)
  minor = int(minor)
  change = int(change)
  target_major, target_minor, target_change = target.split('.')
  target_major = int(target_major)
  target_minor = int(target_minor)
  target_change = int(target_change)
  if major > target_major:
    return True
  if major < target_major:
    return False
  if minor > target_minor:
    return True
  if minor < target_minor:
    return False
  if change >= target_change:
    return True
  else:
    return False
  
def CheckSketch():
  sketch_result = subprocess.getoutput('sketch')
  # The first line should be something like:
  # SKETCH version 1.7.4
  # The following is not a very robust way to check the version number.
  if 'SKETCH version' not in sketch_result:
    return False
  # Now check version number.
  first_line = sketch_result.splitlines()[0]
  _, _, version_number = first_line.strip().split()
  # Expect to see >= 1.7.4.
  if not CheckVersionNumber(version_number, '1.7.4'):
    return False
  # Now Sketch seems working.
  helper.PrintWithGreenColor('Sketch %s seems successfully installed.' %
                       version_number)
  # Save environment variables into files.
  sketch_loc = subprocess.getoutput('whereis sketch')
  env_variables['CSG_SKETCH'] = sketch_loc.strip().split()[1].strip()
  # Auto-complete paths.
  readline.set_completer_delims(' \t\n;')
  readline.parse_and_bind('tab: complete')
  readline.set_completer(AutoComplete)
  while 'CSG_SKETCH_FRONTEND' not in env_variables:
    sketch_frontend_folder = '/home/runner/work/inverseCSG/inverseCSG/sketch-frontend'
    env_variables['CSG_SKETCH_FRONTEND'] = sketch_frontend_folder
  while 'CSG_SKETCH_BACKEND' not in env_variables:
    sketch_backend_folder = '/home/runner/work/inverseCSG/inverseCSG/sketch-backend'
    env_variables['CSG_SKETCH_BACKEND'] = sketch_backend_folder
  return True

def InstallCGAL():
  helper.Run('sudo apt-get install libcgal-dev -y')
  cgal_url = 'https://github.com/CGAL/cgal/releases/download/' \
             'releases%2FCGAL-4.12/CGAL-4.12.zip'
  cgal_file = os.path.join(build_folder, 'cgal.zip')
  urllib.request.urlretrieve(cgal_url, cgal_file)
  helper.Run('unzip -o -q %s -d %s' % (cgal_file, build_folder))
  os.remove(cgal_file)
  # Now you have the source code.
  helper.PrintWithGreenColor('Downloaded and unzipped CGAL 4.12')
  cgal_dir = ''
  for folder_name in os.listdir(build_folder):
    if 'cgal' in folder_name or 'CGAL' in folder_name:
      cgal_dir = os.path.join(build_folder, folder_name)
      break
  # Add cgal_root to the environment variable list.
  env_variables['CGAL_DIR'] = os.environ['CGAL_DIR'] = cgal_dir
#   helper.Run('sudo cp '+cgal_dir+'/lib/* /usr/lib')
#   helper.Run('sudo ls /usr/lib/libC*')
  helper.PrintWithGreenColor('Installed libcgal-dev')

def InstallEigen():
  helper.Run('wget https://gitlab.com/libeigen/eigen/-/archive/3.3.4/eigen-3.3.4.zip')
  cpp_lib_folder = os.path.join(root_folder, 'cpp', 'lib')
  helper.Run('unzip eigen-3.3.4.zip -d %s' % os.path.join(cpp_lib_folder))
  helper.Run('ls -latr')
  helper.Run('rm eigen-3.3.4.zip')
  helper.PrintWithGreenColor('Installed Eigen')

def InstallJava():
  helper.Run('sudo apt-get install software-properties-common')
  helper.Run('sudo apt-get update')
  helper.Run('sudo apt install default-jdk')
  # Currently JAVA_HOME is hard coded.
  helper.RunWithStdout('ls /usr/lib/jvm/')
  java_home = subprocess.getoutput('readlink -f /usr/lib/jvm/default-java')
  env_variables['JAVA_HOME'] = os.environ['JAVA_HOME'] = java_home
  path = os.path.join(java_home, 'bin') + ':' + os.environ['PATH']
  env_variables['PATH'] = os.environ['PATH'] = path
  helper.Run('%s -version' % os.path.join(java_home, 'bin', 'java'))

def InstallMaven():
  with urllib.request.urlopen('https://maven.apache.org/download.cgi') as response:
    now = False
    for l in response.readlines():
      if now:
        maven_mirror = l.decode('utf-8').split('b>')[1][:-2]
        break
      if l.decode('utf-8').find('The currently selected download mirror is') >= 0:
        now = True
  maven_url = maven_mirror + 'maven/maven-3/3.5.4/binaries/apache-maven-3.5.4-bin.zip'
  maven_file = os.path.join(build_folder, 'maven.zip')
  print(maven_url)
  urllib.request.urlretrieve(maven_url, maven_file)
  helper.RunWithStdout('unzip -q %s -d %s' % (maven_file, build_folder))
  os.remove(maven_file)
  # ls build dir after maven unzip
  print('build_folder: %s' % (build_folder))
  helper.RunWithStdout('ls %s' % (build_folder))
  # Add it to the environment variable.
  for folder_name in os.listdir(build_folder):
    if 'maven' in folder_name:
      maven_loc = os.path.join(build_folder, folder_name, 'bin')
      # Display maven_loc
      print('maven_loc: %s' % (maven_loc))
      env_variables['PATH'] = os.environ['PATH'] \
                            = maven_loc + ':' + os.environ['PATH']
      print('env_PATH_variables: %s' % (env_variables['PATH']))

  # Check maven.
  # helper.RunWithStdout('sudo rm /usr/bin/mvn') 
  helper.RunWithStdout('sudo ln -s '+maven_loc+'/mvn' +' /usr/bin/mvn' )
  helper.RunWithStdout('mvn -v')

def InstallSketch():
  # Download sketch-backend.
  sketch_folder = os.path.join(build_folder, 'sketch')
  if not os.path.exists(sketch_folder):
    os.makedirs(sketch_folder)
  # Sketch-backend.
  os.chdir(sketch_folder)
  helper.Run('git clone https://github.com/asolarlez/sketch-backend')
  #helper.Run('sudo mv sketch-backend sketch-backend-default')
  ## Use this version of sketch.
  ## decomment this if SNOPT installed
  ## helper.Run('sudo hg clone -r numsynth2 sketch-backend-default sketch-backend') 
  #helper.Run('sudo hg clone -r 04b3403 sketch-backend-default sketch-backend')
  sketch_backend_folder = os.path.join(sketch_folder, 'sketch-backend')
  env_variables['CSG_SKETCH_BACKEND'] = sketch_backend_folder
  os.chdir(sketch_backend_folder)
  helper.Run('bash autogen.sh')
  #helper.RunWithStdout('ls')
  #helper.RunWithStdout('find . -name "config.log"')
  #helper.RunWithStdout('sudo df -h .')
  #helper.RunWithStdout('ls -l configure')
  #helper.RunWithStdout('sudo cat /etc/fstab')
  helper.RunWithStdout('./configure')
  #helper.RunWithStdout('sudo gcc -v')
  #helper.RunWithStdout('sudo cp '+ os.path.join(root_folder,'StringHTable.h') + ' ' + os.path.join(sketch_folder, 'sketch-backend/src/SketchSolver/InputParser/StringHTable.h'))
  #helper.RunWithStdout('sudo make -j2 -w -s --no-print-directory')
  helper.RunWithStdout('make -j{} -w -s --no-print-directory'.format(cpu_cores))
  # Interestingly, I need to manually do the following copy and paste work to
  # avoid an error in sketch-frontend.
  sketch_solver_folder = os.path.join(sketch_backend_folder, 'src/SketchSolver')
  helper.RunWithStdout('ls '+ os.path.join(sketch_solver_folder))
  shutil.copyfile(os.path.join(sketch_solver_folder, 'libcegis.a'), \
                  os.path.join(sketch_solver_folder, '.libs/libcegis.a'))
  shutil.copyfile(os.path.join(sketch_solver_folder, 'cegis'), \
                  os.path.join(sketch_solver_folder, '.libs/cegis'))

  # Download sketch-frontend.
  os.chdir(sketch_folder)
  helper.Run('git clone https://github.com/asolarlez/sketch-frontend')
  #helper.Run('sudo mv sketch-frontend sketch-frontend-default')
  # Use this version of sketch.
  #helper.Run('sudo hg clone -r 2c8b363 sketch-frontend-default sketch-frontend')
  sketch_frontend_folder = os.path.join(sketch_folder, 'sketch-frontend')
  env_variables['CSG_SKETCH_FRONTEND'] = sketch_frontend_folder
  os.chdir(sketch_frontend_folder)
  shutil.copyfile(os.path.join(root_folder, 'pom.xml'), \
                  os.path.join(sketch_frontend_folder, 'pom.xml'))
  helper.Run('sudo make system-install DESTDIR=/usr/bin SUDOINSTALL=1 -w --no-print-directory -s')

  # Now check Sketch again.
  if not CheckSketch():
    helper.PrintWithRedColor('Failed to install Sketch. Please fix.')
    sys.exit(-1)


################################################################################
# Variables.
################################################################################
env_variables = {}

################################################################################
# Beginning of the script.
################################################################################
# Usage: python3 install.py <build folder>
if len(sys.argv) < 2:
  print('Usage: python3 install.py <build_folder>')
  sys.exit(-1)
cpu_cores = subprocess.getoutput('grep cores /proc/cpuinfo').split()[3]
build_folder = os.path.realpath(sys.argv[1])
root_folder = os.path.dirname(os.path.realpath(sys.argv[0]))
if not os.path.exists(build_folder):
  os.makedirs(build_folder)
helper.PrintWithGreenColor('Build folder created.')

# Add a new environment variable to save the location of the root folder.
env_variables['CSG_ROOT'] = os.environ['CSG_ROOT'] = root_folder

# show LIBC version
helper.RunWithStdout('sudo dpkg -l libc6')

# This may work on Xenial
helper.Run('sudo apt-get update')
helper.Run('sudo apt-get install build-essential ' \
  'software-properties-common -y')
helper.RunWithStdout('sudo apt-get install gcc-snapshot -y')

# Install python dependencies.
helper.RunWithStdout('sudo python3 -m pip install numpy scipy matplotlib ipython '
           'jupyter pandas sympy nose')
helper.RunWithStdout('sudo python3 -m pip install -U scikit-learn')
helper.RunWithStdout('sudo apt-get install autoconf libtool flex bison zsh cmake unzip -y')

# BISON version should be gt 3
helper.RunWithStdout('bison --version')

# Install CGAL.
InstallCGAL()

# Install Eigen-3.3.4.
InstallEigen()

# Compile cpp.
cpp_build_folder = os.path.join(build_folder, 'cpp')
if not os.path.exists(cpp_build_folder):
  os.makedirs(cpp_build_folder)
os.chdir(cpp_build_folder)
helper.RunWithStdout('sudo ls /usr/bin/gcc*')
helper.RunWithStdout('sudo ls /usr/bin/g++*')
os.environ['CC'] = '/usr/bin/gcc-9'
os.environ['CXX'] = '/usr/bin/g++-9'
helper.Run('sudo cmake -DCGAL_DIR=%s %s' % (env_variables['CGAL_DIR'], \
                                       os.path.join(root_folder, 'cpp')))
helper.Run('sudo make -j{} -w -s --no-print-directory -j'.format(cpu_cores))
helper.PrintWithGreenColor('C++ program compiled successfully.')
env_variables['CSG_CPP_EXE'] = os.path.join(cpp_build_folder,
                                            'csg_cpp_command')

# Install Sketch.
# Try calling Sketch. If it is successful, we are done.
if CheckSketch():
  SaveCustomizedEnvironmentVariables(env_variables, os.path.join(
    build_folder, 'ENVIRONMENT'))
  helper.PrintWithGreenColor('Installation Done.')
  sys.exit(0)
else:
  # If we are here, Sketch is not properly installed.
  # First, install Oracle JDK 8.
  print('Attempt to install Oracle JDK 8. Asking for sudo privilege.')
  InstallJava()

  # Next, install maven.
  InstallMaven()

  InstallSketch()

SaveCustomizedEnvironmentVariables(env_variables, os.path.join(
  build_folder, 'ENVIRONMENT'))

################################################################################
# Tests on samples
################################################################################

# Check on example file from CSGInverse samples
os.chdir(root_folder)
# Decomment this code if you RAM can handle these calculations
# helper.RunWithStdout('sudo python3 run_tests.py build ex_140')

# Check csg_cpp_command
os.chdir(root_folder)
helper.RunWithStdout('sudo dpkg -l libc6')
helper.RunWithStdout('sudo ldd csg_cpp_command')
# install LIBC6 2.29 (Last One from Ubuntu 19.10's gcc/g++-9)
helper.RunWithStdout('wget http://archive.ubuntu.com/ubuntu/pool/main/g/glibc/libc6_2.29-0ubuntu2_amd64.deb')
helper.RunWithStdout('sudo dpkg -i --auto-deconfigure  --force-all  libc6_2.29-0ubuntu2_amd64.deb')
helper.RunWithStdout('sudo dpkg -l --force-all  libc6') # should now be version 2.29
helper.RunWithStdout('sudo ./csg_cpp_command') # should display clean-csg/genetic/csg-mesh-diff/ransac/legacy-sketch-tree...

# TODO: Launch code on node-step part files

# TODO: Generate thumbnails of results



helper.PrintWithGreenColor('Installation Done.')
