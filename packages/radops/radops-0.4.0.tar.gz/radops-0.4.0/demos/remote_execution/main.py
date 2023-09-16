import sys

from radops.settings import settings

if __name__ == "__main__":
    if len(sys.argv) >= 2:
        if sys.argv[1] == "settings":
            print(settings)
        else:
            print(sys.argv[1])
    else:
        print("Hello world.")
