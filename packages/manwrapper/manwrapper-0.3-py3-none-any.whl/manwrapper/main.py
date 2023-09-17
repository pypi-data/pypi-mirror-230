import subprocess
import sys

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print("Usage: manwrapper <topic>")
        print("Please provide a topic for the manual.")
        sys.exit(1)

    manTopic = sys.argv[1]

    cmd = ['man', '-P', 'cat', manTopic]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    encoding = sys.getdefaultencoding()

    if stdout:
        print(stdout.decode(encoding))
    if stderr:
        print("Error:", stderr.decode(encoding))

if __name__ == "__main__":
    main()
