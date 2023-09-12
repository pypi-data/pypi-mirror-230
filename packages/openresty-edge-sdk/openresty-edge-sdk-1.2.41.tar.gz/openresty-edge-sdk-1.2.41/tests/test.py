# -*- coding: utf-8 -*-

import unittest
import sys
import re


def main(argv):
    suite = unittest.TestSuite()
    testLoader = unittest.TestLoader

    pattern = argv[0] if argv and argv[0] else 'test_*.py'
    mobj = re.match('.*/?tests/(.+)', pattern)
    if mobj:
        pattern = mobj.group(1)

    suite.addTests(testLoader().discover('./tests', pattern=pattern))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    sys.exit(not result.wasSuccessful())


if __name__ == "__main__":
    main(sys.argv[1:])
