import sys
import kdistiller


def main():

    print(f"Welcome to kdistiler, version {kdistiller.__version__}")

    if len(sys.argv) > 1:
        print(sys.argv[1])
    else:
        print("no arg given")


if __name__ == "__main__":
    main()
