import subprocess
import sys

def main():
    if len(sys.argv) < 2:
        print("Por favor, proporciona un tema para el manual.")
        sys.exit(1)

    manTopic = sys.argv[1]

    cmd = ['man', '-P', 'cat', manTopic]

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = p.communicate()

    if stdout:
        print(stdout.decode('utf-8'))
    else:
        print("Error:", stderr.decode('utf-8'))

if __name__ == "__main__":
    main()
