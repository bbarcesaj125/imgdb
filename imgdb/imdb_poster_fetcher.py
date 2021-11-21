from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from tqdm import tqdm


def imdb_download_poster():
    url = "http://www.ovh.net/files/10Mb.dat"
    file_name = url.split("/")[-1]
    r = urlopen(url)
    file_size = int(r.getheader("Content-Length"))
    print("Downloading: %s Size: %s" % (file_name, file_size))

    block_size = 1024
    progress_bar = tqdm(total=file_size, unit="iB", unit_scale=True)
    with open(file_name, "wb") as f:
        while True:
            buffer = r.read(block_size)
            if not buffer:
                break

            f.write(buffer)
            progress_bar.update(len(buffer))
    progress_bar.close()
    if file_size != 0 and progress_bar.n != file_size:
        print("It looks like something unexpected happened. Aborting!")


if __name__ == "__main__":
    imdb_download_poster()
