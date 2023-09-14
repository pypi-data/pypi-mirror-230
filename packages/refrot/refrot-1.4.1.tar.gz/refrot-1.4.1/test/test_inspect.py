import unittest

from refrot.inspect import static_url


class TestInspect(unittest.TestCase):
    def test_static_url(self):
        url = 'http://mysite.com/simple.js'
        self.assertEqual(static_url(url), True)

        url = 'http://mysite.com/simple.css'
        self.assertEqual(static_url(url), True)

        url = 'http://mysite.com/robots.txt'
        self.assertEqual(static_url(url), True)

        url = 'http://mysite.edu/simple.js?v=4825356b'
        self.assertEqual(static_url(url), True)

        url = 'http://mysite.com'
        self.assertEqual(static_url(url), False)

        url = 'http://mysite.com/accounts'
        self.assertEqual(static_url(url), False)

        url = 'http://mysite.com/accounts/'
        self.assertEqual(static_url(url), False)

        url = 'http://mysite.us/accounts/'
        self.assertEqual(static_url(url), False)

        url = 'http://mysite.edu/accounts/'
        self.assertEqual(static_url(url), False)

        url = 'http://mysite.edu/accounts.htm'
        self.assertEqual(static_url(url), False)

        url = 'http://mysite.edu/accounts.html'
        self.assertEqual(static_url(url), False)


if __name__ == '__main__':
    unittest.main()

