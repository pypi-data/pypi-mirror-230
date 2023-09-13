from api import HDGBavariaAPI


def main():
    test = HDGBavariaAPI("https://myhdg-demo.hdg-bavaria.com")
    print(test.get_data())


if __name__ == "__main__":
    main()
