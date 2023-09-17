import subprocess
import sys

def get_man_page(topic):
    cmd = ['man', '-P', 'cat', topic]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    encoding = sys.getdefaultencoding()

    if stdout:
        return stdout.decode(encoding)
    if stderr:
        return "Error: " + stderr.decode(encoding)

def main():
    if len(sys.argv) < 2 or sys.argv[1] in ['-h', '--help']:
        print("Usage: manwrapper <topic>")
        print("Please provide a topic for the manual.")
        sys.exit(1)

    manTopic = sys.argv[1]
    output = get_man_page(manTopic)
    print(output)

if __name__ == "__main__":
    main()
