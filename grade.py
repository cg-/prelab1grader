import argparse
import zipfile
from os import path
from os import mkdir
from os import listdir
from os import linesep
from os import chdir
from shutil import copyfile
import subprocess

parser = argparse.ArgumentParser(description='Grades the scripts for prelab 1.')
parser.add_argument('zipfile', metavar='i', help='the input zip file to process')
parser.add_argument('--debug', dest='debug', action='store_true', default=False)

args = parser.parse_args()

def debug(s):
    if args.debug:
        print "debug: " + s

# first we make a working directory
if path.isdir(".working"):
    debug(".working already exists, using that directory")
else:
    mkdir(".working")
if path.isdir(".working/test"):
    debug(".working/test already exists, using that directory")
else:
    mkdir(".working/test")
count = 1
while count < 6:
    test_filename = ".working/test/testfile" + str(count)
    count += 1
    if not path.exists(test_filename):
        with open(test_filename, "w") as testfile:
            count2 = 1
            while count2 < 6:
                testfile.write("asd123 this is line " + str(count2) + linesep)
                count2 += 1
        testfile.close()


# then we extract the zip file
if path.isdir(".working/zip_contents"):
    debug("zip contents directory already exists, using that.")
else:
    with zipfile.ZipFile(args.zipfile) as zip:
        zip.extractall(".working/zip_contents")
        zip.close()

# we'll make it so we only examine students once. we'll keep a log file
students_examined = []
if path.exists("outputloglist.txt"):
    with open("outputloglist.txt", "r") as output_log:
        students_examined = output_log.read().splitlines()
        output_log.close()


debug("Students Examined...")
for s in students_examined:
    debug(s)

with open("outputloglist.txt", "a") as output_log:
    with open("outputscores.txt", "a") as output_scores:
        labdir = listdir(".working/zip_contents")
        for student_name in listdir(".working/zip_contents/" + labdir[0]):
            output_log.write(student_name + linesep)
            debug("Finding files for: " + student_name)
            debug("Checking if already examined.")
            if student_name in students_examined:
                debug("Already examined.")
                continue
            debug("Checking for grades.csv")
            if student_name == "grades.csv":
                debug("Skipping grades.csv")
                continue
            submitted_files = listdir(".working/zip_contents/" + labdir[0] +"/" + student_name + "/" + "Submission attachment(s)")
            suspected_script = ""
            for file in submitted_files:
                debug("Examining " + file)
                name, extension = path.splitext(file)
                if suspected_script == "":
                    if extension == ".sh":
                        suspected_script = file
                    if extension == ".sh~":
                        suspected_script = file
                    elif "script" in name.lower():
                        suspected_script = file
                    elif extension == ".txt":
                        suspected_script = file
                    elif "shell" in name.lower():
                        suspected_script = file
                    elif "10" in name.lower():
                        suspected_script = file
            debug("Suspected script is: " + suspected_script)
            if suspected_script == "":
                debug("Suspected script not found.")
                continue
            suspected_script = ".working/zip_contents/" + labdir[0] +"/" + student_name + "/" + "Submission attachment(s)" + "/" + suspected_script
            debug("Suspected script full path is: " + suspected_script)
            name, extension = path.splitext(suspected_script)
            if extension != ".sh":
                safety = ""
                while safety != "y" and safety != "n":
                    print suspected_script + " appears to be a weird file type."
                    safety = raw_input("Do you want to try to run it anyways? (This might crash) (y/n)")
                if safety == "n":
                    continue

            debug("Copying file...")
            copyfile(suspected_script, ".working/test/script.sh")
            chdir(".working/test")
            debug("Trying to run command.")
            print "\nGrading Student: " + student_name
            print "About to start the script. If this hangs, you'll want to CTRL+C. If it crashes, the student's script didn't work. In that case, just restart this script."
            shell_output = subprocess.check_output(["bash", "script.sh"])
            chdir("../..")
            print "Script Output: \n"
            print "-=-=-=-=-=-=-=-=-=-"
            print shell_output
            print "-=-=-=-=-=-=-=-=-=-"
            score = raw_input("Score? ")
            output_scores.write(student_name + " " + score + linesep)
        output_scores.close()
    output_log.close()

