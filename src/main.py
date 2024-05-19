import argparse


def main():
    parser = argparse.ArgumentParser(description="Process some addresses.")
    parser.add_argument('address', metavar='address', type=str)
    args = parser.parse_args()
    print(args.address)


if __name__ == '__main__':
    main()
