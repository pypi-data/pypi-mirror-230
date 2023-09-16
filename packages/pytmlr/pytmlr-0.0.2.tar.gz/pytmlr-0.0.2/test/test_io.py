from pyt.fileio import load, dump
import torch
import numpy as np


def test_dump():
    x = np.zeros(n, dtype=np.int32)
    dump(x, "./data/test.pkl")
    dump(x, "./data/test.pgz")
    dump(x, "./data/test.pbz2")
    dump(x, "./data/test.npy")
    x = [0] * n
    dump(x, "./data/test.json")
    dump(x, "./data/test.yaml")
    x = "Hello World!"
    dump(x, "./data/test.txt")
    x = torch.zeros(n, dtype=torch.int32, device="cuda")
    dump(x, "./data/test.pt")

    image = load("https://github.com/imageio/imageio-binaries/raw/master/images/clock.png")
    dump(image, "./data/test.png")
    dump(image, "./data/test.jpg")
    dump(image, "./data/test.jpeg")

    image = np.stack([image] * 10, axis=0)
    dump(image, "./data/test.gif")


def test_load():
    image = load("https://github.com/imageio/imageio-binaries/raw/master/images/clock.png")
    assert image.shape == (300, 400), f"{image.shape} {image.dtype}"

    image = load("https://github.com/imageio/imageio-binaries/raw/master/images/bricks.jpg")
    assert image.shape == (512, 512, 3), f"{image.shape} {image.dtype}"

    image = load("https://upload.wikimedia.org/wikipedia/commons/d/d3/Newtons_cradle_animation_book_2.gif")
    assert image.shape == (36, 360, 480, 3), f"{image.shape} {image.dtype}"

    x = load("./data/test.pkl")
    assert x.shape == (n,) and (x == 0).all(), f"{x.shape} {x}"
    x = load("./data/test.pgz")
    assert x.shape == (n,) and (x == 0).all(), f"{x.shape} {x}"
    x = load("./data/test.pbz2")
    assert x.shape == (n,) and (x == 0).all(), f"{x.shape} {x}"
    x = load("./data/test.npy")
    assert x.shape == (n,) and (x == 0).all(), f"{x.shape} {x}"

    x = load("./data/test.json")
    assert x == [0] * n, f"{x.shape} {x}"
    x = load("./data/test.yaml")
    assert x == [0] * n, f"{x.shape} {x}"
    x = load("./data/test.txt")
    assert x == "Hello World!"

    x = load("./data/test.pt")
    assert x.shape == (n,) and (x == 0).all(), f"{x.shape} {x}"


if __name__ == "__main__":
    n = 1000
    test_dump()
    test_load()
