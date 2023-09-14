import unittest

from refrot import hparser


class TestParser(unittest.TestCase):
    def test_make_link_absolute(self):
        parser = hparser.LinkParser()
        base = 'http://foo.us/blog/politics/'

        url = 'projects.html'
        link = parser.make_link_absolute(base, url)
        self.assertEqual(link, 'http://foo.us/blog/politics/projects.html')

        url = '../projects.html'
        link = parser.make_link_absolute(base, url)
        self.assertEqual(link, 'http://foo.us/blog/projects.html')

        url = '../../projects.html'
        link = parser.make_link_absolute(base, url)
        self.assertEqual(link, 'http://foo.us/projects.html')

        base = 'http://foo.us/blog/politics/hello.html'

        url = 'projects.html'
        link = parser.make_link_absolute(base, url)
        self.assertEqual(link, 'http://foo.us/blog/politics/projects.html')

        url = '../projects.html'
        link = parser.make_link_absolute(base, url)
        self.assertEqual(link, 'http://foo.us/blog/projects.html')

        url = '../../projects.html'
        link = parser.make_link_absolute(base, url)
        self.assertEqual(link, 'http://foo.us/projects.html')

    def test_parse(self):
        HTML = """
            <!DOCTYPE html>
            <html lang='en'>
            <body>
                <a href='../index.html'>Home</a>
                <a href='../projects.html'>Projects</a>
                <a href='mailto:craig@seagrape.us'>Contact</a>
                <a href='#section1'>Section 1</a>
                <a href='hello.html'>hello post</a>
                <a href='goodbye.html'>goodbye post</a>
            </body>
            </html>
        """
        parser = hparser.LinkParser()
        parser.feed(HTML)
        self.assertEqual(len(parser.links), 4)
        self.assertEqual(parser.links[0], '../index.html')
        self.assertEqual(parser.links[1], '../projects.html')
        self.assertEqual(parser.links[2], 'hello.html')
        self.assertEqual(parser.links[3], 'goodbye.html')

    def test_absolute_links(self):
        HTML = """
            <!DOCTYPE html>
            <html lang='en'>
            <body>
                <a href='../index.html'>Home</a>
                <a href='../projects.html'>Projects</a>
                <a href='mailto:craig@seagrape.us'>Contact</a>
                <a href='#section1'>Section 1</a>
                <a href='hello.html'>hello post</a>
                <a href='goodbye.html'>goodbye post</a>
            </body>
            </html>
        """
        parser = hparser.LinkParser()
        parser.feed(HTML)
        url = 'https://foo.com/blog/index.html'
        parser.make_links_absolute(url)
        self.assertEqual(parser.links[0], 'https://foo.com/index.html')
        self.assertEqual(parser.links[1], 'https://foo.com/projects.html')
        self.assertEqual(parser.links[2], 'https://foo.com/blog/hello.html')
        self.assertEqual(parser.links[3], 'https://foo.com/blog/goodbye.html')

    def test_ignore_internal_links(self):
        HTML = """
            <!DOCTYPE html>
            <html lang='en'>
            <body>
                <a href='index.html'>Home</a>
                <a href='projects.html'>Projects</a>
                <a href='#section1'>Section 1</a>
                <a href='hello.html#sincere'>hello post</a>
                <a href='goodbye.html#tearful'>goodbye post</a>
            </body>
            </html>
        """
        parser = hparser.LinkParser()
        parser.feed(HTML)
        self.assertEqual(len(parser.links), 4)
        self.assertEqual(parser.links[0], 'index.html')
        self.assertEqual(parser.links[1], 'projects.html')
        self.assertEqual(parser.links[2], 'hello.html')
        self.assertEqual(parser.links[3], 'goodbye.html')

    def test_header_links(self):
        HTML = """
            <!DOCTYPE html>
            <html lang='en'>
            <head>
                <link href='static/img/1.png'>
                <link href='static/js/2.js'>
                <link href='static/css/3.css'>
            </head>
            <body>
                <p>Hello</p>
            </body>
            </html>
        """
        parser = hparser.LinkParser()
        parser.feed(HTML)
        self.assertEqual(len(parser.links), 3)
        self.assertEqual(parser.links[0], 'static/img/1.png')
        self.assertEqual(parser.links[1], 'static/js/2.js')
        self.assertEqual(parser.links[2], 'static/css/3.css')

    def test_img_links(self):
        HTML = """
            <!DOCTYPE html>
            <html lang='en'>
            <body>
                <img src="img/a.jpg">
            </body>
            </html>
        """
        parser = hparser.LinkParser()
        parser.feed(HTML)
        self.assertEqual(len(parser.links), 1)
        self.assertEqual(parser.links[0], 'img/a.jpg')


if __name__ == '__main__':
    unittest.main()

