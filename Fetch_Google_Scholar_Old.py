"""
This is test code and may not work for long (if at all) as Google constantly changes their interface without an API
"""

# import urllib.request
import datetime
# import time
import requests


class Publication:
    def __init__(self):
        self.year = 0
        self.author = 0
        self.order = 0
        self.article_code = ""
        self.citation_nums = ""
        self.cite_data = {}


def read_input_data(file_name: str) -> list:
    with open(file_name, "r") as infile:
        file_data = infile.readlines()
    input_data = []
    for line in file_data[1:]:  # skip header
        new_pub = Publication()
        data = line.strip().split("\t")
        new_pub.year = data[0]
        new_pub.author = data[1]
        new_pub.order = data[2]
        new_pub.article_code = data[3]
        new_pub.citation_nums = data[4]
        input_data.append(new_pub)
    return input_data


def get_webpage(url: str, encoding: str) -> str:
    """
    function to fetch the webpage specifed by url and
    return a single string containing the contents of the page
    """
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 '
                             '(KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}
    # webpage = urllib.request.urlopen(url, headers=headers)
    webpage = requests.get(url, headers=headers)
    # page = webpage.read()
    # page = page.decode(encoding, "ignore")
    # return page
    # print(webpage.text)
    return webpage.text


def extract_cite_count(page: str) -> int:
    query = "<div id=\"gs_ab_md\"><div class=\"gs_ab_mdw\">"
    if "Your search did not match any articles" in page:
        return 0
    else:
        p = page.find(query)
        x = page[p+len(query):]
        # print(x)
        if "About" in x:
            x = x.replace("About", "")
        x = x[:x.find("result")]
        # print(x)
        try:
            n = int(x.strip())
        except ValueError:
            n = -1
        return n


def dump_page(text: str, pub: Publication, year: str) -> None:
    with open("tmp_data_{}_{}.txt".format(pub.article_code, year), "w", encoding="UTF-8") as outfile:
        outfile.write(text)


def fetch_pub_data(pub: Publication) -> None:
    req_cnt = 0
    min_req_cnt = 0
    current_year = datetime.datetime.now().year
    # reset citation data
    pub.cite_data["total"] = 0
    for y in range(1997, current_year + 1):
        pub.cite_data[y] = 0
    if pub.citation_nums == ".":
        print("  None  ")
    else:
        with open("scraper_api_key.txt", "r") as infile:
            apikey = infile.read().strip()
        # curl "http://api.scraperapi.com?api_key=23038b92027c20f7ed0ed02852911337&url=http://httpbin.org/ip"
        scraper_url = "http://api.scraperapi.com?api_key=" + apikey + "&url="

        total_prefix = "https://scholar.google.com/scholar?oi=bibs&hl=en&cites="
        sub_prefix = "https://scholar.google.com/scholar?hl=en&as_sdt=0%2C47&sciodt=0%2C47&cites={}&scipsc="
        try_again = True
        try_cnt = 0
        total_cites = -1
        min_req_cnt += 1
        while try_again and try_cnt < 5:
            req_cnt += 1
            total_page = get_webpage(scraper_url + total_prefix + pub.citation_nums, "UTF-8")
            dump_page(total_page, pub, "total")
            total_cites = extract_cite_count(total_page)
            try_cnt += 1
            if total_cites > -1:
                try_again = False
        print("  Total:", total_cites)
        pub.cite_data["total"] = total_cites
        if total_cites > 0:
            # everything up publication year
            start_year = int(pub.year)
            # start_year = 1997
            # time.sleep(45)
            try_again = True
            try_cnt = 0
            y_cites = -1
            min_req_cnt += 1
            while try_again and try_cnt < 5:
                req_cnt += 1
                year_page = get_webpage(scraper_url + sub_prefix.format(pub.citation_nums) + "&as_yhi={0}".format(start_year), "UTF-8")
                dump_page(year_page, pub, str(start_year))
                y_cites = extract_cite_count(year_page)
                if y_cites > -1:
                    try_again = False
            print("  -"+str(start_year), y_cites)
            pub.cite_data[start_year] = y_cites
            for y in range(start_year+1, current_year+1):  # one year at a time
                # time.sleep(45)
                try_again = True
                try_cnt = 0
                y_cites = -1
                min_req_cnt += 1
                while try_again and try_cnt < 5:
                    req_cnt += 1
                    year_page = get_webpage(scraper_url + sub_prefix.format(pub.citation_nums) + "&as_ylo={0}&as_yhi={0}".format(y), "UTF-8")
                    dump_page(year_page, pub, str(y))
                    y_cites = extract_cite_count(year_page)
                    if y_cites > -1:
                        try_again = False
                print(" ", y, y_cites)
                pub.cite_data[y] = y_cites
        else:  # skip searching google scholar and add numbers for uncited pubs
            for y in range(1997, current_year+1):
                pub.cite_data[y] = 0
    print("# requests = {}, minimum possible requests = {}".format(req_cnt, min_req_cnt))


def write_output(pub_data: list) -> None:
    current_year = datetime.datetime.now().year
    with open("GSCitation.txt", "w") as outfile:
        # header
        outfile.write("Year\t# Authors\tOrder\tArticle")
        for y in range(1997, current_year+1):
            outfile.write("\t12/31/{}".format(y))
        outfile.write("\t\tYear Total\tTotal\n")
        # publication data
        for pub in pub_data:
            print(pub.article_code, pub.cite_data["total"], sep="\t", end="")
            csum = 0
            outfile.write("{}\t{}\t{}\t{}".format(pub.year, pub.author, pub.order, pub.article_code))
            precite = 0
            for y in range(1997, current_year+1):
                if y < int(pub.year):
                    outfile.write("\tn/a")
                    precite += pub.cite_data[y]
                elif y == int(pub.year):
                    outfile.write("\t{}".format(pub.cite_data[y] + precite))
                else:
                    outfile.write("\t{}".format(pub.cite_data[y]))
                csum += pub.cite_data[y]
                print("\t" + str(pub.cite_data[y]), end="")
            outfile.write("\t\t{}\t{}\n".format(csum, pub.cite_data["total"]))
            print("\t" + str(csum))


def main():
    print("Get Data from Google Scholar")
    print()
    default = "impact_google_input.txt"
    data_name = input("Enter name of data file (default = {}): ".format(default))
    if data_name == "":
        data_name = default
    pub_data = read_input_data(data_name)
    print()
    for pub in pub_data:
        print("Fetching data from", pub.article_code)
        fetch_pub_data(pub)
    write_output(pub_data)


if __name__ == "__main__":
    main()
